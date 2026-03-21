# Operations Guide

## Full redeploy on the droplet

Tears down the running stack, prunes old images, pulls latest code, rebuilds, and
starts fresh. Use this after any code or bundle change.

```bash
docker compose --profile api down -v && \
docker image prune -a && \
git pull && \
docker compose --profile api build && \
docker compose --profile api up -d && \
docker compose --profile api logs -f
```

## Reloading the bundle without a full redeploy

If the bundle data has changed but the bundle ID is unchanged (e.g. you re-ran
ingestion on the same paper set), the server will skip the load on startup because
it sees the bundle as already loaded. Force a reload with:

```bash
BUNDLE_FORCE_RELOAD=1 docker compose --profile api up -d
```

This clears the Bundle, Entity, and Relationship tables and re-loads from the
bundle directory before serving requests.

## Batch ingestion (local)

Requires Postgres accessible on `localhost:5432` (the `local` profile):

```bash
docker compose --profile local up -d
export DATABASE_URL=postgresql://postgres:$(grep POSTGRES_PASSWORD .env | cut -d= -f2)@localhost:5432/kgserver
./rin.sh --list <name>        # e.g. adrenal, smorgasbord
```

See `./rin.sh --list` for available paper sets.

After ingestion completes, the new bundle is in `bundle/`. Redeploy with
`BUNDLE_FORCE_RELOAD=1 docker compose --profile api up -d` (or full redeploy above).
