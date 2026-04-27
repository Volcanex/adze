# Widgets — Dashboard-privileged Flask blueprints

Each subdirectory is one widget (stripe, youtube, beehiiv, vimeo,
calendly, inbox, subscribers). A widget is a small Flask blueprint that
provides embeddable content or actions inside artist pages.

## Shape

```
widgets/<name>/
  __init__.py     # Flask Blueprint definition and routes
  README.md       # Embed syntax and backend interaction notes
  (other files)   # templates, static assets, helpers as needed
```

Use `stripe/` or `youtube/` as the reference implementation when adding
a new widget.

## Trust model

Widgets run with **admin auth** and may write to artist page files.
They are developed by Gabriel, not by the in-browser vibe coder.
`_shared/docs/00-behaviour.md` (lines 31–37) documents why the vibe
coder is sandboxed out of widget creation.

## Adding a widget

1. `_shared/widgets/<name>/__init__.py` with a `Blueprint`
2. Register it in `_shared/admin_api.py`
3. Add a `README.md` with embed syntax and any per-artist config
4. Test by calling it from a scratch test page before shipping
5. `docker restart adze-flask` to reload
