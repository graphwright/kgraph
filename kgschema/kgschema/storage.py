"""Storage interface definitions for the knowledge graph framework.

This module defines abstract interfaces for persisting knowledge graph data:
entities, relationships, and documents. These interfaces decouple the core
framework from specific storage backends, enabling:

- **In-memory storage** for testing and development
- **Relational databases** (PostgreSQL, MySQL) for ACID guarantees
- **Vector databases** (Pinecone, Weaviate, Qdrant) for embedding search
- **Graph databases** (Neo4j, ArangoDB) for relationship traversal

All interfaces are async-first to support non-blocking I/O with database
drivers like asyncpg, motor, or aioredis.

The storage layer supports key knowledge graph operations:
    - Entity lifecycle: create, read, update, delete, promote, merge
    - Relationship management: add, query by subject/object, update references
    - Document tracking: store source documents for provenance
    - Similarity search: find entities by embedding vectors
"""

from abc import ABC, abstractmethod
from typing import Sequence

from kgschema.document import BaseDocument
from kgschema.entity import BaseEntity
from kgschema.relationship import BaseRelationship


class EntityStorageInterface(ABC):
    """Abstract interface for entity storage operations.

    Entity storage is the primary persistence layer for knowledge graph nodes.
    It must support both basic CRUD operations and specialized queries for
    the entity lifecycle:

    - **Canonical entities**: Stable entities linked to authoritative sources
      (UMLS CUIs, Wikidata QIDs, etc.)
    - **Provisional entities**: Newly discovered mentions awaiting promotion
      based on usage frequency and confidence thresholds

    Implementations must handle:
        - Efficient lookup by ID and name/synonyms
        - Embedding-based similarity search for resolution and merge detection
        - Atomic promotion (provisional → canonical) and merge operations
        - Pagination for listing large entity collections

    Thread safety: Implementations should be safe for concurrent access from
    multiple async tasks.
    """

    @abstractmethod
    async def add(self, entity: BaseEntity) -> str:
        """Store an entity and return its ID.

        This is the primary method for persisting new entities. The entity's
        `entity_id` field determines its storage key.

        Args:
            entity: The entity to store. Must have a valid entity_id.

        Returns:
            The entity_id of the stored entity.

        Raises:
            ValueError: If entity_id is missing or invalid.

        Note:
            If an entity with the same ID already exists, implementations
            may either update it (upsert behavior) or raise an error,
            depending on the backend's policy.
        """

    @abstractmethod
    async def get(self, entity_id: str) -> BaseEntity | None:
        """Retrieve an entity by its unique identifier.

        Args:
            entity_id: The unique identifier of the entity to retrieve.

        Returns:
            The entity if found, or None if no entity exists with that ID.
        """

    @abstractmethod
    async def get_batch(self, entity_ids: Sequence[str]) -> list[BaseEntity | None]:
        """Retrieve multiple entities by ID in a single operation.

        Batch retrieval is more efficient than multiple get() calls,
        especially for network-based storage backends.

        Args:
            entity_ids: Sequence of entity IDs to retrieve.

        Returns:
            List of entities in the same order as input IDs. Missing
            entities are represented as None in the corresponding position.
        """

    @abstractmethod
    async def find_by_embedding(
        self,
        embedding: Sequence[float],
        threshold: float = 0.8,
        limit: int = 10,
    ) -> list[tuple[BaseEntity, float]]:
        """Find entities semantically similar to the given embedding vector.

        This is the core operation for entity resolution and duplicate
        detection. Uses cosine similarity (or similar metric) to compare
        the query embedding against stored entity embeddings.

        Args:
            embedding: Query embedding vector. Must have the same dimension
                as stored entity embeddings.
            threshold: Minimum similarity score (0.0 to 1.0) for inclusion
                in results. Higher thresholds return fewer, more similar results.
            limit: Maximum number of results to return.

        Returns:
            List of (entity, similarity_score) tuples, sorted by descending
            similarity. Only includes entities with similarity >= threshold.
            Returns empty list if no entities meet the threshold.

        Note:
            Performance depends heavily on the storage backend. Consider
            using specialized vector indices (pgvector, FAISS, HNSW) for
            large entity collections.
        """

    @abstractmethod
    async def find_by_name(
        self,
        name: str,
        entity_type: str | None = None,
        limit: int = 10,
    ) -> list[BaseEntity]:
        """Find entities matching the given name or synonym.

        Searches the entity's primary name and any registered synonyms.
        Matching may be exact or fuzzy depending on the implementation.

        Args:
            name: The name or synonym to search for.
            entity_type: Optional filter to restrict results to a specific
                entity type (e.g., 'drug', 'gene', 'person').
            limit: Maximum number of results to return.

        Returns:
            List of matching entities, ordered by relevance (implementation-
            dependent). Returns empty list if no matches found.
        """

    @abstractmethod
    async def find_provisional_for_promotion(
        self,
        min_usage: int,
        min_confidence: float,
    ) -> list[BaseEntity]:
        """Find provisional entities eligible for promotion to canonical status.

        Promotion eligibility is based on:
            - Entity status is PROVISIONAL
            - Usage count >= min_usage (evidence of repeated mentions)
            - Confidence score >= min_confidence

        Args:
            min_usage: Minimum number of times the entity must have been
                referenced across documents.
            min_confidence: Minimum confidence score from entity resolution.

        Returns:
            List of provisional entities meeting the promotion criteria.
            These entities are candidates for canonical ID assignment.
        """

    @abstractmethod
    async def update(self, entity: BaseEntity) -> bool:
        """Update an existing entity's data.

        Replaces the stored entity with the provided entity. The entity_id
        must match an existing entity.

        Args:
            entity: The updated entity. The entity_id field identifies
                which entity to update.

        Returns:
            True if the entity was found and updated, False if no entity
            exists with the given ID.
        """

    @abstractmethod
    async def promote(
        self,
        entity_id: str,
        new_entity_id: str,
        canonical_ids: dict[str, str],
    ) -> BaseEntity | None:
        """Promote a provisional entity to canonical status.

        Promotion involves:
            1. Changing the entity's status from PROVISIONAL to CANONICAL
            2. Assigning the new canonical entity_id
            3. Recording canonical IDs from external authorities

        Args:
            entity_id: Current ID of the provisional entity to promote.
            new_entity_id: New canonical ID for the entity (typically
                derived from an authority like UMLS or Wikidata).
            canonical_ids: Mapping of authority names to their IDs for this
                entity (e.g., {'umls': 'C0004057', 'mesh': 'D001241'}).

        Returns:
            The updated entity with canonical status, or None if no entity
            was found with the given entity_id.

        Note:
            Implementations should also update any relationships referencing
            the old entity_id, or provide a separate method for this.
        """

    @abstractmethod
    async def merge(
        self,
        source_ids: Sequence[str],
        target_id: str,
    ) -> bool:
        """Merge multiple entities into a single target entity.

        Used when duplicate detection identifies entities that represent
        the same real-world concept. The merge operation:
            - Combines usage counts from all source entities into target
            - Merges synonyms from source entities into target
            - Removes source entities from storage
            - (Optionally) Updates relationship references

        Args:
            source_ids: IDs of entities to merge into the target. These
                entities will be deleted after merging.
            target_id: ID of the entity that will absorb the source entities.
                Must exist in storage.

        Returns:
            True if the merge succeeded, False if target_id was not found
            or if any source entity could not be processed.
        """

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity from storage.

        Args:
            entity_id: ID of the entity to delete.

        Returns:
            True if the entity was found and deleted, False if no entity
            exists with the given ID.

        Warning:
            Deleting entities may leave orphaned relationship references.
            Consider using merge() instead to preserve data integrity.
        """

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of entities in storage.

        Returns:
            Integer count of all entities (both canonical and provisional).
        """

    @abstractmethod
    async def list_all(
        self,
        status: str | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[BaseEntity]:
        """List entities with pagination and optional filtering.

        Args:
            status: Optional filter by entity status. Valid values:
                - 'canonical': Only canonical entities
                - 'provisional': Only provisional entities
                - None: All entities regardless of status
            limit: Maximum number of entities to return (default 1000).
            offset: Number of entities to skip for pagination (default 0).

        Returns:
            List of entities matching the filter criteria. Order is
            implementation-dependent but should be consistent across
            paginated calls.
        """


class RelationshipStorageInterface(ABC):
    """Abstract interface for relationship (edge) storage operations.

    Relationships represent the edges in the knowledge graph, connecting
    entity nodes via typed predicates. Each relationship is a triple:
    (subject_entity, predicate, object_entity) with additional metadata.

    Key operations:
        - **Graph traversal**: Query outgoing edges (by subject) or
          incoming edges (by object) for graph navigation
        - **Triple lookup**: Check if a specific relationship exists
        - **Reference updates**: Maintain referential integrity when
          entities are promoted or merged
        - **Provenance tracking**: Query relationships by source document

    Relationships may be extracted from multiple documents, so implementations
    should support aggregating evidence (confidence scores, source documents)
    when the same triple is extracted repeatedly.
    """

    @abstractmethod
    async def add(self, relationship: BaseRelationship) -> str:
        """Store a relationship and return an identifier.

        Args:
            relationship: The relationship to store, containing subject_id,
                predicate, object_id, and metadata (confidence, sources).

        Returns:
            An identifier for the stored relationship. This may be a
            composite key derived from the triple or a generated ID.

        Note:
            If a relationship with the same (subject, predicate, object)
            triple already exists, implementations may:
                - Merge metadata (combine source documents, update confidence)
                - Replace the existing relationship
                - Raise an error
            The exact behavior is implementation-dependent.
        """

    @abstractmethod
    async def get_by_subject(
        self,
        subject_id: str,
        predicate: str | None = None,
    ) -> list[BaseRelationship]:
        """Get all relationships where the given entity is the subject.

        This retrieves outgoing edges from an entity—relationships where
        the entity is the "doer" or source of the action.

        Args:
            subject_id: ID of the entity whose outgoing relationships to find.
            predicate: Optional filter to restrict results to a specific
                relationship type (e.g., 'treats', 'cites', 'authored_by').

        Returns:
            List of relationships with the given subject. Returns empty
            list if no matching relationships exist.

        Example:
            # Get all things that aspirin treats
            relationships = await storage.get_by_subject(aspirin_id, 'treats')
        """

    @abstractmethod
    async def get_by_object(
        self,
        object_id: str,
        predicate: str | None = None,
    ) -> list[BaseRelationship]:
        """Get all relationships where the given entity is the object.

        This retrieves incoming edges to an entity—relationships where
        the entity is the "receiver" or target of the action.

        Args:
            object_id: ID of the entity whose incoming relationships to find.
            predicate: Optional filter to restrict results to a specific
                relationship type.

        Returns:
            List of relationships with the given object. Returns empty
            list if no matching relationships exist.

        Example:
            # Get all drugs that treat headache
            relationships = await storage.get_by_object(headache_id, 'treats')
        """

    @abstractmethod
    async def find_by_triple(
        self,
        subject_id: str,
        predicate: str,
        object_id: str,
    ) -> BaseRelationship | None:
        """Find a specific relationship by its complete triple.

        Args:
            subject_id: ID of the subject entity.
            predicate: The relationship type/predicate.
            object_id: ID of the object entity.

        Returns:
            The relationship if it exists, or None if no such triple
            has been stored.

        Example:
            # Check if aspirin treats headache
            rel = await storage.find_by_triple(aspirin_id, 'treats', headache_id)
            if rel:
                print(f"Confidence: {rel.confidence}")
        """

    @abstractmethod
    async def update_entity_references(
        self,
        old_entity_id: str,
        new_entity_id: str,
    ) -> int:
        """Update all relationships referencing an entity to use a new ID.

        This is critical for maintaining referential integrity when:
            - Promoting a provisional entity (ID changes)
            - Merging duplicate entities (source IDs point to target)

        Args:
            old_entity_id: The entity ID being replaced.
            new_entity_id: The entity ID to use in its place.

        Returns:
            The number of relationship references that were updated.
            A relationship with both subject and object matching old_entity_id
            counts as two updates.
        """

    @abstractmethod
    async def get_by_document(
        self,
        document_id: str,
    ) -> list[BaseRelationship]:
        """Get all relationships extracted from a specific document.

        Useful for:
            - Viewing all knowledge extracted from a document
            - Re-processing a document (delete old relationships first)
            - Audit and provenance tracking

        Args:
            document_id: ID of the source document.

        Returns:
            List of relationships where document_id appears in the
            source_documents metadata. Returns empty list if no
            relationships reference that document.
        """

    @abstractmethod
    async def delete(
        self,
        subject_id: str,
        predicate: str,
        object_id: str,
    ) -> bool:
        """Delete a specific relationship by its triple.

        Args:
            subject_id: ID of the subject entity.
            predicate: The relationship type/predicate.
            object_id: ID of the object entity.

        Returns:
            True if the relationship was found and deleted, False if
            no such relationship exists.
        """

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of relationships in storage.

        Returns:
            Integer count of all stored relationships.
        """

    @abstractmethod
    async def list_all(
        self,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[BaseRelationship]:
        """List all relationships with pagination.

        Args:
            limit: Maximum number of relationships to return (default 1000).
            offset: Number of relationships to skip for pagination (default 0).

        Returns:
            List of relationships. Order is implementation-dependent but
            should be consistent across paginated calls.
        """


class DocumentStorageInterface(ABC):
    """Abstract interface for document storage operations.

    Document storage provides persistence for source documents that have been
    ingested into the knowledge graph. Documents are retained for:

    - **Provenance**: Track where entities and relationships originated
    - **Deduplication**: Detect if a document has already been processed
    - **Re-processing**: Enable re-extraction when pipeline components improve
    - **Debugging**: Examine source content when validating extractions

    Documents may store full content or just metadata, depending on storage
    constraints and use case requirements.
    """

    @abstractmethod
    async def add(self, document: BaseDocument) -> str:
        """Store a document and return its ID.

        Args:
            document: The document to store, including content and metadata.

        Returns:
            The document_id of the stored document.

        Note:
            If a document with the same ID already exists, implementations
            may update it or raise an error.
        """

    @abstractmethod
    async def get(self, document_id: str) -> BaseDocument | None:
        """Retrieve a document by its unique identifier.

        Args:
            document_id: The unique identifier of the document.

        Returns:
            The document if found, or None if no document exists with that ID.
        """

    @abstractmethod
    async def find_by_source(self, source_uri: str) -> BaseDocument | None:
        """Find a document by its source URI.

        Used for deduplication—check if a document from a given source
        has already been ingested.

        Args:
            source_uri: The URI from which the document was obtained
                (e.g., URL, file path, DOI).

        Returns:
            The document if found, or None if no document has that source_uri.
        """

    @abstractmethod
    async def list_ids(self, limit: int = 100, offset: int = 0) -> list[str]:
        """List document IDs with pagination.

        Useful for batch operations that need to iterate over all documents
        without loading full document content.

        Args:
            limit: Maximum number of IDs to return (default 100).
            offset: Number of IDs to skip for pagination (default 0).

        Returns:
            List of document IDs. Order is implementation-dependent but
            should be consistent across paginated calls.
        """

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete a document from storage.

        Args:
            document_id: ID of the document to delete.

        Returns:
            True if the document was found and deleted, False if no
            document exists with the given ID.

        Warning:
            Deleting a document does not automatically delete entities
            or relationships extracted from it. Consider whether to
            preserve or clean up related data.
        """

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of documents in storage.

        Returns:
            Integer count of all stored documents.
        """
