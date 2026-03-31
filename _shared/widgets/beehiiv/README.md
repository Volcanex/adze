# beehiiv widget (T2 platform)

Tracks Beehiiv newsletter stats and recent posts — subscriber count, open rates, and latest publications shown in the artist dashboard.

## Built-in endpoints it calls (no setup needed)
- `POST /api/adze/beehiiv-verify` — validates the API key and publication ID, stores credentials
- `GET /api/adze/beehiiv-stats` — fetches subscriber stats and recent posts from Beehiiv API

## Custom endpoints
None — fully self-contained.

## Setup
Artist enters their Beehiiv API key (`key_…`) and Publication ID in the widget settings panel. The widget verifies and stores them server-side. No api.py changes required.
