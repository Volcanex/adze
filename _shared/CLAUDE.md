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
- `shell_assets.py` — **the one declaration of what the artist admin shell
  loads**: `SHELL_DIR`, `VENDOR_DIR`, `TOKENS_DIR`, and `TOKEN_FILES` (the
  design-language cascade, order-significant), plus `token_assets()`,
  `shell_assets(*entry)` and `token_links(prefix)` for the bootstrap `<head>`.
  Both surfaces that mount the shell — `landing.py` (the dash) and
  `features/content_admin.py` (the editor) — import from here. Before it, the
  token list existed in four places (a constant and a hand-written `<head>`
  block in each), and since the two share `admin-shell.css`, a file added to
  one and not the other renders the same stylesheet two ways with nothing
  failing. Don't reintroduce local copies of these constants.
- `autocode_proxy.py` — HTTP + SSE surface for the Auto-Code chat tab,
  under `/api/adze/autocode/*`. Owns auth, the per-artist system prompt,
  worktree tabs, and compile-on-publish; delegates the agent itself to
  `dsh_agent`. **No longer a reverse-proxy** — it used to spawn
  `opencode serve` in a per-artist container and forward to it (and before
  that, a TUI-in-xterm bridge, `auto_code_bridge.py`).
- `dsh_agent.py` — the agent backend (since 2026-08-24): DeepSeek Harness
  via its Python SDK, running as a subprocess of the Flask process. Holds
  one session per artist, and translates harness notifications into
  **opencode's event schema** so `dashboard.html` needs no changes — its
  `dispatch()` is still the consumer, so changing an event shape here
  breaks the browser. Model is `deepseek/deepseek-v4-flash` over the
  existing OpenRouter key.
- `dsh_cordis.yml` — the agent's plugin composition, handed to the runtime
  as `DSH_CORDIS_CONFIG`. Notable for what it omits: no `dsh-bash-local`,
  so **the model has no shell** — file tools are its entire surface. It is
  a full replacement for the runtime's bundled default, not an overlay.
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
- `sandbox.py` — per-artist container-lifecycle helpers. **Dead code as of
  2026-08-24**: its last two importers (`autocode_proxy`, `artist_repos`)
  both stopped using containers when Auto-Code moved in-process. Left on
  disk rather than deleted in the same change; delete it once nothing has
  missed it. Do not confuse with `artists/sandbox/`, which is a test
  artist, or the `/api/sandbox/*` URL namespace, which is unrelated.
- `docs/` — the **Auto-Code context**. Load-bearing.

## `docs/` is load-bearing — do not delete

`autocode_proxy.py` (`_build_system_prompt`) builds a per-artist context
from `_shared/docs/*.md` (in filename order), then appends artist
config/page information. It is prepended to the **first** message of a
session only — the harness keeps conversation state after that, so
re-sending it every turn would just re-buy the same tokens. This is how
Auto-Code learns Adze conventions.

Note the docs are written for an agent that had a shell. The current one
does not (see `dsh_cordis.yml`), so any instruction to run a command is
one the model cannot follow.

- **To update Auto-Code's behaviour:** edit or add a numbered file
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
Gabriel-only tooling. Auto-Code is scoped to the artist site and
should not create dashboard widgets unless Gabriel explicitly changes
that boundary — see `_shared/docs/00-behaviour.md` lines 31–37 for why.

## Terminal Access — retired 2026-07

The tmux/Claude-Code-CLI "Terminal Access" tab (`terminal_bridge.py`, the
`/terminal` Socket.IO namespace, `_claude_sessions`/`claude-stream*`
endpoints in `admin_api.py`, and the corresponding dashboard.html panel)
was removed. **Auto-Code is the surviving AI-editing feature** and now the
sole consumer of the shared per-artist sandbox container
(`sandbox.py`/`artist_repos.py`). If you find a stray reference to
Terminal Access, tmux sessions, or `previewFrameClaude`/`claudeInput`
elsewhere, it's stale — flag and remove it.

## Artist sign-in — the three front doors

An artist can arrive at one of three places, and they are deliberately not
the same thing:

