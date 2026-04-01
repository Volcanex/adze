# Site Format

## Page structure

Each page is a directory inside `artists/{slug}/`. **Directory names must be lowercase** (e.g. `home/`, `about/`, `gallery/`). Never use uppercase or mixed-case directory names — the server routes to lowercase paths.

```
artists/myartist/
  default-styles.css   ← site-wide CSS variables (colours, fonts, sizes)
  config.json          ← site metadata
  home/
    content.md         ← page source
    config.json        ← page metadata
  about/
    content.md
    config.json
```

## default-styles.css

Site-wide CSS custom properties live in `default-styles.css` in the artist's root directory. The compiler auto-injects this into every page's `<style>` block before the page's own CSS.

```css
:root {
    --primary: #2a2a28;
    --accent: #7a8a6e;
    --bg: #f5f2ed;
    --text-font: 'Inter', sans-serif;
    --heading-font: 'Cardo', serif;
}
```

Page CSS can reference these variables with `var(--primary)` etc. Pages can override individual vars if needed, but the defaults apply everywhere.

Artists can edit these visually in the Default Styles tab of the dashboard.

## content.md format

```html
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Description">
<meta property="og:image" content="../assets/images/og.jpg">

<style>
  /* Page-specific CSS — ALL styling must be inline here */
  body {
    background: #f5f2ed;
    font-family: 'Inter', sans-serif;
  }
</style>

<html>
  <!-- Page content -->
  <h1>Hello World</h1>
  <p>This is my site.</p>
</html>
```

The compiler extracts `<style>`, `<html>`, and `<meta>` blocks and wraps them in a full HTML5 document (`<!DOCTYPE html>`, `<head>`, `<body>`).

**NEVER include** in content.md:
- `<!DOCTYPE>`, `<head>`, `<body>`, or `<title>` tags — the compiler adds these
- `<link rel="stylesheet">` or external CDN links (e.g. Font Awesome, Google Fonts CDN)
- `<script src="...">` tags loading external libraries

All CSS must be in the `<style>` block. Fonts are loaded via `@font-face` pointing to `../assets/fonts/`. Inline `<script>` at the end of the `<html>` block is fine for page interactivity.

## Page config.json

```json
{
  "title": "Home",
  "slug": "artists/myartist/home",
  "description": "Welcome to my site",
  "categories": []
}
```

**Critical:** `slug` must always start with `"artists/{slug}/"`. A bare slug like `"photography"` will overwrite platform-level pages.

## Site config.json

```json
{
  "name": "My Artist",
  "slug": "myartist",
  "domain": "myartist.com",
  "admin_token": "...",
  "description": "Portfolio site",
  "contact_email": "me@example.com",
  "favicon": "images/favicon.png",
  "features": ["bookings"],
  "platform_widgets": ["youtube", "stripe"]
}
```

## Asset paths

From `content.md`, assets are referenced with relative paths:
```html
<img src="../assets/images/photo.jpg">
<link href="../assets/fonts/MyFont.woff2">
```

## Creating a new page

1. `mkdir artists/{slug}/pagename` — **lowercase only**
2. Create `config.json`:
   ```json
   { "title": "Page Title", "slug": "artists/{slug}/pagename", "description": "...", "categories": [] }
   ```
3. Create `content.md`: copy the full `<style>…</style>\n<html>…</html>` from an existing page so fonts, colours, nav, and responsive layout are consistent.
4. Update the nav in other pages: `<a href="../pagename/">Page Title</a>`
5. Click **Save** in the dashboard to compile and publish

## Environment variables & secrets

- Store API keys in `.env` in the artist directory
- Load in `api.py`: `import os; from dotenv import load_dotenv; load_dotenv(); key = os.getenv('MY_KEY')`
- NEVER put secret values in `content.md`, HTML, CSS, or any frontend code
- Common keys: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_ENDPOINT_SECRET`

## Custom backend (api.py)

Artists can have a custom backend at `artists/{slug}/api.py`:

```python
from flask import Blueprint, jsonify, request
bp = Blueprint('artist_myartist', __name__, url_prefix='/api/artists/myartist')

@bp.route('/my-endpoint')
def my_endpoint():
    return jsonify({'ok': True})
```

Rules:
- Blueprint must be named `bp` with the correct `url_prefix`
- Use JSON files in the artist directory for storage
- NEVER import from files outside the artist directory
- Server needs a restart to pick up `api.py` changes — tell the user

## Stripe integration

If the artist has Stripe set up (`STRIPE_SECRET_KEY` in `.env`), `api.py` has checkout routes.

To add a buy button: create a button that POSTs to `/api/artists/{slug}/create-checkout` with `{ price_id }`, then redirect to the returned `url`. Price IDs look like `price_xxxxx` — visible in the Stripe tab.

Stripe Checkout handles the entire payment UI — never collect card details on the site.
