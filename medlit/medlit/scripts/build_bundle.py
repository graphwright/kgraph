#!/usr/bin/env python3
"""build_bundle: Build kgbundle from merged and extracted.

Reads merged_dir (entities.json, relationships.json, id_map.json, synonym_cache.json)
and bundles_dir (paper_*.json), writes output_dir in kgbundle format for kgserver.
"""

import sys
from pathlib import Path

from medlit.pipeline.bundle_builder import run_build_bundle


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="build_bundle: Build kgbundle from merged and extracted.",
    )
    parser.add_argument("--merged-dir", type=Path, required=True, help="ingest merged output directory")
    parser.add_argument("--bundles-dir", type=Path, required=True, help="extract paper_*.json bundles directory")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("bundle"),
        help="Output kgbundle directory (default: bundle)",
    )
    parser.add_argument(
        "--pmc-xmls-dir",
        type=Path,
        default=None,
        help="If provided, copy JATS-XML source files for each paper into output_dir/sources/",
    )
    args = parser.parse_args()

    merged_dir = args.merged_dir.resolve()
    bundles_dir = args.bundles_dir.resolve()
    output_dir = args.output_dir.resolve()
    pmc_xmls_dir = args.pmc_xmls_dir.resolve() if args.pmc_xmls_dir else None

    if not merged_dir.is_dir():
        print(f"Error: merged-dir is not a directory: {merged_dir}", file=sys.stderr)
        return 1
    if not (merged_dir / "id_map.json").exists():
        print(
            f"Error: id_map.json not found in {merged_dir}. Run ingest so that merged_dir contains id_map.json.",
            file=sys.stderr,
        )
        return 1
    if not bundles_dir.is_dir():
        print(f"Error: bundles-dir is not a directory: {bundles_dir}", file=sys.stderr)
        return 1

    try:
        summary = run_build_bundle(merged_dir, bundles_dir, output_dir, pmc_xmls_dir=pmc_xmls_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(
        f"build_bundle complete: {summary['entity_count']} entities, {summary['relationship_count']} relationships, " f"{summary['evidence_count']} evidence, {summary['mention_count']} mentions",
        file=sys.stderr,
    )
    print(f"Manifest: {summary['manifest_path']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
