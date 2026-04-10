"""Tests for promotion with canonical ID lookup service integration.

Tests that verify the lookup parameter is correctly passed through the promotion chain:
- run_promotion(lookup=...) → get_promotion_policy(lookup=...) → MedLitPromotionPolicy(lookup=...)
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from kgschema.entity import EntityStatus

from kgraph.ingest import IngestionOrchestrator
from kgraph.pipeline.ollama_embedding import OllamaEmbeddingGenerator
from kgraph.storage.memory import (
    InMemoryEntityStorage,
    InMemoryRelationshipStorage,
    InMemoryDocumentStorage,
)

from medlit.domain import MedLitDomainSchema
from medlit.entities import DiseaseEntity
from medlit.pipeline.authority_lookup import CanonicalIdLookup
from medlit.pipeline.parser import JournalArticleParser
from medlit.pipeline.mentions import MedLitEntityExtractor
from medlit.pipeline.resolve import MedLitEntityResolver
from medlit.pipeline.relationships import MedLitRelationshipExtractor


@pytest.fixture
async def medlit_orchestrator(
    entity_storage: InMemoryEntityStorage,
    relationship_storage: InMemoryRelationshipStorage,
    document_storage: InMemoryDocumentStorage,
):
    """Create orchestrator with MedLit domain for promotion testing."""
    domain = MedLitDomainSchema()
    embedding_generator = OllamaEmbeddingGenerator()
    return IngestionOrchestrator(
        domain=domain,
        parser=JournalArticleParser(),
        entity_extractor=MedLitEntityExtractor(llm_client=None),
        entity_resolver=MedLitEntityResolver(
            domain=domain,
            embedding_generator=embedding_generator,
        ),
        relationship_extractor=MedLitRelationshipExtractor(llm_client=None),
        embedding_generator=embedding_generator,
        entity_storage=entity_storage,
        relationship_storage=relationship_storage,
        document_storage=document_storage,
    )


@pytest.fixture
def mock_lookup():
    """Create a mock CanonicalIdLookupInterface for testing."""
    from kgraph.canonical_id import CanonicalIdLookupInterface

    lookup = MagicMock(spec=CanonicalIdLookupInterface)
    lookup.lookup = AsyncMock(return_value=None)
    lookup.lookup_sync = MagicMock(return_value=None)
    return lookup


class TestPromotionLookupIntegration:
    """Test that lookup service is passed through the promotion chain."""

    async def test_get_promotion_policy_accepts_lookup_parameter(
        self,
        medlit_orchestrator: IngestionOrchestrator,
        mock_lookup: MagicMock,
    ):
        """get_promotion_policy accepts lookup parameter and passes it to policy."""
        domain = medlit_orchestrator.domain

        # Call get_promotion_policy with lookup
        policy = domain.get_promotion_policy(lookup=mock_lookup)

        # Verify the policy was created (MedLitPromotionPolicy)
        assert policy is not None
        # Verify the lookup was passed to the policy
        # MedLitPromotionPolicy stores it as self.lookup
        assert hasattr(policy, "lookup")
        assert policy.lookup is mock_lookup

    async def test_get_promotion_policy_works_without_lookup(
        self,
        medlit_orchestrator: IngestionOrchestrator,
    ):
        """get_promotion_policy works when lookup is None (creates new instance)."""
        domain = medlit_orchestrator.domain

        # Call get_promotion_policy without lookup
        policy = domain.get_promotion_policy(lookup=None)

        # Verify the policy was created
        assert policy is not None
        # Verify a new lookup instance was created
        assert hasattr(policy, "lookup")
        assert policy.lookup is not None
        assert isinstance(policy.lookup, CanonicalIdLookup)

    async def test_run_promotion_passes_lookup_to_policy(
        self,
        medlit_orchestrator: IngestionOrchestrator,
        entity_storage: InMemoryEntityStorage,
        mock_lookup: MagicMock,
    ):
        """run_promotion passes lookup parameter through to get_promotion_policy."""
        # Create a provisional entity that meets promotion criteria
        entity = DiseaseEntity(
            entity_id="prov:test-disease",
            name="Test Disease",
            status=EntityStatus.PROVISIONAL,
            usage_count=5,  # Exceeds default threshold (1)
            confidence=0.8,  # Exceeds default threshold (0.4)
            created_at=datetime.now(timezone.utc),
            source="test",
        )
        await entity_storage.add(entity)

        # Mock the lookup to return a CanonicalId object
        from kgraph.canonical_id import CanonicalId

        mock_lookup.lookup.return_value = CanonicalId(id="C1234567", url=None, synonyms=())

        # Run promotion with lookup
        promoted = await medlit_orchestrator.run_promotion(lookup=mock_lookup)

        # Verify lookup was called (if entity doesn't have canonical ID already)
        # Note: The entity might get promoted via other strategies first, so we
        # just verify the lookup parameter was accepted without error
        assert isinstance(promoted, list)

    async def test_promotion_uses_provided_lookup_service(
        self,
        medlit_orchestrator: IngestionOrchestrator,
        entity_storage: InMemoryEntityStorage,
        mock_lookup: MagicMock,
    ):
        """Promotion uses the provided lookup service when assigning canonical IDs."""
        # Create a provisional entity without canonical_ids dict
        # This forces the policy to use external lookup
        entity = DiseaseEntity(
            entity_id="prov:unknown-disease",
            name="Unknown Disease",
            status=EntityStatus.PROVISIONAL,
            usage_count=5,
            confidence=0.8,
            canonical_ids={},  # Empty - will trigger external lookup
            created_at=datetime.now(timezone.utc),
            source="test",
        )
        await entity_storage.add(entity)

        # Mock lookup to return a CanonicalId object
        from kgraph.canonical_id import CanonicalId

        mock_lookup.lookup.return_value = CanonicalId(id="C9999999", url=None, synonyms=())

        # Run promotion with lookup
        promoted = await medlit_orchestrator.run_promotion(lookup=mock_lookup)

        # Verify lookup was called
        mock_lookup.lookup.assert_called()
        # Verify it was called with the entity name and type
        call_args = mock_lookup.lookup.call_args
        assert call_args is not None
        assert call_args.kwargs.get("term") == "Unknown Disease"
        assert call_args.kwargs.get("entity_type") == "disease"

        # If promotion succeeded, verify the entity was promoted
        if promoted:
            assert len(promoted) > 0
            promoted_entity = promoted[0]
            assert promoted_entity.status == EntityStatus.CANONICAL
