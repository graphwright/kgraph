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

## Diagnosing a suspicious entity or relationship

When the graph shows a link that looks wrong, work outward from the source text:

1. **Check the extraction layer.** Use the `get_paper_source` and `get_mentions` MCP tools to
   pull the paper text and the mentions extracted from it, and confirm each mention matches
   what the passage actually says. If the mentions are wrong, the problem is in Pass 1.
2. **If the mentions look clean, suspect a false-positive merge.** A bogus link that appears
   only *after* Pass 2 deduplication is usually an over-eager entity merge rather than an
   extraction error.
3. **Merge-bug signature.** In `merged/id_map.json`, look for multiple source IDs mapping to
   the same canonical ID. That is what a merge looks like; check whether the merged entities
   were genuinely the same thing.

Note that mention positional metadata is currently broken (see "Known Defects" in `TODO.md`),
so `get_mentions` cannot yet point at a character offset within the source — you have to
locate the quoted span by text search.
