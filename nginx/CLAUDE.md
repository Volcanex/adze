# Nginx — Per-domain configs and TLS

Host nginx (not containerised) fronts the `adze-flask` container. Each
artist domain gets its own file under `sites-available/`.

## Per-domain config shape

Use an existing file (e.g. `ninasere.com` in this directory) as the
template. Each config typically:

- Listens on 80 + 443 with Let's Encrypt TLS
- Serves static assets from `output/artists/<slug>/` with 24h cache
- Proxies `/api/*` to `127.0.0.1:5001` (the Flask container)
- Falls back to the Flask proxy for everything else

## Adding a new artist domain

1. Copy an existing config and edit the `server_name`, root path, and
   asset alias.
2. `sudo nginx -t` to validate.
3. `sudo systemctl reload nginx` to apply.
4. If this is a new TLS cert, run the cert issuance step (see
   `init-certs.sh` in the repo root for the Certbot bootstrap).

## Bind-mounted into the container

`nginx/sites-available/` is also volume-mounted into the `adze-flask`
container so the app can read per-artist config metadata. Editing these
files takes effect on the host via `nginx -s reload`; inside the
container, any code reading them picks up changes on the next request.
