"""Two-pass ingestion orchestrator for the knowledge graph framework.

This module provides the `IngestionOrchestrator` class, which coordinates the
complete document ingestion pipeline. The orchestrator manages the two-pass
process that transforms raw documents into structured knowledge:

**Pass 1 - Entity Extraction:**
    1. Parse raw document bytes into structured `BaseDocument`
    2. Extract entity mentions using the configured `EntityExtractorInterface`
    3. Resolve mentions to canonical or provisional entities
    4. Generate embeddings for new entities
    5. Store entities, updating usage counts for existing ones

**Pass 2 - Relationship Extraction:**
    1. Extract relationships between resolved entities
    2. Validate relationships against the domain schema
    3. Store relationships with source document references

The orchestrator also provides methods for:
    - Batch ingestion of multiple documents
    - Entity promotion (provisional → canonical)
    - Duplicate detection via embedding similarity
    - Entity merging
    - JSON export of entities and relationships

Example usage:
    ```python
    orchestrator = IngestionOrchestrator(
        domain=my_domain_schema,
        parser=my_parser,
        entity_extractor=my_extractor,
        entity_resolver=my_resolver,
        relationship_extractor=my_rel_extractor,
        embedding_generator=my_embedder,
        entity_storage=entity_store,
        relationship_storage=rel_store,
        document_storage=doc_store,
    )

    result = await orchestrator.ingest_document(
        raw_content=document_bytes,
        content_type="text/plain",
    )
    print(f"Extracted {result.entities_extracted} entities")
    ```
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np
from pydantic import BaseModel, ConfigDict
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

from kgraph.canonical_id import CanonicalId
from kgraph.pprint_logging import setup_logging
from kgraph.provenance import ProvenanceAccumulator
from kgraph.promotion import PromotionPolicy
from kgraph.pipeline.embedding import EmbeddingGeneratorInterface
from kgraph.pipeline.interfaces import (
    DocumentParserInterface,
    EntityExtractorInterface,
    EntityResolverInterface,
    RelationshipExtractorInterface,
)
from kgraph.pipeline.streaming import (
    DocumentChunkerInterface,
    StreamingEntityExtractorInterface,
    StreamingRelationshipExtractorInterface,
)

from kgschema.domain import DomainSchema
from kgschema.entity import BaseEntity, EntityStatus
from kgschema.relationship import BaseRelationship
from kgschema.storage import (
    DocumentStorageInterface,
    EntityStorageInterface,
    RelationshipStorageInterface,
)


def _record_relationship_evidence(
    accumulator: Optional[ProvenanceAccumulator],
    rel: BaseRelationship,
) -> None:
    """If accumulator and rel.evidence are set, record evidence rows."""
    if accumulator is None or getattr(rel, "evidence", None) is None:
        return
    evidence = rel.evidence
    rel_key = f"{rel.subject_id}:{rel.predicate}:{rel.object_id}"
    confidence = getattr(rel, "confidence", 0.0) or 0.0
    evidence_text = (evidence.notes or {}).get("evidence_text", "") or ""

    def add_from_provenance(prov) -> None:
        if prov is None:
            return
        accumulator.add_evidence(
            relationship_key=rel_key,
            document_id=prov.document_id,
            section=prov.section,
            start_offset=prov.start_offset if prov.start_offset is not None else 0,
            end_offset=prov.end_offset if prov.end_offset is not None else 0,
            text_span=evidence_text,
            confidence=confidence,
            supports=True,
        )

    add_from_provenance(evidence.primary)
    for prov in evidence.mentions or ():
        add_from_provenance(prov)


class DocumentResult(BaseModel):
    """Result of processing a single document through the ingestion pipeline.

    Contains statistics about the extraction process and any errors encountered.
    Immutable (frozen) to ensure results can be safely shared and stored.

    Attributes:
        document_id: Unique identifier assigned to the parsed document.
        entities_extracted: Total number of entity mentions found in the document.
        entities_new: Number of mentions that created new provisional entities.
        entities_existing: Number of mentions that matched existing entities.
        relationships_extracted: Number of relationships stored from this document.
        errors: Tuple of error messages encountered during processing.
    """

    model_config = {"frozen": True}

    document_id: str
    entities_extracted: int
    entities_new: int
    entities_existing: int
    relationships_extracted: int
    errors: tuple[str, ...] = ()


class IngestionResult(BaseModel):
    """Result of batch document ingestion.

    Aggregates statistics across multiple documents and provides per-document
    breakdown via the `document_results` field.

    Attributes:
        documents_processed: Total number of documents in the batch.
        documents_failed: Number of documents that had errors during processing.
        total_entities_extracted: Sum of entity mentions across all documents.
        total_relationships_extracted: Sum of relationships across all documents.
        document_results: Per-document results for detailed inspection.
        errors: Top-level errors that prevented document processing.
    """

    model_config = {"frozen": True}

    documents_processed: int
    documents_failed: int
    total_entities_extracted: int
    total_relationships_extracted: int
    document_results: tuple[DocumentResult, ...] = ()
    errors: tuple[str, ...] = ()


def _determine_canonical_id_source(canonical_id: str) -> str:
    """Determine the canonical_ids dict key from canonical_id format.

    Args:
        canonical_id: The canonical ID string (e.g., "HGNC:1100", "MeSH:D001943", "C0006142")

    Returns:
        Source key for canonical_ids dict (e.g., "hgnc", "mesh", "umls", "dbpedia")
    """
    if canonical_id.startswith("MeSH:"):
        return "mesh"
    if canonical_id.startswith("HGNC:"):
        return "hgnc"
    if canonical_id.startswith("RxNorm:"):
        return "rxnorm"
    if canonical_id.startswith("DBPedia:"):
        return "dbpedia"
    if canonical_id.startswith("UniProt:"):
        return "uniprot"
    # Try to infer from format
    if canonical_id.startswith("C") and len(canonical_id) > 1 and canonical_id[1:].isdigit():
        return "umls"
    if len(canonical_id) == 6 and canonical_id[0] in ("P", "Q") and canonical_id[1:].isalnum():
        return "uniprot"
    # Default fallback
    return "dbpedia"


class IngestionOrchestrator(BaseModel):
    """Orchestrates two-pass document ingestion for knowledge graph construction.

    The orchestrator is the main entry point for document processing. It
    coordinates all pipeline components (parser, extractors, resolver,
    embedding generator) and storage backends to transform raw documents
    into structured knowledge graph data.

    **Two-Pass Architecture:**

    - **Pass 1 (Entity Extraction)**: Extracts entity mentions from documents,
      resolves them to canonical or provisional entities, generates embeddings,
      and updates storage with new entities or incremented usage counts.

    - **Pass 2 (Relationship Extraction)**: Identifies relationships between
      the resolved entities and stores them with source document references.

    **Additional Operations:**

    - `run_promotion()`: Promotes provisional entities to canonical status
      based on usage frequency and confidence thresholds.
    - `find_merge_candidates()`: Detects potential duplicate entities using
      embedding similarity.
    - `merge_entities()`: Combines duplicate entities and updates references.
    - `export_*()`: Exports entities and relationships to JSON files.

    Attributes:
        domain: Schema defining entity types, relationship types, and validation.
        parser: Converts raw bytes to structured documents.
        entity_extractor: Extracts entity mentions from documents.
        entity_resolver: Maps mentions to canonical or provisional entities.
        relationship_extractor: Extracts relationships between entities.
        embedding_generator: Creates semantic vectors for similarity operations.
        entity_storage: Persistence backend for entities.
        relationship_storage: Persistence backend for relationships.
        document_storage: Persistence backend for source documents.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    domain: DomainSchema
    parser: DocumentParserInterface
    entity_extractor: EntityExtractorInterface
    entity_resolver: EntityResolverInterface
    relationship_extractor: RelationshipExtractorInterface
    embedding_generator: EmbeddingGeneratorInterface
    entity_storage: EntityStorageInterface
    relationship_storage: RelationshipStorageInterface
    document_storage: DocumentStorageInterface
    # Optional streaming path: when set, entity/relationship extraction use chunked streaming
    document_chunker: DocumentChunkerInterface | None = None
    streaming_entity_extractor: StreamingEntityExtractorInterface | None = None
    streaming_relationship_extractor: StreamingRelationshipExtractorInterface | None = None
    provenance_accumulator: Optional[ProvenanceAccumulator] = None

    async def extract_entities_from_document(  # pylint: disable=too-many-statements
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
    ) -> DocumentResult:
        """Runs the first pass of the ingestion pipeline on a single document.

        This pass focuses on identifying, resolving, and storing entities. The
        process includes:
        1.  Parsing the raw content into a structured document.
        2.  Extracting potential entity mentions from the document text.
        3.  Resolving each mention to either an existing or a new entity.
        4.  Generating a vector embedding for new entities.
        5.  Storing new entities or updating the usage count of existing ones.

        Args:
            raw_content: The raw byte content of the document to process.
            content_type: The MIME type of the document (e.g., "application/json").
            source_uri: An optional URI identifying the document's origin.

        Returns:
            A `DocumentResult` object containing statistics about the entity
            extraction pass, including counts of new and existing entities,
            and any errors encountered.
        """
        errors: list[str] = []
        use_streaming = self.document_chunker is not None and self.streaming_entity_extractor is not None
        document = None
        mentions: list[Any] = []

        if use_streaming:
            assert self.document_chunker is not None
            assert self.streaming_entity_extractor is not None
            # Get chunks: try chunk_from_raw for XML when chunker supports it
            content_type_base = (content_type or "").split(";")[0].strip().lower()
            is_xml = content_type_base in ("application/xml", "text/xml")
            chunk_document_id = Path(source_uri).stem if source_uri else ""

            try:
                if is_xml and chunk_document_id and hasattr(self.document_chunker, "chunk_from_raw"):
                    chunks = await self.document_chunker.chunk_from_raw(raw_content, content_type, chunk_document_id, source_uri)
                else:
                    document = await self.parser.parse(raw_content, content_type, source_uri)
                    chunks = await self.document_chunker.chunk(document)
            except NotImplementedError:
                document = await self.parser.parse(raw_content, content_type, source_uri)
                chunks = await self.document_chunker.chunk(document)
            except Exception as e:
                return DocumentResult(
                    document_id="",
                    entities_extracted=0,
                    entities_new=0,
                    entities_existing=0,
                    relationships_extracted=0,
                    errors=(f"Parse error: {e}",),
                )

            async for batch in self.streaming_entity_extractor.extract_streaming(chunks):
                mentions.extend(batch)

            if document is None:
                try:
                    document = await self.parser.parse(raw_content, content_type, source_uri)
                except Exception as e:
                    return DocumentResult(
                        document_id=chunk_document_id or "",
                        entities_extracted=len(mentions),
                        entities_new=0,
                        entities_existing=0,
                        relationships_extracted=0,
                        errors=(f"Parse error after extraction: {e}",),
                    )
            await self.document_storage.add(document)
        else:
            # Legacy path: parse, store, extract
            try:
                document = await self.parser.parse(raw_content, content_type, source_uri)
            except Exception as e:
                return DocumentResult(
                    document_id="",
                    entities_extracted=0,
                    entities_new=0,
                    entities_existing=0,
                    relationships_extracted=0,
                    errors=(f"Parse error: {e}",),
                )
            await self.document_storage.add(document)
            mentions = await self.entity_extractor.extract(document)

        entities_new = 0
        entities_existing = 0
        resolved_entities: list[BaseEntity] = []

        for mention in mentions:
            try:
                entity, _ = await self.entity_resolver.resolve(mention, self.entity_storage)

                # Validate entity against domain schema
                validation_issues = self.domain.validate_entity(entity)
                if validation_issues:
                    issue_msgs = "; ".join(f"{i.field}: {i.message}" for i in validation_issues)
                    errors.append(f"Entity validation failed: {entity.name} ({entity.get_entity_type()}) - {issue_msgs}")
                    continue

                # Check if entity already exists
                existing = await self.entity_storage.get(entity.entity_id)
                if existing:
                    # Increment usage count
                    updated = existing.model_copy(update={"usage_count": existing.usage_count + 1})
                    await self.entity_storage.update(updated)
                    if self.provenance_accumulator is not None:
                        doc_meta = document.metadata if hasattr(document, "metadata") and document.metadata else None
                        self.provenance_accumulator.add_mention(
                            entity_id=updated.entity_id,
                            document_id=document.document_id,
                            section=doc_meta.get("section") if doc_meta else None,
                            start_offset=mention.start_offset,
                            end_offset=mention.end_offset,
                            text_span=mention.text,
                            context=mention.context,
                            confidence=mention.confidence,
                            extraction_method=doc_meta.get("extraction_method", "llm") if doc_meta else "llm",
                            created_at=datetime.now(timezone.utc).isoformat(),
                        )
                    resolved_entities.append(updated)
                    entities_existing += 1
                else:
                    # Generate embedding if needed and not present
                    if entity.embedding is None:
                        try:
                            embedding = await self.embedding_generator.generate(entity.name)
                            entity = entity.model_copy(update={"embedding": embedding})
                        except Exception as e:
                            errors.append(f"Embedding generation failed: {e}")

                    # Ensure entity source is set to document_id for relationship extraction
                    if entity.source != document.document_id:
                        entity = entity.model_copy(update={"source": document.document_id})

                    await self.entity_storage.add(entity)
                    if self.provenance_accumulator is not None:
                        doc_meta = document.metadata if hasattr(document, "metadata") and document.metadata else None
                        self.provenance_accumulator.add_mention(
                            entity_id=entity.entity_id,
                            document_id=document.document_id,
                            section=doc_meta.get("section") if doc_meta else None,
                            start_offset=mention.start_offset,
                            end_offset=mention.end_offset,
                            text_span=mention.text,
                            context=mention.context,
                            confidence=mention.confidence,
                            extraction_method=doc_meta.get("extraction_method", "llm") if doc_meta else "llm",
                            created_at=datetime.now(timezone.utc).isoformat(),
                        )
                    resolved_entities.append(entity)
                    entities_new += 1

            except Exception as e:
                errors.append(f"Entity resolution error for '{mention.text}': {e}")

        return DocumentResult(
            document_id=document.document_id,
            entities_extracted=len(mentions),
            entities_new=entities_new,
            entities_existing=entities_existing,
            relationships_extracted=0,
            errors=tuple(errors),
        )

    async def extract_relationships_from_document(
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
        document_id: str | None = None,
    ) -> DocumentResult:
        """Runs the second pass of the ingestion pipeline on a single document.

        This pass focuses on identifying and storing relationships between
        entities that have already been extracted and stored. The process includes:
        1.  Retrieving the parsed document from storage or parsing it if needed.
        2.  Fetching the set of entities previously extracted from this document.
        3.  Extracting potential relationships between those entities.
        4.  Validating and storing the extracted relationships.

        Args:
            raw_content: The raw byte content of the document.
            content_type: The MIME type of the document.
            source_uri: An optional URI for finding the pre-existing document.
            document_id: The specific ID of the document to process. If provided,
                         it is used to fetch the exact document and its associated
                         entities, bypassing lookup by `source_uri`.

        Returns:
            A `DocumentResult` object containing statistics about the relationship
            extraction pass and any errors encountered.
        """
        errors: list[str] = []

        # Try to get document from storage first (to use the same document_id as entity extraction)
        # If document_id is provided, use it to find entities directly
        # If not found, parse it (for standalone relationship extraction)
        document = None
        target_document_id = document_id  # Use provided document_id if available

        if source_uri:
            document = await self.document_storage.find_by_source(source_uri)
            if document and not target_document_id:
                # Only use document's ID if we didn't get one from parameter
                target_document_id = document.document_id

        if document is None:
            # Document not in storage, parse it
            try:
                document = await self.parser.parse(raw_content, content_type, source_uri)
                # Only use parsed document's ID if we don't have a target_document_id
                if not target_document_id:
                    target_document_id = document.document_id
            except Exception as e:
                return DocumentResult(
                    document_id="",
                    entities_extracted=0,
                    entities_new=0,
                    entities_existing=0,
                    relationships_extracted=0,
                    errors=(f"Parse error: {e}",),
                )

        # Get entities that were extracted from this document
        # Strategy: Get all entities and filter by source document ID
        # Use target_document_id (from parameter or document) to find entities
        all_entities = await self.entity_storage.list_all(limit=100000)  # Get all entities
        document_entities = [e for e in all_entities if e.source == target_document_id]

        # If no entities found by source, try to get entity IDs from document metadata
        # (for pre-extracted relationships that reference specific entity IDs)
        if not document_entities:
            entity_ids = document.metadata.get("entity_ids", [])
            if entity_ids:
                for entity_id in entity_ids:
                    entity = await self.entity_storage.get(entity_id)
                    if entity:
                        document_entities.append(entity)

        relationships: list[BaseRelationship] = []

        if document_entities:
            use_streaming_rels = self.streaming_relationship_extractor is not None and self.document_chunker is not None
            try:
                if use_streaming_rels:
                    assert self.document_chunker is not None
                    assert self.streaming_relationship_extractor is not None
                    chunks = await self.document_chunker.chunk(document)
                    async for rel_batch in self.streaming_relationship_extractor.extract_windowed(chunks, document_entities):
                        for rel in rel_batch:
                            if await self.domain.validate_relationship(rel, entity_storage=self.entity_storage):
                                await self.relationship_storage.add(rel)
                                _record_relationship_evidence(self.provenance_accumulator, rel)
                                relationships.append(rel)
                            else:
                                errors.append(f"Relationship validation failed: {rel.subject_id} " f"-{rel.predicate}-> {rel.object_id}")
                else:
                    extracted_rels = await self.relationship_extractor.extract(document, document_entities)
                    for rel in extracted_rels:
                        if await self.domain.validate_relationship(rel, entity_storage=self.entity_storage):
                            await self.relationship_storage.add(rel)
                            _record_relationship_evidence(self.provenance_accumulator, rel)
                            relationships.append(rel)
                        else:
                            errors.append(f"Relationship validation failed: {rel.subject_id} " f"-{rel.predicate}-> {rel.object_id}")
            except Exception as e:
                errors.append(f"Relationship extraction error: {e}")
        # If no entities found, that's fine - just return 0 relationships (no error)

        return DocumentResult(
            document_id=document.document_id,
            entities_extracted=0,
            entities_new=0,
            entities_existing=0,
            relationships_extracted=len(relationships),
            errors=tuple(errors),
        )

    async def ingest_document(
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
    ) -> DocumentResult:
        """Ingests a single document through the complete two-pass pipeline.

        This convenience method orchestrates both the entity extraction pass and
        the relationship extraction pass in sequence for a single document.
        For more granular control over the ingestion process, such as running
        promotion between passes, call `extract_entities_from_document` and
        `extract_relationships_from_document` separately.

        Args:
            raw_content: The raw byte content of the document to process.
            content_type: The MIME type of the document (e.g., "application/json").
            source_uri: An optional URI identifying the document's origin.

        Returns:
            A `DocumentResult` object containing the combined statistics from
            both the entity and relationship extraction passes.
        """
        # Pass 1: Extract entities
        entity_result = await self.extract_entities_from_document(
            raw_content=raw_content,
            content_type=content_type,
            source_uri=source_uri,
        )

        # Pass 2: Extract relationships
        # Pass the document_id from entity extraction to ensure we find the same entities
        relationship_result = await self.extract_relationships_from_document(
            raw_content=raw_content,
            content_type=content_type,
            source_uri=source_uri,
            document_id=entity_result.document_id,
        )

        # Combine results
        return DocumentResult(
            document_id=entity_result.document_id or relationship_result.document_id,
            entities_extracted=entity_result.entities_extracted,
            entities_new=entity_result.entities_new,
            entities_existing=entity_result.entities_existing,
            relationships_extracted=relationship_result.relationships_extracted,
            errors=entity_result.errors + relationship_result.errors,
        )

    async def ingest_batch(
        self,
        documents: Sequence[tuple[bytes, str, str | None]],
    ) -> IngestionResult:
        """Ingests a batch of documents using the two-pass pipeline.

        This method iterates through a sequence of documents and calls
        `ingest_document` for each one, collecting the results.

        Args:
            documents: A sequence of tuples, where each tuple contains the
                       raw content, content type, and optional source URI
                       for a single document.

        Returns:
            An `IngestionResult` object containing aggregated statistics for the
            entire batch, as well as a list of individual `DocumentResult`
            objects.
        """
        results: list[DocumentResult] = []
        errors: list[str] = []
        documents_failed = 0

        for raw_content, content_type, source_uri in documents:
            try:
                result = await self.ingest_document(raw_content, content_type, source_uri)
                results.append(result)
                if result.errors:
                    documents_failed += 1
            except Exception as e:
                errors.append(f"Document ingestion failed: {e}")
                documents_failed += 1

        total_entities = sum(r.entities_extracted for r in results)
        total_relationships = sum(r.relationships_extracted for r in results)

        return IngestionResult(
            documents_processed=len(documents),
            documents_failed=documents_failed,
            total_entities_extracted=total_entities,
            total_relationships_extracted=total_relationships,
            document_results=tuple(results),
            errors=tuple(errors),
        )

    async def _lookup_canonical_ids_batch(
        self,
        policy: PromotionPolicy,
        candidates: list[BaseEntity],
        logger: Any,
    ) -> dict[str, CanonicalId | None]:
        """Look up canonical IDs for all candidate entities in batches.

        Args:
            policy: The promotion policy to use for lookups
            candidates: List of candidate entities
            logger: Logger instance

        Returns:
            Dictionary mapping entity_id to CanonicalId or None
        """
        import asyncio

        BATCH_SIZE = 15
        entity_canonical_id_map: dict[str, CanonicalId | None] = {}

        for i in range(0, len(candidates), BATCH_SIZE):
            batch = candidates[i : i + BATCH_SIZE]
            logger.debug(
                {
                    "message": f"Processing promotion batch {i // BATCH_SIZE + 1} ({len(batch)} entities)",
                    "batch_start": i,
                    "batch_end": min(i + BATCH_SIZE, len(candidates)),
                },
                pprint=True,
            )

            # Parallel lookup of canonical IDs
            tasks = [policy.assign_canonical_id(entity) for entity in batch]
            canonical_ids = await asyncio.gather(*tasks)

            # Map results
            for entity, canonical_id in zip(batch, canonical_ids):
                entity_canonical_id_map[entity.entity_id] = canonical_id

        return entity_canonical_id_map

    async def _promote_single_entity(
        self,
        entity: BaseEntity,
        entity_canonical_id_map: dict[str, CanonicalId | None],
        policy: PromotionPolicy,
        logger: Any,
    ) -> BaseEntity | None | bool:
        """Promote a single entity to canonical status.

        Args:
            entity: The entity to promote
            entity_canonical_id_map: Map of entity_id to CanonicalId
            policy: The promotion policy
            logger: Logger instance

        Returns:
            BaseEntity if successfully promoted, None if no canonical ID found,
            False if storage promotion failed
        """
        canonical_id_obj = entity_canonical_id_map.get(entity.entity_id)

        # Force-promote: If canonical ID found, promote regardless of thresholds
        if canonical_id_obj is None:
            logger.debug(
                {
                    "message": f"Entity {entity.name} ({entity.entity_id}) cannot be assigned a canonical ID",
                    "entity": entity,
                },
                pprint=True,
            )
            return None

        # Extract canonical ID string for storage operations
        canonical_id = canonical_id_obj.id

        # Canonical ID found - check if this is a force-promote (thresholds not met)
        force_promote = not policy.should_promote(entity)
        if force_promote:
            logger.info(
                {
                    "message": f"Force-promoting {entity.name} - canonical ID found ({canonical_id}) despite not meeting thresholds",
                    "entity": entity,
                    "canonical_id": canonical_id,
                    "reason": "canonical_id_found",
                },
                pprint=True,
            )

        # Update entity in storage with new ID and status
        new_canonical_ids = entity.canonical_ids.copy()
        # Determine source key from canonical_id format
        source_key = _determine_canonical_id_source(canonical_id)
        new_canonical_ids[source_key] = canonical_id

        promoted_entity = await self.entity_storage.promote(entity.entity_id, canonical_id, canonical_ids=new_canonical_ids)

        if promoted_entity:
            # Update metadata with URLs from CanonicalId object
            if canonical_id_obj.url:
                updated_metadata = promoted_entity.metadata.copy()
                # Store primary URL from CanonicalId object
                updated_metadata["canonical_url"] = canonical_id_obj.url
                # Build canonical_urls dict from new_canonical_ids (for backward compatibility)
                try:
                    from examples.medlit.pipeline.canonical_urls import build_canonical_urls_from_dict

                    entity_type = promoted_entity.get_entity_type()
                    canonical_urls = build_canonical_urls_from_dict(new_canonical_ids, entity_type=entity_type)
                    if canonical_urls:
                        updated_metadata["canonical_urls"] = canonical_urls
                except ImportError:
                    # If canonical_urls module not available, just use the primary URL
                    pass

                # Update entity with new metadata
                promoted_entity = promoted_entity.model_copy(update={"metadata": updated_metadata})
                await self.entity_storage.update(promoted_entity)

            # Update all relationships pointing to old ID
            await self.relationship_storage.update_entity_references(entity.entity_id, canonical_id)
            return promoted_entity
        else:
            logger.warning(
                {
                    "message": f"Storage promotion failed for {entity.name} ({entity.entity_id})",
                    "entity": entity,
                },
                pprint=True,
            )
            return False

    async def run_promotion(self, lookup=None) -> list[BaseEntity]:
        """Promotes eligible provisional entities to canonical status.

        This method orchestrates the promotion process, which is a critical
        step between the entity and relationship extraction passes. It uses the
        domain's configured `PromotionPolicy` to evaluate provisional entities
        and upgrade them to canonical status if they meet the criteria.

        The process involves:
        1.  Identifying provisional entities that meet usage and confidence thresholds.
        2.  Using the promotion policy (and optional lookup service) to assign
            a canonical ID to each candidate.
        3.  Updating the entity's status and ID in storage.
        4.  Updating all relationship references from the old provisional ID to
            the new canonical ID.

        Args:
            lookup: An optional canonical ID lookup service (e.g., an API client)
                    to be used by the promotion policy.

        Returns:
            A list of the `BaseEntity` objects that were successfully promoted
            to canonical status during this run.
        """

        logger = setup_logging()
        logger.info("Starting entity promotion process")

        policy = self.domain.get_promotion_policy(lookup=lookup)
        config = self.domain.promotion_config

        logger.info(
            {"message": "Promotion configuration", "config": config},
            pprint=True,
        )

        # Get candidates meeting basic thresholds
        candidates = await self.entity_storage.find_provisional_for_promotion(
            min_usage=config.min_usage_count,
            min_confidence=config.min_confidence,
        )

        logger.info(f"Found {len(candidates)} provisional entities meeting basic thresholds " f"(usage>={config.min_usage_count}, confidence>={config.min_confidence})")

        if candidates:
            logger.debug(
                {
                    "message": "Candidate entities for promotion",
                    "count": len(candidates),
                    "candidates": candidates[:10],  # Log first 10
                },
                pprint=True,
            )

        promoted: list[BaseEntity] = []
        skipped_no_policy: list[BaseEntity] = []
        skipped_no_canonical_id: list[BaseEntity] = []
        skipped_storage_failure: list[BaseEntity] = []

        if not candidates:
            logger.info("No candidate entities for promotion")
        else:
            logger.info(f"Looking up canonical IDs for {len(candidates)} candidate entities...")

        # Step 1: Parallelize canonical ID lookups for all candidates
        entity_canonical_id_map = await self._lookup_canonical_ids_batch(policy, candidates, logger)

        # Step 2: Process results and promote entities
        for entity in candidates:
            logger.debug(
                {
                    "message": f"Evaluating entity for promotion: {entity.name} ({entity.entity_id})",
                    "entity": entity,
                },
                pprint=True,
            )

            result = await self._promote_single_entity(entity, entity_canonical_id_map, policy, logger)
            if result is None:
                skipped_no_canonical_id.append(entity)
            elif result is False:
                skipped_storage_failure.append(entity)
            else:
                # Type narrowing: result must be BaseEntity here
                assert isinstance(result, BaseEntity), "Expected BaseEntity when result is not None/False"
                promoted.append(result)

        logger.info(
            f"Promotion complete: {len(promoted)} promoted, "
            f"{len(skipped_no_policy)} skipped (policy), "
            f"{len(skipped_no_canonical_id)} skipped (no canonical ID), "
            f"{len(skipped_storage_failure)} skipped (storage failure)"
        )

        if skipped_no_canonical_id:
            logger.debug(
                {
                    "message": f"Entities skipped due to missing canonical ID ({len(skipped_no_canonical_id)}):",
                    "skipped": skipped_no_canonical_id[:10],  # Log first 10
                },
                pprint=True,
            )

        return promoted

    async def find_merge_candidates(
        self,
        similarity_threshold: float = 0.95,
    ) -> list[tuple[BaseEntity, BaseEntity, float]]:
        """Finds potential duplicate entities based on embedding similarity.

        This method scans all canonical entities that have an embedding, computes
        the pairwise cosine similarity between them, and identifies pairs that
        exceed a given threshold. This is useful for data cleaning and
        maintaining graph quality.

        Note:
            This performs an O(n²) comparison and can be computationally
            expensive for a large number of entities. For larger-scale
            applications, consider approximate nearest neighbor (ANN) search
            methods.

        Args:
            similarity_threshold: The minimum cosine similarity score (between 0.0
                and 1.0) required to consider two entities a potential match.

        Returns:
            A list of tuples, where each tuple contains two entity objects and
            their similarity score. `[(entity1, entity2, score), ...]`.

        Example:
            ```python
            candidates = await orchestrator.find_merge_candidates(threshold=0.98)
            for e1, e2, sim in candidates:
                print(f"{e1.name} ↔ {e2.name}: {sim:.3f}")
            ```
        """
        candidates: list[tuple[BaseEntity, BaseEntity, float]] = []

        # 1. Get all canonical entities with embeddings
        all_canonical_entities = await self.entity_storage.list_all(status=EntityStatus.CANONICAL.value)
        entities_with_embeddings = [e for e in all_canonical_entities if e.embedding is not None]

        if len(entities_with_embeddings) < 2:
            return candidates

        # 2. Extract embeddings into a matrix
        embedding_matrix = np.array([e.embedding for e in entities_with_embeddings])

        # 3. Calculate cosine similarity for all pairs
        # This gives a matrix where similarity_matrix[i, j] is the similarity
        # between entity i and entity j.
        similarity_matrix = cosine_similarity(embedding_matrix)

        # 4. Find pairs above the threshold
        # We only need to check the upper triangle of the matrix (where i < j)
        # to avoid duplicate pairs (a,b) and (b,a) and self-comparisons (a,a).
        num_entities = len(entities_with_embeddings)
        for i in range(num_entities):
            for j in range(i + 1, num_entities):
                similarity = similarity_matrix[i, j]
                if similarity >= similarity_threshold:
                    entity1 = entities_with_embeddings[i]
                    entity2 = entities_with_embeddings[j]
                    candidates.append((entity1, entity2, similarity))

        return candidates

    async def merge_entities(
        self,
        source_ids: Sequence[str],
        target_id: str,
    ) -> bool:
        """Merges one or more source entities into a single target entity.

        This operation is crucial for deduplication and graph cleaning. It
        combines data from the source entities into the target, updates all
        relationship references to point to the target, and then deletes the
        source entities.

        The merge logic includes:
        1.  Re-mapping all relationships from source entities to the target entity.
        2.  Combining synonyms and summing usage counts.
        3.  Delegating the core entity data merge and deletion to the storage backend.

        Args:
            source_ids: A sequence of entity IDs to merge and then delete.
            target_id: The ID of the entity that will absorb the source entities.

        Returns:
            `True` if the merge was successful, `False` otherwise (e.g., if
            the target entity does not exist).

        Example:
            ```python
            # After finding merge candidates
            candidates = await orchestrator.find_merge_candidates()
            for e1, e2, sim in candidates:
                # Keep the entity with more usage, merge the other into it
                if e1.usage_count >= e2.usage_count:
                    await orchestrator.merge_entities([e2.entity_id], e1.entity_id)
                else:
                    await orchestrator.merge_entities([e1.entity_id], e2.entity_id)
            ```
        """
        # Update relationship references
        for source_id in source_ids:
            if source_id != target_id:
                await self.relationship_storage.update_entity_references(source_id, target_id)

        # Merge entity data
        return await self.entity_storage.merge(source_ids, target_id)

    def _serialize_entity(self, entity: BaseEntity) -> dict[str, Any]:
        """Serialize an entity to a JSON-compatible dictionary."""
        return {
            "entity_id": entity.entity_id,
            "status": entity.status.value,
            "name": entity.name,
            "synonyms": list(entity.synonyms),
            "entity_type": entity.get_entity_type(),
            "canonical_ids": entity.canonical_ids,
            "embedding": list(entity.embedding) if entity.embedding else None,
            "confidence": entity.confidence,
            "usage_count": entity.usage_count,
            "created_at": entity.created_at.isoformat(),
            "source": entity.source,
            "metadata": entity.metadata,
        }

    def _serialize_relationship(self, rel: BaseRelationship) -> dict[str, Any]:
        """Serialize a relationship to a JSON-compatible dictionary."""
        return {
            "subject_id": rel.subject_id,
            "predicate": rel.predicate,
            "object_id": rel.object_id,
            "edge_type": rel.get_edge_type(),
            "confidence": rel.confidence,
            "source_documents": list(rel.source_documents),
            "created_at": rel.created_at.isoformat(),
            "last_updated": rel.last_updated.isoformat() if rel.last_updated else None,
            "metadata": rel.metadata,
        }

    async def export_entities(
        self,
        output_path: str | Path,
        include_provisional: bool = False,
    ) -> int:
        """Exports entities from storage to a JSON file.

        Serializes entities into a JSON format, by default including only
        canonical entities.

        Args:
            output_path: The path where the JSON file will be saved.
            include_provisional: If `True`, includes both canonical and
                                 provisional entities in the export. Defaults
                                 to `False`.

        Returns:
            The total number of entities exported.
        """
        output_path = Path(output_path)

        if include_provisional:
            entities = await self.entity_storage.list_all()
        else:
            entities = await self.entity_storage.list_all(status=EntityStatus.CANONICAL.value)

        export_data = {
            "domain": self.domain.name,
            "exported_at": datetime.now().isoformat(),
            "entity_count": len(entities),
            "entities": [self._serialize_entity(e) for e in entities],
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        return len(entities)

    async def export_document(
        self,
        document_id: str,
        output_path: str | Path,
    ) -> dict[str, int]:
        """Exports data related to a single document to a JSON file.

        This function gathers all relationships and provisional entities that
        originated from a specific document and writes them to a file.

        Args:
            document_id: The ID of the document to export data for.
            output_path: The path where the JSON file will be saved.

        Returns:
            A dictionary containing the counts of exported relationships and
            provisional entities.
        """
        output_path = Path(output_path)

        # Get document metadata
        document = await self.document_storage.get(document_id)

        # Get relationships from this document
        relationships = await self.relationship_storage.get_by_document(document_id)

        # Get provisional entities from this document
        # Filter by source field matching document_id
        all_provisional = await self.entity_storage.list_all(status=EntityStatus.PROVISIONAL.value)
        provisional_entities = [e for e in all_provisional if e.source == document_id]

        export_data = {
            "document_id": document_id,
            "document_title": document.title if document else None,
            "exported_at": datetime.now().isoformat(),
            "relationship_count": len(relationships),
            "provisional_entity_count": len(provisional_entities),
            "relationships": [self._serialize_relationship(r) for r in relationships],
            "provisional_entities": [self._serialize_entity(e) for e in provisional_entities],
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        return {
            "relationships": len(relationships),
            "provisional_entities": len(provisional_entities),
        }

    async def export_all(
        self,
        output_dir: str | Path,
    ) -> dict[str, Any]:
        """Exports the entire graph into a directory of JSON files.

        This method orchestrates a full export, creating a file for all
        canonical entities and separate files for each document's specific
        data (relationships and provisional entities).

        The output directory will contain:
        - `entities.json`: All canonical entities.
        - `paper_{document_id}.json`: One file for each processed document.

        Args:
            output_dir: The path to the directory where files will be saved.

        Returns:
            A summary dictionary containing statistics about the export,
            including the number of entities and documents exported.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export canonical entities
        entities_count = await self.export_entities(
            output_dir / "entities.json",
            include_provisional=False,
        )

        # Export each document
        document_ids = await self.document_storage.list_ids(limit=10000)
        document_stats = {}
        for doc_id in document_ids:
            stats = await self.export_document(
                doc_id,
                output_dir / f"paper_{doc_id}.json",
            )
            document_stats[doc_id] = stats

        return {
            "output_dir": str(output_dir),
            "canonical_entities": entities_count,
            "documents_exported": len(document_ids),
            "document_stats": document_stats,
        }
