# Remove Auto-Code entirely

**Decision:** Gabriel, 2026-07-30 — Auto-Code goes. Not deprecated, removed.
Terminal Access was already retired 2026-07; this removes the last AI-editing
feature and the container machinery both of them shared.

**Worktree:** `agents/remove-autocode` · **Done when:** every item below is
struck, `adze-flask` restarts clean, and the five `content_admin` artists can
still load and publish their admin.

---

## Delete outright

| Path | Size | Notes |
|---|---|---|
| `_shared/autocode_proxy.py` | 27 KB | The feature |
| `_shared/vibe_agent.py` | 37 KB | The agent loop |
| `_shared/sandbox.py` | 3.3 KB | Container lifecycle. Its own docstring says it is now the sole owner since Terminal Access went |
| `Dockerfile.terminal` | 5.5 KB | Builds `adze-terminal:latest` |
| `claude-login.sh` | 67 B | |
| `_claude_sessions.json` | 55 B | |
| `_vibe_sessions/` | dir | |

## Unwire

- `flask_server.py` — blueprint registration, `/api/sandbox/dashboard` route.
- `_shared/admin_api.py` — Auto-Code endpoints and any `sandbox`/`autocode` imports.
- `_shared/dashboard.html` — the **Auto-Code tab**, its nav entry, and the
  `marked` + `dompurify` CDN `<script>` tags loaded solely to render its chat.
  Removing those two drops two of the six CDN origins the dashboard blocks on
  before first paint.
- `docker-compose.yml` — any sandbox/terminal service or socket mount.
- `_shared/artist_repos.py` — check, it matched the grep.

## Docker reclaim

```
adze-terminal-rose            Up 3 weeks
adze-terminal-liberalsport    Up 3 weeks
adze-terminal-lydialott       Up 4 weeks
adze-terminal:latest          3.1 GB
```

These are **orphans** — Terminal Access was retired this month and nothing
should have kept them alive. Stop, remove, then `docker rmi adze-terminal`.
Host also carries **18.39 GB reclaimable build cache**, much of it likely from
these images; `docker builder prune` after, but confirm with Gabriel first —
other projects on `h` share the daemon.

## Docs to correct

`CLAUDE.md` (root), `artists/CLAUDE.md`, `_shared/CLAUDE.md`,
`_shared/shell/CLAUDE.md`, `_shared/widgets/CLAUDE.md`,
`artists/jackdt/CLAUDE.md`, `artists/rose/CLAUDE.md`,
`_shared/ARTIST-SYSTEM.md`, `_shared/docs/00-behaviour.md`,
`_shared/docs/DOCS_GUIDE.md`.

The whole **"⚠ Concurrent edits with Auto-Code"** protocol in root `CLAUDE.md`
and `artists/CLAUDE.md` disappears with the feature — that is the single
biggest simplification here. No more checking for a running sandbox before
writing to `artists/<slug>/`.

Re-run `python3 scripts/compile_docs.py` and `bash scripts/sync-agent-docs.sh`.

## gcore compliance

`pyproject.toml` currently declares:

```toml
[tool.gcore]
depends = ["openrouter", "stripe", "slack", "purelymail"]
```

`autocode_proxy.py` and `vibe_agent.py` are the **only** consumers of
`OPENROUTER_API_KEY`. Once they go, drop `openrouter` from `depends` and
remove the key from `.env` — otherwise brain L5 keeps probing a dependency
Adze no longer has, and a lapse pages the alert spine for nothing.

---

## ⚠ Traps

**1. `artists/sandbox/` is a test artist, not the feature.** It has
`config.json`, `home/`, `about/`. Do not delete it while grepping for
"sandbox".

**2. `/api/sandbox/*` is an unrelated legacy URL namespace.** It is *not*
served by `sandbox.py`. Only `/api/sandbox/dashboard` exists, in
`flask_server.py`. See the bug below before touching it.

**3. Loom widget matches are false positives** — `_shared/widgets/loom/*`
mentions "sandbox" as the iframe `sandbox` attribute.

---

## Pre-existing bug found while mapping this — NOT caused by the removal

`artists/nina/widgets/edit-photos.js` and
`artists/serebrenina/widgets/add-film.js` call:

```
/api/sandbox/get-page-content
/api/sandbox/edit-page
/api/sandbox/upload-file
```

Those routes **do not exist**. They live on the `/api/adze` blueprint
(`_shared/admin_api.py:2413`, `:2480`, `:2923`), and `apiFetch`
(`_shared/dashboard.html:2133`) passes the URL through verbatim with no prefix
rewriting.

**So both widgets are already broken** — Nina cannot edit her photos and
Serebrenina cannot add films. Two live artists, and plausibly two of the
unhappy ones. The fix is `/api/sandbox/` → `/api/adze/` in both files, five
call sites total.

Flagged to Gabriel 2026-07-30, not fixed — needs a decision on whether to
verify against the live sites first. Do **not** silently fold it into the
Auto-Code removal; it is unrelated and deserves its own commit.
