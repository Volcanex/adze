# dashboard-themes/ — admin dashboard color themes

Each subdirectory is one selectable theme; it must contain a `theme.css`.

- Discovery: `admin_api.py` `/admin/dashboard-themes` lists every
  subdir that has a `theme.css`. Dir name = theme name.
- Subdirs whose name starts with `_` are skipped by the listing
  (`_example/` is the template — copy it to start a new theme).
- `theme.css` must override CSS custom properties (`--accent`, `--bg`,
  …) only — do not re-style selectors, or dashboard updates will break
  the theme.
