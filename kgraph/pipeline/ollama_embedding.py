"""Ollama embedding generator.

Uses Ollama's /api/embed endpoint (single or batch input).
"""

import os
from typing import Optional, Sequence

import httpx

from kgraph.pipeline.embedding import EmbeddingGeneratorInterface


class OllamaEmbeddingGenerator(EmbeddingGeneratorInterface):
    """Embedding generator using Ollama.

    Uses Ollama's /api/embed API. Supports single text or batch of texts
    in one request. Default model is nomic-embed-text; mxbai-embed-large
    also works well.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        ollama_host: str | None = None,
        timeout: float = 30.0,
    ):
        self.model = model
        self.ollama_host: str = (
            ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434") or "http://localhost:11434"
        )
        self.timeout = timeout
        self._dimension: Optional[int] = None

    @property
    def dimension(self) -> int:
        """Return embedding dimension for the model.

        Common dimensions:
        - nomic-embed-text: 768
        - mxbai-embed-large: 1024
        - bge-large: 1024
        """
        if self._dimension is None:
            raise RuntimeError("Dimension not yet determined. Call generate() at least once first.")
        return self._dimension

    def _url(self) -> str:
        return f"{self.ollama_host.rstrip('/')}/api/embed"

    async def generate(self, text: str) -> tuple[float, ...]:
        """Generate embedding for a single text using Ollama /api/embed."""
        result = await self._request_batch([text])
        return result[0]

    async def _request_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        """One HTTP request for one or more texts. Response order matches input order."""
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload: dict = {"model": self.model}
            if len(texts) == 1:
                payload["input"] = texts[0]
            else:
                payload["input"] = texts
            response = await client.post(self._url(), json=payload)
            response.raise_for_status()
            data = response.json()
        emb_list = data.get("embeddings")
        if not emb_list or not isinstance(emb_list, list):
            raise ValueError(f"Unexpected response format: {data}")
        if len(emb_list) != len(texts):
            raise ValueError(f"Embedding count {len(emb_list)} does not match input count {len(texts)}")
        if self._dimension is None and emb_list:
            self._dimension = len(emb_list[0])
        return [tuple(e) for e in emb_list]

    async def generate_batch(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        """Generate embeddings for multiple texts in one request when possible."""
        if not texts:
            return []
        return await self._request_batch(list(texts))
