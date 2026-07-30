# Adze

Multi-tenant artist site hosting. Each artist gets a directory under `artists/<slug>/` containing `config.json` and per-page subdirectories with a `content.md`. `compile.py` turns those into static HTML under `static/artists/<slug>/`. Flask serves them via domain-based routing keyed off `config.json`'s `domain` field.

## Runtime
- Docker container `adze-flask` on `127.0.0.1:5001` (host nginx fronts it).
- `flask_server.py`, `compile.py`, `_shared/`, `artists/`, `static/`, `output/`, `nginx/sites-available/` are bind-mounted into the container — host edits take effect after restart.
- Recompile a single artist: `python3 compile.py --artist <slug>` (run on host).
- **On this Hetzner host, `gabriel` is not in the `docker` group**, so docker commands need sudo: `sudo docker restart adze-flask`. The container's PID-1 surfaces on the host `ps` as a root-owned `python3 flask_server.py` — that's normal, not a separate bare-host process. Don't `kill` it from the host; use `sudo docker restart adze-flask`.
- `restart.sh` in the repo is stale; do **not** use it (no `venv/` exists here either).
- Studio admin state lives under `data/` (`hours.json`, `leads.json`, `pinned_order.json`, `todos.json`), bind-mounted via `./data:/app/data` (docker-compose.yml) — so it persists across both `docker restart` and `docker compose down/up`. Each blob is read/written through `_read_studio_json`/`_write_studio_json` in `admin_api.py`; super-admin only.

## ⚠ Outbound mail is on the wrong domain — KNOWN BROKEN, NEEDS FIXING

Password-reset and artist-feedback email currently sends from
**`noreply@lastplace.co.uk`**, not `noreply@adze.studio`. Artists resetting an
Adze password get mail from a Last Place address.

**Why:** Purelymail holds exactly one domain — `lastplace.co.uk`. `adze.studio`
is not registered there at all (`createUser` → `Unknown domain "adze.studio"`),
and `PURELYMAIL_API_TOKEN` is an account API token which *cannot* authenticate
an SMTP session, so a real mailbox is required either way.

**To fix:** add `adze.studio` in the Purelymail UI, set its MX + DKIM records,
provision `noreply@adze.studio`, then change `ADZE_SMTP_USER` / `ADZE_SMTP_FROM`
in `.env` and `docker compose up -d`. Nothing in the code needs touching —
`_shared/mailer.py` is entirely env-driven.

**Also outstanding, and it matters more:** `lastplace.co.uk` has no SPF/DKIM/
DMARC aimed at Purelymail as far as we know, and deliverability was never
verified beyond "the SMTP handshake succeeded". Until those records exist,
**assume reset emails land in spam.** The reset flow warns the recipient about
this in the mail body *and* on the confirmation screen, because a warning
inside a mail nobody sees is useless.

**Port gotcha:** this Hetzner host blocks outbound **465, 25 and 2525**; only
**587** is open. A blocked port presents as a bare connect *timeout*, not a
refusal, so it looks exactly like a wrong password. `mailer.py` uses STARTTLS on
587 for this reason — don't "fix" a timeout by rotating credentials.

## Layout
- `artists/<slug>/config.json` — `name`, `slug`, `domain`, `admin_token`
  - SEO fields (edited in the dashboard **Presence** tab): `seo` (Person/MusicGroup/Organization site identity → JSON-LD), `robots` (custom robots.txt override). `compile.py` generates per-page meta description + Open Graph/Twitter + JSON-LD (`_build_seo_head`) and writes `sitemap.xml` + `robots.txt` at each site root (`_write_artist_seo_files`). adze.studio's own robots/sitemap/favicon are Flask routes in `admin_api.py` mapped at the site root by `nginx/sites-available/adze.studio`.
- `artists/<slug>/<page>/content.md` — Markdown + inline `<style>`/`<script>` for each page
- `artists/<slug>/assets/` — fonts, images, JS referenced via `../assets/...`
- `_shared/` — code shared across artist sites
- `static/artists/<slug>/` — compiled output (do not edit by hand)
- `nginx/sites-available/` — per-domain nginx configs

## Routing
- Default: domain-based — `_get_artist_by_domain(host)` matches `config.json`'s `domain`
- `/preview/<slug>/` — same-origin route for cross-site iframe embeds (added for lastplacesite case studies)
- **Asset URLs must be flat.** Flask registers `/assets/<page_slug>/<path>` (`serve_page_assets`), so any `/assets/<subdir>/file` request is read as "page asset for page `<subdir>`" and 404s with *"Assets directory not found"*. Put artist images directly in `assets/` with flat prefixed names (`work-…`, `exh-…`), **not** in `assets/works/…` subfolders. nginx serves them fine in prod, but Flask (dashboard preview iframe) does not — so subfolders break the preview.

