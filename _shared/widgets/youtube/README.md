# youtube widget (T2 platform)

Tracks YouTube channel stats (subscribers, views, video count) and shows the latest uploads with thumbnails and view counts.

## Built-in endpoints it calls (no setup needed)
- `POST /api/adze/youtube-verify` — validates the API key and channel ID, stores credentials
- `GET /api/adze/youtube-stats` — fetches channel stats and latest videos from YouTube Data API v3

## Custom endpoints
None — fully self-contained.

## Setup
Artist enters their **YouTube Data API v3 key** (`AIzaSy…`) and **Channel ID** in the widget settings panel. The API key is obtained from Google Cloud Console — enable the YouTube Data API v3 on the project. No api.py changes required.
