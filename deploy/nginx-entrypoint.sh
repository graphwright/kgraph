#!/bin/sh
# Bootstrap nginx with a self-signed cert if Let's Encrypt certs don't exist yet,
# then obtain real certs via certbot webroot challenge and reload.
# nginx runs in the foreground as the container's main process.
set -e

DOMAIN="graphwright.io"
LIVE_DIR="/etc/letsencrypt/live/${DOMAIN}"
OPTIONS_FILE="/etc/letsencrypt/options-ssl-nginx.conf"
DHPARAM_FILE="/etc/letsencrypt/ssl-dhparams.pem"
WEBROOT="/var/www/certbot"

if [ ! -f "$OPTIONS_FILE" ]; then
    mkdir -p /etc/letsencrypt
    cat > "$OPTIONS_FILE" <<'EOF'
ssl_session_cache shared:le_nginx_SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";
EOF
fi

if [ ! -f "$DHPARAM_FILE" ]; then
    echo "[entrypoint] Generating DH params (this takes a moment)..."
    openssl dhparam -out "$DHPARAM_FILE" 2048 2>/dev/null
fi

CERT_COUNT=0
if [ -f "${LIVE_DIR}/fullchain.pem" ]; then
    CERT_COUNT=$(grep -c "BEGIN CERTIFICATE" "${LIVE_DIR}/fullchain.pem" 2>/dev/null || echo 0)
fi

if [ "$CERT_COUNT" -le 1 ]; then
    echo "[entrypoint] No valid Let's Encrypt cert found — creating self-signed bootstrap cert."
    mkdir -p "${LIVE_DIR}"
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout "${LIVE_DIR}/privkey.pem" \
        -out "${LIVE_DIR}/fullchain.pem" \
        -subj "/CN=${DOMAIN}" 2>/dev/null
fi

# Start nginx in the background temporarily so the ACME webroot challenge can be served.
echo "[entrypoint] Starting nginx in background for ACME challenge."
nginx &
NGINX_PID=$!
sleep 2

if [ "$CERT_COUNT" -le 1 ]; then
    echo "[entrypoint] Requesting Let's Encrypt certificate via webroot."
    if certbot certonly --webroot \
        --webroot-path "$WEBROOT" \
        --non-interactive \
        --agree-tos \
        --email "will.ware@gmail.com" \
        -d "$DOMAIN" \
        -d "www.${DOMAIN}" 2>&1; then
        echo "[entrypoint] Certificate obtained — reloading nginx."
        nginx -s reload
    else
        echo "[entrypoint] Certbot failed (DNS not pointed here yet?). Running with self-signed cert."
    fi
fi

# Stop background nginx and hand off to foreground nginx as PID 1.
# This makes nginx the container's main process so Docker can manage it properly.
echo "[entrypoint] Handing off to foreground nginx."
nginx -s quit
wait "$NGINX_PID" 2>/dev/null || true

# Renewal loop runs in the background; foreground nginx is the main process.
(
    while true; do
        sleep 12h
        echo "[entrypoint] Running certbot renewal check."
        certbot renew --quiet --deploy-hook "nginx -s reload" || true
    done
) &

exec nginx -g 'daemon off;'
