server {
    server_name ninasere.com www.ninasere.com;

    root /home/gabriel/adze/output/artists/nina;

    location /assets/ {
        alias /home/gabriel/adze/output/artists/nina/assets/;
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

    listen 80;
    listen [::]:80;
}