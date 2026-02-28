# The Pipeline

Each stage in detail: **parsing** (and chunking), **extraction** (entity then relationship), **dedup**, **resolution** (to canonical or provisional), and **bundle building**. The framework exposes interfaces for each; domain pipelines (e.g. medlit) implement them.

## Two-pass architecture

The knowledge graph ingestion pipeline uses a **two-pass architecture** to transform raw documents into structured knowledge:

1. **Pass 1 (Entity Extraction)**: Parse documents, extract entity mentions, and resolve them to canonical or provisional entities.
2. **Pass 2 (Relationship Extraction)**: Identify relationships (edges) between resolved entities within each document.

This separation allows the system to build a consistent entity vocabulary before attempting relationship extraction, which improves accuracy and enables cross-document entity linking.

The pipeline consists of pluggable components for parsing, extraction, resolution, and embedding generation. Each component is defined as an abstract interface, allowing domain-specific implementations.

For a complete, real-world example, see the `examples/sherlock` directory.

## Component Interfaces

Each interface is designed to be stateless and async-first, enabling parallel processing and easy testing with mock implementations.

### DocumentParserInterface

Converts raw document bytes into structured `BaseDocument` instances. This is the entry point for document ingestion—the parser handles format detection, content extraction, and metadata identification.

Parsers are responsible for:
- Decoding raw bytes based on content type (UTF-8 text, PDF binary, HTML, etc.)
- Extracting document structure (title, sections, paragraphs)
- Identifying metadata (author, date, source identifiers)
- Normalizing content for downstream extraction

```python
from kgraph.pipeline import DocumentParserInterface
from kgraph.document import BaseDocument

class DocumentParserInterface(ABC):
    async def parse(
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
    ) -> BaseDocument: ...
```

Example implementation using an LLM for structure extraction:

```python
class LLMDocumentParser(DocumentParserInterface):
    def __init__(self, llm_client, document_class: type[BaseDocument]):
        self._llm = llm_client
        self._doc_class = document_class

    async def parse(
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
    ) -> BaseDocument:
        text = raw_content.decode("utf-8")

        # Use LLM to extract structure
        response = await self._llm.complete(
            f"Extract title and sections from this document:\n\n{text}"
        )

        return self._doc_class(
            document_id=str(uuid.uuid4()),
            title=response.title,
            content=text,
            content_type=content_type,
            source_uri=source_uri,
            created_at=datetime.now(timezone.utc),
            metadata={"sections": response.sections},
        )
```

### EntityExtractorInterface

Extracts entity mentions from documents. This is the core of **Pass 1**—identifying text spans that refer to entities of interest.

The extractor produces `EntityMention` objects representing raw extractions that have not yet been resolved to canonical entities. This separation of extraction and resolution allows different strategies for each phase and enables batch processing optimizations.

```python
from kgraph.pipeline import EntityExtractorInterface
from kgraph import EntityMention

class EntityExtractorInterface(ABC):
    async def extract(self, document: BaseDocument) -> list[EntityMention]: ...
```

`EntityMention` captures raw extractions before resolution:

```python
mention = EntityMention(
    text="aspirin",                    # Exact text span
    entity_type="drug",                # Domain-specific type
    start_offset=145,                  # Position in document
    end_offset=152,
    confidence=0.95,                   # Extraction confidence
    context="patients taking aspirin showed...",  # Surrounding text
    metadata={"extraction_model": "gpt-4"},
)
```

Example NER-based extractor:

```python
class SpacyEntityExtractor(EntityExtractorInterface):
    def __init__(self, nlp, type_mapping: dict[str, str]):
        self._nlp = nlp
        self._type_map = type_mapping  # spaCy label -> domain type

    async def extract(self, document: BaseDocument) -> list[EntityMention]:
        doc = self._nlp(document.content)
        mentions = []
        for ent in doc.ents:
            if ent.label_ in self._type_map:
                mentions.append(EntityMention(
                    text=ent.text,
                    entity_type=self._type_map[ent.label_],
                    start_offset=ent.start_char,
                    end_offset=ent.end_char,
                    confidence=0.9,
                ))
        return mentions
```

### EntityResolverInterface

Maps mentions to canonical or provisional entities. Resolution is the critical step that transforms raw text spans into structured knowledge graph nodes.

The resolver must decide whether a mention refers to:
- An **existing canonical entity** already in the knowledge graph
- A **new canonical entity** that can be linked to an external authority (UMLS, DBPedia, etc.)
- A **provisional entity** that requires further evidence before promotion

The returned confidence score enables quality filtering and informs the entity promotion process.

```python
from kgraph.pipeline import EntityResolverInterface
from kgraph.storage import EntityStorageInterface

class EntityResolverInterface(ABC):
    async def resolve(
        self,
        mention: EntityMention,
        existing_storage: EntityStorageInterface,
    ) -> tuple[BaseEntity, float]: ...

    async def resolve_batch(
        self,
        mentions: Sequence[EntityMention],
        existing_storage: EntityStorageInterface,
    ) -> list[tuple[BaseEntity, float]]: ...
```

Resolution strategy:

1. Search existing entities by name/synonym
2. Search by embedding similarity if available
3. Query external authority using `CanonicalIdLookupInterface` (UMLS, DBPedia, etc.)
4. Create provisional entity if no match found

The resolver can use a `CanonicalIdLookupInterface` implementation to look up canonical IDs from external authorities. See [Canonical IDs and Entity Resolution](canonical-ids-and-entity-resolution.md) for details.

