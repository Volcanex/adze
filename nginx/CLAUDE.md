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

1. Write the config to `nginx/sites-available/<domain>` (copy an existing
   file and edit `server_name`, root path, and asset alias).
2. Symlink it into sites-enabled:
   `sudo ln -sf /home/gabriel/adze/nginx/sites-available/<domain> /etc/nginx/sites-enabled/<domain>`
3. `sudo nginx -t` to validate.
4. `sudo systemctl reload nginx` to apply (HTTP only at this point).
5. Issue the TLS cert — certbot rewrites the config to add HTTPS + redirect:
   `sudo certbot --nginx -d <domain> -d www.<domain>`
6. `sudo docker restart adze-flask` so Flask picks up the new artist config.

Note: `init-certs.sh` in the repo root is for `adze.studio` only (old
Docker-based certbot flow) — don't use it for artist domains.

## Bind-mounted into the container

`nginx/sites-available/` is also volume-mounted into the `adze-flask`
container so the app can read per-artist config metadata. Editing these
files takes effect on the host via `nginx -s reload`; inside the
container, any code reading them picks up changes on the next request.
