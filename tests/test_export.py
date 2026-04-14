"""Tests for exporting entities and documents to JSON files.

This module verifies:
- Entity export: Writing canonical (and optionally provisional) entities to
  a global entities.json file with all fields properly serialized
- Document export: Writing per-document JSON files containing relationships
  and provisional entities extracted from that document
- Full export: Generating both the global entities.json and per-document files
- Storage list_all methods: Pagination, status filtering, and document-based queries
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgschema.entity import EntityStatus
from kgraph.export import write_bundle
from kgraph.ingest import IngestionOrchestrator
from kgraph.provenance import ProvenanceAccumulator
from kgraph.storage.memory import (
    InMemoryDocumentStorage,
    InMemoryEntityStorage,
    InMemoryRelationshipStorage,
)
from tests.conftest import (
    MockDocumentParser,
    MockEmbeddingGenerator,
    MockEntityExtractor,
    MockEntityResolver,
    MockRelationshipExtractor,
    SimpleDocument,
    SimpleDomainSchema,
    SimpleEntity,
    SimpleRelationship,
    make_test_entity,
    make_test_relationship,
)


@pytest.fixture
def orchestrator(
    tmp_path: Path,
) -> IngestionOrchestrator:
    """Create an orchestrator for export tests."""
    return IngestionOrchestrator(
        domain=SimpleDomainSchema(),
        parser=MockDocumentParser(),
        entity_extractor=MockEntityExtractor(),
        entity_resolver=MockEntityResolver(),
        relationship_extractor=MockRelationshipExtractor(),
        embedding_generator=MockEmbeddingGenerator(),
        entity_storage=InMemoryEntityStorage(),
        relationship_storage=InMemoryRelationshipStorage(),
        document_storage=InMemoryDocumentStorage(),
    )


class TestExportEntities:
    """Tests for exporting entities to a JSON file.

    By default, only canonical entities are exported to the global entities.json.
    Provisional entities can be included via the include_provisional flag.
    """

    async def test_export_canonical_entities(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Default export includes only canonical entities, excluding provisionals."""
        # Add canonical and provisional entities
        canonical = make_test_entity(
            "Canonical Entity",
            status=EntityStatus.CANONICAL,
            entity_id="canonical-1",
        )
        provisional = make_test_entity(
            "Provisional Entity",
            status=EntityStatus.PROVISIONAL,
            entity_id="provisional-1",
        )
        await orchestrator.entity_storage.add(canonical)
        await orchestrator.entity_storage.add(provisional)

        # Export
        output_file = tmp_path / "entities.json"
        count = await orchestrator.export_entities(output_file)

        assert count == 1
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["domain"] == "test_domain"
        assert data["entity_count"] == 1
        assert len(data["entities"]) == 1
        assert data["entities"][0]["entity_id"] == "canonical-1"
        assert data["entities"][0]["status"] == "canonical"

    async def test_export_includes_provisional_when_requested(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Export with include_provisional=True includes both canonical and provisional entities."""
        canonical = make_test_entity(
            "Canonical Entity",
            status=EntityStatus.CANONICAL,
            entity_id="canonical-1",
        )
        provisional = make_test_entity(
            "Provisional Entity",
            status=EntityStatus.PROVISIONAL,
            entity_id="provisional-1",
        )
        await orchestrator.entity_storage.add(canonical)
        await orchestrator.entity_storage.add(provisional)

        output_file = tmp_path / "all_entities.json"
        count = await orchestrator.export_entities(output_file, include_provisional=True)

        assert count == 2

        with open(output_file) as f:
            data = json.load(f)

        assert data["entity_count"] == 2
        entity_ids = {e["entity_id"] for e in data["entities"]}
        assert entity_ids == {"canonical-1", "provisional-1"}

    async def test_export_entity_fields(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """All entity fields are correctly serialized: ID, name, synonyms, embedding, canonical_ids, etc."""
        entity = SimpleEntity(
            entity_id="test-123",
            status=EntityStatus.CANONICAL,
            name="Test Entity",
            synonyms=("alias1", "alias2"),
            embedding=(0.1, 0.2, 0.3),
            canonical_ids={
                "wikidata": "Wikidata:Q12345",
                "test_authority": "id-123",
            },
            confidence=0.95,
            usage_count=5,
            created_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            source="test_source",
            metadata={"key": "value"},
        )
        await orchestrator.entity_storage.add(entity)

        output_file = tmp_path / "entities.json"
        await orchestrator.export_entities(output_file)

        with open(output_file) as f:
            data = json.load(f)

        exported = data["entities"][0]
        assert exported["entity_id"] == "test-123"
        assert exported["status"] == "canonical"
        assert exported["name"] == "Test Entity"
        assert exported["synonyms"] == ["alias1", "alias2"]
        assert exported["embedding"] == [0.1, 0.2, 0.3]
        assert exported["canonical_ids"]["wikidata"] == "Wikidata:Q12345"
        assert exported["confidence"] == 0.95
        assert exported["usage_count"] == 5
        assert exported["source"] == "test_source"
        assert exported["metadata"] == {"key": "value"}
        assert exported["entity_type"] == "test_entity"

    async def test_export_creates_parent_directories(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Export automatically creates missing parent directories for the output file."""
        entity = make_test_entity("Entity", status=EntityStatus.CANONICAL, entity_id="e1")
        await orchestrator.entity_storage.add(entity)

        output_file = tmp_path / "subdir" / "deep" / "entities.json"
        await orchestrator.export_entities(output_file)

        assert output_file.exists()


class TestExportDocument:
    """Tests for exporting per-document JSON files (paper_{doc_id}.json).

    Each document export includes relationships sourced from that document
    and provisional entities that originated from it.
    """

    async def test_export_document_relationships(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Document export includes relationships whose source_documents include the document ID."""
        # Create and store a document
        doc = SimpleDocument(
            document_id="doc-1",
            content="Test content",
            content_type="text/plain",
            source_uri="file://test.txt",
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.document_storage.add(doc)

        # Create entities
        e1 = make_test_entity("Entity 1", status=EntityStatus.CANONICAL, entity_id="e1")
        e2 = make_test_entity("Entity 2", status=EntityStatus.CANONICAL, entity_id="e2")
        await orchestrator.entity_storage.add(e1)
        await orchestrator.entity_storage.add(e2)

        # Create relationship from this document
        rel = SimpleRelationship(
            subject_id="e1",
            predicate="related_to",
            object_id="e2",
            confidence=0.9,
            source_documents=("doc-1",),
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.relationship_storage.add(rel)

        # Export
        output_file = tmp_path / "paper_doc-1.json"
        stats = await orchestrator.export_document("doc-1", output_file)

        assert stats["relationships"] == 1
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["document_id"] == "doc-1"
        assert data["relationship_count"] == 1
        assert len(data["relationships"]) == 1
        assert data["relationships"][0]["subject_id"] == "e1"
        assert data["relationships"][0]["predicate"] == "related_to"
        assert data["relationships"][0]["object_id"] == "e2"

    async def test_export_document_provisional_entities(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Document export includes provisional entities whose source matches the document ID."""
        doc = SimpleDocument(
            document_id="doc-1",
            content="Test content",
            content_type="text/plain",
            source_uri="file://test.txt",
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.document_storage.add(doc)

        # Create provisional entity from this document
        provisional = SimpleEntity(
            entity_id="prov-1",
            status=EntityStatus.PROVISIONAL,
            name="Provisional",
            confidence=0.8,
            usage_count=1,
            created_at=datetime.now(timezone.utc),
            source="doc-1",  # Source matches document ID
        )
        await orchestrator.entity_storage.add(provisional)

        # Create provisional entity from another document
        other_provisional = SimpleEntity(
            entity_id="prov-2",
            status=EntityStatus.PROVISIONAL,
            name="Other Provisional",
            confidence=0.8,
            usage_count=1,
            created_at=datetime.now(timezone.utc),
            source="doc-2",  # Different source
        )
        await orchestrator.entity_storage.add(other_provisional)

        output_file = tmp_path / "paper_doc-1.json"
        stats = await orchestrator.export_document("doc-1", output_file)

        assert stats["provisional_entities"] == 1

        with open(output_file) as f:
            data = json.load(f)

        assert data["provisional_entity_count"] == 1
        assert len(data["provisional_entities"]) == 1
        assert data["provisional_entities"][0]["entity_id"] == "prov-1"

    async def test_export_document_includes_title(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Document export includes the document title metadata when present."""
        doc = SimpleDocument(
            document_id="doc-1",
            title="My Document Title",
            content="Test content",
            content_type="text/plain",
            source_uri="file://test.txt",
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.document_storage.add(doc)

        output_file = tmp_path / "paper_doc-1.json"
        await orchestrator.export_document("doc-1", output_file)

        with open(output_file) as f:
            data = json.load(f)

        assert data["document_title"] == "My Document Title"

    async def test_export_nonexistent_document(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Export for a nonexistent document ID creates a file with zero relationships/entities."""
        output_file = tmp_path / "paper_missing.json"
        stats = await orchestrator.export_document("nonexistent", output_file)

        assert stats["relationships"] == 0
        assert stats["provisional_entities"] == 0

        with open(output_file) as f:
            data = json.load(f)

        assert data["document_id"] == "nonexistent"
        assert data["document_title"] is None


class TestExportAll:
    """Tests for full export: global entities.json plus per-document files.

    The export_all method generates a complete export of the knowledge graph:
    entities.json with all canonical entities, and paper_{doc_id}.json for each
    ingested document.
    """

    async def test_export_all_creates_files(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Full export creates entities.json and paper_{doc_id}.json for each document."""
        # Ingest some documents
        await orchestrator.ingest_document(
            b"Document with [Entity1] and [Entity2]",
            "text/plain",
            "file://doc1.txt",
        )
        await orchestrator.ingest_document(
            b"Another document with [Entity3]",
            "text/plain",
            "file://doc2.txt",
        )

        # Promote some entities to canonical
        entities = await orchestrator.entity_storage.list_all()
        for entity in entities[:2]:
            await orchestrator.entity_storage.promote(entity.entity_id, f"canonical-{entity.name}", canonical_ids={})

        # Export
        output_dir = tmp_path / "export"
        result = await orchestrator.export_all(output_dir)

        # Verify structure
        assert result["documents_exported"] == 2
        assert (output_dir / "entities.json").exists()

        # Verify entities.json
        with open(output_dir / "entities.json") as f:
            entities_data = json.load(f)
        assert entities_data["entity_count"] == 2

    async def test_export_all_returns_statistics(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None:
        """Full export returns statistics: output_dir, canonical_entities, documents_exported, per-document stats."""
        # Ingest a document
        result = await orchestrator.ingest_document(
            b"[Entity1] relates to [Entity2]",
            "text/plain",
            "file://doc.txt",
        )
        doc_id = result.document_id

        # Promote one entity
        entities = await orchestrator.entity_storage.list_all()
        if entities:
            await orchestrator.entity_storage.promote(entities[0].entity_id, "canonical-1", canonical_ids={})

        output_dir = tmp_path / "export"
        stats = await orchestrator.export_all(output_dir)

        assert stats["output_dir"] == str(output_dir)
        assert stats["canonical_entities"] == 1
        assert stats["documents_exported"] == 1
        assert doc_id in stats["document_stats"]


class TestListAllMethods:
    """Tests for storage list_all methods used by export functionality.

    These methods support pagination (limit/offset), status filtering for entities,
    and document-based queries for relationships.
    """

    async def test_entity_list_all(self, orchestrator: IngestionOrchestrator) -> None:
        """list_all() returns all entities regardless of status."""
        e1 = make_test_entity("E1", status=EntityStatus.CANONICAL, entity_id="e1")
        e2 = make_test_entity("E2", status=EntityStatus.PROVISIONAL, entity_id="e2")
        await orchestrator.entity_storage.add(e1)
        await orchestrator.entity_storage.add(e2)

        all_entities = await orchestrator.entity_storage.list_all()
        assert len(all_entities) == 2

    async def test_entity_list_all_with_status_filter(self, orchestrator: IngestionOrchestrator) -> None:
        """list_all(status='canonical'/'provisional') filters entities by status."""
        e1 = make_test_entity("E1", status=EntityStatus.CANONICAL, entity_id="e1")
        e2 = make_test_entity("E2", status=EntityStatus.PROVISIONAL, entity_id="e2")
        await orchestrator.entity_storage.add(e1)
        await orchestrator.entity_storage.add(e2)

        canonical = await orchestrator.entity_storage.list_all(status="canonical")
        provisional = await orchestrator.entity_storage.list_all(status="provisional")

        assert len(canonical) == 1
        assert canonical[0].entity_id == "e1"
        assert len(provisional) == 1
        assert provisional[0].entity_id == "e2"

    async def test_entity_list_all_pagination(self, orchestrator: IngestionOrchestrator) -> None:
        """list_all(limit, offset) supports pagination for large result sets."""
        for i in range(5):
            e = make_test_entity(f"E{i}", entity_id=f"e{i}")
            await orchestrator.entity_storage.add(e)

        page1 = await orchestrator.entity_storage.list_all(limit=2, offset=0)
        page2 = await orchestrator.entity_storage.list_all(limit=2, offset=2)
        page3 = await orchestrator.entity_storage.list_all(limit=2, offset=4)

        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_relationship_get_by_document(self, orchestrator: IngestionOrchestrator) -> None:
        """get_by_document() returns relationships whose source_documents include the given document ID."""
        rel1 = SimpleRelationship(
            subject_id="e1",
            predicate="related_to",
            object_id="e2",
            source_documents=("doc-1",),
            created_at=datetime.now(timezone.utc),
        )
        rel2 = SimpleRelationship(
            subject_id="e2",
            predicate="causes",
            object_id="e3",
            source_documents=("doc-2",),
            created_at=datetime.now(timezone.utc),
        )
        rel3 = SimpleRelationship(
            subject_id="e1",
            predicate="causes",
            object_id="e3",
            source_documents=("doc-1", "doc-2"),  # In both documents
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.relationship_storage.add(rel1)
        await orchestrator.relationship_storage.add(rel2)
        await orchestrator.relationship_storage.add(rel3)

        doc1_rels = await orchestrator.relationship_storage.get_by_document("doc-1")
        doc2_rels = await orchestrator.relationship_storage.get_by_document("doc-2")

        assert len(doc1_rels) == 2  # rel1 and rel3
        assert len(doc2_rels) == 2  # rel2 and rel3

    async def test_relationship_list_all(self, orchestrator: IngestionOrchestrator) -> None:
        """list_all() returns all relationships in storage."""
        rel1 = make_test_relationship("e1", "e2")
        rel2 = make_test_relationship("e2", "e3")
        await orchestrator.relationship_storage.add(rel1)
        await orchestrator.relationship_storage.add(rel2)

        all_rels = await orchestrator.relationship_storage.list_all()
        assert len(all_rels) == 2


class TestExportBundleProvenance:
    """Tests for bundle export with provenance (mentions.jsonl, evidence.jsonl, summary fields)."""

    async def test_write_bundle_with_provenance_writes_mentions_and_evidence(
        self, orchestrator: IngestionOrchestrator, tmp_path: Path
    ) -> None:
        """With provenance_accumulator populated, write_bundle writes mentions.jsonl and evidence.jsonl and sets manifest."""
        e1 = make_test_entity("Entity1", status=EntityStatus.CANONICAL, entity_id="e1")
        e2 = make_test_entity("Entity2", status=EntityStatus.CANONICAL, entity_id="e2")
        await orchestrator.entity_storage.add(e1)
        await orchestrator.entity_storage.add(e2)

        rel = SimpleRelationship(
            subject_id="e1",
            predicate="related_to",
            object_id="e2",
            confidence=0.9,
            source_documents=("doc-1",),
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.relationship_storage.add(rel)

        acc = ProvenanceAccumulator()
        acc.add_mention(
            entity_id="e1",
            document_id="doc-1",
            section="abstract",
            start_offset=0,
            end_offset=7,
            text_span="Entity1",
            context="First mention of Entity1",
            confidence=0.95,
            extraction_method="llm",
            created_at="2024-01-15T12:00:00Z",
        )
        acc.add_mention(
            entity_id="e1",
            document_id="doc-2",
            section=None,
            start_offset=10,
            end_offset=17,
            text_span="Entity1",
            context=None,
            confidence=0.9,
            extraction_method="llm",
            created_at="2024-01-15T12:01:00Z",
        )
        acc.add_evidence(
            relationship_key="e1:related_to:e2",
            document_id="doc-1",
            section="results",
            start_offset=100,
            end_offset=130,
            text_span="Entity1 is related to Entity2.",
            confidence=0.88,
            supports=True,
        )

        bundle_path = tmp_path / "bundle"
        await write_bundle(
            entity_storage=orchestrator.entity_storage,
            relationship_storage=orchestrator.relationship_storage,
            bundle_path=bundle_path,
            domain="test_domain",
            label="Test bundle",
            provenance_accumulator=acc,
        )

        assert (bundle_path / "manifest.json").exists()
        with open(bundle_path / "manifest.json") as f:
            manifest = json.load(f)
        assert manifest.get("mentions") is not None
        assert manifest["mentions"]["path"] == "mentions.jsonl"
        assert manifest.get("evidence") is not None
        assert manifest["evidence"]["path"] == "evidence.jsonl"

        mentions_file = bundle_path / "mentions.jsonl"
        assert mentions_file.exists()
        lines = mentions_file.read_text().strip().split("\n")
        assert len(lines) == 2
        m1 = json.loads(lines[0])
        assert m1["entity_id"] == "e1"
        assert m1["document_id"] == "doc-1"
        assert m1["section"] == "abstract"
        assert m1["text_span"] == "Entity1"
        m2 = json.loads(lines[1])
        assert m2["document_id"] == "doc-2"

        evidence_file = bundle_path / "evidence.jsonl"
        assert evidence_file.exists()
        elines = evidence_file.read_text().strip().split("\n")
        assert len(elines) == 1
        ev = json.loads(elines[0])
        assert ev["relationship_key"] == "e1:related_to:e2"
        assert ev["text_span"] == "Entity1 is related to Entity2."
        assert ev["confidence"] == 0.88

    async def test_write_bundle_entity_rows_get_provenance_summary(
        self, orchestrator: IngestionOrchestrator, tmp_path: Path
    ) -> None:
        """Entity rows in entities.jsonl include first_seen_document, total_mentions, supporting_documents."""
        e1 = make_test_entity("E1", status=EntityStatus.CANONICAL, entity_id="e1")
        await orchestrator.entity_storage.add(e1)

        acc = ProvenanceAccumulator()
        acc.add_mention(
            entity_id="e1",
            document_id="doc-a",
            section="intro",
            start_offset=0,
            end_offset=2,
            text_span="E1",
            context=None,
            confidence=1.0,
            extraction_method="test",
            created_at="2024-01-01T00:00:00Z",
        )
        acc.add_mention(
            entity_id="e1",
            document_id="doc-b",
            section=None,
            start_offset=0,
            end_offset=2,
            text_span="E1",
            context=None,
            confidence=1.0,
            extraction_method="test",
            created_at="2024-01-02T00:00:00Z",
        )

        bundle_path = tmp_path / "bundle"
        await write_bundle(
            entity_storage=orchestrator.entity_storage,
            relationship_storage=orchestrator.relationship_storage,
            bundle_path=bundle_path,
            domain="test",
            provenance_accumulator=acc,
        )

        entities_lines = (bundle_path / "entities.jsonl").read_text().strip().split("\n")
        assert len(entities_lines) == 1
        row = json.loads(entities_lines[0])
        assert row["entity_id"] == "e1"
        assert row["first_seen_document"] == "doc-a"
        assert row["first_seen_section"] == "intro"
        assert row["total_mentions"] == 2
        assert set(row["supporting_documents"]) == {"doc-a", "doc-b"}

    async def test_write_bundle_relationship_rows_get_evidence_summary(
        self, orchestrator: IngestionOrchestrator, tmp_path: Path
    ) -> None:
        """Relationship rows in relationships.jsonl include evidence_count, strongest_evidence_quote, evidence_confidence_avg."""
        e1 = make_test_entity("E1", status=EntityStatus.CANONICAL, entity_id="e1")
        e2 = make_test_entity("E2", status=EntityStatus.CANONICAL, entity_id="e2")
        await orchestrator.entity_storage.add(e1)
        await orchestrator.entity_storage.add(e2)
        rel = SimpleRelationship(
            subject_id="e1",
            predicate="causes",
            object_id="e2",
            confidence=0.9,
            source_documents=("d1",),
            created_at=datetime.now(timezone.utc),
        )
        await orchestrator.relationship_storage.add(rel)

        acc = ProvenanceAccumulator()
        acc.add_evidence(
            relationship_key="e1:causes:e2",
            document_id="d1",
            section=None,
            start_offset=0,
            end_offset=20,
            text_span="E1 causes E2.",
            confidence=0.9,
            supports=True,
        )
        acc.add_evidence(
            relationship_key="e1:causes:e2",
            document_id="d1",
            section=None,
            start_offset=50,
            end_offset=75,
            text_span="Strong evidence: E1 causes E2.",
            confidence=0.95,
            supports=True,
        )

        bundle_path = tmp_path / "bundle"
        await write_bundle(
            entity_storage=orchestrator.entity_storage,
            relationship_storage=orchestrator.relationship_storage,
            bundle_path=bundle_path,
            domain="test",
            provenance_accumulator=acc,
        )

        rel_lines = (bundle_path / "relationships.jsonl").read_text().strip().split("\n")
        assert len(rel_lines) == 1
        row = json.loads(rel_lines[0])
        assert row["subject_id"] == "e1"
        assert row["predicate"] == "causes"
        assert row["object_id"] == "e2"
        assert row["evidence_count"] == 2
        assert row["strongest_evidence_quote"] == "Strong evidence: E1 causes E2."
        assert row["evidence_confidence_avg"] == round((0.9 + 0.95) / 2, 4)

    async def test_write_bundle_without_provenance_no_mentions_or_evidence_files(
        self, orchestrator: IngestionOrchestrator, tmp_path: Path
    ) -> None:
        """Without provenance_accumulator, no mentions.jsonl or evidence.jsonl and manifest has no mentions/evidence."""
        e1 = make_test_entity("E1", status=EntityStatus.CANONICAL, entity_id="e1")
        await orchestrator.entity_storage.add(e1)
        rel = make_test_relationship("e1", "e2")
        await orchestrator.relationship_storage.add(rel)

        bundle_path = tmp_path / "bundle"
        await write_bundle(
            entity_storage=orchestrator.entity_storage,
            relationship_storage=orchestrator.relationship_storage,
            bundle_path=bundle_path,
            domain="test",
        )

        assert not (bundle_path / "mentions.jsonl").exists()
        assert not (bundle_path / "evidence.jsonl").exists()
        with open(bundle_path / "manifest.json") as f:
            manifest = json.load(f)
        assert manifest.get("mentions") is None
        assert manifest.get("evidence") is None