```python
class HybridEntityResolver(EntityResolverInterface):
    def __init__(
        self,
        embedding_gen: EmbeddingGeneratorInterface,
        authority_client,  # External ID authority
        entity_factory,    # Creates domain-specific entities
    ):
        self._embedder = embedding_gen
        self._authority = authority_client
        self._factory = entity_factory

    async def resolve(
        self,
        mention: EntityMention,
        existing_storage: EntityStorageInterface,
    ) -> tuple[BaseEntity, float]:
        # Try name match first
        existing = await existing_storage.find_by_name(
            mention.text, mention.entity_type, limit=1
        )
        if existing:
            return existing[0], 0.95

        # Try embedding similarity
        embedding = await self._embedder.generate(mention.text)
        similar = await existing_storage.find_by_embedding(
            embedding, threshold=0.9, limit=1
        )
        if similar:
            return similar[0][0], similar[0][1]

        # Try external authority (using CanonicalIdLookupInterface)
        canonical_id_obj = await self._authority.lookup(
            mention.text, mention.entity_type
        )
        if canonical_id_obj:
            entity = self._factory.create_canonical(
                canonical_id=canonical_id_obj.id,
                name=mention.text,  # Use mention text as name
                entity_type=mention.entity_type,
                embedding=embedding,
            )
            return entity, mention.confidence

        # Create provisional
        entity = self._factory.create_provisional(
            name=mention.text,
            entity_type=mention.entity_type,
            embedding=embedding,
            confidence=mention.confidence,
        )
        return entity, mention.confidence
```

### RelationshipExtractorInterface

Extracts relationships between entities. This is **Pass 2** of the pipeline—identifying the edges that connect entity nodes in the knowledge graph.

Relationship extraction operates on resolved entities, not raw mentions, which enables:
- Consistent entity references across relationships
- Cross-document relationship aggregation
- Confidence scoring based on entity resolution quality

The predicate vocabulary is typically domain-specific (e.g., 'treats', 'causes' for medical; 'cites', 'amends' for legal).

```python
from kgraph.pipeline import RelationshipExtractorInterface

class RelationshipExtractorInterface(ABC):
    async def extract(
        self,
        document: BaseDocument,
        entities: Sequence[BaseEntity],
    ) -> list[BaseRelationship]: ...
```

Example LLM-based extractor:

```python
class LLMRelationshipExtractor(RelationshipExtractorInterface):
    def __init__(self, llm_client, relationship_factory, valid_predicates: list[str]):
        self._llm = llm_client
        self._factory = relationship_factory
        self._predicates = valid_predicates

    async def extract(
        self,
        document: BaseDocument,
        entities: Sequence[BaseEntity],
    ) -> list[BaseRelationship]:
        # Build entity context for LLM
        entity_list = "\n".join(
            f"- {e.name} ({e.get_entity_type()}): {e.entity_id}"
            for e in entities
        )

        prompt = f"""
        Given these entities:
        {entity_list}

        And this document:
        {document.content[:2000]}

        Extract relationships using these predicates: {self._predicates}
        Format: subject_id | predicate | object_id | confidence
        """

        response = await self._llm.complete(prompt)
        return self._parse_relationships(response, document.document_id)
```

### EmbeddingGeneratorInterface

Generates semantic vector embeddings for entity similarity. Embeddings enable:

- **Entity resolution**: Finding existing entities with similar meaning but different surface forms
- **Duplicate detection**: Identifying canonical entities that should be merged
- **Semantic search**: Querying the knowledge graph by meaning rather than exact text

The `dimension` property is critical for storage backends that need to pre-allocate vector columns or configure similarity indices.

```python
from kgraph.pipeline.embedding import EmbeddingGeneratorInterface

class EmbeddingGeneratorInterface(ABC):
    @property
    def dimension(self) -> int: ...

    async def generate(self, text: str) -> tuple[float, ...]: ...

    async def generate_batch(
        self, texts: Sequence[str]
    ) -> list[tuple[float, ...]]: ...
```

Example OpenAI implementation:

```python
class OpenAIEmbedding(EmbeddingGeneratorInterface):
    def __init__(self, client, model: str = "text-embedding-3-small"):
        self._client = client
        self._model = model
        self._dim = 1536  # Model-dependent

    @property
    def dimension(self) -> int:
        return self._dim

    async def generate(self, text: str) -> tuple[float, ...]:
        response = await self._client.embeddings.create(
            model=self._model,
            input=text,
        )
        return tuple(response.data[0].embedding)

    async def generate_batch(
        self, texts: Sequence[str]
    ) -> list[tuple[float, ...]]:
        response = await self._client.embeddings.create(
            model=self._model,
            input=list(texts),
        )
        return [tuple(d.embedding) for d in response.data]
```

## Assembling the Pipeline

The `IngestionOrchestrator` connects all pipeline components and manages the two-pass ingestion workflow. It handles:

- Document parsing and storage
- Pass 1: Entity extraction, resolution, and storage
- Pass 2: Relationship extraction and storage
- Entity promotion (provisional → canonical based on usage thresholds)

Connect components via `IngestionOrchestrator`:

```python
from kgraph import IngestionOrchestrator

orchestrator = IngestionOrchestrator(
    domain=my_domain,
    parser=my_parser,
    entity_extractor=my_entity_extractor,
    entity_resolver=my_resolver,
    relationship_extractor=my_rel_extractor,
    embedding_generator=my_embedder,
    entity_storage=entity_storage,
    relationship_storage=relationship_storage,
    document_storage=document_storage,
)

# Ingest a single document
result = await orchestrator.ingest_document(
    raw_content=document_bytes,
    content_type="text/plain",
    source_uri="https://example.com/doc.txt",
)

# Batch ingestion
results = await orchestrator.ingest_batch([
    (doc1_bytes, "text/plain", "source1"),
    (doc2_bytes, "application/pdf", "source2"),
])

# Run promotion after ingestion
promoted = await orchestrator.run_promotion()
```
