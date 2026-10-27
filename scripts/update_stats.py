#!/usr/bin/env python3
"""Pull this year's Garmin activities and write year-to-date totals for the site.

Runs daily from .github/workflows/garmin-stats.yml. Needs one secret:
GARMIN_API_KEY, a Personal API key created in Garmin Connect (web) under
Settings > Personal API Key.

Only totals are written to _data/stats.json. No maps, routes, locations,
times of day or health data ever leave Garmin through this script.

Run locally:  GARMIN_API_KEY=... python3 scripts/update_stats.py
"""

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_HOST = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
ACTIVITIES_PATH = "/activitylist-service/activities/search/activities"
PAGE_SIZE = 50
MAX_PAGES = 40  # 2,000 activities, far more than a year needs

OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "_data", "stats.json")

# ---------------------------------------------------------------------------
# What counts as what. These are Garmin's activity type keys. Edit the lists
# to change how activities are counted.
# ---------------------------------------------------------------------------
GYM_TYPES = {
    "strength_training",
    "pilates",
    "hiit",
    "indoor_cardio",
    "fitness_equipment",
    "elliptical",
    "stair_climbing",
    "indoor_rowing",
}
# Not counted anywhere (everyday movement rather than training).
IGNORED_TYPES = {"walking", "casual_walking", "speed_walking", "other"}

CLIMBING_WORDS = ("climb", "boulder")


def is_ride(key):
    return "cycl" in key or "biking" in key or key in {"virtual_ride", "bmx"}


def is_ski(key):
    return "ski" in key or "snowboard" in key


def bucket(key):
    """Return 'ride', 'gym', 'ski', 'climb', 'other' or None (ignored)."""
    key = (key or "").lower()
    if is_ride(key):
        return "ride"
    if key in GYM_TYPES:
        return "gym"
    if is_ski(key):
        return "ski"
    if any(w in key for w in CLIMBING_WORDS):
        return "climb"
    if key in IGNORED_TYPES:
        return None
    return "other"


LABELS = {
    "road_biking": "Road ride",
    "gravel_cycling": "Gravel ride",
    "mountain_biking": "Mountain bike ride",
    "cyclocross": "Cyclocross ride",
    "indoor_cycling": "Indoor ride",
    "virtual_ride": "Virtual ride",
    "strength_training": "Strength session",
    "pilates": "Pilates",
    "resort_skiing": "Ski day",
    "resort_skiing_snowboarding_ws": "Ski day",
    "backcountry_skiing": "Backcountry ski",
    "cross_country_skiing_ws": "XC ski",
    "skate_skiing_ws": "Skate ski",
    "indoor_climbing": "Climbing session",
    "bouldering": "Bouldering session",
}


def label_for(key):
    key = (key or "").lower()
    if key in LABELS:
        return LABELS[key]
    if is_ride(key):
        return "Ride"
    if is_ski(key):
        return "Ski"
    if any(w in key for w in CLIMBING_WORDS):
        return "Climbing session"
    return key.replace("_", " ").capitalize() or "Activity"


# ---------------------------------------------------------------------------
# Garmin API
# ---------------------------------------------------------------------------
def _request(method, url, headers):
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        hint = ""
        if err.code in (401, 403):
            hint = " The Garmin key may be wrong, deleted or expired. Create a new one and update the GARMIN_API_KEY secret."
        elif err.code == 429:
            hint = " Garmin is rate limiting requests. The next daily run will try again."
        raise SystemExit(f"Garmin request failed: HTTP {err.code} for {urllib.parse.urlsplit(url).path}.{hint}")
    except urllib.error.URLError as err:
        raise SystemExit(f"Could not reach Garmin: {err.reason}")


def get_access_token(api_key):
    body = _request("POST", API_HOST + TOKEN_PATH, {
        "Authorization": f"ApiKey {api_key}",
        "Accept": "application/json, text/plain",
    }).strip()
    # Garmin may return the token as plain text or inside JSON.
    try:
        data = json.loads(body)
    except ValueError:
        return body.strip('"')
    if isinstance(data, str):
        return data
    for field in ("access_token", "accessToken", "token"):
        if isinstance(data, dict) and data.get(field):
            return data[field]
    raise SystemExit("Garmin returned a token response in an unexpected format.")


def fetch_activities(token, start_date, end_date):
    """Newest-first list of activities between the two dates (inclusive)."""
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    found = []
    for page in range(MAX_PAGES):
        query = urllib.parse.urlencode({
            "start": page * PAGE_SIZE,
            "limit": PAGE_SIZE,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        })
        data = json.loads(_request("GET", f"{API_HOST}{ACTIVITIES_PATH}?{query}", headers))
        if isinstance(data, dict):
            data = data.get("activityList") or data.get("activities") or []
        if not data:
            break
        found.extend(data)
        oldest = activity_date(data[-1])
        if len(data) < PAGE_SIZE or (oldest and oldest < start_date):
            break
    return found


# ---------------------------------------------------------------------------
# Totals
# ---------------------------------------------------------------------------
def activity_date(a):
    stamp = a.get("startTimeLocal") or a.get("startTimeGMT") or ""
    try:
        return dt.date.fromisoformat(str(stamp)[:10])
    except ValueError:
        return None


def type_key(a):
    t = a.get("activityType")
    if isinstance(t, dict):
        return t.get("typeKey", "")
    return str(t or "")


def summarize(activities, year):
    miles = 0.0
    rides = other = 0
    ski_dates = set()
    gym_dates = set()
    climb_dates = set()
    latest = None
    seen = set()

    for a in activities:
        day = activity_date(a)
        if not day or day.year != year:
            continue
        ident = a.get("activityId") or (a.get("startTimeLocal"), type_key(a))
        if ident in seen:
            continue
        seen.add(ident)

        key = type_key(a).lower()
        kind = bucket(key)
        if kind is None:
            continue
        if kind == "ride":
            rides += 1
            miles += float(a.get("distance") or 0) / 1609.344
        elif kind == "gym":
            gym_dates.add(day)
        elif kind == "ski":
            ski_dates.add(day)
        elif kind == "climb":
            climb_dates.add(day)
        else:
            other += 1

        stamp = str(a.get("startTimeLocal") or day.isoformat())
        if latest is None or stamp > latest[0]:
            latest = (stamp, key, day)

    return {
        "year": year,
        "miles_ridden": round(miles),
        "rides": rides,
        "gym_days": len(gym_dates),
        "ski_days": len(ski_dates),
        "climbing_days": len(climb_dates),
        "other_sessions": other,
        "latest": {"label": label_for(latest[1]), "date": latest[2].isoformat()} if latest else None,
    }


def main():
    api_key = os.environ.get("GARMIN_API_KEY", "").strip()
    if not api_key:
        print("GARMIN_API_KEY is not set, so there is nothing to update yet.")
        return 0

    today = dt.date.today()
    year_start = dt.date(today.year, 1, 1)
    token = get_access_token(api_key)
    activities = fetch_activities(token, year_start, today)
    stats = summarize(activities, today.year)

    old = {}
    if os.path.exists(OUT_FILE):
        with open(OUT_FILE, encoding="utf-8") as f:
            old = json.load(f)
    old_core = {k: v for k, v in old.items() if k != "updated"}
    if old_core == stats:
        print("No change in totals.")
        return 0

    stats["updated"] = today.isoformat()
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        f.write("\n")
    print(f"Updated totals from {len(activities)} activities: "
          f"{stats['miles_ridden']} mi, {stats['gym_days']} gym days, "
          f"{stats['ski_days']} ski days, "
          f"{stats['climbing_days']} climbing days, {stats['other_sessions']} other.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
