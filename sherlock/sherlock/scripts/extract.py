#!/usr/bin/env python3
"""extract: LLM extraction from 'A Scandal in Bohemia' → per-story bundle JSON.

Fetches the story text (from Project Gutenberg or a local file), chunks it into
paragraph windows, calls the configured LLM once per window, and writes a single
bundle JSON file.

Usage:
  sherlock-extract --output-dir output/ --llm-backend anthropic
  sherlock-extract --output-dir output/ --llm-backend ollama
  sherlock-extract --output-dir output/ --story-file scandal.txt --llm-backend anthropic
  sherlock-extract --output-dir output/ --llm-backend anthropic --window-size 5 --limit-chunks 10

Set ANTHROPIC_API_KEY for Anthropic, or run Ollama locally.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

from ..bundle_models import StoryInfo
from ..pipeline.parser import (
    SCANDAL_STORY_ID,
    SCANDAL_TITLE,
    SCANDAL_YEAR,
    chunk_story_windowed,
    get_story_text,
)
from ..pipeline.extractor import extract_story


SCANDAL_STORY_METADATA = StoryInfo(
    story_id=SCANDAL_STORY_ID,
    title=SCANDAL_TITLE,
    collection="The Adventures of Sherlock Holmes",
    author="Arthur Conan Doyle",
    year=SCANDAL_YEAR,
    source_uri="https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    document_id=SCANDAL_STORY_ID,
)


async def run_extract(
    output_dir: Path,
    llm_backend: str,
    story_file: Optional[Path] = None,
    window_size: int = 3,
    limit_chunks: Optional[int] = None,
    skip_if_exists: bool = True,
) -> None:
    """Run full extraction pipeline for A Scandal in Bohemia."""
    from kgraph.pipeline.pass1_llm import get_pass1_llm

    story_id = SCANDAL_STORY_ID
    out_path = output_dir / f"story_{story_id}.json"

    if skip_if_exists and out_path.exists():
        print(f"  Skip (exists): {out_path.name}", file=sys.stderr)
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch story text
    print(f"  Fetching story text...", file=sys.stderr)
    story_text = get_story_text(local_path=story_file)
    if not story_text:
        print("ERROR: Could not get story text", file=sys.stderr)
        sys.exit(1)
    print(f"  Story text: {len(story_text)} chars", file=sys.stderr)

    # Chunk
    chunks = chunk_story_windowed(story_text, window_size=window_size)
    if limit_chunks is not None:
        chunks = chunks[:limit_chunks]
    print(f"  Chunks: {len(chunks)} windows (window_size={window_size})", file=sys.stderr)

    # LLM
    llm = get_pass1_llm(llm_backend)
    story_info = SCANDAL_STORY_METADATA

    print(f"  Extracting with {llm_backend}...", file=sys.stderr)
    bundle = await extract_story(story_info, chunks, llm, verbose=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle.to_bundle_dict(), f, indent=2)

    print(
        f"  Wrote {out_path.name} ({len(bundle.entities)} entities, {len(bundle.relationships)} rels)",
        file=sys.stderr,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="extract: Extract Sherlock Holmes entities+relationships via LLM.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--output-dir", type=Path, default=Path("sherlock_output"), help="Output directory for bundle JSON")
    parser.add_argument(
        "--llm-backend",
        type=str,
        choices=("anthropic", "openai", "ollama"),
        default=os.environ.get("LLM_BACKEND", "ollama"),
        help="LLM backend (default: LLM_BACKEND or ollama)",
    )
    parser.add_argument("--story-file", type=Path, default=None, help="Local story text file (overrides Gutenberg fetch)")
    parser.add_argument("--window-size", type=int, default=3, help="Number of paragraphs per chunk window (default: 3)")
    parser.add_argument("--limit-chunks", type=int, default=None, help="Limit number of chunks to process (for testing)")
    parser.add_argument("--overwrite", action="store_true", help="Re-extract even if output file already exists")

    args = parser.parse_args()

    asyncio.run(
        run_extract(
            output_dir=args.output_dir,
            llm_backend=args.llm_backend,
            story_file=args.story_file,
            window_size=args.window_size,
            limit_chunks=args.limit_chunks,
            skip_if_exists=not args.overwrite,
        )
    )


if __name__ == "__main__":
    main()
