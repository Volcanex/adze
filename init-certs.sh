#!/bin/bash
# One-time SSL certificate bootstrap for adze.studio
# Run this on a fresh server after `docker compose up -d`
# nginx must be running and DNS must point to this server

set -e

source .env 2>/dev/null || true
EMAIL="${CERTBOT_EMAIL:-}"

if [ -z "$EMAIL" ]; then
    echo "Error: CERTBOT_EMAIL not set in .env"
    exit 1
fi

echo "→ Issuing SSL certificate for adze.studio..."
docker compose run --rm certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d adze.studio \
    -d www.adze.studio \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive

echo "→ Reloading nginx with SSL..."
docker compose exec nginx nginx -s reload

echo "✓ adze.studio is live with SSL"
