"""HTTP client for the pluggable domain service.

The domain service is a separate microservice that implements domain-specific
logic: authority lookup (e.g. UMLS, DBPedia), survivor selection during merge,
and synonym similarity thresholds per entity type.

The identity server calls the domain service via HTTP so that domain logic can
change without redeploying the identity server. If the domain service is
unreachable, all methods degrade gracefully to sensible defaults:
  - ``resolve_authority`` → None (entity stays provisional)
  - ``select_survivor`` → candidate with highest usage_count (first if tied)
  - ``synonym_criteria`` → 0.90
"""

import logging
import os
from typing import Optional

import httpx

from .models import DomainCanonicalId, DomainCandidateEntity, DomainResolveAuthorityRequest, DomainSelectSurvivorRequest, DomainSynonymCriteriaRequest

logger = logging.getLogger(__name__)

#: Default similarity threshold used when the domain service is unreachable.
_DEFAULT_SIMILARITY_THRESHOLD = 0.90


class DomainClient:
    """HTTP client that calls the domain service.

    Parameters
    ----------
    base_url:
        Base URL of the domain service.  Reads ``DOMAIN_SERVICE_URL`` from the
        environment; defaults to ``http://domain-stub:8080``.
    timeout:
        HTTP request timeout in seconds.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0) -> None:
        self._base_url = base_url or os.environ.get("DOMAIN_SERVICE_URL", "http://domain-stub:8080")
        self._timeout = timeout

    async def resolve_authority(self, mention: str, entity_type: str, document_id: str) -> Optional[DomainCanonicalId]:
        """Ask the domain service whether this mention has a canonical ID.

        Parameters
        ----------
        mention:
            Surface form of the entity mention.
        entity_type:
            Domain-specific entity type hint.
        document_id:
            Source document identifier.

        Returns
        -------
        Optional[DomainCanonicalId]
            The canonical ID from the authority source, or ``None`` if no match
            was found or the domain service is unreachable.
        """
        payload = DomainResolveAuthorityRequest(mention=mention, entity_type=entity_type, document_id=document_id)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = client.post(f"{self._base_url}/resolve-authority", json=payload.model_dump())
                resp = await resp if hasattr(resp, "__await__") else resp  # type: ignore[assignment]
        except Exception:
            logger.debug("DomainClient.resolve_authority: domain service unreachable, defaulting to None", exc_info=True)
            return None

        try:
            resp.raise_for_status()
            data = resp.json()
            cid_data = data.get("canonical_id")
            if cid_data is None:
                return None
            return DomainCanonicalId(**cid_data)
        except Exception:
            logger.debug("DomainClient.resolve_authority: unexpected response; defaulting to None", exc_info=True)
            return None

    async def select_survivor(self, candidates: list[DomainCandidateEntity]) -> str:
        """Ask the domain service which candidate should survive a merge.

        Parameters
        ----------
        candidates:
            All entities being considered for merge.

        Returns
        -------
        str
            The entity ID of the chosen survivor.  Falls back to the candidate
            with the highest ``usage_count`` (first if tied) if the domain
            service is unreachable.
        """
        payload = DomainSelectSurvivorRequest(candidates=candidates)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self._base_url}/select-survivor", json=payload.model_dump())
            resp.raise_for_status()
            return resp.json()["survivor_id"]
        except Exception:
            logger.debug("DomainClient.select_survivor: domain service unreachable; falling back to highest usage_count", exc_info=True)
            best = max(candidates, key=lambda c: c.usage_count)
            return best.entity_id

    async def synonym_criteria(self, entity_type: str) -> float:
        """Fetch the cosine similarity threshold for synonym detection.

        Parameters
        ----------
        entity_type:
            Domain-specific entity type.

        Returns
        -------
        float
            Minimum cosine similarity threshold.  Defaults to 0.90 if the
            domain service is unreachable.
        """
        payload = DomainSynonymCriteriaRequest(entity_type=entity_type)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self._base_url}/synonym-criteria", json=payload.model_dump())
            resp.raise_for_status()
            return float(resp.json()["similarity_threshold"])
        except Exception:
            logger.debug("DomainClient.synonym_criteria: domain service unreachable; defaulting to %.2f", _DEFAULT_SIMILARITY_THRESHOLD, exc_info=True)
            return _DEFAULT_SIMILARITY_THRESHOLD
