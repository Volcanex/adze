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

## Super-admin dashboard

The `/admin` route is a super-admin-only dashboard. Auth uses `DEV_ADMIN_TOKEN`.

Features: view all artists (metadata, storage, last login, traffic), create new artists, view aggregate traffic, tail API and Vibe Coder logs, view per-artist resource usage.

After deploying, add the nginx route:

```bash
# Add to /etc/nginx/sites-available/adze.studio, inside the server block:
# location = /admin {
#     proxy_pass http://127.0.0.1:5001/api/adze/admin;
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
#     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#     proxy_set_header X-Forwarded-Proto $scheme;
# }
sudo nginx -t && sudo systemctl reload nginx
```

The `/docs` route is now auth-gated — requires a logged-in artist session or super-admin session. Unauthenticated visitors see a login form.

## Docker architecture

Flask runs inside a Docker container (`adze-flask`). All artist data lives on the **host** filesystem and is mounted into the container as bind volumes:

```
Host                              → Container
artists/                          → /app/artists/      (artist configs, content, assets, DBs)
output/                           → /app/output/       (compiled static sites)
_shared/                          → /app/_shared/      (platform code)
logs/                             → /app/logs/         (application logs)
flask_server.py, compile.py       → /app/              (live-mounted, restart to pick up changes)
claude_auth (Docker volume)       → /root/.claude      (Claude CLI auth, persists across rebuilds)
```

The container itself is stateless — all persistent data is on the host. Rebuilding the container (`docker compose build`) doesn't lose any data.

## Cron jobs

Two cron jobs run on the **host** (not inside Docker):

```bash
# Daily GCS backup at 3am
0 3 * * * /home/gabriel/adze/backup-gcs.sh >> /home/gabriel/adze/logs/backup-gcs.log 2>&1

# System status update every 5 minutes (feeds the admin dashboard)
*/5 * * * * /home/gabriel/adze/status-update.sh
```

To set up on a new server:
```bash
crontab -e
# paste the two lines above
```

## GCS backups

Daily rolling backup of the **host data** (not the Docker image) to `gs://adze-backups/adze/daily/`. 7-day retention.

**What's backed up:**
- `artists/` — all artist configs, content, assets, SQLite analytics databases (~170MB)
- `logs/` — API and Vibe Coder logs
- `.env` — secrets
- `nginx/` — custom domain configs
- `_claude_sessions.json` — active vibe coder sessions

**What's NOT backed up (regenerable):**
- `output/` — compiled static sites (regenerate with `python3 compile.py`)
- Docker image — rebuild with `docker compose build`
- `claude_auth` volume — re-login with `docker exec -it adze-flask claude login`

**Cost:** ~$0.07/month (170MB x 7 days at $0.02/GB/month)

```bash
# Manual backup
/home/gabriel/adze/backup-gcs.sh

# Check backups
gsutil ls -l gs://adze-backups/adze/daily/
```

**Restore:**
```bash
gsutil cp gs://adze-backups/adze/daily/2026-04-01.tar.gz /tmp/
cd /home/gabriel/adze && tar xzf /tmp/2026-04-01.tar.gz
docker compose restart flask
python3 compile.py   # regenerate output/
```

## System status

`status-update.sh` runs on the host every 5 minutes and writes Docker stats, disk usage, and backup info to `logs/status.json`. The admin dashboard (`/admin`) reads this file to display system health.

Includes: container status, CPU/memory, disk usage, last backup date/size, backup count.

## nginx config reference

The adze.studio nginx config lives in `nginx/adze.studio.conf` in the repo. It proxies to `127.0.0.1:5001` where Docker Flask is listening. Artist domain configs go in `nginx/sites-available/` (written by the activate-domain endpoint).
