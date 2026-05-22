#!/usr/bin/env python3
"""build_bundle: Assemble kgbundle from deduped Sherlock story bundle.

Reads the deduplicated story bundle JSON (from sherlock-ingest) and writes a
kgbundle directory (entities.jsonl, relationships.jsonl, evidence.jsonl, manifest.json)
that can be loaded directly by kgserver.

Usage:
  sherlock-build-bundle --input deduped/deduped_story_scandal_in_bohemia.json --output-dir bundle/
  sherlock-build-bundle --input sherlock_output/deduped/deduped_story_scandal_in_bohemia.json
"""

import argparse
import sys
from pathlib import Path

from ..pipeline.bundle_builder import build_bundle_from_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="build_bundle: Assemble kgbundle from deduped Sherlock story bundle.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input deduped story bundle JSON",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for kgbundle (default: bundle/ next to input)",
    )
    parser.add_argument(
        "--no-story-provenance",
        action="store_true",
        help="Skip adding DESCRIBED_IN edges from all entities to the Story node",
    )

    args = parser.parse_args()
    input_path: Path = args.input

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output_dir or input_path.parent.parent / "bundle"

    print(f"build_bundle: {input_path} → {output_dir}/", file=sys.stderr)
    stats = build_bundle_from_files(
        input_path,
        output_dir,
        add_story_provenance=not args.no_story_provenance,
    )

    print(f"  entities: {stats['entities']}", file=sys.stderr)
    print(f"  relationships: {stats['relationships']}", file=sys.stderr)
    print(f"  evidence: {stats['evidence']}", file=sys.stderr)
    print(f"  Wrote {output_dir}/", file=sys.stderr)


if __name__ == "__main__":
    main()
