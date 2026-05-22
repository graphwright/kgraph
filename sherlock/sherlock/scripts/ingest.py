#!/usr/bin/env python3
"""ingest: Deduplication and alias resolution for Sherlock story bundle.

Reads a story bundle JSON (from sherlock-extract), runs the dedup pipeline
(SAME_AS resolution, alias normalisation, entity merging), and writes the
deduplicated bundle JSON.

Usage:
  sherlock-ingest --input story_scandal_in_bohemia.json --output deduped/
  sherlock-ingest --input sherlock_output/story_scandal_in_bohemia.json
"""

import argparse
import json
import sys
from pathlib import Path

from ..pipeline.dedup import run_dedup_from_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ingest: Dedup and alias-resolve Sherlock story bundle.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input story bundle JSON (from sherlock-extract)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for deduped bundle (default: same as input with _deduped suffix)",
    )

    args = parser.parse_args()
    input_path: Path = args.input

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output_dir or input_path.parent / "deduped"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / input_path.name.replace("story_", "deduped_story_")

    print(f"ingest: {input_path} → {output_path}", file=sys.stderr)
    stats = run_dedup_from_file(input_path, output_path)

    print(f"  entities: {stats['entities_before']} → {stats['entities_after']} (-{stats['entities_merged']} merged)", file=sys.stderr)
    print(f"  relationships: {stats['relationships_before']} → {stats['relationships_after']}", file=sys.stderr)
    print(f"  Wrote {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
