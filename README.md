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
   ---

   Write the post here. Leave a blank line between paragraphs.

   ## A heading

   - a bullet
   - another bullet
   ```

   `image` and `youtube_id` are optional, so delete those lines if you don't need them. The YouTube id is the part after `watch?v=` in a video link.
4. Click **Commit changes**. The post appears on the Journal page and the home page.

A post dated in the future won't show up until that date has passed and the site rebuilds.

## Adding photos

Upload images to `assets/img/posts/` (**Add file → Upload files**). Keep them under about 500 KB: export from your phone or Lightroom at around 1600 px wide. Then use them in a post:

```
![Start line at Barry-Roubaix](/assets/img/posts/barry-start.jpg)
```

## Updating the race calendar

Edit `_data/season.yml`. Change `status` to `registered`, `lottery`, `planned`, `done` or `dropped`. Once you've written a race report, paste its link into `report`.

## Changing site settings

`_config.yml` holds the site description, the YouTube and Instagram links, and the email signup link (`newsletter_url`). Leave a link empty to hide it.

## Brand colors

These are at the top of `assets/css/style.css`: ground `#EEF0EC`, ink `#14201B`, accent orange `#E8562A`.
