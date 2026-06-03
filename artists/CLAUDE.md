# Artists — coordination with Terminal Access

The dashboard ships Terminal Access: a per-artist tmux shell that usually starts Claude Code, lets developers log in with their own subscription, and edits files in `artists/<slug>/` directly. **You and Terminal Access are working on the same files. Last write wins.** Generator scripts that bulk-`Write` page files have already wiped live dashboard edits in the past; don't repeat that mistake.

## Hard rule before bulk-editing an artist

Before you `Write` (or regenerate via a script that `Write`s) anything under `artists/<slug>/`:

1. `tmux ls | grep "adze-<slug>"` — check whether a live Terminal Access session is attached to that artist.
2. If a session exists, assume someone may have unsaved context or pending edits. **Read the live files you plan to touch** and either integrate the current state into your generator before regenerating, or use targeted `Edit` calls for just the lines you need to change.
3. If unsure, ask the user. Do not regenerate over fresh dashboard/terminal work.

## Default approach: `Edit`, not `Write`

For changes to an existing artist, prefer scoped `Edit` calls on the live `content.md`. Reach for a generator script only when scaffolding a new artist or doing a true rewrite the user has explicitly approved.

If you do keep a per-artist generator script (e.g. `/tmp/gen_<slug>.py`), treat it as **scaffolding only** — once the user has been editing in the browser or Terminal Access, the live `content.md` is the source of truth. Regenerating means re-importing the live state into the script first.

## What Terminal Access changes

Terminal Access does not guarantee a tidy per-tool edit log. It is a real shell/Claude Code session in the artist directory, so the reliable source of truth is the filesystem. Use `git diff -- artists/<slug>/` when the repo is tracking changes, otherwise read the files directly.

## Ownership / ACL invariant

`artists/` carries a POSIX default ACL granting `u:1000:rwX, g:1000:rwX`
plus the setgid bit, so anything created under it — even by `root` from a
host shell — stays writable by uid 1000 (the Flask container's `adze`
user, which is also host `gabriel`). If you ever see `PermissionError`
writing to `artists/<slug>/...`, re-apply with:

```
sudo find artists -type d -exec chmod g+s {} +
sudo setfacl -R   -m u:1000:rwX,g:1000:rwX artists
sudo setfacl -R -d -m u:1000:rwX,g:1000:rwX artists
```

Host-side scripts that scaffold artists (e.g. `scripts/merge-leads-into-artists.py`)
also refuse to run as root, as defense in depth.

## If you want a hard guard
A pre-write check that bails on recent vibe activity would be a small change to `flask_server.py`/`compile.py` or a wrapper. Not implemented yet — propose it to the user if collisions keep happening.
