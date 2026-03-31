# subscribers widget (T2 platform)

Manages the artist's email subscriber list — view all subscribers, delete individual entries, and export the full list as CSV.

## Built-in endpoints it calls (no setup needed)
- `GET /api/adze/list-subscribers` — fetches all subscribers for this artist
- `POST /api/adze/delete-subscriber` — removes a subscriber by email
- `GET /api/adze/export-subscribers` — returns a CSV download of all subscribers

## Custom endpoints
None — fully self-contained.

## Setup
No credentials needed. Subscribers are collected automatically when visitors submit an email capture form on the artist's site. No api.py changes required.
