"""Pipeline components for medical literature extraction."""

from .authority_lookup import CanonicalIdLookup
from kgraph.pipeline.llm_client import LLMClientInterface, OllamaLLMClient
from kgraph.pipeline.ollama_embedding import OllamaEmbeddingGenerator

# Backward compatibility alias
OllamaMedLitEmbeddingGenerator = OllamaEmbeddingGenerator
from .mentions import MedLitEntityExtractor
from .ner_extractor import MedLitNEREntityExtractor
from .parser import JournalArticleParser
from .relationships import MedLitRelationshipExtractor
from .resolve import MedLitEntityResolver

__all__ = [
    "CanonicalIdLookup",
    "JournalArticleParser",
    "MedLitEntityExtractor",
    "MedLitEntityResolver",
    "MedLitNEREntityExtractor",
    "MedLitRelationshipExtractor",
    "OllamaMedLitEmbeddingGenerator",
    "LLMClientInterface",
    "OllamaLLMClient",
]
