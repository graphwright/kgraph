"""MedlitPipeline: top-level IngestPipeline implementation for medlit.

Implements the IngestPipeline ABC (or ducks as one if the interface package
is not installed) by delegating to the medlit pipeline scripts.
"""

from pathlib import Path
from typing import Any, Optional

try:
    from pipeline_interface import IngestPipeline
except ImportError:
    from abc import ABC as IngestPipeline  # type: ignore[assignment]

from medlit.domain_spec import ENTITY_TYPE_SPECS


class MedlitPipeline(IngestPipeline):  # type: ignore[misc]
    """End-to-end medlit knowledge-graph ingestion pipeline.

    Orchestrates fetch_vocab → extract → ingest → build_bundle stages
    for medical-literature papers in JATS-XML or pre-parsed JSON format.
    """

    def get_entity_type_specs(self) -> dict[str, Any]:
        """Return entity type specifications from the medlit domain spec."""
        return dict(ENTITY_TYPE_SPECS)

    def fetch_vocab(
        self,
        input_dir: Path,
        output_dir: Path,
        llm_backend: str = "anthropic",
        papers: Optional[list[str]] = None,
        limit: Optional[int] = None,
    ) -> None:
        """Extract vocabulary from papers and write vocab.json + seeded_synonym_cache.json.

        Args:
            input_dir: Directory containing paper XML/JSON files.
            output_dir: Output directory for vocab.json and seeded_synonym_cache.json.
            llm_backend: LLM backend to use ("anthropic", "openai", or "ollama").
            papers: Optional list of glob patterns to filter input files.
            limit: Optional maximum number of papers to process.
        """
        import asyncio
        from medlit.scripts.fetch_vocab import run_fetch_vocab

        asyncio.run(run_fetch_vocab(input_dir, output_dir, llm_backend, papers, limit))

    def extract(
        self,
        input_dir: Path,
        output_dir: Path,
        llm_backend: str = "anthropic",
        papers: Optional[list[str]] = None,
        limit: Optional[int] = None,
        vocab_dir: Optional[Path] = None,
    ) -> None:
        """Run Pass 1 + Pass 2 extraction and write per-paper bundle JSON files.

        Args:
            input_dir: Directory containing paper XML/JSON files.
            output_dir: Output directory for paper_*.json bundle files.
            llm_backend: LLM backend to use.
            papers: Optional list of glob patterns to filter input files.
            limit: Optional maximum number of papers to process.
            vocab_dir: Optional path to vocab.json / seeded_synonym_cache.json.
        """
        import asyncio
        from medlit.scripts.extract import run_extract

        asyncio.run(
            run_extract(
                input_dir=input_dir,
                output_dir=output_dir,
                llm_backend=llm_backend,
                papers=papers,
                limit=limit,
                vocab_dir=vocab_dir,
            )
        )

    def run_ingest(
        self,
        bundle_dir: Path,
        output_dir: Path,
        synonym_cache_path: Optional[Path] = None,
        canonical_id_cache_path: Optional[Path] = None,
        similarity_threshold: float = 0.88,
    ) -> dict[str, Any]:
        """Deduplicate and promote entities/relationships from per-paper bundles.

        Args:
            bundle_dir: Directory containing paper_*.json bundle files.
            output_dir: Output directory for merged entities.json and relationships.json.
            synonym_cache_path: Optional path to synonym cache file.
            canonical_id_cache_path: Optional path to canonical ID lookup cache.
            similarity_threshold: Min cosine similarity for embedding-based merge.

        Returns:
            Result dict with entities_count, relationships_count, and output paths.
        """
        from medlit.pipeline.dedup import run_ingest as _run_ingest

        return _run_ingest(
            bundle_dir=bundle_dir,
            output_dir=output_dir,
            synonym_cache_path=synonym_cache_path,
            canonical_id_cache_path=canonical_id_cache_path,
            similarity_threshold=similarity_threshold,
        )

    def build_bundle(
        self,
        merged_dir: Path,
        bundles_dir: Path,
        output_dir: Path,
        pmc_xmls_dir: Optional[Path] = None,
    ) -> dict[str, Any]:
        """Build kgbundle from merged ingest output and per-paper bundles.

        Args:
            merged_dir: ingest output directory (entities.json, relationships.json, id_map.json).
            bundles_dir: Directory containing paper_*.json bundle files.
            output_dir: Output directory in kgbundle format.
            pmc_xmls_dir: Optional directory of JATS-XML sources to copy into output.

        Returns:
            Summary dict with entity_count, relationship_count, evidence_count, manifest_path.
        """
        from medlit.pipeline.bundle_builder import run_build_bundle

        return run_build_bundle(
            merged_dir=merged_dir,
            bundles_dir=bundles_dir,
            output_dir=output_dir,
            pmc_xmls_dir=pmc_xmls_dir,
        )
