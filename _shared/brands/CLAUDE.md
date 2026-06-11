# Brands — workspace-keyed white-labelling

A brand pack skins artist-facing surfaces (intake portal, handover page) and
adds a co-brand lockup ("Last Place × Adze") to the dashboard/admin chrome.
Packs are keyed off the artist's `workspace` field in `config.json`
(`_artist_workspace`, default `lastplace`). **No pack → default Adze branding**
— that fallback is the point; don't make any surface assume a pack exists.

## Pack layout
```
brands/<workspace>/
  brand.json    name, tagline, accent, lockup_font, contact_email,
                logo_asset, favicon_asset, welcome_heading, welcome_copy,
                how_it_works — ALL optional, each falls back to an Adze default
  brand.css     CSS custom-property overrides ONLY (same rule as
                dashboard-themes) + @font-face blocks. Loaded after the page's
                own :root, so the cascade does the re-skin. Include a
                [data-theme="dark"] block or the dark toggle half-reverts to
                the Adze dark palette.
  assets/       logo, fonts (lastplace's Cormorant is SIL OFL — redistributable)
```

## Resolution and serving
- `_shared/brands.py` — `get_brand` / `brand_json` / `brand_asset_path`
  (traversal-guarded; `brand.css` resolves at pack root, all else in `assets/`).
- `GET /api/adze/brand/<workspace>/<file>` serves assets, no auth, 1-day cache.
- `GET /api/adze/brand-info` resolves the caller's workspace (authed artist
  first, then admin identity's first workspace) → brand.json + `asset_base_url`.
  Returns `{}` when unbranded; frontends must treat that as "stay Adze".
- Server-side substitution happens via `_brand_substitutions(cfg)` in
  admin_api.py — plain-text `{{BRAND_*}}` replacement, no template engine.
  Intake and handover share it; keep new placeholders in that one helper.

## Gotchas
- Cormorant filenames contain literal `[wght]` brackets — URL-encode as
  `%5B`/`%5D` inside CSS `url()` when writing @font-face in JS.
- The dashboard/admin lockup only co-brands post-auth (login screens stay
  plain Adze — workspace is unknown before login). admin.html co-brands only
  identities scoped to exactly one non-`personal` workspace, so super-admins
  keep the vanilla mark.
- The handover page (`/handover/<slug>/<token>`, `handover_token` in config)
  is where artist credentials live now. The intake portal no longer receives
  `{{ADMIN_TOKEN}}` — do not reintroduce credentials there.
