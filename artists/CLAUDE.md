# Artists — coordination with Auto-Code

The dashboard's **Auto-Code** tab runs `opencode serve` inside a per-artist
sandbox container (`adze-terminal-<slug>`, name is historical) and edits
files in `artists/<slug>/` directly via the host bind-mount. **You and
Auto-Code are working on the same files. Last write wins.** Generator
scripts that bulk-`Write` page files have already wiped live dashboard
edits in the past; don't repeat that mistake.

(Terminal Access — a separate tmux/Claude-Code-CLI feature that used to
share this same sandbox container — was retired 2026-07. Any doc or code
still describing a tmux session, `/terminal` Socket.IO namespace, or
`claude-stream` endpoints is stale.)

## Hard rule before bulk-editing an artist

Before you `Write` (or regenerate via a script that `Write`s) anything under `artists/<slug>/`:

1. `docker ps --filter label=adze.artist_slug=<slug> --format '{{.Names}}'` — check whether that artist's sandbox container is running (a strong signal Auto-Code has been active recently; it evicts after 30 min idle).
2. If it's running, assume someone may have unsaved context or pending edits. **Read the live files you plan to touch** and either integrate the current state into your generator before regenerating, or use targeted `Edit` calls for just the lines you need to change.
3. If unsure, ask the user. Do not regenerate over fresh dashboard/Auto-Code work.

## Default approach: `Edit`, not `Write`

For changes to an existing artist, prefer scoped `Edit` calls on the live `content.md`. Reach for a generator script only when scaffolding a new artist or doing a true rewrite the user has explicitly approved.

If you do keep a per-artist generator script (e.g. `/tmp/gen_<slug>.py`), treat it as **scaffolding only** — once the user has been editing in the browser or via Auto-Code, the live `content.md` is the source of truth. Regenerating means re-importing the live state into the script first.

## What Auto-Code changes

Auto-Code does not guarantee a tidy per-tool edit log. It's a real agent session editing files in the artist directory, so the reliable source of truth is the filesystem. Use `git diff -- artists/<slug>/` when the repo is tracking changes, otherwise read the files directly.

## Copy slots — `data-copy` (added 2026-07-31)

Marked runs of text in a hand-authored page are editable from the artist
admin's **Text** section. The mark is one attribute on the element that
directly wraps the text:

- `data-copy="<slot-id>"` — plain text only, no formatting
- `data-copy-rich="<slot-id>"` — bold / italic / link only, nothing else

Slot ids are lowercase-kebab, derived from meaning (`bio`,
`education-foundation`), and unique within their page. Derive from meaning
and never from position: an id like `block-3` breaks the moment anyone
reorders the page.

**The text in `content.md` stays the default and the source of truth.**
`artists/<slug>/copy.json` is an override layer only, so an artist with no
overrides compiles byte-identically to before the slot existed. Verified:
after marking rose, 42 of her 45 compiled pages were byte-identical and the
three that changed differed only by the inert attribute itself.

**Mark the SOURCE, never the generated output.** The distinction is not
"hand-authored pages only" — it is *which file you put the attribute in*:

- A hand-authored page → mark its `content.md`. That file is the source.
- A **generated** page (one listed in `.generated.json`) → mark its
  **Jinja template** under `artists/<slug>/templates/`. The template is
  the source; `content.md` is output.
- Never mark a generated page's `content.md` directly. That file is
  rewritten from the template on every publish, so the attribute lasts
  until the next one.

Marking the template works because of the order inside a rebuild:
`render()` regenerates `content.md` **from the template** (so the
attribute is re-emitted every time), `_scan_copy_slots` then discovers the
slot from `content.md`, and `compile.py` applies the `copy.json` override
on the way into `output/`. Verified end to end on jackdt's `/music/` lede
on 2026-08-05: the override reached the live page, survived two further
publishes, and reverted cleanly to the template's default when cleared.

**A new page is not finished until its prose is in the copy editor.** The
artist's admin should never drift behind the site — if you add a section
and skip this, the artist can edit every page except the newest one, which
is the one they most want to change. Mark the eyebrow, the lede, and any
standing prose as you build the template, not as a follow-up.

Never mark: nav or menu links, brand/logo text, footer credit lines,
anything inside `<style>`/`<script>`, anything containing a substitution
marker like `<!-- EXHIBITIONS_BLOCK -->`, or text generated from
`content.json` (that is already editable in the content admin — don't
build a second surface onto the same words). Mark the element that
*directly* wraps the text: for a block containing an `<h3>` and two
`<p>`s, mark the `<p>`s, because replacing the wrapper's inner content
would destroy its structure.

**Why adding the attribute is render-inert**, so nobody has to re-derive
it: `compile.py`'s `parse_content` lifts the page's `<html>` block
verbatim by regex — no markdown pass, no sanitiser, no attribute
whitelist — and no artist page contains a `[data-*]` CSS selector or any
`dataset`/`getAttribute` JS. The attribute cannot alter rendering.

Rich slots emit an **inline fragment**, never block markup — a slot is the
inner content of an element the artist already wrote (`<p class="lede">`,
`<li>`). See `_shared/shell/CLAUDE.md` for the editor half and
`_shared/copy_slots.py` for the write-time gate, which is the actual
security control (the client-side restriction is a convenience).

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
