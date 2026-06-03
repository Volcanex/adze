# Shared — Flask code, docs, widgets, and themes

Platform code shared across all artist sites. Organised into a few subsystems:

- `admin_api.py` — the `/api/adze/*` endpoints (admin dashboard,
  artist management, file edit, deploy, analytics).
- `auth.py`, `db.py` — per-artist auth + SQLite analytics database.
- `dashboard.html` — single-file admin UI served to Gabriel.
- `widgets/` — dashboard-privileged Flask blueprints (stripe, youtube,
  beehiiv, vimeo, calendly, inbox, subscribers). See `widgets/CLAUDE.md`.
- `features/` — modular site-wide capabilities (e.g. `bookings.py`). See
  `features/CLAUDE.md`.
- `terminal_bridge.py` — Socket.IO/tmux bridge for Terminal Access.
- `autocode_proxy.py` — Flask reverse-proxy for the Auto-Code chat tab.
  Spawns `opencode serve` inside each per-artist sandbox container and
  forwards REST + `/global/event` SSE under `/api/adze/autocode/*`. The
  proxy unwraps opencode's `{directory, project, payload}` SSE envelope
  so the browser receives clean events. Replaced the old TUI-in-xterm
  bridge (`auto_code_bridge.py`, retired).
- `asset_store.py` — shared asset-storage primitives behind **both** the
  admin dashboard (`/api/adze/upload-file`) and the intake portal
  (`/api/adze/intake/<slug>/<token>/upload`): `safe_rel()` (per-segment
  `secure_filename`, Zip-Slip guard), `store_fileobj()` (save at a client
  `rel_path` + output mirror + `asset_meta`), and `extract_zip()` (unpack
  preserving the folder tree, skipping dirs/`__MACOSX`/dotfiles, with an
  ext-policy callback + file/byte caps). Both upload endpoints accept a
  `rel_path` form field (folder picker / `webkitdirectory`) and a `.zip` with
  `extract=1`. Intake roots everything under `intake/` so its delete/label
  boundary still holds; admin preserves structure directly under `assets/`.
  Folder support is **local artists only** — external (remote Seed) asset ops
  don't route through these endpoints.
- `asset_tree.js` — the shared **frontend** half, served at
  `/api/adze/asset-tree.js` (same-origin route, not `/static`). `window.AssetTree`
  gives both `admin.html` and `intake.html` identical folder-tree navigation
  (`level`/`crumbHTML`/`folderTileHTML`), folder/zip upload collection
  (`filesFromInput`/`filesFromDataTransfer` → `upload`), and one-time CSS
  (`injectCSS`). Each page keeps its own tile/label markup; only the new
  folder code is shared.
- `sandbox.py` — shared container-lifecycle helpers (name, network,
  volume mounts, `ensure_terminal_container`). Used by `autocode_proxy`;
  `terminal_bridge` still has its own copy — fold them later.
- `docs/` — the **Terminal Access / Claude Code context**. Load-bearing.

## `docs/` is load-bearing — do not delete

`terminal_bridge.py` builds a per-artist context from `_shared/docs/*.md`
(in filename order), then appends artist config/page information before
launching Claude Code inside the artist tmux session. Legacy
`admin_api.py` prompt helpers may still read these docs too. This is how
Terminal Access learns Adze conventions.

- **To update Terminal Access behaviour:** edit or add a numbered file
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
Gabriel-only tooling. Terminal Access is scoped to the artist site and
should not create dashboard widgets unless Gabriel explicitly changes
that boundary — see `_shared/docs/00-behaviour.md` lines 31–37 for why.

## Gotchas

- `shared/` (no underscore) at the repo root is a legacy stub — use
  `_shared/` only.
- Changes here take effect after `docker restart adze-flask` (source is
  bind-mounted, no rebuild needed).
