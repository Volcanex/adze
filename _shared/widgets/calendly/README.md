# calendly widget (T2 platform)

Shows upcoming meetings and the artist's scheduling link — pulls live event data from Calendly so the artist can see what's booked from their dashboard.

## Built-in endpoints it calls (no setup needed)
- `POST /api/adze/calendly-verify` — validates the personal access token, stores credential
- `GET /api/adze/calendly-stats` — fetches upcoming scheduled events from Calendly API

## Custom endpoints
None — fully self-contained.

## Setup
Artist enters their Calendly personal access token (`eyJraWQi…`) in the widget settings panel. Token needs read access to events. No api.py changes required.
