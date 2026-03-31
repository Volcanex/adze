# Deployment

## How it runs

Flask runs in Docker. Host nginx handles SSL and all routing (adze.studio plus any other sites on the machine). Host certbot renews SSL certs.

```
Internet → host nginx (ports 80/443) → Docker Flask (127.0.0.1:5001)
```

## Day-to-day

```bash
cd /home/gabriel/adze

docker compose up -d            # start
docker compose restart flask    # pick up code changes (~2s)
docker compose logs -f flask    # logs
```

Source code (`_shared/`, `flask_server.py`, `compile.py`) is mounted as a volume — changes are live after a restart, no rebuild needed.

**Rebuild only when:**
- `requirements.txt` changes (new Python package)
- `Dockerfile` changes

```bash
docker compose build flask && docker compose up -d flask
```

## Environment variables

In `.env` at the repo root (gitignored):

```
DEV_ADMIN_TOKEN=...
CERTBOT_EMAIL=gabrielpenman@gmail.com
```

## Moving to a new server

1. Install Docker and nginx:
   ```bash
   apt install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx
   ```

2. Clone the repo:
   ```bash
   git clone <repo> /home/gabriel/adze
   cd /home/gabriel/adze
   ```

3. Copy `.env` across (or recreate it from `.env.example`).

4. Start Flask:
   ```bash
   docker compose up -d
   ```

5. Copy the nginx config and get SSL:
   ```bash
   sudo cp nginx/adze.studio.conf /etc/nginx/sites-available/adze.studio
   sudo ln -s /etc/nginx/sites-available/adze.studio /etc/nginx/sites-enabled/adze.studio
   sudo nginx -t && sudo systemctl reload nginx
   sudo certbot --nginx -d adze.studio -d www.adze.studio --non-interactive --agree-tos -m gabrielpenman@gmail.com --redirect
   ```

6. Add SSE timeouts for the Vibe Coder (streams can run 5+ minutes, nginx default is 60s):
   ```bash
   sudo sed -i '/client_max_body_size 50M;/a\\n        # Vibe Coder streams can run 5+ minutes\n        proxy_read_timeout 600s;\n        proxy_send_timeout 600s;\n        proxy_connect_timeout 60s;\n\n        # Disable buffering for SSE streams\n        proxy_buffering off;' /etc/nginx/sites-available/adze.studio
   sudo nginx -t && sudo systemctl reload nginx
   ```

7. Log in to Claude (one-time):
   ```bash
   docker exec -it adze-flask claude login
   ```

## Claude CLI auth

Auth saves to the `claude_auth` Docker volume — survives rebuilds. On a new server, run `claude login` once.

**Copying auth from old server (skips the login step):**
```bash
# On old server
docker run --rm -v adze_claude_auth:/data -v $(pwd):/backup alpine tar czf /backup/claude-auth.tar.gz /data

# On new server
docker run --rm -v adze_claude_auth:/data -v $(pwd):/backup alpine tar xzf /backup/claude-auth.tar.gz
```

## Artist custom domains (activate-domain)

When an artist activates a custom domain from the dashboard, Flask writes the nginx config to `nginx/sites-available/{domain}` in the repo. Because Flask runs in Docker it can't touch host nginx directly, so the dashboard shows the commands to run on the server:

```bash
sudo cp /home/gabriel/adze/nginx/sites-available/{domain} /etc/nginx/sites-available/{domain}
sudo ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/{domain}
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d {domain} -d www.{domain} --non-interactive --agree-tos -m gabrielpenman@gmail.com --redirect
```

These are one-time per domain — copy, paste, done.

## nginx config reference

The adze.studio nginx config lives in `nginx/adze.studio.conf` in the repo. It proxies to `127.0.0.1:5001` where Docker Flask is listening. Artist domain configs go in `nginx/sites-available/` (written by the activate-domain endpoint).
