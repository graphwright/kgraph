# Deployment HOWTO — nginx-proxy architecture

nginx is no longer installed on the droplets. A Dockerized `nginxproxy/nginx-proxy`
container handles TLS termination and reverse proxying for the entire stack. Certs
are issued by Let's Encrypt via the `acme-companion` sidecar and stored in a Docker
volume on each droplet.

## How it works

- `nginx-proxy` watches the Docker socket and auto-generates nginx config from
  container environment variables (`VIRTUAL_HOST`, `VIRTUAL_PORT`).
- `acme-companion` issues and renews TLS certs automatically. Certs live in the
  `nginx-certs` Docker volume — they survive `docker compose down/up`.
- Path-based routing that nginx-proxy can't derive automatically lives in
  `deploy/vhost.d/graphwright.io`. The GH Actions workflow copies this file to
  `/opt/graphwright/vhost.d/` on the droplet, and the compose file bind-mounts it
  read-only into `nginx-proxy`.

## Droplet prerequisites (one-time setup)

These steps only need to happen once on a fresh droplet. After that, CI handles
everything.

### 1. Remove host nginx (if present)

```bash
systemctl stop nginx
systemctl disable nginx
apt remove -y nginx nginx-common
```

### 2. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

### 3. Open firewall ports 80 and 443

In the Digital Ocean control panel: Networking → Firewalls → add inbound rules
for TCP 80 and TCP 443.

### 4. Point DNS at the droplet IP

For prod: `graphwright.io` A record → `104.131.171.175`
For staging: `STAGING_DOMAIN` A record → `137.184.49.99` (or whatever you set)

DNS must resolve **before** the stack first comes up, or Let's Encrypt will fail
the ACME challenge.

### 5. Create `/opt/graphwright` directory

```bash
mkdir -p /opt/graphwright/gwchat-config /opt/graphwright/vhost.d
```

## First deploy (manual)

After the droplet is prepped, trigger a deploy by pushing to `main` (staging) or
tagging a release (prod). The GH Actions workflow will SSH in, write compose files,
and run `docker compose up`.

On first boot, `acme-companion` will issue the TLS cert — this takes ~30 seconds.
Check progress with:

```bash
docker compose -f /opt/graphwright/docker-compose.prod.yml logs acme-companion -f
```

Once you see `Certificate obtained successfully`, HTTPS is live.

## Routine deploys (CI)

Push to `main` → deploys to staging automatically.
Push a tag `v*` → deploys to prod automatically.

The workflow:
1. Builds and pushes Docker images to ghcr.io.
2. SSHes into the droplet.
3. Writes `docker-compose.prod.yml` (or staging), `gwchat-config/medlit.yaml`, and
   `vhost.d/graphwright.io` from the repo.
4. Runs `docker compose up -d --pull always --remove-orphans`.
5. No nginx reload needed — nginx-proxy picks up changes automatically.

## Manual deploy / rollback

SSH into the droplet and run:

```bash
cd /opt/graphwright
# update images
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --remove-orphans
```

To roll back to a specific image SHA:

```bash
# edit docker-compose.prod.yml to pin image tags to a specific SHA, then:
docker compose -f docker-compose.prod.yml up -d
```

## Checking cert status

```bash
docker exec $(docker ps -qf name=acme-companion) --list
```

## GitHub Actions secrets and variables required

| Name | Type | Value |
|------|------|-------|
| `DROPLET_SSH_KEY` | secret | private key for root@droplet |
| `GHCR_PAT` | secret | GitHub PAT with `read:packages` |
| `GHCR_USER` | secret | GitHub username |
| `POSTGRES_PASSWORD` | secret | postgres superuser password |
| `ANTHROPIC_API_KEY` | secret | |
| `OPENAI_API_KEY` | secret | |
| `UMLS_API_KEY` | secret | |
| `REGISTRY` | variable | `ghcr.io/graphwright` |
| `LLM_PROVIDER` | variable | `anthropic` |
| `PASS1_LLM_BACKEND` | variable | `anthropic` |
| `INGEST_PIPELINE_CLASS` | variable | (leave blank for default) |
| `STAGING_DOMAIN` | variable | staging hostname, e.g. `staging.graphwright.io` |

## Staging notes

The staging compose file (`docker-compose.staging.yml`) sets `LETSENCRYPT_TEST=true`,
which uses Let's Encrypt's staging CA. Staging certs are not trusted by browsers
but avoid rate limits while you're iterating on the setup. Remove that variable
(or set it to `false`) when you're ready for a real cert on staging.

`STAGING_DOMAIN` must be set as a GH Actions variable for the staging domain to
be picked up by the compose file.

## Troubleshooting

**HTTPS not working after first deploy**
- Check DNS resolves: `dig graphwright.io`
- Check cert issuance: `docker compose logs acme-companion`
- Check nginx-proxy config: `docker exec <nginx-proxy-container> nginx -T`

**502 Bad Gateway**
- Check the target container is healthy: `docker compose ps`
- Check logs: `docker compose logs api`

**SSE / WebSocket drops**
- The `vhost.d/graphwright.io` file sets `proxy_read_timeout 3600s` and disables
  buffering for `/sse`, `/mcp/`, `/messages/`. If you regenerate this file, make
  sure those settings are preserved.
