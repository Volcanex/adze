# Artists — coordination with the in-browser vibe coder

The dashboard ships a vibe coder that lets users (and another Claude) edit files in `artists/<slug>/` directly via the UI. **You and the vibe coder are working on the same files. Last write wins.** Generator scripts that bulk-`Write` page files have already wiped vibe-coder edits in the past — don't repeat the mistake.

## Hard rule before bulk-editing an artist

Before you `Write` (or regenerate via a script that `Write`s) anything under `artists/<slug>/`:

1. `tail -200 /home/gabriel/adze/logs/vibe.log | grep "\[<slug>\]"` — check for any vibe-coder activity in the last few hours. The log has `── PROMPT ──`, `TOOL: Edit/Write …`, and `── END (ok) ──` markers.
2. If you see edits since your last regen, **read each touched file** and either:
   - integrate the vibe-coder changes into your generator before regenerating, OR
   - switch to targeted `Edit` calls for just the lines you need to change.
3. If unsure, ask the user. Do not regenerate over fresh in-browser work.

## Default approach: `Edit`, not `Write`

For changes to an existing artist, prefer scoped `Edit` calls on the live `content.md`. Reach for a generator script only when scaffolding a new artist or doing a true rewrite the user has explicitly approved.

If you do keep a per-artist generator script (e.g. `/tmp/gen_<slug>.py`), treat it as **scaffolding only** — once the user has been editing in the browser, the live `content.md` is the source of truth. Regenerating means re-importing the live state into the script first.

## What the vibe coder logs

`logs/vibe.log` lines look like:
```
2026-04-23 08:25:02 [<slug>] ── PROMPT ── ...user prompt...
2026-04-23 08:25:14 [<slug>] TOOL: Edit → {...}
2026-04-23 08:25:17 [<slug>] TEXT: ...
2026-04-23 08:34:09 [<slug>] ── END (ok) ──
```
Long `Edit` payloads are truncated with `…`. If you need the precise old/new strings, read the file as it stands now — the edit's effect is on disk.

## If you want a hard guard
A pre-write check that bails on recent vibe activity would be a small change to `flask_server.py`/`compile.py` or a wrapper. Not implemented yet — propose it to the user if collisions keep happening.
