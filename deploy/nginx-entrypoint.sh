#!/bin/sh
# Bootstrap nginx with a self-signed cert if Let's Encrypt certs don't exist yet,
# then obtain real certs via certbot webroot challenge and reload.
set -e

DOMAIN="graphwright.io"
LIVE_DIR="/etc/letsencrypt/live/${DOMAIN}"
OPTIONS_FILE="/etc/letsencrypt/options-ssl-nginx.conf"
DHPARAM_FILE="/etc/letsencrypt/ssl-dhparams.pem"
WEBROOT="/var/www/certbot"

# Write certbot's options-ssl-nginx.conf if absent (certbot normally creates this).
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

# Generate DH params if absent (2048-bit is fine; 4096 is slow at first boot).
if [ ! -f "$DHPARAM_FILE" ]; then
    echo "[entrypoint] Generating DH params (this takes a moment)..."
    openssl dhparam -out "$DHPARAM_FILE" 2048 2>/dev/null
fi

# If no real certs exist, plant a self-signed cert so nginx can start on 443.
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

# Run nginx in the background so the ACME HTTP challenge can be served on port 80.
echo "[entrypoint] Starting nginx in background for ACME challenge."
nginx &
NGINX_PID=$!

# Give nginx a moment to bind ports before certbot tries to verify.
sleep 2

# Attempt cert issuance only when we don't already have a real cert.
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

# Periodic renewal loop — runs every 12 hours; reload nginx if certs were renewed.
echo "[entrypoint] Entering renewal loop."
while kill -0 "$NGINX_PID" 2>/dev/null; do
    sleep 12h &
    wait $!
    echo "[entrypoint] Running certbot renewal check."
    certbot renew --quiet --deploy-hook "nginx -s reload" || true
done

echo "[entrypoint] nginx exited — shutting down."
