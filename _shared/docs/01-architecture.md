# Architecture (your slice)

You're scoped to one artist directory. Everything you can read or write
lives inside it.

```
artists/{slug}/                ← your working directory
  config.json                  ← site metadata (name, domain, contact_email, features)
  default-styles.css           ← site-wide CSS variables, auto-injected into every page
  api.py                       ← optional: custom Flask blueprint (advanced)
  {page-slug}/
    content.md                 ← page source: <style>...</style><html>...</html>
    config.json                ← page metadata (title, slug, description)
  assets/
    images/                    ← uploaded images
    fonts/                     ← uploaded fonts
  widgets/                     ← Tier 4 site widgets (you can create these — see 04-widgets.md)
  data.db                      ← analytics, auto-managed (do not edit)
  subscribers.json             ← mailing list (managed by features)
  submissions.json             ← contact form submissions (managed by features)
```

## Compile flow

When the user clicks **Save** in the dashboard:

```
content.md  →  compile.py  →  static HTML in output/  →  served by nginx
```

You don't run the compiler yourself. Tell the user to click Save after
edits to publish.

## Custom backend (api.py)

If a feature needs a backend endpoint, add it to `artists/{slug}/api.py`
as a Flask Blueprint. It auto-mounts at `/api/artists/{slug}/...`. Use
JSON files for storage; no subprocess, no raw network calls.
