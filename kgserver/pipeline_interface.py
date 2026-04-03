"""
Abstract base class for domain-specific ingest pipelines.

kgserver is domain-agnostic: it does not import any domain package directly.
Instead, a concrete implementation of IngestPipeline is loaded at startup from
the class path specified in the INGEST_PIPELINE_CLASS environment variable.

Domain packages (e.g. medlit_bundle) implement this interface and register
themselves via that env var.

Example::

    INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline
"""

from abc import ABC, abstractmethod
from pathlib import Path


class IngestPipeline(ABC):
    """
    Domain-specific ingest pipeline contract.

    Implementations provide the four pipeline stages used by ingest_worker,
    plus entity-type metadata for graph visualization.

    All Path arguments are absolute paths to existing directories.
    Implementations may assume the directories already exist.
    """

    @abstractmethod
    async def fetch_vocab(
        self,
        input_dir: Path,
        vocab_dir: Path,
        llm_backend: str,
        papers: object,
        limit: int,
    ) -> None:
        """
        Pass 0: build/merge vocabulary from documents in input_dir into vocab_dir.

        Parameters
        ----------
        input_dir:
            Directory containing raw input documents (e.g. PubMed XML files).
        vocab_dir:
            Persistent workspace directory for accumulated vocabulary files.
        llm_backend:
            LLM backend identifier (e.g. "anthropic", "openai").
        papers:
            Optional paper filter; pass None to process all documents in input_dir.
        limit:
            Maximum number of documents to process in this call.
        """

    @abstractmethod
    async def extract(
        self,
        input_dir: Path,
        bundles_dir: Path,
        llm_backend: str,
        limit: int,
        vocab_file: Path,
    ) -> None:
        """
        Pass 1 + 2: extract entities and relationships from documents, writing
        per-document bundle JSON files into bundles_dir.

        Parameters
        ----------
        input_dir:
            Directory containing raw input documents.
        bundles_dir:
            Output directory for per-document bundle JSON files (paper_*.json).
        llm_backend:
            LLM backend identifier.
        limit:
            Maximum number of documents to process.
        vocab_file:
            Path to the accumulated vocabulary file produced by fetch_vocab.
        """

    @abstractmethod
    def run_ingest(
        self,
        bundle_dir: Path,
        output_dir: Path,
        synonym_cache_path: Path,
        canonical_id_cache_path: object,
    ) -> None:
        """
        Pass 2 post-processing: merge bundle files, resolve synonyms and canonical IDs.

        Parameters
        ----------
        bundle_dir:
            Directory containing per-document bundle JSON files.
        output_dir:
            Directory for merged output (synonym_cache.json, etc.).
        synonym_cache_path:
            Path to the seeded or accumulated synonym cache file.
        canonical_id_cache_path:
            Optional path to a canonical ID cache file; pass None to skip.
        """

    @abstractmethod
    def build_bundle(
        self,
        merged_dir: Path,
        bundles_dir: Path,
        output_dir: Path,
    ) -> None:
        """
        Pass 3: assemble the final loadable bundle (manifest.json + NDJSON files).

        Parameters
        ----------
        merged_dir:
            Directory containing merged/deduped data from run_ingest.
        bundles_dir:
            Directory containing per-document bundle JSON files.
        output_dir:
            Output directory; must contain manifest.json on success.
        """

    def get_entity_type_specs(self) -> dict[str, dict[str, str]]:
        """
        Return entity-type metadata for graph visualization.

        Returns a mapping of entity_type string to a dict with keys:
            - ``"color"``: hex color string (e.g. ``"#e57373"``)
            - ``"label"``: human-readable display label

        A ``"default"`` key must be included as a fallback for unknown types.

        The base implementation returns only the default entry.  Override in
        domain subclasses to add domain-specific entity types.
        """
        return {"default": {"color": "#78909c", "label": "Other"}}
