"""Promotion policy for medical literature domain.

Promotes provisional entities to canonical status when they have authoritative
identifiers (UMLS, HGNC, RxNorm, UniProt) or meet usage/confidence thresholds.
"""

from typing import Optional

from kgraph.canonical_id import (
    CanonicalId,
    CanonicalIdLookupInterface,
    check_entity_id_format,
    extract_canonical_id_from_entity,
)
from kgraph.pprint_logging import setup_logging
from kgraph.promotion import PromotionPolicy

from kgschema.entity import BaseEntity, EntityStatus

from .pipeline.authority_lookup import CanonicalIdLookup


class MedLitPromotionPolicy(PromotionPolicy):
    """Promotion policy for medical literature domain.

    Assigns canonical IDs based on authoritative medical ontologies:
    - Diseases: UMLS IDs (e.g., "C0006142")
    - Genes: HGNC IDs (e.g., "HGNC:1100")
    - Drugs: RxNorm IDs (e.g., "RxNorm:1187832")
    - Proteins: UniProt IDs (e.g., "UniProt:P38398")

    Promotion strategy:
    1. If entity already has canonical_id in canonical_ids dict, use that
    2. If entity_id is already a canonical ID format, use it directly
    3. Otherwise, look up canonical ID from authority APIs (UMLS, HGNC, RxNorm, UniProt)

    Some entity types do not have their own authority but map naturally to one
    that does.  ``_AUTHORITY_TYPE_OVERRIDES`` redirects those types so the
    lookup uses the right ontology.
    """

    # Entity types that should be looked up under a different authority type.
    # E.g. hormones are drugs for the purposes of RxNorm lookup; enzymes are
    # proteins for the purposes of UniProt lookup.
    _AUTHORITY_TYPE_OVERRIDES: dict[str, str] = {
        "hormone": "drug",
        "enzyme": "protein",
        "biomarker": "disease",
    }

    def __init__(self, config, lookup: Optional[CanonicalIdLookupInterface] = None):
        """Initialize promotion policy.

        Args:
            config: Promotion configuration with thresholds.
            lookup: Optional canonical ID lookup service. If None, will create
                    a new CanonicalIdLookup instance (without UMLS API key unless set in env).
        """
        super().__init__(config)
        self.lookup: CanonicalIdLookupInterface = lookup or CanonicalIdLookup()

    def should_promote(self, entity: BaseEntity) -> bool:
        """Check if entity meets promotion thresholds.

        Force-promote rules (bypass standard thresholds):
        - If confidence >= 0.7, ignore usage count requirement
        - If canonical ID is found (checked in run_promotion), promote regardless

        Standard thresholds:
        - usage_count >= min_usage_count (default: 1)
        - confidence >= min_confidence (default: 0.4)
        - embedding required only if require_embedding=True (default: False)
        """
        logger = setup_logging()

        if entity.status != EntityStatus.PROVISIONAL:
            logger.debug(
                {
                    "message": f"Entity {entity.name} ({entity.entity_id}) is not provisional (status: {entity.status})",
                    "entity": entity,
                },
                pprint=True,
            )
            return False

        # Force-promote: High confidence bypasses usage requirement
        if entity.confidence >= 0.7:
            logger.debug(
                {
                    "message": f"Force-promoting {entity.name} - high confidence ({entity.confidence} >= 0.7)",
                    "entity": entity,
                    "reason": "high_confidence",
                },
                pprint=True,
            )
            return True

        # Standard threshold checks
        confidence_ok = entity.confidence >= self.config.min_confidence
        usage_ok = entity.usage_count >= self.config.min_usage_count
        embedding_ok = not self.config.require_embedding or entity.embedding is not None

        result = confidence_ok and usage_ok and embedding_ok

        logger.debug(
            {
                "message": f"Promotion check for {entity.name} ({entity.entity_id})",
                "entity": entity,
                "config": self.config,
                "confidence_check": {
                    "value": entity.confidence,
                    "threshold": self.config.min_confidence,
                    "passed": confidence_ok,
                },
                "usage_check": {
                    "value": entity.usage_count,
                    "threshold": self.config.min_usage_count,
                    "passed": usage_ok,
                },
                "embedding_check": {
                    "present": entity.embedding is not None,
                    "required": self.config.require_embedding,
                    "passed": embedding_ok,
                },
                "result": result,
            },
            pprint=True,
        )

        return result

    async def assign_canonical_id(self, entity: BaseEntity) -> Optional[CanonicalId]:
        """Assign canonical ID for a provisional entity.

        Args:
            entity: The provisional entity to promote.

        Returns:
            CanonicalId if available, None otherwise.
        """
        logger = setup_logging()

        logger.debug(
            {
                "message": f"Attempting to assign canonical ID for {entity.name}",
                "entity": entity,
                "entity_id": entity.entity_id,
                "entity_type": entity.get_entity_type(),
            },
            pprint=True,
        )

        # Strategy 1: Check if entity already has canonical_ids with authoritative ID
        # Priority order: umls > hgnc > rxnorm > uniprot
        canonical_id = extract_canonical_id_from_entity(
            entity,
            priority_sources=["umls", "hgnc", "rxnorm", "uniprot"],
        )
        if canonical_id:
            logger.debug(
                {
                    "message": f"Found canonical ID from entity.canonical_ids for {entity.name}: {canonical_id.id}",
                    "entity": entity,
                    "canonical_id": canonical_id.id,
                },
                pprint=True,
            )
            return canonical_id

        # Strategy 2: Check if entity_id is already in canonical format
        entity_type = entity.get_entity_type()
        format_patterns = {
            "disease": ("C",),  # UMLS
            "symptom": ("C",),  # UMLS
            "procedure": ("C",),  # UMLS
            "gene": ("HGNC:", "numeric"),
            "drug": ("RxNorm:", "numeric"),
            "protein": ("UniProt:", "uniprot"),
        }
        canonical_id = check_entity_id_format(entity, format_patterns)
        if canonical_id:
            logger.debug(
                {
                    "message": f"Found canonical ID from entity_id format for {entity.name}: {canonical_id.id}",
                    "entity": entity,
                    "canonical_id": canonical_id.id,
                },
                pprint=True,
            )
            return canonical_id

        # Strategy 3: Look up from authority APIs.
        # Some entity types don't have their own authority; remap them first.
        lookup_type = self._AUTHORITY_TYPE_OVERRIDES.get(entity_type, entity_type)
        lookup_result = await self.lookup.lookup(term=entity.name, entity_type=lookup_type)

        if lookup_result:
            logger.debug(
                {
                    "message": f"Found canonical ID via external lookup for {entity.name}: {lookup_result.id}",
                    "entity": entity,
                    "canonical_id": lookup_result.id,
                    "source": "external_api",
                },
                pprint=True,
            )
            return lookup_result

        # No canonical ID found via any strategy
        logger.debug(
            {
                "message": f"Cannot assign canonical ID for {entity.name}",
                "entity": entity,
                "entity_id": entity.entity_id,
                "entity_type": entity_type,
                "reason": "No canonical_ids dict entry found, entity_id does not match any known format, and external lookup returned None",
            },
            pprint=True,
        )
        return None
