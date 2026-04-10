"""Entity resolution for medical literature domain.

Resolves entity mentions to canonical entities using UMLS, HGNC, RxNorm, UniProt IDs.
"""

from datetime import datetime, timezone
import uuid
from typing import Sequence

from pydantic import BaseModel, ConfigDict

from kgraph.pprint_logging import setup_logging
from kgraph.pipeline.embedding import EmbeddingGeneratorInterface
from kgraph.pipeline.interfaces import EntityResolverInterface

from kgschema.domain import DomainSchema
from kgschema.entity import BaseEntity, EntityMention, EntityStatus
from kgschema.storage import EntityStorageInterface

from .canonical_urls import build_canonical_url, build_canonical_urls_from_dict


class MedLitEntityResolver(BaseModel, EntityResolverInterface):
    """Resolve medical entity mentions to canonical or provisional entities.

    Resolution strategy (hybrid approach):
    1. If mention has canonical_id_hint (from pre-extracted entities), use that
    2. Check if entity with that ID already exists in storage
    3. If not, create new canonical entity (since we have authoritative IDs)
    4. For mentions without canonical IDs:
       a. Try embedding-based semantic matching against existing entities (if embedding_generator provided)
       b. If no match found, create provisional entities

    The embedding-based matching acts as a semantic cache, catching variations like:
    - "BRCA-1" vs "BRCA1"
    - "breast cancer 1 gene" vs "BRCA1"
    - "TP53" vs "p53"
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    domain: DomainSchema
    embedding_generator: EmbeddingGeneratorInterface | None = None
    similarity_threshold: float = 0.85

    async def resolve(
        self,
        mention: EntityMention,
        existing_storage: EntityStorageInterface,
    ) -> tuple[BaseEntity, float]:
        """Resolves a single entity mention to a canonical or provisional entity.

        This method implements the core resolution logic, applying a hybrid
        strategy. It prioritizes explicit canonical IDs, falls back to
        embedding-based similarity matching, and finally creates a new
        provisional entity if no match is found.

        Args:
            mention: The `EntityMention` to resolve.
            existing_storage: The entity storage backend to query for existing
                              entities.

        Returns:
            A tuple containing the resolved `BaseEntity` (which may be new or
            existing, canonical or provisional) and a confidence score for the
            resolution.

        Raises:
            ValueError: If the mention's entity type is not defined in the
                        domain schema.
        """
        logger = setup_logging()

        entity_type = mention.entity_type
        entity_cls = self.domain.entity_types.get(entity_type)

        if entity_cls is None:
            raise ValueError(f"Unknown entity_type {entity_type!r}")

        # Check for canonical ID hint (from pre-extracted entities)
        canonical_id = mention.metadata.get("canonical_id_hint") if mention.metadata else None

        logger.debug(
            f"Resolving mention: '{mention.text}' (type: {entity_type}, confidence: {mention.confidence:.3f})",
            extra={"mention": mention},
            pprint=True,
        )

        if canonical_id:
            logger.debug(
                {
                    "message": f"Mention '{mention.text}' has canonical_id_hint: {canonical_id}",
                    "canonical_id": canonical_id,
                },
                pprint=True,
            )

            # Try to find existing entity with this ID
            existing = await existing_storage.get(canonical_id)
            if existing:
                # Entity already exists - return it with high confidence
                logger.debug(
                    {
                        "message": f"Found existing canonical entity for '{mention.text}': {canonical_id}",
                        "existing_entity": existing,
                    },
                    pprint=True,
                )
                return existing, mention.confidence

            # Create new canonical entity with the authoritative ID
            # Extract canonical_ids dict from the ID format
            canonical_ids = self._parse_canonical_id(canonical_id, entity_type)

            # Build canonical URLs from canonical IDs
            canonical_urls = build_canonical_urls_from_dict(canonical_ids, entity_type=entity_type)
            metadata: dict[str, str | dict[str, str]] = {}
            if canonical_urls:
                # Store URLs in metadata - prefer primary canonical ID URL if available
                metadata["canonical_urls"] = canonical_urls
                # Also store primary URL for convenience (from the main canonical_id)
                primary_url = build_canonical_url(canonical_id, entity_type=entity_type)
                if primary_url:
                    metadata["canonical_url"] = primary_url

            # logger.info(
            #     {
            #         "text": mention.text,
            #         "canonical_id": canonical_id,
            #     },
            #     pprint=True,
            # )
            entity = entity_cls(
                entity_id=canonical_id,
                status=EntityStatus.CANONICAL,
                name=mention.text,
                synonyms=tuple(),
                embedding=None,  # Will be generated later
                canonical_ids=canonical_ids,
                confidence=mention.confidence,
                usage_count=1,
                created_at=datetime.now(timezone.utc),
                source=mention.metadata.get("document_id", "medlit:extracted") if mention.metadata else "medlit:extracted",
                metadata=metadata,
            )
            return entity, mention.confidence

        # No canonical ID - try embedding-based semantic matching first
        if self.embedding_generator:
            try:
                # Generate embedding for the mention text
                mention_embedding = await self.embedding_generator.generate(mention.text)

                # Search for similar entities in storage
                similar_entities = await existing_storage.find_by_embedding(
                    embedding=list(mention_embedding),
                    threshold=self.similarity_threshold,
                    limit=1,  # Just get the best match
                )

                if similar_entities:
                    # Found a match via embedding similarity
                    matched_entity, similarity_score = similar_entities[0]
                    logger.debug(
                        {
                            "message": f"Found similar entity via embedding for '{mention.text}': {matched_entity.name} (similarity: {similarity_score:.3f})",
                            "matched_entity_id": matched_entity.entity_id,
                            "similarity": similarity_score,
                        },
                        pprint=True,
                    )
                    # Return the matched entity with combined confidence
                    combined_confidence = float(similarity_score) * mention.confidence
                    return matched_entity, combined_confidence
            except Exception as e:
                # If embedding matching fails, log and continue to provisional creation
                logger.debug(
                    f"Embedding-based matching failed for '{mention.text}': {e}. Falling back to provisional entity creation.",
                    pprint=True,
                )

        # No canonical ID and no embedding match - create provisional entity
        provisional_id = f"prov:{uuid.uuid4().hex}"
        # logger.info(
        #     {
        #         "text": mention.text,
        #         "provisional_id": provisional_id,
        #     },
        #     pprint=True,
        # )
        entity = entity_cls(
            entity_id=provisional_id,
            status=EntityStatus.PROVISIONAL,
            name=mention.text,
            synonyms=tuple(),
            embedding=None,
            canonical_ids={},
            confidence=mention.confidence * 0.5,  # Lower confidence for provisional
            usage_count=1,
            created_at=datetime.now(timezone.utc),
            source=mention.metadata.get("document_id", "unknown") if mention.metadata else "unknown",
            metadata={},
        )

        return entity, entity.confidence

    async def resolve_batch(
        self,
        mentions: Sequence[EntityMention],
        existing_storage: EntityStorageInterface,
    ) -> list[tuple[BaseEntity, float]]:
        """Resolves a sequence of entity mentions.

        This method currently resolves mentions sequentially by calling `resolve`
        for each one. It is designed to be a placeholder for a future, more
        optimized implementation that could batch database lookups or API calls.

        Args:
            mentions: A sequence of `EntityMention` objects to resolve.
            existing_storage: The entity storage backend, passed to `resolve`.

        Returns:
            A list of (entity, confidence) tuples, with each tuple
            corresponding to an input mention in the same order.
        """
        # Simple sequential resolution for now
        # TODO: Could batch lookups for better performance
        return [await self.resolve(m, existing_storage) for m in mentions]

    def _parse_canonical_id(self, entity_id: str, entity_type: str) -> dict[str, str]:
        """Parses a canonical ID string into a structured dictionary.

        This utility function takes a raw ID string (e.g., "HGNC:1100") and
        converts it into a `canonical_ids` dictionary (e.g.,
        `{"hgnc": "HGNC:1100"}`). It handles both prefixed IDs and attempts to
        infer the authority for non-prefixed IDs based on the entity type.

        Args:
            entity_id: The canonical ID string to parse.
            entity_type: The entity's type, used to infer the authority for
                         non-prefixed IDs.

        Returns:
            A dictionary mapping the authority name (e.g., "hgnc") to the
            full canonical ID.
        """
        canonical_ids: dict[str, str] = {}

        # Check for full ROR URL (https://ror.org/...) — must be handled before
        # the generic ":" split, which would yield prefix="https" otherwise.
        if entity_id.startswith("https://ror.org/"):
            canonical_ids["ror"] = entity_id
        # Check for prefix format (HGNC:1100, RxNorm:1187832, ROR:04aj4c181, ORCID:...)
        elif ":" in entity_id:
            prefix, _ = entity_id.split(":", 1)
            prefix_lower = prefix.lower()
            canonical_ids[prefix_lower] = entity_id
        else:
            # No prefix - infer from entity type
            if entity_type == "disease":
                # Assume UMLS format (C followed by digits)
                if entity_id.startswith("C") and entity_id[1:].isdigit():
                    canonical_ids["umls"] = entity_id
            elif entity_type == "gene":
                # Assume HGNC format (but should have prefix)
                canonical_ids["hgnc"] = entity_id
            elif entity_type == "drug":
                # Assume RxNorm format (but should have prefix)
                canonical_ids["rxnorm"] = entity_id
            elif entity_type == "protein":
                # Check for UniProt prefix format (UniProt:P38398)
                if entity_id.startswith("UniProt:"):
                    canonical_ids["uniprot"] = entity_id
                # Assume UniProt format (P/Q followed by alphanumeric) - add prefix
                elif entity_id.startswith("P") or entity_id.startswith("Q"):
                    canonical_ids["uniprot"] = f"UniProt:{entity_id}"

        return canonical_ids
