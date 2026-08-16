server {
    server_name jackdt.com www.jackdt.com;

    root /home/gabriel/adze/output/artists/jackdt;

    location /assets/ {
        alias /home/gabriel/adze/output/artists/jackdt/assets/;
        expires 24h;
        add_header Cache-Control "public, max-age=86400";
    }


    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        # Video uploads go through /admin, so this is the real ceiling on the
        # `file` field — Flask's own MAX_CONTENT_LENGTH is 2GB and never binds
        # first. Over the limit nginx returns its own 413 HTML page, which the
        # admin's fetch can only report as a bare failure, so the field's
        # `max_mb` (200, in config.json) is set just under this and refuses the
        # file client-side instead. Change the two together. Assets are stored
        # twice — canonical plus the output/ mirror — so 200MB costs 400MB.
        client_max_body_size 220M;
    }

    location / {
        # Pages must revalidate. Without this there is NO Cache-Control on the
        # HTML, so browsers cache it heuristically off Last-Modified and keep
        # serving a stale page for hours after a publish — a nav item removed
        # on the server stayed visible in the browser for a day. It has to sit
        # here rather than in a `\.html$` location: a request for /home/ is
        # served through try_files' directory-index path, which never re-runs
        # location matching, so a regex block never sees it. /assets/ has its
        # own location above and keeps its 24h.
        add_header Cache-Control "no-cache" always;
        try_files $uri $uri/ @api;
    }

    location @api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    listen [::]:443 ssl; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/jackdt.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/jackdt.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}
server {
    if ($host = www.jackdt.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = jackdt.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    server_name jackdt.com www.jackdt.com;

    listen 80;
    listen [::]:80;
    return 404; # managed by Certbot




}