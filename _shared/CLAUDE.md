# Shared — Flask code, docs, widgets, and themes

Platform code shared across all artist sites. Organised into a few subsystems:

- `admin_api.py` — the `/api/adze/*` endpoints (admin dashboard,
  artist management, file edit, deploy, analytics).
- `auth.py`, `db.py` — per-artist auth + SQLite analytics database.
- `dashboard.html` — single-file admin UI served to Gabriel.
- `widgets/` — dashboard-privileged Flask blueprints (stripe, youtube,
  beehiiv, vimeo, calendly, inbox, subscribers, email). See `widgets/CLAUDE.md`.
  `email` manages a site's business mailboxes + forwards on the shared
  Purelymail account (`integrations/purelymail.py`, workspace 'email' config).
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

## Workspace subdomains ({workspace}.adze.studio)

`admin.html` is the one admin SPA. It is served at `adze.studio/admin`
**and** at any `{workspace}.adze.studio` (wildcard vhost
`nginx/sites-available/workspace.adze.studio`, root → `/api/adze/admin`).
There is no separate per-workspace admin file — the dashboard scopes
itself to the logged-in identity's workspace (`_current_workspaces`), so
Clive (workspace `lastplace`) sees only his artists.

- **Redirect:** a non-super identity scoped to exactly one workspace is
  bounced from `adze.studio/admin` to `{workspace}.adze.studio` by
  `_applyIdentity` in `admin.html`. Super (Gabriel) is never redirected.
- **Cross-subdomain session:** `admin_login` sets `adze_admin_session`
  with `domain=.adze.studio` so one login carries across the redirect.
  `admin.html` `init()` falls back to `/admin/whoami` (cookie) when the
  origin has no localStorage token. **Consequence:** every admin endpoint
  must accept the cookie, not just the `X-Admin-Token` header — use
  `_require_super_admin()` (header+cookie), never a bare
  `is_admin_token(request.headers.get('X-Admin-Token'))`.

## Pipeline stage model (canonical)

The studio pipeline is one ordered list, `STAGES` in `admin.html`:
`contact → discovery → s01 → s02 → s03 → revisions → handover → hosting`.
It drives both the dashboard stage filter and the circular **stage loop**
on artist detail (`renderArtistStageLoop`). Stage lives in the lead block
(`lead.stage` in `artists/<slug>/config.json`, written via
`/admin/artists/<slug>/lead`). Legacy numeric `1-6` values auto-resolve
via `NUMERIC_TO_STAGE` (`resolveStage`); the existing data was migrated to
the new IDs. Add/rename a stage in the one `STAGES` array — everything
else derives from it.

## Pay engine + pot (Articles of Agreement)

Pricing follows Last Place's signed Articles. **Fish size is defined by the
job fee**, not chosen freely:

- `FISH_BANDS` is the canonical size→fee-ceiling→commission table, **mirrored
  in two places that must stay in sync**: JS in `admin.html` (live UI) and
  Python `FISH_BANDS`/`_fish_for_fee` in `admin_api.py` (authoritative writes
  + reconciliation). Bands: Minnow £0/0%, Perch ≤£260/4%, Mackerel ≤£650/8%,
  Ray ≤£2000/12%, Shark >£2000/16% (inclusive upper bound; fee ≤0 → Minnow).
- Lead block gained `job_fee`, `sourced_by` (commission recipient),
  `fish_override`, `discovery_fee`, `discovery_fee_credited`, `billed_period`.
  `fish_size` is now a **derived cache** of `job_fee`; the lead PUT recomputes
  it server-side unless `fish_override` is set (manual pre-quote estimate).
- Per-job pay card (`renderPayBreakdown` in `admin.html`): fee → commission (to
  sourcer) → 15%×2 directors → hours×£25 → pot delta. **Hours come from the
  `data/hours.json` log** (scopes `artist:<slug>`/`lead:<id>`); the orphaned
  `lead.clive_hours`/`gabe_hours` scalars are ignored. Hours `person` is
  `clive`/`gabe`; normalised to `clive`/`gabriel` (`_person_key`/`personKey`).
- **Pot tab** (`/admin/reconciliations` + `…/preview`, `_compute_reconciliation`):
  a job's fee/commission/15% are recognised **once, in the month its
  `billed_period` matches** (fee − all its hours − 15%×2 − commission → pot).
  Until billed, its hours are pot draws like non-job work. Non-job pot work =
  any hours scope not prefixed `artist:`/`lead:` (the `leadgen`/`networking`/
  `lp_dev`/`hosted_edits` categories). Snapshots append to
  `data/reconciliations.json`, carrying the pot balance forward; pot shortfall
  is flagged (pro-rata/rollover deferred).

## Email templates (studio-wide per workspace)

Per-stage email drafts stored at `data/email_templates_<workspace>.json`
(mutable studio state, not the git-tracked `brands/` pack), keyed by the 8
`STAGES` ids → `{subject, body}` (body is Markdown, edited with EasyMDE in the
Templates tab). `GET/PUT /admin/email-templates`; `GET
/admin/artists/<slug>/draft-email?stage=` renders one via `_brand_substitutions`
plus `{{FEE}}`/`{{FISH}}`/`{{STAGE}}`/`{{INTAKE_URL}}`/`{{HANDOVER_URL}}` and
returns `{subject, body}` for the Copy/mailto modal. **Templates are stored and
substituted verbatim — never AI-generated or rewritten** (the Articles forbid AI
in client comms); "draft" means substitution only, sending is manual.

## Gotchas

- `shared/` (no underscore) at the repo root is a legacy stub — use
  `_shared/` only.
- Changes here take effect after `docker restart adze-flask` (source is
  bind-mounted, no rebuild needed).
