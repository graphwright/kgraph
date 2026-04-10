#!/usr/bin/env python3
"""ingest: Deduplication and promotion over per-paper bundles.

Reads all paper_*.json bundles from --bundle-dir (output of extract), builds
name/type index and synonym cache, resolves SAME_AS, assigns canonical IDs,
and writes merged entities and relationships to --output-dir. Original
bundle files are never modified.

Usage (legacy file-based pipeline):
  python -m medlit.scripts.ingest --bundle-dir extracted/ --output-dir merged/

Usage (identity server):
  python -m medlit.scripts.ingest --bundle-dir extracted/ --output-dir merged/ \\
      --use-identity-server
  Requires DATABASE_URL env var pointing to a running Postgres instance with
  the kgserver schema already created.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from medlit.pipeline.dedup import run_ingest, run_ingest_with_identity_server


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ingest: Deduplicate and promote entities/relationships from per-paper bundles.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing paper_*.json bundle files (extract output)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("merged"),
        help="Output directory for merged entities.json, relationships.json",
    )
    parser.add_argument(
        "--use-identity-server",
        action="store_true",
        help=("Use PostgresIdentityServer for entity resolution instead of the " "legacy file-based synonym cache and authority lookup chain. " "Requires DATABASE_URL env var."),
    )
    # Legacy options (only used when --use-identity-server is NOT set)
    parser.add_argument(
        "--synonym-cache",
        type=Path,
        default=None,
        help="(Legacy) Path to synonym cache file (default: <output-dir>/synonym_cache.json)",
    )
    parser.add_argument(
        "--canonical-id-cache",
        type=Path,
        default=None,
        help="(Legacy) Path to canonical ID lookup cache. If set, ingest resolves entities via authority APIs.",
    )
    parser.add_argument(
        "--no-canonical-id-lookup",
        action="store_true",
        help="(Legacy) Disable authority lookup even if --canonical-id-cache is set.",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.88,
        help="(Legacy) Min cosine similarity for embedding-based provisional merge (default 0.88).",
    )
    args = parser.parse_args()

    if not args.bundle_dir.exists():
        print(f"Error: bundle dir not found: {args.bundle_dir}", file=sys.stderr)
        sys.exit(1)

    if args.use_identity_server:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("Error: --use-identity-server requires DATABASE_URL env var", file=sys.stderr)
            sys.exit(1)

        from sqlalchemy import create_engine
        from sqlmodel import Session, SQLModel
        from medlit.domain import MedLitDomainSchema
        from kgserver.storage.backends.identity import AuthorityCache, PostgresIdentityServer

        engine = create_engine(db_url)
        SQLModel.metadata.create_all(engine)
        domain = MedLitDomainSchema()
        authority_cache = AuthorityCache.from_env()

        with Session(engine) as session:
            identity_server = PostgresIdentityServer(
                session=session,
                domain=domain,
                authority_cache=authority_cache,
            )
            result = asyncio.run(
                run_ingest_with_identity_server(
                    bundle_dir=args.bundle_dir,
                    output_dir=args.output_dir,
                    identity_server=identity_server,
                )
            )
            session.commit()
    else:
        canonical_id_cache_path = None
        if args.canonical_id_cache is not None and not args.no_canonical_id_lookup:
            canonical_id_cache_path = args.canonical_id_cache

        result = run_ingest(
            bundle_dir=args.bundle_dir,
            output_dir=args.output_dir,
            synonym_cache_path=args.synonym_cache,
            canonical_id_cache_path=canonical_id_cache_path,
            similarity_threshold=args.similarity_threshold,
        )

    if "error" in result:
        print(result["error"], file=sys.stderr)
        sys.exit(1)
    print(
        f"ingest done: {result['entities_count']} entities, {result['relationships_count']} relationships",
        file=sys.stderr,
    )
    print(f"  entities: {result['entities_path']}", file=sys.stderr)
    print(f"  relationships: {result['relationships_path']}", file=sys.stderr)


if __name__ == "__main__":
    main()
