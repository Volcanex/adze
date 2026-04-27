# Features — Site-wide capability modules

Each file is one feature module that can be enabled for an artist site
(e.g. `bookings.py` for a Calendly-style booking flow). Unlike widgets,
features tend to be larger, page-spanning capabilities.

## Adding a feature

1. Create `_shared/features/<name>.py` with a Flask Blueprint.
2. Register the blueprint in `_shared/admin_api.py`.
3. Document the registration and per-artist config in a short note here
   or in the feature's own module docstring.
4. See `_shared/docs/01-architecture.md` (lines 60–80) for the
   expected registration pattern.

## Feature vs widget

- **Widget**: embeddable content in one spot on a page (a video, a
  signup box, a price card). Small surface.
- **Feature**: a system spanning multiple pages or long-running state
  (booking workflow, ecommerce, content moderation). Larger surface.

If you're unsure which, start with a widget — it's the narrower
commitment.
