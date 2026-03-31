# stripe widget (T2 platform)

Manages Stripe payments — account connection, product catalogue, and order history. Includes a buy button component for use in page layouts.

## Built-in endpoints it calls (no setup needed)
- `GET /api/adze/stripe-status` — checks if Stripe is connected for this artist
- `GET /api/adze/stripe-products` — lists Stripe products
- `POST /api/adze/stripe-create-product` — creates a Stripe product
- `POST /api/adze/stripe-delete-product` — deletes a Stripe product
- `POST /api/adze/stripe-scaffold` — writes starter api.py endpoints to the artist's backend
- `GET /api/adze/list-env` / `POST /api/adze/update-env` — reads/writes env vars (STRIPE_SECRET_KEY)
- `GET /api/adze/artist-info` — fetches artist metadata

## Custom endpoints it expects in artist api.py
- `POST /api/artists/{slug}/create-checkout` — creates a Stripe checkout session, returns `{url}`
- `GET /api/artists/{slug}/orders` — returns list of completed orders

Use `stripe-scaffold` to auto-generate these in api.py. The artist must set `STRIPE_SECRET_KEY` in their env vars.

## Setup flow
1. Artist enters their Stripe secret key in the widget settings panel
2. Widget calls `stripe-scaffold` to write the backend endpoints into api.py
3. Artist publishes — buy button becomes live
