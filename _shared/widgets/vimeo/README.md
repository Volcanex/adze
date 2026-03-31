# vimeo widget (T2 platform)

Shows the artist's Vimeo portfolio with video thumbnails, play counts, and a lightbox player — plus channel-level stats like total views and followers.

## Built-in endpoints it calls (no setup needed)
- `POST /api/adze/vimeo-verify` — validates the access token, stores credential
- `GET /api/adze/vimeo-stats` — fetches channel stats and video list from Vimeo API

## Custom endpoints
None — fully self-contained.

## Setup
Artist enters their Vimeo personal access token in the widget settings panel. The token must have **Public** and **Private** scopes — generate one in Vimeo Developer settings by creating an app. No api.py changes required.
