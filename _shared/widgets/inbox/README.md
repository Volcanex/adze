# inbox widget (T2 platform)

Displays contact form submissions sent to the artist's site — read/unread status, delete, and mark-all-read. Works with the built-in contact form submission system.

## Built-in endpoints it calls (no setup needed)
- `GET /api/adze/list-submissions` — fetches all contact form submissions for this artist
- `POST /api/adze/delete-submission` — deletes a submission by ID
- `POST /api/adze/mark-submission-read` — marks a submission read or unread by ID

## Custom endpoints
None — fully self-contained.

## Setup
No credentials needed. Works automatically as long as the artist's site has a contact form that posts to the built-in submission endpoint. No api.py changes required.
