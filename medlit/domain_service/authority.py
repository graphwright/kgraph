"""Authority lookup wrapper for the medlit domain service.

Wraps ``medlit.pipeline.authority_lookup.CanonicalIdLookup`` with:
- The ``_AUTHORITY_TYPE_OVERRIDES`` remapping from ``MedLitPromotionPolicy``
  (hormone→drug, enzyme→protein, biomarker→disease) so the right ontology
  is used for each entity type.
- The LOOKUP_BLOCKLIST check (generic/type-like terms never sent to APIs).
- Persistent on-disk JSON cache via ``JsonFileCanonicalIdCache``.

The lookup instance is a module-level singleton so the cache is shared across
all requests in a single process.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from medlit.pipeline.authority_lookup import CanonicalIdLookup, LOOKUP_BLOCKLIST
from medlit.pipeline.canonical_urls import build_canonical_url

from .models import AuthorityInfo, CanonicalIdResponse

logger = logging.getLogger(__name__)

# Entity types that should be looked up under a different authority.
# Mirrors MedLitPromotionPolicy._AUTHORITY_TYPE_OVERRIDES.
_AUTHORITY_TYPE_OVERRIDES: dict[str, str] = {
    "hormone": "drug",
    "enzyme": "protein",
    "biomarker": "disease",
}

_lookup: Optional[CanonicalIdLookup] = None


_AUTHORITY_METADATA: tuple[AuthorityInfo, ...] = (
    AuthorityInfo(
        name="UMLS",
        entity_types=frozenset({"disease", "symptom", "procedure", "biomarker"}),
        base_url="https://uts-ws.nlm.nih.gov/rest",
        requires_api_key=True,
    ),
    AuthorityInfo(
        name="MeSH",
        entity_types=frozenset({"disease", "symptom", "procedure"}),
        base_url="https://id.nlm.nih.gov/mesh",
        requires_api_key=False,
    ),
    AuthorityInfo(
        name="HGNC",
        entity_types=frozenset({"gene"}),
        base_url="https://rest.genenames.org",
        requires_api_key=False,
    ),
    AuthorityInfo(
        name="RxNorm",
        entity_types=frozenset({"drug", "hormone"}),
        base_url="https://rxnav.nlm.nih.gov/REST",
        requires_api_key=False,
    ),
    AuthorityInfo(
        name="UniProt",
        entity_types=frozenset({"protein", "enzyme"}),
        base_url="https://rest.uniprot.org",
        requires_api_key=False,
    ),
    AuthorityInfo(
        name="ROR",
        entity_types=frozenset({"institution"}),
        base_url="https://api.ror.org",
        requires_api_key=False,
    ),
    AuthorityInfo(
        name="ORCID",
        entity_types=frozenset({"author"}),
        base_url="https://pub.orcid.org",
        requires_api_key=False,
    ),
    AuthorityInfo(
        name="DBPedia",
        entity_types=frozenset({"*"}),
        base_url="https://lookup.dbpedia.org/api",
        requires_api_key=False,
    ),
)


def authority_for_entity_type(entity_type: str) -> str:
    """Return the likely backing authority for an entity type."""
    lookup_type = _AUTHORITY_TYPE_OVERRIDES.get(entity_type.lower().strip(), entity_type.lower().strip())
    if lookup_type in {"disease", "symptom", "procedure", "biomarker"}:
        return "UMLS"
    if lookup_type == "gene":
        return "HGNC"
    if lookup_type == "drug":
        return "RxNorm"
    if lookup_type == "protein":
        return "UniProt"
    if lookup_type == "institution":
        return "ROR"
    if lookup_type == "author":
        return "ORCID"
    return "DBPedia"


def get_authorities_info() -> tuple[AuthorityInfo, ...]:
    """Return static authority metadata for diagnostics/observability endpoints."""
    return _AUTHORITY_METADATA


def get_lookup() -> CanonicalIdLookup:
    """Return the module-level CanonicalIdLookup singleton, creating it on first call."""
    global _lookup
    if _lookup is None:
        cache_path = Path(os.environ.get("CANONICAL_ID_CACHE_PATH", "./canonical_id_cache.json"))
        umls_api_key = os.environ.get("UMLS_API_KEY")
        _lookup = CanonicalIdLookup(
            umls_api_key=umls_api_key,
            cache_file=cache_path,
        )
        logger.info("CanonicalIdLookup initialised (cache=%s, umls_key=%s)", cache_path, "set" if umls_api_key else "not set")
    return _lookup


async def resolve_authority(mention: str, entity_type: str) -> Optional[CanonicalIdResponse]:
    """Look up a canonical ID for a mention from medical ontology authorities.

    Parameters
    ----------
    mention:
        Surface form of the entity mention (already normalised by the identity server).
    entity_type:
        Domain entity type (e.g. 'disease', 'gene', 'drug').

    Returns
    -------
    Optional[CanonicalIdResponse]
        Canonical ID if found, ``None`` if the mention has no authority match.
    """
    mention_lower = mention.strip().lower()

    # Block generic terms before hitting the API (avoids "gene" → Gene Autry etc.)
    if mention_lower in LOOKUP_BLOCKLIST:
        logger.debug("resolve_authority: blocklisted term '%s' (%s)", mention, entity_type)
        return None

    # Remap entity type to the correct authority ontology.
    lookup_type = _AUTHORITY_TYPE_OVERRIDES.get(entity_type, entity_type)

    lookup = get_lookup()
    try:
        result = await lookup.lookup(term=mention, entity_type=lookup_type)
    except Exception:
        logger.exception("resolve_authority: lookup failed for '%s' (%s)", mention, entity_type)
        return None

    if result is None:
        return None

    # Build URL if not already present (lookup returns CanonicalId with url set
    # by build_canonical_url, but we rebuild for safety).
    url = result.url or build_canonical_url(result.id, entity_type=lookup_type)
    synonyms = tuple(result.synonyms) if result.synonyms else (mention,)

    return CanonicalIdResponse(
        id=result.id,
        url=url,
        synonyms=synonyms,
        authority=authority_for_entity_type(entity_type),
        confidence=1.0,
    )
