# email widget (T2 platform)

Business email management for an artist's own domain. Lists and manages
mailboxes + forwarding rules on the shared Purelymail account, and renders
ready-made Gmail / IMAP / POP connection setup per mailbox (server settings
are constant; the address is filled in dynamically).

## Backend endpoints (in `_shared/admin_api.py`)
- `GET  /api/adze/email-status` — mailboxes, forwards, + client settings for the artist's domain
- `POST /api/adze/email-add-mailbox` — `{localpart}` → creates mailbox, returns one-time password
- `POST /api/adze/email-delete-mailbox` — `{address}`
- `POST /api/adze/email-add-forward` — `{localpart, targets:[...]}`
- `POST /api/adze/email-delete-forward` — `{id}`

All ops are scoped to the artist's `config.json` `domain`.

## Setup
1. Workspace 'email' integration in `_shared/workspaces.py` holds
   `purelymail_token` (from `PURELYMAIL_API_TOKEN`) + the constant IMAP/POP/SMTP
   hosts. The token env var is wired in `docker-compose.yml` and `.env`.
2. Opt an artist in: add `"email"` to `platform_widgets` in their `config.json`.
3. `sudo docker restart adze-flask`.

## Notes
- One Purelymail account backs every workspace domain — marginal cost per
  client ≈ £0. This is the reson the panel can become a billable Adze tier.
- The widget never stores mailbox passwords; the create call shows the
  generated password once. Reading mail stays in the user's own client.
