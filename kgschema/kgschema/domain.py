"""Domain schema definition for the knowledge graph framework.

A domain schema defines the vocabulary and rules for a specific knowledge
domain (medical literature, legal documents, academic CS papers, etc.).
Each domain specifies:

- **Entity types**: The kinds of entities that can exist (drugs, diseases,
  legal cases, algorithms, etc.) and their concrete class implementations.

- **Relationship types**: Valid predicates between entities (treats, cites,
  implements, etc.) and their class implementations.

- **Document types**: Source document formats the domain processes (journal
  articles, court filings, conference papers, etc.).

- **Validation rules**: Domain-specific constraints on entities and
  relationships beyond basic type checking.

- **Promotion configuration**: Thresholds for promoting provisional entities
  to canonical status, which may vary by domain based on data quality and
  external authority availability.

The domain schema serves as the central configuration point for domain-specific
behavior, allowing the core knowledge graph framework to remain domain-agnostic
while supporting specialized use cases.

Example usage:
    ```python
    class MedicalDomainSchema(DomainSchema):
        @property
        def name(self) -> str:
            return "medical"

        @property
        def entity_types(self) -> dict[str, type[BaseEntity]]:
            return {"drug": DrugEntity, "disease": DiseaseEntity, "gene": GeneEntity}

        @property
        def relationship_types(self) -> dict[str, type[BaseRelationship]]:
            return {"treats": TreatsRelationship, "causes": CausesRelationship}
        # ... etc
    ```
"""

import logging
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, model_validator

from kgschema.document import BaseDocument
from kgschema.entity import BaseEntity, PromotionConfig
from kgschema.promotion import PromotionPolicy
from kgschema.relationship import BaseRelationship
from kgschema.storage import EntityStorageInterface

logger = logging.getLogger(__name__)


class ValidationIssue(BaseModel, frozen=True):
    """A structured validation error with location and diagnostic information.

    Provides detailed information about why validation failed, enabling
    better error messages and programmatic handling of validation failures.

    Attributes:
        field: The field that failed validation (e.g., "entity_type", "confidence")
        message: Human-readable description of the issue
        value: The invalid value (optional, for debugging)
        code: Machine-readable error code (optional, for programmatic handling)
    """

    field: str = Field(description="The field or location that failed validation")
    message: str = Field(description="Human-readable description of the validation issue")
    value: str | None = Field(default=None, description="The invalid value (as string for display)")
    code: str | None = Field(default=None, description="Machine-readable error code")


class PredicateConstraint(BaseModel, frozen=True):
    """Defines the valid subject and object entity types for a predicate."""

    subject_types: set[str] = Field(default_factory=set, description="Set of valid subject entity types")
    object_types: set[str] = Field(default_factory=set, description="Set of valid object entity types")

    @model_validator(mode="after")
    def check_not_empty(self) -> "PredicateConstraint":
        if not self.subject_types:
            raise ValueError("PredicateConstraint must specify at least one subject type")
        if not self.object_types:
            raise ValueError("PredicateConstraint must specify at least one object type")
        return self


class Provenance(BaseModel, frozen=True):
    """Tracks the precise location of extracted information within a document.

    Used to record where entities, relationships, and other extracted data
    originated, enabling traceability back to source text.

    Fields:
        document_id: Unique identifier of the source document
        source_uri: Optional URI/path to the original document
        section: Name of the document section (e.g., "abstract", "methods", "results")
        paragraph: Paragraph number/index within the section (0-based)
        start_offset: Character offset where the relevant text begins
        end_offset: Character offset where the relevant text ends
    """

    document_id: str = Field(description="Unique identifier of the source document")
    source_uri: str | None = Field(default=None, description="Optional URI/path to the original document")
    section: str | None = Field(default=None, description="Document section name (e.g., 'abstract', 'methods', 'results')")
    paragraph: int | None = Field(default=None, description="Paragraph number/index within the section (0-based)", ge=0)
    start_offset: int | None = Field(default=None, description="Character offset where the relevant text begins", ge=0)
    end_offset: int | None = Field(default=None, description="Character offset where the relevant text ends", ge=0)


class Evidence(BaseModel, frozen=True):
    kind: str
    source_documents: tuple[str, ...] = Field(min_length=1)
    primary: Provenance | None = None
    mentions: tuple[Provenance, ...] = ()
    notes: dict[str, object] = Field(default_factory=dict)


