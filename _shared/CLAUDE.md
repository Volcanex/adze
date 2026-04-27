# Shared — Flask code, docs, widgets, and themes

Platform code shared across all artist sites. Organised into a few subsystems:

- `admin_api.py` — the `/api/adze/*` endpoints (admin dashboard, vibe
  coder, artist management, file edit, deploy, analytics).
- `auth.py`, `db.py` — per-artist auth + SQLite analytics database.
- `dashboard.html` — single-file admin UI served to Gabriel.
- `widgets/` — dashboard-privileged Flask blueprints (stripe, youtube,
  beehiiv, vimeo, calendly, inbox, subscribers). See `widgets/CLAUDE.md`.
- `features/` — modular site-wide capabilities (e.g. `bookings.py`). See
  `features/CLAUDE.md`.
- `docs/` — the **vibe coder's system prompt**. Load-bearing.

## `docs/` is load-bearing — do not delete

`admin_api.py`'s `_get_artist_system_prompt()` concatenates every `.md`
file in `_shared/docs/` (in filename order) and feeds the result to the
in-browser vibe coder as its system prompt. That's how the vibe coder
knows Adze conventions.

- **To update vibe-coder behaviour:** edit or add a numbered file
  (`NN-name.md`) in `_shared/docs/`. See `_shared/docs/DOCS_GUIDE.md`.
- **Do not** rename, reorder, or delete `_shared/docs/*.md` files
  without updating the code path too.
- Structure is documented in `_shared/docs/DOCS_GUIDE.md` itself (lines
  15–21).

## Adding a widget or feature

See the relevant CLAUDE.md:
- New widget → `_shared/widgets/CLAUDE.md`
- New platform-wide feature → `_shared/features/CLAUDE.md`

Widgets run with admin auth and can write to artist pages; they are
Gabriel-only tooling. The artist-facing vibe coder cannot create
widgets — see `_shared/docs/00-behaviour.md` lines 31–37 for why.

## Gotchas

- `shared/` (no underscore) at the repo root is a legacy stub — use
  `_shared/` only.
- Changes here take effect after `docker restart adze-flask` (source is
  bind-mounted, no rebuild needed).
