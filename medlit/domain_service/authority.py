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

from .models import CanonicalIdResponse

logger = logging.getLogger(__name__)

# Entity types that should be looked up under a different authority.
# Mirrors MedLitPromotionPolicy._AUTHORITY_TYPE_OVERRIDES.
_AUTHORITY_TYPE_OVERRIDES: dict[str, str] = {
    "hormone": "drug",
    "enzyme": "protein",
    "biomarker": "disease",
}

_lookup: Optional[CanonicalIdLookup] = None


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
    synonyms = list(result.synonyms) if result.synonyms else [mention]

    return CanonicalIdResponse(id=result.id, url=url, synonyms=synonyms)