class DomainSchema(ABC):
    """Abstract schema definition for a knowledge domain.

    Each domain (medical, legal, CS papers, etc.) implements this interface
    to define its vocabulary of types and validation rules. The schema is
    used throughout the ingestion pipeline to:

    - Validate extracted entities and relationships before storage
    - Configure entity promotion thresholds
    - Determine valid predicates between entity type pairs
    - Deserialize domain-specific entity/relationship subclasses

    Implementations should be stateless and thread-safe, as the same schema
    instance may be used across multiple concurrent ingestion operations.

    Required methods to implement:
        - name: Unique domain identifier
        - entity_types: Registry of entity type names to classes
        - relationship_types: Registry of predicate names to classes
        - document_types: Registry of document format names to classes
        - validate_entity: Domain-specific entity validation
        - validate_relationship: Domain-specific relationship validation

    Optional methods to override:
        - promotion_config: Customize promotion thresholds
        - get_valid_predicates: Restrict predicates by entity type pair
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique identifier for this domain.

        The domain name is used for:
            - Namespacing entities in multi-domain deployments
            - Selecting the correct deserializer for stored data
            - Logging and debugging

        Returns:
            A short, lowercase identifier (e.g., 'medical', 'legal', 'cs_papers').
            Should contain only alphanumeric characters and underscores.
        """

    @property
    @abstractmethod
    def entity_types(self) -> dict[str, type[BaseEntity]]:
        """Return the registry of entity types for this domain.

        Maps type name strings to concrete BaseEntity subclasses. The type
        names are used in entity extraction and must match the values
        returned by each entity's `get_entity_type()` method.

        Returns:
            Dictionary mapping entity type names to their implementing classes.

        Example:
            ```python
            return {
                'drug': DrugEntity,
                'disease': DiseaseEntity,
                'gene': GeneEntity,
            }
            ```
        """

    @property
    @abstractmethod
    def relationship_types(self) -> dict[str, type[BaseRelationship]]:
        """Return the registry of relationship types for this domain.

        Maps predicate name strings to concrete BaseRelationship subclasses.
        The predicate names define the vocabulary of edges in the knowledge
        graph and must match the values used in relationship extraction.

        Returns:
            Dictionary mapping predicate names to their implementing classes.

        Example:
            ```python
            return {
                'treats': TreatsRelationship,
                'causes': CausesRelationship,
                'interacts_with': InteractionRelationship,
            }
            ```
        """

    @property
    @abstractmethod
    def predicate_constraints(self) -> dict[str, PredicateConstraint]:
        """Return a dictionary of predicate constraints for this domain.

        This maps predicate names to a PredicateConstraint object, which
        defines the valid subject and object entity types for that predicate.
        These constraints are used to validate relationships during ingestion
        and to filter valid predicates for a given subject-object pair.

        Returns:
            Dictionary mapping predicate names (e.g., "treats") to
            PredicateConstraint instances.

        Example:
            ```python
            return {
                "treats": PredicateConstraint(
                    subject_types={"drug", "procedure"},
                    object_types={"disease", "symptom"},
                ),
                "causes": PredicateConstraint(
                    subject_types={"gene", "exposure"},
                    object_types={"disease"},
                ),
            }
            ```
        """

    @property
    @abstractmethod
    def document_types(self) -> dict[str, type[BaseDocument]]:
        """Return the registry of document types for this domain.

        Maps document format names to concrete BaseDocument subclasses.
        Different document types may have different structures and metadata
        fields relevant to the domain.

        Returns:
            Dictionary mapping document type names to their implementing classes.

        Example:
            ```python
            return {
                'journal_article': JournalArticle,
                'clinical_trial': ClinicalTrialDocument,
                'drug_label': DrugLabelDocument,
            }
            ```
        """

    @property
    def promotion_config(self) -> PromotionConfig:
        """Return the configuration for promoting provisional entities.

        Promotion configuration controls when provisional entities (newly
        discovered mentions without canonical IDs) are promoted to canonical
        status. The thresholds should be tuned based on:

        - Data quality: Noisy extraction requires higher thresholds
        - External authority availability: Domains with good authorities
          (UMLS, Wikidata) can use higher confidence requirements
        - Entity importance: Critical domains may require more evidence

        Override this property to customize thresholds for your domain.
        The default configuration uses framework defaults.

        Returns:
            PromotionConfig with min_usage_count, min_confidence, and
            require_embedding settings appropriate for this domain.
        """
        return PromotionConfig()

    @abstractmethod
    def validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]:
        """Validate an entity against domain-specific rules.

        Called by the ingestion pipeline before storing an entity. Use this
        to enforce constraints beyond basic type checking, such as:

        - Required fields for specific entity types
        - Value constraints (e.g., confidence thresholds)
        - Cross-field validation (e.g., canonical entities must have IDs)

        Args:
            entity: The entity to validate.

        Returns:
            Empty list if the entity is valid, otherwise a list of ValidationIssue
            objects describing each validation failure. Multiple issues can be
            returned to help users fix all problems at once.

        Example:
            ```python
            def validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]:
                issues = []
                if entity.get_entity_type() not in self.entity_types:
                    issues.append(ValidationIssue(
                        field="entity_type",
                        message=f"Unknown entity type: {entity.get_entity_type()}",
                        value=entity.get_entity_type(),
                        code="UNKNOWN_TYPE",
                    ))
                return issues
            ```

        Note:
            At minimum, implementations should verify that the entity's type
            (from `get_entity_type()`) is registered in `entity_types`.
        """

    async def validate_relationship(
        self,
        relationship: BaseRelationship,
        entity_storage: EntityStorageInterface | None = None,
    ) -> bool:
        """Validate a relationship against domain-specific rules.

        This method first performs predicate constraint validation using the
        `predicate_constraints` defined by the domain. If the relationship's
        subject or object types do not conform to the constraints for its
        predicate, a warning is logged, and the relationship is considered invalid.

        If an `entity_storage` is provided, it will be used to look up the
        subject and object entities to determine their types. Otherwise,
        it will attempt to infer types directly from the relationship object
        (e.g., for testing or when entities are not yet stored).

        Subclasses can override this method to add further domain-specific
        validation logic. It is recommended to call `super().validate_relationship()`
        to ensure base predicate constraints are checked.

        Args:
            relationship: The relationship to validate.
            entity_storage: Optional entity storage to look up subject/object types.

        Returns:
            True if the relationship is valid for this domain, False otherwise.
        """
        if relationship.predicate not in self.relationship_types:
            logger.warning("Relationship predicate '%s' is not registered in domain '%s'. Relationship: %s", relationship.predicate, self.name, relationship)
            return False

        # Determine subject and object types for validation
        subject_type: str | None = None
        object_type: str | None = None

        if entity_storage:
            # Use entity storage to get actual entity types
            try:
                subject_entity = await entity_storage.get(relationship.subject_id)
                object_entity = await entity_storage.get(relationship.object_id)
                if subject_entity:
                    subject_type = subject_entity.get_entity_type()
                if object_entity:
                    object_type = object_entity.get_entity_type()
            except Exception as e:
                logger.debug("Error fetching entities from storage for relationship validation: %s", e)
                # Fallback to direct access if storage lookup fails
                subject_type = getattr(relationship, "subject_entity_type", None)
                object_type = getattr(relationship, "object_entity_type", None)
        else:
            # Attempt to get entity types directly from relationship object (e.g., for mock relationships)
            subject_type = getattr(relationship, "subject_entity_type", None)
            object_type = getattr(relationship, "object_entity_type", None)

        if subject_type is None or object_type is None:
            logger.warning("Could not determine subject_type or object_type for relationship %s in domain '%s'. Skipping type validation.", relationship, self.name)
            return True  # Allow for now if types can't be determined

        # Perform predicate constraint validation
        if relationship.predicate in self.predicate_constraints:
            constraints = self.predicate_constraints[relationship.predicate]

            # Check if types match as-is
            subject_valid = subject_type in constraints.subject_types
            object_valid = object_type in constraints.object_types

            if not subject_valid or not object_valid:
                # Types don't match - check if swapping would help
                swapped_subject_valid = object_type in constraints.subject_types
                swapped_object_valid = subject_type in constraints.object_types

                if swapped_subject_valid and swapped_object_valid:
                    # Swapping would fix the type mismatch - log a helpful message
                    logger.warning(
                        "Type mismatch for predicate '%s' in domain '%s': "
                        "Subject type='%s' and Object type='%s' appear to be reversed. "
                        "Expected subject types: %s, object types: %s. "
                        "Swapping would fix this. Relationship: %s",
                        relationship.predicate,
                        self.name,
                        subject_type,
                        object_type,
                        constraints.subject_types,
                        constraints.object_types,
                        relationship,
                    )
                    return False
                else:
                    # Neither original nor swapped work - log standard error
                    if not subject_valid:
                        logger.warning(
                            "Invalid subject type for predicate '%s' in domain '%s': Got '%s', expected one of %s. Relationship: %s",
                            relationship.predicate,
                            self.name,
                            subject_type,
                            constraints.subject_types,
                            relationship,
                        )
                    if not object_valid:
                        logger.warning(
                            "Invalid object type for predicate '%s' in domain '%s': Got '%s', expected one of %s. Relationship: %s",
                            relationship.predicate,
                            self.name,
                            object_type,
                            constraints.object_types,
                            relationship,
                        )
                    return False
        else:
            logger.debug("No predicate constraints defined for '%s' in domain '%s'. Skipping type validation.", relationship.predicate, self.name)

        return True

    def get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]:
        """Return predicates valid between two entity types.

        Override this method to enforce type-specific relationship constraints.
        For example, in a medical domain, "treats" might only be valid from
        Drug to Disease, not from Disease to Drug.

        The default implementation allows any predicate registered in
        `relationship_types` between any entity type pair.

        Args:
            subject_type: The entity type of the relationship subject.
            object_type: The entity type of the relationship object.

        Returns:
            List of predicate names that are valid for this entity type pair.
            Returns an empty list if no predicates are valid.

        Example:
            ```python
            def get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]:
                if subject_type == "drug" and object_type == "disease":
                    return ["treats", "prevents", "exacerbates"]
                if subject_type == "gene" and object_type == "disease":
                    return ["associated_with", "causes"]
                return []  # No other combinations allowed
            ```
        """
        return list(self.relationship_types.keys())

    def normalize_mention(self, mention: str) -> str:
        """Normalize a mention string before identity resolution.

        Called by the identity server before ``resolve()`` to apply
        domain-specific string normalization (e.g. spelling variants,
        case folding, abbreviation expansion).

        The default implementation returns the mention unchanged.
        Override in domain subclasses to apply domain-specific rules.

        Parameters
        ----------
        mention:
            Raw surface form of the entity mention.

        Returns
        -------
        str
            Normalized mention string.
        """
        return mention

    @abstractmethod
    def get_promotion_policy(self, lookup=None) -> PromotionPolicy:
        """Return the promotion policy for this domain.

        Override this method to provide domain-specific promotion logic.
        Default implementation raises NotImplementedError.

        Args:
            lookup: Optional canonical ID lookup service. Domains that support
                   external lookups can use this to pass the service to the policy.
        """

    @abstractmethod
    def preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity:
        """Return the preferred survivor when merging a set of synonym candidates.

        Called by the identity server's ``on_entity_added`` hook after
        ``find_synonyms`` returns candidates. The domain implements its own
        preference rules, for example:

        - Prefer canonical over provisional (a canonical entity already has a
          stable external ID and should not be displaced by a provisional one)
        - Among entities of equal status, prefer the one with the highest
          ``usage_count`` (more evidence)
        - Prefer the entity with an authoritative ``canonical_ids`` entry
          (e.g. a UMLS CUI or MeSH term) over one without

        The returned entity must be a member of ``candidates``. The caller
        passes its ``entity_id`` as ``survivor_id`` to ``IdentityServer.merge``.

        Parameters
        ----------
        candidates:
            Non-empty list of entities identified as synonyms. Guaranteed to
            contain at least two elements when called from ``on_entity_added``.

        Returns
        -------
        BaseEntity
            The entity that should survive the merge.
        """

    @property
    def evidence_model(self) -> type[Evidence]:
        """Return the domain's version of Evidence

        The domain can add stuff to the evidence:
            - A predicate might be supported (or counter-argued) by lab data or test results
            - Or by whether some paper from the past was retracted or not

        Returns:
            A type that is, or is a subclass of, the Evidence type
        """
        return Evidence

    @property
    def provenance_model(self) -> type[Provenance]:
        """Return the domain's version of Provenance

        The domain can add stuff to the provenance, much like Evidence

        Returns:
            A type that is, or is a subclass of, the Provenance type
        """
        return Provenance
