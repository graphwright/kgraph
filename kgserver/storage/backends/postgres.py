"""
PostgreSQL implementation of the storage interface.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Sequence
from sqlalchemy import func, text
from sqlmodel import Session, select
from storage.interfaces import StorageInterface
from storage.models import Bundle, BundleEvidence, Entity, IngestJob, Mention, Relationship
from kgbundle import BundleManifestV1, EntityRow, EvidenceRow, MentionRow, RelationshipRow
from pydantic import ValidationError


class PostgresStorage(StorageInterface):
    """
    PostgreSQL implementation of the storage interface.
    """

    def __init__(self, session: Session):
        self._session = session

    def load_bundle(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None:
        """
        Load a data bundle into the storage.
        This is an idempotent operation. If the bundle is already loaded, it will do nothing.
        """
        if self.is_bundle_loaded(bundle_manifest.bundle_id):
            print(f"Bundle {bundle_manifest.bundle_id} already loaded. Skipping.")
            return

        print(f"Loading bundle {bundle_manifest.bundle_id} from {bundle_path}")
        # Truncate all bundle tables so re-loads are idempotent. Must include
        # bundle_mention and bundle_evidence — they have no FKs to entity/relationship,
        # so CASCADE would not clear them. Old mentions with wrong document_ids would
        # otherwise persist across runs and contaminate query results.
        self._session.execute(text("TRUNCATE TABLE bundle, relationship, entity, bundle_mention, bundle_evidence RESTART IDENTITY CASCADE"))
        self._session.commit()

        # Load entities
        if bundle_manifest.entities:
            entities_file = f"{bundle_path}/{bundle_manifest.entities.path}"
            self._debug_print_sample_entities(entities_file)
            self._load_entities(entities_file)

        # Load relationships
        if bundle_manifest.relationships:
            relationships_file = f"{bundle_path}/{bundle_manifest.relationships.path}"
            self._load_relationships(relationships_file)

        # Load provenance when present
        if bundle_manifest.mentions is not None:
            mentions_path = f"{bundle_path}/{bundle_manifest.mentions.path}"
            try:
                with open(mentions_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        mention_row = MentionRow.model_validate_json(line)
                        self._session.add(
                            Mention(
                                entity_id=mention_row.entity_id,
                                document_id=mention_row.document_id,
                                section=mention_row.section,
                                start_offset=mention_row.start_offset,
                                end_offset=mention_row.end_offset,
                                text_span=mention_row.text_span,
                                context=mention_row.context,
                                confidence=mention_row.confidence,
                                extraction_method=mention_row.extraction_method,
                                created_at=mention_row.created_at,
                            )
                        )
            except FileNotFoundError:
                pass
        if bundle_manifest.evidence is not None:
            evidence_path = f"{bundle_path}/{bundle_manifest.evidence.path}"
            try:
                with open(evidence_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        evidence_row = EvidenceRow.model_validate_json(line)
                        self._session.add(
                            BundleEvidence(
                                relationship_key=evidence_row.relationship_key,
                                document_id=evidence_row.document_id,
                                section=evidence_row.section,
                                start_offset=evidence_row.start_offset,
                                end_offset=evidence_row.end_offset,
                                text_span=evidence_row.text_span,
                                confidence=evidence_row.confidence,
                                supports=evidence_row.supports,
                            )
                        )
            except FileNotFoundError:
                pass

        self.record_bundle(bundle_manifest)
        self._session.commit()

    def load_bundle_incremental(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None:
        """
        Load a bundle into the graph without truncating; upsert entities (accumulate
        usage_count) and relationships, append provenance.
        """
        if bundle_manifest.entities:
            entities_file = f"{bundle_path}/{bundle_manifest.entities.path}"
            self._load_entities_incremental(entities_file)
        if bundle_manifest.relationships:
            relationships_file = f"{bundle_path}/{bundle_manifest.relationships.path}"
            self._load_relationships_incremental(relationships_file)
        if bundle_manifest.mentions is not None:
            mentions_path = f"{bundle_path}/{bundle_manifest.mentions.path}"
            try:
                with open(mentions_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        mention_row = MentionRow.model_validate_json(line)
                        self._session.add(
                            Mention(
                                entity_id=mention_row.entity_id,
                                document_id=mention_row.document_id,
                                section=mention_row.section,
                                start_offset=mention_row.start_offset,
                                end_offset=mention_row.end_offset,
                                text_span=mention_row.text_span,
                                context=mention_row.context,
                                confidence=mention_row.confidence,
                                extraction_method=mention_row.extraction_method,
                                created_at=mention_row.created_at,
                            )
                        )
            except FileNotFoundError:
                pass
        if bundle_manifest.evidence is not None:
            evidence_path = f"{bundle_path}/{bundle_manifest.evidence.path}"
            try:
                with open(evidence_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        evidence_row = EvidenceRow.model_validate_json(line)
                        self._session.add(
                            BundleEvidence(
                                relationship_key=evidence_row.relationship_key,
                                document_id=evidence_row.document_id,
                                section=evidence_row.section,
                                start_offset=evidence_row.start_offset,
                                end_offset=evidence_row.end_offset,
                                text_span=evidence_row.text_span,
                                confidence=evidence_row.confidence,
                                supports=evidence_row.supports,
                            )
                        )
            except FileNotFoundError:
                pass
        self.record_bundle(bundle_manifest)
        self._session.commit()

    def _load_entities_incremental(self, entities_file: str) -> None:
        """Upsert entities from JSONL; on conflict add usage_count to existing row."""
        with open(entities_file, "r") as f:
            for line in f:
                entity_data = json.loads(line)
                try:
                    entity_row = EntityRow.model_validate(entity_data)
                    entity_data = entity_row.model_dump(exclude_unset=True)
                except ValidationError:
                    continue
                normalized = self._normalize_entity(entity_data)
                # Build INSERT ... ON CONFLICT (entity_id) DO UPDATE SET usage_count = entity.usage_count + excluded.usage_count, ...
                usage = normalized.get("usage_count") or 0
                name = normalized.get("name")
                entity_type = normalized.get("entity_type", "")
                status = normalized.get("status")
                confidence = normalized.get("confidence")
                source = normalized.get("source")
                canonical_url = normalized.get("canonical_url")
                synonyms = json.dumps(normalized.get("synonyms") or [])
                properties = json.dumps(normalized.get("properties") or {})
                entity_id = normalized["entity_id"]
                stmt = text("""
                    INSERT INTO entity (entity_id, entity_type, name, status, confidence, usage_count, source, canonical_url, synonyms, properties)
                    VALUES (:entity_id, :entity_type, :name, :status, :confidence, :usage_count, :source, :canonical_url,
                            CAST(:synonyms AS json), CAST(:properties AS json))
                    ON CONFLICT (entity_id) DO UPDATE SET
                        usage_count = entity.usage_count + COALESCE(EXCLUDED.usage_count, 0),
                        name = COALESCE(EXCLUDED.name, entity.name),
                        entity_type = COALESCE(EXCLUDED.entity_type, entity.entity_type),
                        status = COALESCE(EXCLUDED.status, entity.status),
                        confidence = COALESCE(EXCLUDED.confidence, entity.confidence),
                        source = COALESCE(EXCLUDED.source, entity.source),
                        canonical_url = COALESCE(EXCLUDED.canonical_url, entity.canonical_url),
                        synonyms = COALESCE(EXCLUDED.synonyms, entity.synonyms),
                        properties = COALESCE(EXCLUDED.properties, entity.properties)
                """)
                self._session.execute(
                    stmt,
                    {
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "name": name,
                        "status": status,
                        "confidence": confidence,
                        "usage_count": usage,
                        "source": source,
                        "canonical_url": canonical_url,
                        "synonyms": synonyms,
                        "properties": properties,
                    },
                )

    def _load_relationships_incremental(self, relationships_file: str) -> None:
        """Upsert relationships from JSONL by (subject_id, predicate, object_id)."""
        with open(relationships_file, "r") as f:
            for line in f:
                relationship_data = json.loads(line)
                try:
                    relationship_row = RelationshipRow.model_validate(relationship_data)
                    relationship_data = relationship_row.model_dump(exclude_unset=True)
                except ValidationError:
                    continue
                relationship_data = self._normalize_relationship(relationship_data)
                # Relationship has id UUID PK; we upsert on the unique triple.
                # Use session.merge with a new UUID so we don't conflict on id; but merge uses PK.
                # So we need to select by triple first: if exists get its id and merge; else add new.
                subj = relationship_data.get("subject_id")
                pred = relationship_data.get("predicate")
                obj = relationship_data.get("object_id")
                if subj is None or pred is None or obj is None:
                    continue
                existing = self.get_relationship(subj, pred, obj)
                if existing:
                    # Update in place (confidence, source_documents, properties)
                    existing.confidence = relationship_data.get("confidence", existing.confidence)
                    existing.source_documents = relationship_data.get("source_documents", existing.source_documents) or []
                    existing.properties = relationship_data.get("properties", existing.properties) or {}
                    self._session.add(existing)
                else:
                    rel = Relationship(**relationship_data)
                    self._session.add(rel)

    def create_ingest_job(self, url: str) -> IngestJob:
        """Create a new ingest job and return it."""
        job = IngestJob(
            id=uuid.uuid4().hex,
            url=url,
            status="queued",
            created_at=datetime.now(timezone.utc),
        )
        self._session.add(job)
        self._session.commit()
        self._session.refresh(job)
        return job

    def get_ingest_job(self, job_id: str) -> Optional[IngestJob]:
        """Get an ingest job by id, or None if not found."""
        return self._session.get(IngestJob, job_id)

    def update_ingest_job(self, job_id: str, **fields: Any) -> Optional[IngestJob]:
        """Update an ingest job by id; return updated model or None if not found."""
        job = self._session.get(IngestJob, job_id)
        if job is None:
            return None
        allowed = {"status", "started_at", "completed_at", "paper_title", "pmcid", "entities_added", "relationships_added", "error"}
        for key, value in fields.items():
            if key in allowed and hasattr(job, key):
                setattr(job, key, value)
        self._session.add(job)
        self._session.commit()
        self._session.refresh(job)
        return job

    def _debug_print_sample_entities(self, entities_file: str) -> None:
        """Print first few entities for debugging."""
        print("  Debug: Checking first 3 entities from bundle...")
        with open(entities_file, "r") as f:
            for i, line in enumerate(f):
                if i >= 3:
                    break
                entity_data = json.loads(line)
                entity_id = entity_data.get("entity_id", "unknown")
                status = entity_data.get("status", "unknown")
                props = entity_data.get("properties", {})
                print(f"    Entity {i+1}: {entity_id} (status: {status})")
                print(f"      Properties type: {type(props).__name__}")
                if isinstance(props, dict):
                    print(f"      Properties keys: {list(props.keys())}")
                    if props:
                        print(f"      Properties sample: {str(props)[:300]}")
                else:
                    print(f"      Properties value: {str(props)[:300]}")

    def _load_entities(self, entities_file: str) -> None:
        """Load entities from JSONL file."""
        canonical_url_count = 0
        total_entities = 0
        canonical_entities = 0
        sample_with_url = None
        sample_without_url = None
        sample_entity_raw = None
        sample_canonical_entity = None

        with open(entities_file, "r") as f:
            for line in f:
                entity_data = json.loads(line)
                try:
                    entity_row = EntityRow.model_validate(entity_data)
                    entity_data = entity_row.model_dump(exclude_unset=True)
                except ValidationError as e:
                    print(f"  ⚠ Validation error for entity: {e}")
                    print(f"    Problematic data: {line.strip()}")
                    continue  # Skip this entity

                total_entities += 1
                entity_id = entity_data.get("entity_id", "unknown")
                status = entity_data.get("status", "unknown")

                # Track canonical entities and capture samples
                is_canonical = status == "canonical" or (not entity_id.startswith("prov:") and status != "provisional")
                if is_canonical:
                    canonical_entities += 1
                    if sample_canonical_entity is None:
                        sample_canonical_entity = self._capture_entity_sample(entity_data, entity_id, status)

                if sample_entity_raw is None:
                    sample_entity_raw = self._capture_entity_sample(entity_data, entity_id, status)

                # Check if canonical_url exists in properties before normalization
                has_url_in_props, props = self._check_canonical_url_in_props(entity_data, entity_id, status)
                if has_url_in_props and sample_with_url is None:
                    sample_with_url = {
                        "entity_id": entity_id,
                        "status": status,
                        "properties": props,
                        "canonical_url_in_props": props.get("canonical_url") or props.get("canonicalUrl"),
                    }

                # Flatten metadata into top-level fields if present
                normalized_data = self._normalize_entity(entity_data)

                # Verify canonical_url was extracted
                if normalized_data.get("canonical_url"):
                    canonical_url_count += 1
                elif has_url_in_props and sample_without_url is None:
                    sample_without_url = {
                        "entity_id": entity_id,
                        "status": status,
                        "properties_before": props,
                        "properties_after": normalized_data.get("properties"),
                        "canonical_url_after": normalized_data.get("canonical_url"),
                    }

                entity = Entity(**normalized_data)
                self._session.merge(entity)

        self._print_entity_loading_summary(canonical_url_count, canonical_entities, total_entities, sample_canonical_entity, sample_entity_raw, sample_with_url, sample_without_url)

    def _capture_entity_sample(self, entity_data: dict, entity_id: str, status: str) -> dict:
        """Capture a sample entity for debugging."""
        return {
            "entity_id": entity_id,
            "status": status,
            "has_properties": "properties" in entity_data,
            "properties_type": type(entity_data.get("properties")).__name__ if "properties" in entity_data else None,
            "properties_keys": list(entity_data.get("properties", {}).keys()) if isinstance(entity_data.get("properties"), dict) else None,
            "properties_value": str(entity_data.get("properties"))[:200] if "properties" in entity_data else None,
        }

    def _check_canonical_url_in_props(self, entity_data: dict, entity_id: str, status: str) -> tuple[bool, dict]:
        """Check if canonical_url exists in properties and return it along with props."""
        has_url_in_props = False
        props = {}
        if "properties" in entity_data:
            props = entity_data["properties"]
            if isinstance(props, dict):
                if "canonical_url" in props or "canonicalUrl" in props:
                    has_url_in_props = True
        return has_url_in_props, props

    def _print_entity_loading_summary(
        self,
        canonical_url_count: int,
        canonical_entities: int,
        total_entities: int,
        sample_canonical_entity: Optional[dict],
        sample_entity_raw: Optional[dict],
        sample_with_url: Optional[dict],
        sample_without_url: Optional[dict],
    ) -> None:
        """Print summary of entity loading with debug information."""
        if canonical_url_count > 0:
            print(f"  ✓ Extracted canonical_url for {canonical_url_count} of {canonical_entities} canonical entities ({total_entities} total)")
        else:
            print("  ⚠ Warning: No canonical_url found in bundle properties")
            print(f"     Total entities: {total_entities}, Canonical entities: {canonical_entities}")
            if sample_canonical_entity:
                self._print_entity_sample("Sample CANONICAL entity structure:", sample_canonical_entity)
            if sample_entity_raw:
                self._print_entity_sample("Sample entity (any status):", sample_entity_raw)
            if sample_with_url:
                print(f"     Sample entity with URL in properties: {sample_with_url['entity_id']} (status: {sample_with_url['status']})")
                print(f"     URL value: {sample_with_url['canonical_url_in_props']}")
            if sample_without_url:
                print(f"     Sample entity where extraction failed: {sample_without_url['entity_id']} (status: {sample_without_url['status']})")
                print(f"     Properties before: {sample_without_url['properties_before']}")
                print(f"     Properties after: {sample_without_url['properties_after']}")
                print(f"     Canonical URL after: {sample_without_url['canonical_url_after']}")

    def _print_entity_sample(self, title: str, sample: dict) -> None:
        """Print a sample entity structure."""
        print(f"     {title}")
        print(f"       entity_id: {sample['entity_id']}")
        print(f"       status: {sample['status']}")
        print(f"       has_properties: {sample['has_properties']}")
        print(f"       properties_type: {sample['properties_type']}")
        print(f"       properties_keys: {sample['properties_keys']}")
        if "properties_value" in sample:
            print(f"       properties_value (first 200 chars): {sample['properties_value']}")

    def _load_relationships(self, relationships_file: str) -> None:
        """Load relationships from JSONL file."""
        with open(relationships_file, "r") as f:
            for line in f:
                relationship_data = json.loads(line)
                try:
                    relationship_row = RelationshipRow.model_validate(relationship_data)
                    relationship_data = relationship_row.model_dump(exclude_unset=True)
                except ValidationError as e:
                    print(f"  ⚠ Validation error for relationship: {e}")
                    print(f"    Problematic data: {line.strip()}")
                    continue
                # Map source_entity_id/target_entity_id to subject_id/object_id
                relationship_data = self._normalize_relationship(relationship_data)
                relationship = Relationship(**relationship_data)
                self._session.merge(relationship)

    def _normalize_entity(self, data: dict) -> dict:
        """Normalize entity data, flattening metadata fields."""
        result = dict(data)
        # If metadata contains fields that should be top-level, extract them
        if "metadata" in result and isinstance(result["metadata"], dict):
            meta = result.pop("metadata")
            for key in ["status", "usage_count", "source", "created_at", "canonical_url"]:
                if key in meta and key not in result:
                    result[key] = meta[key]
            # Store remaining metadata in properties
            if meta:
                result.setdefault("properties", {}).update(meta)

        # Ensure properties is a dict (handle case where it might be a JSON string or None)
        if "properties" not in result:
            result["properties"] = {}
        elif result["properties"] is None:
            result["properties"] = {}
        elif not isinstance(result["properties"], dict):
            if isinstance(result["properties"], str):
                try:
                    result["properties"] = json.loads(result["properties"])
                except (json.JSONDecodeError, TypeError):
                    result["properties"] = {}
            else:
                result["properties"] = {}

        # Extract canonical_url from properties if not already set
        # Check both canonical_url and canonicalUrl (camelCase variant)
        if "canonical_url" not in result or not result.get("canonical_url"):
            props = result.get("properties", {})
            if isinstance(props, dict):
                # Try canonical_url first
                if "canonical_url" in props:
                    result["canonical_url"] = props.pop("canonical_url")
                # Also try canonicalUrl (camelCase)
                elif "canonicalUrl" in props:
                    result["canonical_url"] = props.pop("canonicalUrl")

        # Move provenance summary fields into properties so Entity() accepts only known columns
        for key in ("first_seen_document", "first_seen_section", "total_mentions", "supporting_documents"):
            if key in result:
                result.setdefault("properties", {})[key] = result.pop(key)
        # Entity model has no created_at; keep it in properties if present
        if "created_at" in result:
            result.setdefault("properties", {})["created_at"] = result.pop("created_at")

        return result

    def _normalize_relationship(self, data: dict) -> dict:
        """Normalize relationship data, mapping field names."""
        result = dict(data)
        # Map source_entity_id -> subject_id
        if "source_entity_id" in result and "subject_id" not in result:
            result["subject_id"] = result.pop("source_entity_id")
        # Map target_entity_id -> object_id
        if "target_entity_id" in result and "object_id" not in result:
            result["object_id"] = result.pop("target_entity_id")
        # Handle metadata -> properties
        if "metadata" in result and isinstance(result["metadata"], dict):
            meta = result.pop("metadata")
            if "source_documents" in meta and "source_documents" not in result:
                result["source_documents"] = meta.pop("source_documents", [])
            result.setdefault("properties", {}).update(meta)
        # Remove fields not in the model
        result.pop("relationship_id", None)
        result.pop("evidence_document_id", None)
        # Move evidence summary fields into properties
        for key in ("evidence_count", "strongest_evidence_quote", "evidence_confidence_avg"):
            if key in result:
                result.setdefault("properties", {})[key] = result.pop(key)
        # Relationship model has no created_at; keep it in properties if present
        if "created_at" in result:
            result.setdefault("properties", {})["created_at"] = result.pop("created_at")
        return result

    def is_bundle_loaded(self, bundle_id: str) -> bool:
        """
        Check if a bundle with the given ID is already loaded.
        """
        bundle = self._session.get(Bundle, bundle_id)
        return bundle is not None

    def record_bundle(self, bundle_manifest: BundleManifestV1) -> None:
        """
        Record that a bundle has been loaded.
        """
        bundle = Bundle(
            bundle_id=bundle_manifest.bundle_id,
            domain=bundle_manifest.domain,
            created_at=datetime.fromisoformat(bundle_manifest.created_at),
            bundle_version=bundle_manifest.bundle_version,
        )
        self._session.add(bundle)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by its ID.
        """
        return self._session.get(Entity, entity_id)

    def get_entities(
        self,
        limit: int = 100,
        offset: int = 0,
        entity_type: Optional[str] = None,
        name: Optional[str] = None,
        name_contains: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Sequence[Entity]:
        """
        List entities with optional filtering.
        """
        statement = select(Entity)
        if entity_type:
            statement = statement.where(Entity.entity_type == entity_type)
        if name:
            statement = statement.where(Entity.name == name)
        if name_contains:
            statement = statement.where(Entity.name.ilike(f"%{name_contains}%"))  # type: ignore[union-attr]
        if source:
            statement = statement.where(Entity.source == source)
        if status:
            statement = statement.where(Entity.status == status)
        statement = statement.order_by(Entity.usage_count.desc()).limit(limit).offset(offset)  # type: ignore[union-attr]
        return self._session.exec(statement).all()

    def count_entities(
        self,
        entity_type: Optional[str] = None,
        name: Optional[str] = None,
        name_contains: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Count entities matching filter criteria.
        """
        statement = select(func.count(Entity.entity_id))  # type: ignore[arg-type] # pylint: disable=not-callable
        if entity_type:
            statement = statement.where(Entity.entity_type == entity_type)
        if name:
            statement = statement.where(Entity.name == name)
        if name_contains:
            statement = statement.where(Entity.name.ilike(f"%{name_contains}%"))  # type: ignore[union-attr]
        if source:
            statement = statement.where(Entity.source == source)
        if status:
            statement = statement.where(Entity.status == status)
        return self._session.exec(statement).one()

    def find_relationships(
        self,
        subject_id: Optional[str] = None,
        predicate: Optional[str] = None,
        object_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Sequence[Relationship]:
        """
        Find relationships matching criteria.
        """
        statement = select(Relationship)
        if subject_id:
            statement = statement.where(Relationship.subject_id == subject_id)
        if predicate:
            statement = statement.where(Relationship.predicate == predicate)
        if object_id:
            statement = statement.where(Relationship.object_id == object_id)
        if limit:
            statement = statement.limit(limit)
        if offset:
            statement = statement.offset(offset)
        return self._session.exec(statement).all()

    def count_relationships(
        self,
        subject_id: Optional[str] = None,
        predicate: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> int:
        """
        Count relationships matching filter criteria.
        """
        statement = select(func.count(Relationship.id))  # type: ignore[arg-type] # pylint: disable=not-callable
        if subject_id:
            statement = statement.where(Relationship.subject_id == subject_id)
        if predicate:
            statement = statement.where(Relationship.predicate == predicate)
        if object_id:
            statement = statement.where(Relationship.object_id == object_id)
        return self._session.exec(statement).one()

    def get_relationship(self, subject_id: str, predicate: str, object_id: str) -> Optional[Relationship]:
        """
        Get a relationship by its canonical triple (subject_id, predicate, object_id).
        """
        statement = select(Relationship).where(
            Relationship.subject_id == subject_id,
            Relationship.predicate == predicate,
            Relationship.object_id == object_id,
        )
        return self._session.exec(statement).first()

    def get_relationships(self, limit: int = 100, offset: int = 0) -> Sequence[Relationship]:
        """
        List all relationships.
        """
        statement = select(Relationship).limit(limit).offset(offset)
        return self._session.exec(statement).all()

    def get_bundle_info(self):
        """
        Get bundle metadata (latest bundle).
        Returns None if no bundle is loaded.
        """
        statement = select(Bundle).order_by(Bundle.created_at.desc()).limit(1)
        return self._session.exec(statement).first()

    def get_mentions_for_entity(self, entity_id: str) -> Sequence[MentionRow]:
        """Return all mention rows for the given entity (bundle provenance)."""
        statement = select(Mention).where(Mention.entity_id == entity_id)
        rows = self._session.exec(statement).all()
        return [
            MentionRow(
                entity_id=r.entity_id,
                document_id=r.document_id,
                section=r.section,
                start_offset=r.start_offset,
                end_offset=r.end_offset,
                text_span=r.text_span,
                context=r.context,
                confidence=r.confidence,
                extraction_method=r.extraction_method,
                created_at=r.created_at,
            )
            for r in rows
        ]

    def get_evidence_for_relationship(self, subject_id: str, predicate: str, object_id: str) -> Sequence[EvidenceRow]:
        """Return all evidence rows for the given relationship triple (bundle provenance)."""
        rel_key = f"{subject_id}:{predicate}:{object_id}"
        statement = select(BundleEvidence).where(BundleEvidence.relationship_key == rel_key)
        rows = self._session.exec(statement).all()
        return [
            EvidenceRow(
                relationship_key=r.relationship_key,
                document_id=r.document_id,
                section=r.section,
                start_offset=r.start_offset,
                end_offset=r.end_offset,
                text_span=r.text_span,
                confidence=r.confidence,
                supports=r.supports,
            )
            for r in rows
        ]

    def close(self) -> None:
        """
        Close connections and clean up resources.
        """
        self._session.close()
