"""Embedding generation contracts used by extraction and entity resolution.

This module defines the interface for generating semantic vector embeddings,
which are dense numerical representations of text that capture meaning.
Embeddings enable several key knowledge graph operations:

- **Entity resolution**: Match entity mentions to existing entities with
  similar meanings but different surface forms (e.g., "heart attack" vs
  "myocardial infarction").

- **Duplicate detection**: Identify canonical entities that should be merged
  by finding pairs with high embedding similarity.

- **Semantic search**: Query the knowledge graph by meaning rather than
  exact text matching.

Implementations typically wrap embedding APIs such as:
    - OpenAI text-embedding-3-small/large
    - Cohere embed-english-v3.0
    - Sentence Transformers (local models)
    - Domain-specific embeddings (BioBERT, LegalBERT, etc.)
"""

from abc import ABC, abstractmethod
from typing import Sequence


class EmbeddingGeneratorInterface(ABC):
    """Generate semantic vector embeddings for text.

    This interface abstracts embedding generation, allowing the knowledge
    graph framework to work with any embedding provider. Implementations
    should be stateless and thread-safe.

    The embedding vectors are stored as immutable tuples of floats to ensure
    they can be safely shared and used as dictionary keys or set members.

    Typical usage:
        ```python
        embedder = OpenAIEmbedding(client, model="text-embedding-3-small")
        embedding = await embedder.generate("aspirin")
        similar_entities = await storage.find_by_embedding(embedding, threshold=0.85)
        ```

    When implementing:
        - Handle empty strings gracefully (return zero vector or raise)
        - Consider rate limiting and retries for API-based implementations
        - Normalize vectors if the similarity search requires it
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimensionality of generated embeddings.

        This property is essential for:
            - Storage backends that need to configure vector columns/indices
            - Validation that embeddings match expected dimensions
            - Memory estimation for batch operations

        The dimension depends on the underlying model:
            - OpenAI text-embedding-3-small: 1536
            - OpenAI text-embedding-3-large: 3072
            - Sentence Transformers all-MiniLM-L6-v2: 384

        Returns:
            Integer dimension of embedding vectors (e.g., 1536, 3072).
        """

    @abstractmethod
    async def generate(self, text: str) -> tuple[float, ...]:
        """Generate an embedding vector for a single text string.

        Transforms the input text into a dense vector representation that
        captures its semantic meaning. Similar texts produce vectors with
        high cosine similarity.

        Args:
            text: Input text to embed. May be a single word, phrase, sentence,
                or paragraph. Very long texts may be truncated by the underlying
                model.

        Returns:
            Embedding vector as an immutable tuple of floats with length
            equal to self.dimension. Values are typically in the range [-1, 1]
            for normalized embeddings.

        Raises:
            ValueError: If text is empty (implementation-dependent).
            RuntimeError: If the embedding API call fails.
        """

    @abstractmethod
    async def generate_batch(
        self,
        texts: Sequence[str],
    ) -> list[tuple[float, ...]]:
        """Generate embeddings for multiple texts efficiently.

        Batch generation is significantly more efficient than calling
        generate() repeatedly, especially for API-based implementations
        that support batch requests.

        Use batch generation when:
            - Processing multiple entity mentions from a document
            - Computing embeddings for entity promotion candidates
            - Initializing embeddings for imported entities

        Args:
            texts: Sequence of input texts to embed. Order is preserved
                in the output.

        Returns:
            List of embedding vectors in the same order as input texts.
            Each vector is a tuple of floats with length self.dimension.

        Raises:
            ValueError: If texts is empty or contains empty strings
                (implementation-dependent).
            RuntimeError: If the embedding API call fails.
        """