1. `theirdomain.com/admin` — the **landing page** (`landing.py`): five
   sections behind a pill row — Overview (the editor button, site links and
   QR, status, a one-line visit count, feedback), Files (a read-only browser
   and rich viewer), History (saved versions, restore), Export (the site as a
   zip), Account. Plus `handoff` into the editor with no second login. This is
   the intended home for anyone who has a live domain.

   **It writes nothing.** Every file route is read-only and the single
   mutating route (`/history/restore`) calls a function the control panel
   already owns. Editing lives in the control panel, which owns autosave,
   publish and snapshot semantics; a second writer here would be a second set
   of rules for the same files.

   Its data comes from `admin_api.py` **payload functions**, never from
   re-walking the artist dir: `artist_files_payload`, `read_artist_file_payload`,
   `export_site_zip`, `snapshots_payload`, `restore_snapshot_for` — each one
   also backing the `/api/adze/*` route it was extracted from. `admin_api`
   owns path safety (`_resolve_artist_file`) and the definition of what an
   export or a snapshot *is*; a copy in `landing.py` would be a second thing
   to get wrong.

   **`_site_payload` is the one payload landing.py owns**, because it reads
   *compiled output* — a page an artist can't reach isn't a page. It also
   cleans the page titles (`_repeated_tail` / `_clean_title`): tab titles carry
   the site name on the end, and `config.json`'s `name` is not the string to
   strip — the artist is `Rose`, the tab says `Rose Jones`. See
   [shell/CLAUDE.md](shell/CLAUDE.md) for how the landing groups the result.

   **`include_assets` is the browse/edit split.** The Manual Edit tab hides
   `assets/` and `widgets/` (`FILES_TREE_HIDDEN_DIRS`) because a dedicated tab
   owns them; the landing's browser shows them (`FILES_BROWSE_HIDDEN_DIRS`)
   because an artist looking at their own site expects their pictures to be
   in it. Browse mode additionally refuses **dotfiles** — `.analytics.json`
   and `.generated.json` are machine-written and `.env` is a secret store.
   Every writer passes `include_assets=False`, so nothing new became writable.
2. `adze.studio/dashboard` — the **editor** (`dashboard.html`). Its sign-in
   screen is identifier-first: name/email/slug, then password. It posts
   `{identifier, password, slug?}` to `/api/adze/login`, which has accepted
   that shape alongside legacy `{slug, token}` since the account store
   landed. `choose: true` in the reply means the account owns several sites
   and the caller must pick one — never guess.
3. `adze.studio/admin` — the **super-admin** SPA, unrelated to the above.

Step one of (2) calls `/api/adze/account/resolve`, which redirects to (1)
when the artist has a domain that actually reaches Adze. **`config.json`'s
`domain` is not evidence of that** — most artists have one set with no
vhost anywhere, and redirecting them there strands them on a parked domain.
`_landing_url()` in `accounts_api.py` therefore requires
`nginx/sites-available/<domain>` to exist. Declining to redirect is the safe
failure (they just sign in on adze.studio); the reverse locks people out.

**Consequence:** an artist whose vhost lives only in the host's
`/etc/nginx/sites-enabled` and not in this repo silently keeps getting the
editor instead of their landing page. The repo dir is the SSOT — put the
vhost here and the redirect turns itself on.

`domain_guard` in `features/artist_admin.py` hard-404s the landing page on
any host but the artist's own, so the landing page cannot be reached on
adze.studio at all. That is why (2) exists as a real destination and not
just a redirector.

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
- `compile.py` and `flask_server.py` are bind-mounted **as single files**, so
  they are pinned to an inode. `sed -i` (and any editor that writes a temp file
  and renames it over the target) makes a new inode and the container keeps
  running the *old* file with no warning. Restart before trusting an edit to
  either, and verify with `docker exec adze-flask grep … /app/compile.py`.
  Everything under the directory mounts (`_shared/**`, `artists/**`) propagates
  normally.
- `compile.py` reporting `Done: 0 pages` is an alarm, not a no-op — it prunes
  output it believes is orphaned, so a page lookup that matches nothing will
  delete the built site.
- **`_file_kind` (`admin_api.py`) returns `page` for `content.html`**, not
  `text`. The dashboard's whole page-edit flow gates on that kind (the split
  CSS/HTML editors, the save dispatch, the file-tree default selection), and
  `admin-landing.js` lists it in `TEXT_KINDS`. `markdown` now means a file that
  really is markdown. Changing the classifier without changing those consumers
  silently drops artists into the raw text editor for their own pages.

## Manual Edit code editors (`dashboard.html`, 2026-08-25)

