# wheelieslow.com

The Wheelieslow website. It's a Jekyll site, which GitHub Pages builds and hosts for free. Every change you commit goes live within a minute or two.

## Writing a new post

1. Open the `_posts` folder and click **Add file → Create new file**.
2. Name it with the date and a short title, all lowercase with dashes:
   `2027-02-09-old-man-winter-race-report.md`
3. Paste this at the top, then write the post underneath in plain text:

   ```
   ---
   title: "Old Man Winter: race report"
   category: Race report
   summary: "One sentence that shows up on the post card."
   image: /assets/img/posts/old-man-winter.jpg
   youtube_id: dQw4w9WgXcQ
   strava_id: 12345678901
   ---

   Write the post here. Leave a blank line between paragraphs.

   ## A heading

   - a bullet
   - another bullet
   ```

   `image`, `youtube_id` and `strava_id` are optional, so delete those lines if you don't need them.
   - `youtube_id` puts the video at the top of the post. It's the part after `watch?v=` (or after `youtu.be/`) in the video link.
   - `strava_id` puts the ride (map, distance, elevation) at the bottom of the post under "The ride". It's the number at the end of the activity link: `strava.com/activities/12345678901`. The activity must be public on Strava, or the embed shows nothing.
4. Click **Commit changes**. The post appears on the Journal page and the home page.

A post dated in the future won't show up until that date has passed and the site rebuilds.

## Videos, rides and photos in the middle of a post

Put any of these on its own line, anywhere in a post, as many times as you like:

```
{% include youtube.html id="dQw4w9WgXcQ" %}
{% include strava.html id="12345678901" %}
{% include photo.html src="/assets/img/posts/barry-start.jpg" alt="Start line at Barry-Roubaix" caption="Cold start in Hastings" %}
```

`caption` is optional. `alt` describes the photo for people using screen readers.

## Adding photos

Upload images to `assets/img/posts/` (**Add file → Upload files**). Keep them under about 500 KB: export from your phone or Lightroom at around 1600 px wide. Then use them in a post:

```
![Start line at Barry-Roubaix](/assets/img/posts/barry-start.jpg)
```

## Updating the race calendar

Edit `_data/season.yml`. Change `status` to `registered`, `lottery`, `planned`, `done` or `dropped`. Once you've written a race report, paste its link into `report`.

## Changing site settings

`_config.yml` holds the site description, the YouTube, Instagram and Strava links, and the email signup link (`newsletter_url`). Leave a link empty to hide it.

It also has `home_photo` and `about_photo`. Upload a photo to `assets/img/`, then set, for example, `home_photo: "/assets/img/home.jpg"` and a short `home_photo_alt` description. The photo replaces the big WS wheel on that page. A tall (portrait) photo works best on the home page, and a square one on the About page.

## Brand colors

These are at the top of `assets/css/style.css`: ground `#EEF0EC`, ink `#14201B`, accent orange `#E8562A`.

## Garmin stats ("2026 so far" on the home page)

A GitHub Action (`.github/workflows/garmin-stats.yml`) runs every morning, asks Garmin for this year's activities, and saves only the totals to `_data/stats.json`: miles ridden, gym and Pilates sessions, ski days (counted once per day), and other activities. Walks aren't counted. No maps, routes or times are saved. The panel stays hidden until that file exists.

Setup, once:
1. In Garmin Connect on the web, go to **Settings → Personal API Key**, accept the terms, choose an expiry (1 year is easiest) and create the key. Copy it straight away; Garmin only shows it once.
2. In this repository, go to **Settings → Secrets and variables → Actions → New repository secret**. Name it `GARMIN_API_KEY` and paste the key.
3. Go to **Actions → Update Garmin stats → Run workflow** to run it now instead of waiting for the morning.

When the key expires, Garmin emails you about a week before. Create a new key and replace the secret.

To change what counts as what, edit the lists at the top of `scripts/update_stats.py`.

## Before launch

Set `hide_from_search: false` in `_config.yml` so search engines can list the site.
