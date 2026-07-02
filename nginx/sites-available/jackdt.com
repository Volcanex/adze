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
        client_max_body_size 50M;
    }

    location / {
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