## Self-documenting agent docs
Whenever you discover something non-obvious about a subdirectory — an unusual convention, a compile gotcha, a deployment quirk, a "future-agent should know" detail — create or update a `CLAUDE.md` in that directory. Run `scripts/sync-agent-docs.sh` so a sibling `AGENTS.md` symlink exists beside it. `AGENTS.md` must point at `CLAUDE.md`, so edits through either filename update the same file. Add a one-line entry to the index below so they remain discoverable from here.

If something in this file becomes wrong, fix it.

## External (remote Seed) artists

An artist is "external" when its `config.json` carries a `remote` block
(`host`, `path`, `key`). Adze reads/writes their files over SSH instead of
the local `artists/<slug>/` tree. The local artist dir holds only the
config skeleton, the per-deployment SSH key (`ssh_key`, gitignored),
and the manifest cache. Bootstrap a new one with
`scripts/add-external-artist.sh <slug> <host> <remote-path>`.

Filesystem ops route through `_shared/remote_fs.py`. The dashboard
auto-detects external artists via `/api/adze/external-manifest` and
applies a stripped-down tab list + points the preview iframe at the
manifest's `preview_url`. **External artists have no AI-assisted editing
tab** — Auto-Code explicitly rejects `remote` artists (`autocode_proxy.py`
returns 400 for tabs on external artists), and Terminal Access (which used
to cover this gap) was retired 2026-07. Manual Edit (SSH-backed via
`remote_fs.py`) is their only editing path today.

**Auth boundary.** Adze SSHes into the Seed box as a filesystem user.
That identity is **distinct** from Seed's own web admin (`ADMIN_PASSWORD`
in Seed's `core/api/admin.py`). Adze External bypasses Seed's web admin
entirely — it operates at the filesystem layer. Don't add Seed admin
gates expecting them to apply to external Adze sessions.

## ⚠ Concurrent edits with Auto-Code
The dashboard's Auto-Code tab runs an agent that can edit `artists/<slug>/` files live in a per-artist sandbox container. **Both you and Auto-Code write to the same files; last write wins.** Before any bulk write to `artists/<slug>/`, run:

```
docker ps --filter label=adze.artist_slug=<slug> --format '{{.Names}}'
```

If that artist's sandbox container is running, read the live files first and integrate, or use targeted `Edit` calls instead of `Write`/regenerator scripts. See [artists/CLAUDE.md](artists/CLAUDE.md) for the full protocol.

(Terminal Access, a separate tmux/Claude-Code-CLI feature, was retired 2026-07 — ignore any stale references to it elsewhere.)

### Index

The block below is auto-generated by `python3 scripts/compile_docs.py`.
Run it after adding, removing, or editing any `CLAUDE.md`. Do not
hand-edit between the markers.

<!-- DOCS:START -->
| Path | Summary |
|------|---------|
| `_shared/CLAUDE.md` | Shared — Flask code, docs, widgets, and themes |
| `_shared/brands/CLAUDE.md` | Brands — workspace-keyed white-labelling |
| `_shared/dashboard-themes/CLAUDE.md` | dashboard-themes/ — admin dashboard color themes |
| `_shared/features/CLAUDE.md` | Features — Site-wide capability modules |
| `_shared/shell/CLAUDE.md` | shell/ — the shared artist-admin front-end |
| `_shared/widgets/CLAUDE.md` | Widgets — Dashboard panels in the artist admin |
| `_shared/widgets/loom/CLAUDE.md` | Loom — visual synth (flagship T2 widget) |
| `artists/CLAUDE.md` | Artists — coordination with Auto-Code |
| `artists/jackdt/CLAUDE.md` | Jack Dennison-Thompson (jackdt) — jackdt.com |
| `artists/rose/CLAUDE.md` | Rose Jones — rosefpjones.com |
| `design-language/CLAUDE.md` | Design Language — canonical reference |
| `design-language/adze/CLAUDE.md` | Adze Design Language |
| `nginx/CLAUDE.md` | Nginx — Per-domain configs and TLS |

_Auto-compiled 2026-07-30 09:36 UTC — 13 doc(s) found._
<!-- DOCS:END -->