`cssEditor`, `htmlEditor`, `rawFileEditor` and `jsEditor` are still plain
`<textarea>`s — same ids, same `.value` — wrapped at DOMContentLoaded by
`enhanceCodeEditor()` in a highlight underlay (`.code-hl`), a line-number
gutter and a status bar. Nothing about the load/save paths changed; they act on
the same nodes as before.

Three things will break it if you touch them without care:

- **The gutter is its own `<pre>`.** hljs emits spans that run across line
  breaks, so building numbered rows by splitting its output on `\n` tears them
  in half. Same rule as `shell/file-viewer.js`.
- **`el.value = …` does not fire `input`**, and the dashboard populates these
  editors that way on every open. `enhanceCodeEditor` forwards the `value`
  property through a wrapper that repaints; drop that and the colour layer
  keeps showing the previously opened file.
- **Typography must stay identical between the textarea and `.code-hl`** — font,
  size, line-height, padding, `tab-size`, `white-space` — or the caret drifts
  off the text. `#rawFileEditor` had inline typography for exactly this reason;
  it now lives in `.code-wrap.is-md`. `.js-editor-block textarea` is more
  specific than `.code-wrap textarea` and declared later, so the widget editor
  carries an explicit override.

Highlighting is best-effort: no `window.hljs`, no known language, or a file over
`CODE_MAX_HL` (120 KB) drops to `.is-plain` — plain text with the gutter intact,
never a blank pane. The highlighter is the vendored copy, served same-origin by
`/api/adze/vendor/highlight.js` so the editors work with no CDN reachable.

## `copy_slots.py` — the sitewide copy override layer (2026-07-31)

New module. Artist pages are hand-authored HTML/CSS where only *marked* runs of
text are editable (`data-copy` / `data-copy-rich` — see
[../artists/CLAUDE.md](../artists/CLAUDE.md)). This module scans a page for
slots, and substitutes overrides from `artists/<slug>/copy.json` at compile time.

**The text in `content.html` stays the default and the source of truth.**
`copy.json` is an override layer only, so an artist with no overrides compiles
byte-identically — verified: after marking rose, 42 of her 45 pages were
byte-identical and the three that changed differed only by the inert attribute.

`sanitize_rich(value, domain=None)` is **the** gate, and runs on write. The
client-side restriction in `field-editors.js` is a convenience, not a control.
`_RICH_TAGS` is `{b, strong, i, em, a, br}` — note there is **no `p`**, which is
why a rich editor must emit an inline fragment (a `<p>` is not nested, it is
stripped, silently merging paragraphs).

Two things in `_clean_href` that look over-careful and are not:

- It **HTML-unescapes and strips C0 controls BEFORE** the scheme check.
  Browsers drop tab/CR/LF inside a URL, so `java&#9;script:` reaches the parser
  as `javascript:`. A scheme check on the raw string — the obvious way to write
  it — walks straight past both that and `java&#115;cript:`.
- `target`/`rel` are **DERIVED from the href, never copied from input**. Quill
  stamps `target="_blank"` on every link it makes including internal ones, while
  a hand-authored source default may carry a `target` the editor never sees.
  This is the only place that sees the final href, so it is the only place that
  can be right. External → `target="_blank" rel="noopener noreferrer"`;
  internal, `mailto:`, `tel:` → neither. An anchor left with no usable href is
  unwrapped to its text rather than published dead.

## `asset_store.py` — the card tier

`store_image` produces three tiers: `full` (original), `display` (≤2000px), and
**`card` (≤480px, q82)** for admin thumbnails and card grids. `store_fileobj`
additionally writes a 64px `.thumbs` sidecar for the asset browser.

The card tier is not cosmetic. Before it existed the admin's 96px thumbnails
loaded the ~1MB display tier, so a grid of Rose's 32 works was ~25MB on 4G.
Rose's `work-tara` card is **56KB against 1.6MB**.

Image entries are `{src, full, card, ar, aspect}`. **`src` still means the
display tier** — artist templates consume `src` and `full`, so `card` was added
purely additively. The client fallback chain is
`entry.card || entry.src || entry.full || entry`.

Backfill existing entries with `scripts/backfill-card-tier.py [--artist SLUG]
[--dry-run]`. It is idempotent and refuses to run on the host (no werkzeug) —
run it in the container. 540 derivatives were backfilled across the five
`content_admin` artists on 2026-07-31.
