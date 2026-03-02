"""Canonical ID lookup from medical ontology authorities.

Provides lookup functionality for canonical IDs from various medical ontology
sources: UMLS, HGNC, RxNorm, and UniProt.

Features persistent caching to avoid repeated API calls across runs.
"""

import os
from pathlib import Path
from typing import Any, Optional, List

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment, misc]

from kgraph.canonical_id import (
    CanonicalId,
    CanonicalIdLookupInterface,
    JsonFileCanonicalIdCache,
)
from kgraph.logging import setup_logging
from kgraph.storage.memory import _cosine_similarity

from .canonical_urls import build_canonical_url

# Terms that are entity-type words or generic concepts; never look up in authorities.
# (e.g. "gene" must not resolve to Gene Autry; "variant" not to SARS-CoV-2 Omicron variant)
LOOKUP_BLOCKLIST = frozenset(
    {
        "gene",
        "disease",
        "drug",
        "protein",
        "symptom",
        "procedure",
        "biomarker",
        "pathway",
        "location",
        "ethnicity",
        "variant",
        "diseases",
        "genes",
        "drugs",
        "proteins",
        "symptoms",
        "procedures",
        "biomarkers",
        "pathways",
        "variants",
        "pathogenic variant",
        "loss-of-function variant",
        "genetic variant",
        "germline variant",
        "somatic variant",
        "sequence variant",
        "gene variant",
    }
)

# Module-level logger for sync methods
logger = setup_logging()

# UMLS semantic type group -> allowed entity types (lowercase) for validate_umls_type.
# Used to catch misclassifications (e.g. cortisol as gene when it is a hormone/drug).
UMLS_SEMANTIC_TYPE_TO_ENTITY_TYPES: dict[str, list[str]] = {
    "Pharmacologic Substance": ["drug"],
    "Clinical Drug": ["drug"],
    "Disease or Syndrome": ["disease", "symptom", "adverseevent"],
    "Finding": ["disease", "symptom", "adverseevent"],
    "Gene or Genome": ["gene"],
    "Amino Acid, Peptide, or Protein": ["protein", "biomarker"],
    "Biologic Function": ["biologicalprocess"],
    "Body Part, Organ, or Organ Component": ["anatomicalstructure"],
    "Body Part": ["anatomicalstructure"],
    "Organ": ["anatomicalstructure"],
    "Diagnostic Procedure": ["procedure"],
    "Therapeutic or Preventive Procedure": ["procedure"],
    "Laboratory Procedure": ["procedure", "biomarker"],
    "Quantitative Concept": ["biomarker"],
    "Steroid": ["drug", "biomarker"],
    "Hormone": ["drug", "biomarker"],
}


def validate_umls_type(
    umls_id: str,
    assigned_type: str,
    _cache: dict[tuple[str, str], tuple[bool, str | None]] | None = None,
    _semantic_types_override: dict[str, list[str]] | None = None,
) -> tuple[bool, str | None]:
    """Return (ok, correct_type_if_known).

    Looks up the UMLS semantic type(s) for the CUI and checks whether assigned_type
    is compatible. Returns (False, expected_type) when assigned_type is incompatible
    and the mapping is unambiguous; (True, None) when compatible; (False, None) when
    ambiguous (multiple allowed types). Uses in-memory cache keyed by (umls_id,
    assigned_type) so each CUI is looked up at most once per run when cache is passed.
    For tests, pass _semantic_types_override mapping CUI -> list of semantic type names
    to avoid live API calls.
    """
    cache = _cache if _cache is not None else {}
    key = (umls_id.strip(), assigned_type.strip().lower())
    if key in cache:
        return cache[key]

    # Strip CUI prefix if present (e.g. "C0020268" or "CUI:C0020268")
    cui = umls_id.strip().replace("CUI:", "").upper()
    if not cui.startswith("C") or len(cui) < 2:
        cache[key] = (True, None)
        return (True, None)

    type_names: List[str]
    if _semantic_types_override is not None:
        type_names = _semantic_types_override.get(cui) or []
    else:
        api_key = os.getenv("UMLS_API_KEY")
        if not api_key:
            cache[key] = (True, None)
            return (True, None)

        try:
            import httpx as _httpx

            with _httpx.Client(timeout=10.0) as client:
                url = f"https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui}"
                resp = client.get(url, params={"apiKey": api_key})
                if resp.status_code != 200:
                    cache[key] = (True, None)
                    return (True, None)
                data = resp.json()
        except Exception as e:
            logger.warning(
                {"message": "UMLS semantic type lookup failed", "umls_id": umls_id, "error": str(e)},
                pprint=True,
            )
            cache[key] = (True, None)
            return (True, None)

        semantic_types = data.get("semanticTypes") or []
        type_names = [st.get("name", "?") for st in semantic_types if isinstance(st, dict) and st.get("name")]
    if not type_names:
        cache[key] = (True, None)
        return (True, None)

    allowed: set[str] = set()
    for st_name in type_names:
        for entity_type in UMLS_SEMANTIC_TYPE_TO_ENTITY_TYPES.get(st_name, []):
            allowed.add(entity_type)

    if not allowed:
        cache[key] = (True, None)
        return (True, None)

    assigned_lower = assigned_type.strip().lower()
    if assigned_lower in allowed:
        cache[key] = (True, None)
        return (True, None)

    # Unambiguous: one allowed type -> suggest it
    if len(allowed) == 1:
        correct = next(iter(allowed))
        cache[key] = (False, correct)
        return (False, correct)
    # Ambiguous: multiple allowed types
    cache[key] = (False, None)
    return (False, None)


class CanonicalIdLookup(CanonicalIdLookupInterface):
    """Look up canonical IDs from various medical ontology authorities.

    Supports lookup from:
    - UMLS (diseases, symptoms, procedures)
    - HGNC (genes)
    - RxNorm (drugs)
    - UniProt (proteins)

    Features persistent caching to disk to avoid repeated API calls across runs.
    """

    def __init__(
        self,
        umls_api_key: Optional[str] = None,
        cache_file: Optional[Path] = None,
        embedding_generator: Any = None,
        similarity_threshold: float = 0.5,
    ):
        """Initialize the canonical ID lookup service.

        Args:
            umls_api_key: Optional UMLS API key. If not provided, will try to
                         read from UMLS_API_KEY environment variable.
            cache_file: Optional path to cache file. If not provided, defaults
                       to "canonical_id_cache.json" in current directory.
            embedding_generator: Optional; if set, used to rerank multiple candidates
                                (UMLS/MeSH) by cosine similarity to the search term.
                                Must have async generate(text: str) -> tuple[float, ...].
            similarity_threshold: Min cosine similarity when using embedding rerank (0-1).
        """
        if httpx is None:
            raise ImportError("httpx is required for authority lookup. Install with: uv add httpx")

        self.client = httpx.AsyncClient(timeout=10.0)
        self.umls_api_key = umls_api_key or os.getenv("UMLS_API_KEY")
        self.cache_file = cache_file or Path("canonical_id_cache.json")
        self._embedding_generator = embedding_generator
        self._similarity_threshold = similarity_threshold
        self._cache = JsonFileCanonicalIdCache(cache_file=self.cache_file)
        self._cache.load(str(self.cache_file))
        self._lookup_count = 0  # Track lookups for periodic saves

    def _save_cache(self, force: bool = False) -> None:
        """Save cache to disk.

        Args:
            force: If True, save even if cache is not marked dirty (for emergency saves).
        """
        self._cache.save(str(self.cache_file))

    async def lookup(self, term: str, entity_type: str) -> Optional[CanonicalId]:
        """Look up canonical ID for a medical term (interface method).

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (disease, gene, drug, protein, etc.)

        Returns:
            CanonicalId if found, None otherwise
        """
        canonical_id_str = await self.lookup_canonical_id(term, entity_type)
        if canonical_id_str:
            url = build_canonical_url(canonical_id_str, entity_type=entity_type)
            return CanonicalId(id=canonical_id_str, url=url, synonyms=(term,))
        return None

    async def lookup_canonical_id(self, term: str, entity_type: str) -> Optional[str]:
        """Look up canonical ID for a medical term.

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (disease, gene, drug, protein, etc.)

        Returns:
            Canonical ID string if found, None otherwise
        """
        logger = setup_logging()

        term_normalized = term.strip().lower()

        # Never look up generic/type-like terms (avoids "gene" → Gene Autry, "variant" → SARS-CoV-2 Omicron).
        # Check before cache so we never return a cached wrong result for these.
        if term_normalized in LOOKUP_BLOCKLIST:
            logger.debug(
                {
                    "message": f"Blocklisted generic term '{term}' ({entity_type}), skipping lookup",
                    "term": term,
                    "entity_type": entity_type,
                },
                pprint=True,
            )
            self._cache.mark_known_bad(term, entity_type)
            return None

        # Check cache
        cached = self._cache.fetch(term, entity_type)
        if cached is not None:
            logger.debug(
                {
                    "message": f"Cache hit for {term} ({entity_type})",
                    "cached_id": cached.id,
                },
                pprint=True,
            )
            return cached.id

        # Check if known bad
        if self._cache.is_known_bad(term, entity_type):
            logger.debug(
                {
                    "message": f"Known bad entry for '{term}' ({entity_type}), skipping lookup",
                    "term": term,
                    "entity_type": entity_type,
                },
                pprint=True,
            )
            return None

        logger.debug(
            {
                "message": f"Cache miss for '{term}' (type: {entity_type}), looking up",
                "term": term,
                "entity_type": entity_type,
            },
            pprint=True,
        )

        # Route to appropriate authority based on entity type
        canonical_id_str: Optional[str] = None

        skip_dbpedia = False
        if entity_type in ("disease", "symptom", "procedure"):
            if term.isupper() and len(term) < 5:
                # looks like an acronym
                skip_dbpedia = True
                # if term == "FAP":
                #    # canonical_id_str = "MeSH:D011125"
                #    canonical_id_str = "D011125"
            else:
                canonical_id_str = await self._lookup_umls(term)
        elif entity_type == "gene":
            canonical_id_str = await self._lookup_hgnc(term)
            # Do not fall back to DBPedia for genes: it returns wrong matches (e.g. "gene" → Gene
            # Autry, "variant" → SARS-CoV-2_Omicron_variant). Viral variants would need a proper
            # source (e.g. GISAID, WHO/Pango nomenclature) if we add variant support later.
            skip_dbpedia = True
        elif entity_type == "drug":
            canonical_id_str = await self._lookup_rxnorm(term)
        elif entity_type == "protein":
            canonical_id_str = await self._lookup_uniprot(term)

        # Fallback to DBPedia for any entity type if specialized lookup failed
        if canonical_id_str is None and not skip_dbpedia:
            dbpedia_result = await self._lookup_dbpedia(term)
            if dbpedia_result:
                # Try to extract authoritative ID from DBPedia properties
                authoritative_id = await self._extract_authoritative_id_from_dbpedia(dbpedia_result, entity_type, term)
                canonical_id_str = authoritative_id if authoritative_id else dbpedia_result

        # Build CanonicalId object with URL
        if canonical_id_str:
            url = build_canonical_url(canonical_id_str, entity_type=entity_type)
            canonical_id = CanonicalId(id=canonical_id_str, url=url, synonyms=(term,))
            self._cache.store(term, entity_type, canonical_id)
            logger.info(
                {
                    "message": f"Found canonical ID for '{term}': {canonical_id_str}",
                    "term": term,
                    "entity_type": entity_type,
                    "canonical_id": canonical_id_str,
                    "url": url,
                },
                pprint=True,
            )
        else:
            # Mark as known bad
            self._cache.mark_known_bad(term, entity_type)
            logger.debug(
                {
                    "message": f"No canonical ID found for '{term}' (type: {entity_type})",
                    "term": term,
                    "entity_type": entity_type,
                },
                pprint=True,
            )

        # Periodically save cache (every 100 new entries to avoid losing work)
        self._lookup_count += 1
        if self._lookup_count % 100 == 0:
            self._save_cache()

        return canonical_id_str

    async def _rerank_by_similarity(
        self,
        term: str,
        candidates: list[tuple[str, str]],
    ) -> Optional[str]:
        """Pick the candidate whose label is most similar to the search term.

        candidates: list of (id, label) e.g. (cui, name) or (mesh_id, label).
        Returns the id of the best candidate above threshold, or None.
        """
        if not self._embedding_generator or not candidates:
            return None
        try:
            term_emb = await self._embedding_generator.generate(term)
            term_vec = term_emb if isinstance(term_emb, tuple) else tuple(term_emb)
            best_id: Optional[str] = None
            best_sim = self._similarity_threshold
            for cand_id, label in candidates:
                label_emb = await self._embedding_generator.generate(label)
                label_vec = label_emb if isinstance(label_emb, tuple) else tuple(label_emb)
                sim = _cosine_similarity(term_vec, label_vec)
                if sim > best_sim:
                    best_sim = sim
                    best_id = cand_id
            return best_id
        except Exception as e:
            logger.warning(
                {"message": "Embedding rerank failed", "term": term, "error": str(e)},
                pprint=True,
            )
            return None

    async def _lookup_umls(self, term: str) -> Optional[str]:
        """Look up UMLS CUI for a disease/symptom term.

        Tries exact match first, then words match for broader candidates.
        When multiple results and embedding_generator is set, reranks by cosine similarity.
        Falls back to MeSH if UMLS API key is not available.
        """
        if not self.umls_api_key:
            return await self._lookup_mesh(term)

        url = "https://uts-ws.nlm.nih.gov/rest/search/current"
        results: list[dict] = []
        try:
            for search_type in ("exact", "words"):
                params = {
                    "string": term,
                    "apiKey": self.umls_api_key,
                    "searchType": search_type,
                    "pageSize": "200",
                }
                response = await self.client.get(url, params=params)
                if response.status_code != 200:
                    continue
                data = response.json()
                page = data.get("result", {}).get("results", [])
                if page:
                    results = page
                    break
        except Exception as e:
            logger.warning(
                {
                    "message": f"UMLS lookup failed for '{term}', trying MeSH fallback",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )

        if not results:
            return await self._lookup_mesh(term)

        if len(results) == 1:
            cui = results[0].get("ui")
            return cui if cui else await self._lookup_mesh(term)

        if self._embedding_generator:
            candidates = [(r.get("ui", ""), r.get("name", "")) for r in results if r.get("ui") and r.get("name")]
            best_cui = await self._rerank_by_similarity(term, candidates)
            if best_cui:
                return best_cui

        return results[0].get("ui") or await self._lookup_mesh(term)

    def _normalize_mesh_search_terms(self, term: str) -> list[str]:
        """Generate normalized search terms for MeSH lookup.

        MeSH uses formal terminology, so we normalize common informal terms.
        Returns a list of search terms to try, in order of preference.

        Args:
            term: Original search term

        Returns:
            List of normalized search terms (original first, then normalized variants)
        """
        search_terms = [term]
        term_lower = term.lower()

        # Common medical term normalizations (MeSH uses formal terminology)
        if "cancer" in term_lower:
            # "breast cancer" → "breast neoplasms"
            normalized = term_lower.replace("cancer", "neoplasms")
            search_terms.append(normalized.title())
        if "tumor" in term_lower or "tumour" in term_lower:
            normalized = term_lower.replace("tumor", "neoplasms").replace("tumour", "neoplasms")
            search_terms.append(normalized.title())

        return search_terms

    async def _lookup_mesh(self, term: str) -> Optional[str]:
        """Look up MeSH descriptor ID for a disease/symptom term.

        MeSH (Medical Subject Headings) is freely accessible without API key.
        Returns MeSH descriptor IDs like "MeSH:D001943" (breast neoplasms).

        Strategy:
        1. Try descriptor lookup with original term and normalized variants
        2. Collect all results and score them together
        3. Return the best match across all search terms
        """
        # Get all normalized search terms
        search_terms = self._normalize_mesh_search_terms(term)

        # Collect results from all search terms
        all_results = []
        seen_mesh_ids = set()

        for search_term in search_terms:
            results = await self._try_mesh_descriptor_lookup_all(search_term)
            for result in results:
                mesh_id = result.get("resource", "").split("/mesh/")[-1] if "/mesh/D" in result.get("resource", "") else None
                if mesh_id and mesh_id not in seen_mesh_ids:
                    all_results.append(result)
                    seen_mesh_ids.add(mesh_id)

        if not all_results:
            return None

        if self._embedding_generator:
            candidates: list[tuple[str, str]] = []
            for r in all_results:
                resource = r.get("resource", "")
                label = r.get("label", "").strip()
                if "/mesh/D" in resource and label:
                    mesh_id = resource.split("/mesh/")[-1]
                    candidates.append((mesh_id, label))
            if candidates:
                best_mesh_id = await self._rerank_by_similarity(term, candidates)
                if best_mesh_id:
                    return f"MeSH:{best_mesh_id}"

        # Score all results together, considering all search terms
        return self._extract_mesh_id_from_results(all_results, search_terms)

    def _extract_mesh_id_from_results(self, data: list, search_terms: str | list[str]) -> Optional[str]:  # pylint: disable=too-many-statements
        """Extract MeSH descriptor ID from API results, preferring best matches.

        Scores results based on how well they match any of the provided search terms.
        This allows normalized terms (e.g., "breast neoplasms") to score well even
        when the original search was "breast cancer".

        Scoring strategy:
        1. Exact match (case-insensitive) gets highest score
        2. Exact word match (all words present) gets high score
        3. Prefer shorter labels (more general terms) over longer ones (complications)
        4. Prefer matches where term is at the start of the label
        5. Penalize matches that are much longer than the search term (likely complications)
        6. Prefer matches to earlier search terms (original > normalized)

        Args:
            data: List of result dictionaries from MeSH API
            search_terms: Single search term (str) or list of search terms tried
                         (original first, then normalized variants). If a single string
                         is provided, it's treated as the only search term.
        """
        # Normalize input - accept either string or list
        if isinstance(search_terms, str):
            # If single string provided, generate normalized variants automatically
            search_terms_list = self._normalize_mesh_search_terms(search_terms)
        else:
            search_terms_list = search_terms

        # Normalize all search terms for comparison
        normalized_search_terms = [s.lower().strip() for s in search_terms_list]
        search_term_word_sets = [set(s.split()) for s in normalized_search_terms]

        scored_results = []

        for result in data:
            label = result.get("label", "").strip()
            label_lower = label.lower()
            label_words = set(label_lower.split())
            label_word_count = len(label_words)

            resource_uri = result.get("resource", "")
            if "/mesh/D" not in resource_uri:
                continue

            mesh_id = resource_uri.split("/mesh/")[-1]

            # Calculate match score - try each search term and take the best match
            best_score = 0.0
            best_term_index = len(search_terms_list)  # Prefer earlier terms
            best_term_lower = ""
            best_term_word_count = 0
            original_term_words = search_term_word_sets[0] if search_term_word_sets else set()

            for term_index, (term_lower, term_words) in enumerate(zip(normalized_search_terms, search_term_word_sets)):
                term_word_count = len(term_words)
                score = 0.0

                # 1. Exact match (case-insensitive) - highest priority
                if term_lower == label_lower:
                    score = 1000.0 - term_index  # Slight penalty for normalized terms
                    # For exact matches, apply additional scoring
                    # Prefer shorter labels (exact match on shorter = more general)
                    if label_word_count <= 2:
                        score += 50.0  # Bonus for short, general terms
                    if score > best_score:
                        best_score = score
                        best_term_index = term_index
                        best_term_lower = term_lower
                        best_term_word_count = term_word_count
                    continue  # This is the best possible match for this term

                # 2. All words from term are in label (exact word match)
                common_words = term_words & label_words

                # Require strong word overlap to prevent false matches
                # For single-word terms, require exact match
                if term_word_count == 1:
                    if len(common_words) == 1:
                        score += 500.0 - term_index * 10
                    else:
                        continue  # No match
                elif len(common_words) == term_word_count:
                    score += 500.0 - term_index * 10  # Bonus for earlier search terms
                elif len(common_words) >= term_word_count - 1:
                    # All words except one match - but check if it's a valid match
                    # For normalized terms (index > 0), require that original term words also match
                    if term_index > 0:
                        # Check if original term's words (non-normalized) match the label
                        original_common = original_term_words & label_words
                        if len(original_common) < len(original_term_words) - 1:
                            # Original term doesn't match well - likely false match
                            continue
                    score += 200.0 - term_index * 5
                else:
                    # For 2+ word terms, require at least term_word_count - 1 words to match
                    continue  # Skip if not enough words match

                # Update best score if this term matches better
                if score > best_score or (score == best_score and term_index < best_term_index):
                    best_score = score
                    best_term_index = term_index
                    best_term_lower = term_lower
                    best_term_word_count = term_word_count

            if best_score == 0.0:
                continue  # No match found for any search term

            # Apply additional scoring based on the best matching term
            # 3. Prefer shorter labels (more general terms)
            # Shorter labels indicate more general concepts
            length_ratio = len(best_term_lower) / max(len(label_lower), 1)
            if length_ratio > 0.8:  # Term is almost as long as label
                best_score += 100.0
            elif length_ratio > 0.6:
                best_score += 50.0
            elif length_ratio < 0.4:  # Label is much longer (likely a complication)
                best_score -= 100.0

            # 4. Prefer matches where term appears at the start
            if label_lower.startswith(best_term_lower):
                best_score += 150.0
            elif best_term_lower in label_lower:
                best_score += 50.0

            # 5. Penalize results with many extra words (likely complications)
            extra_words = label_word_count - best_term_word_count
            if extra_words > 1:
                best_score -= 100.0 * extra_words  # Heavy penalty for extra words (complications)
            elif extra_words == 1:
                best_score -= 50.0  # Moderate penalty for one extra word

            # 6. Special handling: if label is much longer, it's likely a complication
            # Penalize labels that are >50% longer than the search term
            if len(label_lower) > len(best_term_lower) * 1.5:
                best_score -= 150.0

            # 7. Bonus for word count similarity (exact match preferred)
            if label_word_count == best_term_word_count:
                best_score += 100.0
            elif label_word_count == best_term_word_count + 1:
                best_score += 25.0  # Slight bonus for one extra word (handles plurals)

            if best_score > 0:
                scored_results.append((best_score, mesh_id, label))

        if not scored_results:
            return None

        # Sort by score (descending) and return the best match
        scored_results.sort(key=lambda x: x[0], reverse=True)
        best_score, best_mesh_id, best_label = scored_results[0]

        logger.debug(
            {
                "message": f"MeSH match selected for '{search_terms_list[0]}'",
                "search_terms": search_terms_list,
                "selected": best_label,
                "mesh_id": best_mesh_id,
                "score": best_score,
                "alternatives": [(score, label) for score, _, label in scored_results[:3]],
            },
            pprint=True,
        )

        return f"MeSH:{best_mesh_id}"

    async def _try_mesh_descriptor_lookup_all(self, term: str) -> list[dict]:
        """Try to find MeSH descriptors for a term, returning all results.

        Args:
            term: Search term

        Returns:
            List of result dictionaries from MeSH API
        """
        try:
            url = "https://id.nlm.nih.gov/mesh/lookup/descriptor"
            params = {"label": term, "match": "contains", "limit": "10"}
            response = await self.client.get(url, params=params)

            if response.status_code != 200:
                return []

            data = response.json()
            if not data:
                return []

            return data
        except Exception as e:
            logger.warning(
                {
                    "message": f"MeSH lookup failed for '{term}'",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )
            return []

    async def _lookup_hgnc(self, term: str) -> Optional[str]:
        """Look up HGNC ID for a gene.

        Tries official symbol first, then falls back to alias search.
        This handles cases like "p53" which is an alias for "TP53".
        """
        headers = {"Accept": "application/json"}

        try:
            # Strategy 1: Try exact symbol match
            url = f"https://rest.genenames.org/fetch/symbol/{term}"
            response = await self.client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    hgnc_id = docs[0].get("hgnc_id")
                    if hgnc_id:
                        return hgnc_id  # Already includes "HGNC:" prefix

            # Strategy 2: Try alias search (handles "p53" → "TP53")
            url = f"https://rest.genenames.org/search/alias_symbol/{term}"
            response = await self.client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    hgnc_id = docs[0].get("hgnc_id")
                    if hgnc_id:
                        return hgnc_id

            return None
        except Exception as e:
            logger.warning(
                {
                    "message": f"HGNC lookup failed for '{term}'",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )
            return None

    async def _lookup_rxnorm(self, term: str) -> Optional[str]:
        """Look up RxNorm ID for a drug."""
        logger = setup_logging()

        try:
            # RxNorm API (no authentication required!)
            url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={term}"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                id_group = data.get("idGroup", {})
                rxnorm_ids = id_group.get("rxnormId", [])
                if rxnorm_ids:
                    return f"RxNorm:{rxnorm_ids[0]}"
            return None
        except Exception as e:
            logger.warning(
                {
                    "message": f"RxNorm lookup failed for '{term}'",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )
            return None

    async def _lookup_mesh_by_id(self, mesh_id: str) -> Optional[str]:
        """Look up MeSH ID by known ID (no search needed).

        Args:
            mesh_id: MeSH descriptor ID (e.g., "D001943" or "MeSH:D001943")

        Returns:
            Formatted MeSH ID (e.g., "MeSH:D001943")
        """
        # Remove any existing prefix
        mesh_id_clean = mesh_id.replace("MeSH:", "").strip()
        # Validate format (MeSH IDs start with D followed by digits)
        if mesh_id_clean.startswith("D") and mesh_id_clean[1:].isdigit():
            return f"MeSH:{mesh_id_clean}"
        return None

    async def _lookup_umls_by_id(self, umls_id: str) -> Optional[str]:
        """Look up UMLS CUI by known ID (no search needed).

        Args:
            umls_id: UMLS CUI (e.g., "C0006142")

        Returns:
            UMLS CUI string (e.g., "C0006142")
        """
        # Validate format (UMLS CUIs start with C followed by digits)
        umls_id_clean = umls_id.strip()
        if umls_id_clean.startswith("C") and umls_id_clean[1:].isdigit():
            return umls_id_clean
        return None

    async def _lookup_hgnc_by_id(self, hgnc_id: str) -> Optional[str]:
        """Look up HGNC ID by known ID (no search needed).

        Args:
            hgnc_id: HGNC ID (e.g., "1100" or "HGNC:1100")

        Returns:
            Formatted HGNC ID (e.g., "HGNC:1100")
        """
        # Remove any existing prefix
        hgnc_id_clean = hgnc_id.replace("HGNC:", "").strip()
        # Validate format (HGNC IDs are numeric)
        if hgnc_id_clean.isdigit():
            return f"HGNC:{hgnc_id_clean}"
        return None

    async def _lookup_rxnorm_by_id(self, rxnorm_id: str) -> Optional[str]:
        """Look up RxNorm ID by known ID (no search needed).

        Args:
            rxnorm_id: RxNorm ID (e.g., "1187832" or "RxNorm:1187832")

        Returns:
            Formatted RxNorm ID (e.g., "RxNorm:1187832")
        """
        # Remove any existing prefix
        rxnorm_id_clean = rxnorm_id.replace("RxNorm:", "").strip()
        # Validate format (RxNorm IDs are numeric)
        if rxnorm_id_clean.isdigit():
            return f"RxNorm:{rxnorm_id_clean}"
        return None

    async def _lookup_uniprot_by_id(self, uniprot_id: str) -> Optional[str]:
        """Look up UniProt ID by known ID (no search needed).

        Args:
            uniprot_id: UniProt accession (e.g., "P38398" or "UniProt:P38398")

        Returns:
            Formatted UniProt ID (e.g., "UniProt:P38398")
        """
        # Remove any existing prefix
        uniprot_id_clean = uniprot_id.replace("UniProt:", "").strip()
        # Validate format (UniProt accessions start with P, Q, A, O, or number)
        if uniprot_id_clean and (uniprot_id_clean[0].isalpha() or uniprot_id_clean[0].isdigit()):
            return f"UniProt:{uniprot_id_clean}"
        return None

    async def _lookup_uniprot(self, term: str) -> Optional[str]:
        """Look up UniProt ID for a protein."""
        logger = setup_logging()

        try:
            # UniProt REST API (no authentication required!)
            url = "https://rest.uniprot.org/uniprotkb/search"
            params: dict[str, str] = {
                "query": f"protein_name:{term}",
                "format": "json",
                "size": "1",
            }
            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    uniprot_id = results[0].get("primaryAccession")  # e.g., "P38398"
                    return f"UniProt:{uniprot_id}" if uniprot_id else None
            return None
        except Exception as e:
            logger.warning(
                {
                    "message": f"UniProt lookup failed for '{term}'",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )
            return None

    def _dbpedia_label_matches(self, term: str, label: str) -> bool:
        """Check if a DBPedia label is a good match for the search term."""
        import re

        # Strip HTML tags from label (DBPedia returns <B>...</B> highlighting)
        label_clean = re.sub(r"<[^>]+>", "", label).lower().strip()
        term_lower = term.lower().strip()

        # Extract first word (for prefix matching)
        term_first = term_lower.replace("-", " ").split()[0] if term_lower else ""
        label_first = label_clean.replace("-", " ").split()[0] if label_clean else ""

        # Accept if:
        # 1. Term is contained in label (or vice versa)
        # 2. First words share a common prefix of 6+ chars (handles mitochondria/mitochondrion)
        # 3. Label starts with the term (e.g., "breast cancer" matches "breast cancer syndrome")
        common_prefix = len(term_first) >= 6 and len(label_first) >= 6 and term_first[:6] == label_first[:6]

        return term_lower in label_clean or label_clean in term_lower or label_clean.startswith(term_lower) or common_prefix

    async def _lookup_dbpedia(self, term: str) -> Optional[str]:
        """Look up DBPedia URI as fallback for any entity type.

        DBPedia is a general knowledge base extracted from Wikipedia.
        Used as a fallback when specialized medical ontologies don't find a match.

        Only accepts results where the label closely matches the search term
        to avoid garbage matches like "HER2-enriched" → "Insect".
        """
        try:
            # DBPedia Lookup API (no authentication required!)
            url = "https://lookup.dbpedia.org/api/search"
            params = {"query": term.lower(), "format": "json", "maxResults": "5"}
            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                docs = data.get("docs", [])

                for doc in docs:
                    # Get label (returned as list)
                    label_list = doc.get("label", [])
                    label = label_list[0] if label_list else ""

                    if self._dbpedia_label_matches(term, label):
                        resource = doc.get("resource", [])
                        if resource:
                            uri = resource[0] if isinstance(resource, list) else resource
                            return f"DBPedia:{uri.split('/')[-1]}"

            return None
        except Exception as e:
            logger.warning(
                {
                    "message": f"DBPedia lookup failed for '{term}'",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )
            return None

    async def _extract_authoritative_id_from_dbpedia(self, dbpedia_id: str, entity_type: str, original_term: str) -> Optional[str]:  # pylint: disable=too-many-statements
        """Extract authoritative ID from DBPedia resource properties.

        After finding a DBPedia match, query the resource to find authoritative IDs
        (MeSH, UMLS, HGNC, RxNorm, UniProt) that may be embedded in DBPedia properties.
        If found, perform a follow-up lookup with the authoritative source.

        Args:
            dbpedia_id: DBPedia ID in format "DBPedia:ResourceName"
            entity_type: Type of entity (disease, gene, drug, protein, etc.)
            original_term: Original search term for caching

        Returns:
            Authoritative canonical ID if found, None otherwise
        """
        logger = setup_logging()

        # Extract resource name from DBPedia ID
        resource_name = dbpedia_id.replace("DBPedia:", "")
        resource_uri = f"http://dbpedia.org/resource/{resource_name}"

        # Check cache first (keyed by DBPedia ID + entity_type)
        cache_key = f"dbpedia_auth:{dbpedia_id}:{entity_type}"
        cached = self._cache.fetch(cache_key, entity_type)
        if cached is not None:
            logger.debug(
                {
                    "message": f"Cache hit for authoritative ID extraction from {dbpedia_id}",
                    "dbpedia_id": dbpedia_id,
                    "authoritative_id": cached.id,
                },
                pprint=True,
            )
            return cached.id

        try:
            # Query DBPedia SPARQL endpoint for resource properties
            # Try alternative property names (DBPedia uses various prefixes)
            sparql_query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT ?meshId ?umlsId ?hgncId ?rxnormId ?uniprotId
            WHERE {{
                OPTIONAL {{ <{resource_uri}> dbo:meshId ?meshId . }}
                OPTIONAL {{ <{resource_uri}> dbp:umlsId ?umlsId . }}
                OPTIONAL {{ <{resource_uri}> dbp:umls ?umlsId . }}
                OPTIONAL {{ <{resource_uri}> dbo:hgncId ?hgncId . }}
                OPTIONAL {{ <{resource_uri}> dbp:hgncId ?hgncId . }}
                OPTIONAL {{ <{resource_uri}> dbp:rxnormId ?rxnormId . }}
                OPTIONAL {{ <{resource_uri}> dbp:uniprotId ?uniprotId . }}
            }}
            LIMIT 1
            """

            sparql_url = "https://dbpedia.org/sparql"
            params = {"query": sparql_query, "format": "json"}

            response = await self.client.get(sparql_url, params=params)

            if response.status_code == 200:
                data = response.json()
                bindings = data.get("results", {}).get("bindings", [])

                if bindings:
                    result = bindings[0]

                    # Determine which authoritative ID to look for based on entity_type
                    authoritative_id_value: Optional[str] = None
                    authoritative_source: Optional[str] = None

                    entity_type_normalized = entity_type.lower()
                    if entity_type_normalized in ("disease", "symptom", "procedure"):
                        # Prefer MeSH, then UMLS
                        if "meshId" in result and result["meshId"].get("value"):
                            authoritative_id_value = result["meshId"]["value"]
                            authoritative_source = "mesh"
                        elif "umlsId" in result and result["umlsId"].get("value"):
                            authoritative_id_value = result["umlsId"]["value"]
                            authoritative_source = "umls"
                    elif entity_type_normalized == "gene":
                        if "hgncId" in result and result["hgncId"].get("value"):
                            authoritative_id_value = result["hgncId"]["value"]
                            authoritative_source = "hgnc"
                    elif entity_type_normalized == "drug":
                        if "rxnormId" in result and result["rxnormId"].get("value"):
                            authoritative_id_value = result["rxnormId"]["value"]
                            authoritative_source = "rxnorm"
                    elif entity_type_normalized == "protein":
                        if "uniprotId" in result and result["uniprotId"].get("value"):
                            authoritative_id_value = result["uniprotId"]["value"]
                            authoritative_source = "uniprot"

                    # If we found an authoritative ID, do a follow-up lookup
                    if authoritative_id_value and authoritative_source:
                        logger.debug(
                            {
                                "message": f"Found {authoritative_source} ID in DBPedia for {dbpedia_id}: {authoritative_id_value}",
                                "dbpedia_id": dbpedia_id,
                                "authoritative_source": authoritative_source,
                                "authoritative_id": authoritative_id_value,
                            },
                            pprint=True,
                        )

                        # Perform follow-up lookup with authoritative source
                        follow_up_id: Optional[str] = None
                        if authoritative_source == "mesh":
                            # MeSH ID format: D001943 (just the ID, no prefix)
                            follow_up_id = await self._lookup_mesh_by_id(authoritative_id_value)
                        elif authoritative_source == "umls":
                            # UMLS CUI format: C0006142
                            follow_up_id = await self._lookup_umls_by_id(authoritative_id_value)
                        elif authoritative_source == "hgnc":
                            # HGNC format: HGNC:1100
                            follow_up_id = await self._lookup_hgnc_by_id(authoritative_id_value)
                        elif authoritative_source == "rxnorm":
                            # RxNorm format: RxNorm:1187832
                            follow_up_id = await self._lookup_rxnorm_by_id(authoritative_id_value)
                        elif authoritative_source == "uniprot":
                            # UniProt format: UniProt:P38398
                            follow_up_id = await self._lookup_uniprot_by_id(authoritative_id_value)

                        if follow_up_id:
                            # Cache the result
                            url = build_canonical_url(follow_up_id, entity_type=entity_type)
                            canonical_id = CanonicalId(id=follow_up_id, url=url, synonyms=(original_term,))
                            self._cache.store(cache_key, entity_type, canonical_id)
                            logger.info(
                                {
                                    "message": f"Extracted authoritative ID from DBPedia: {follow_up_id} (from {dbpedia_id})",
                                    "dbpedia_id": dbpedia_id,
                                    "authoritative_id": follow_up_id,
                                    "source": authoritative_source,
                                },
                                pprint=True,
                            )
                            return follow_up_id

            # No authoritative ID found in DBPedia properties
            logger.debug(
                {
                    "message": f"No authoritative ID found in DBPedia properties for {dbpedia_id}",
                    "dbpedia_id": dbpedia_id,
                    "entity_type": entity_type,
                },
                pprint=True,
            )
            # Cache as "no authoritative ID found" to avoid repeated queries
            self._cache.mark_known_bad(cache_key, entity_type)
            return None

        except Exception as e:
            # Log at warning level so failures are visible even without DEBUG logging
            logger.warning(
                {
                    "message": f"Failed to extract authoritative ID from DBPedia for {dbpedia_id}: {e}",
                    "dbpedia_id": dbpedia_id,
                    "error": str(e),
                },
                pprint=True,
            )
            # Don't mark as known bad on exception - might be transient (network, timeout, etc.)
            return None

    def _extract_authoritative_id_from_dbpedia_sync(  # pylint: disable=too-many-statements
        self,
        client: "httpx.Client",
        dbpedia_id: str,
        entity_type: str,
        original_term: str,
    ) -> Optional[str]:
        """Synchronous version of authoritative ID extraction from DBPedia.

        Args:
            client: Synchronous HTTP client
            dbpedia_id: DBPedia ID in format "DBPedia:ResourceName"
            entity_type: Type of entity (disease, gene, drug, protein, etc.)
            original_term: Original search term for caching

        Returns:
            Authoritative canonical ID if found, None otherwise
        """
        logger = setup_logging()

        # Extract resource name from DBPedia ID
        resource_name = dbpedia_id.replace("DBPedia:", "")
        resource_uri = f"http://dbpedia.org/resource/{resource_name}"

        # Check cache first (keyed by DBPedia ID + entity_type)
        cache_key = f"dbpedia_auth:{dbpedia_id}:{entity_type}"
        cached = self._cache.fetch(cache_key, entity_type)
        if cached is not None:
            logger.debug(
                {
                    "message": f"Cache hit for authoritative ID extraction from {dbpedia_id}",
                    "dbpedia_id": dbpedia_id,
                    "authoritative_id": cached.id,
                },
                pprint=True,
            )
            return cached.id

        try:
            # Query DBPedia SPARQL endpoint for resource properties
            sparql_query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT ?meshId ?umlsId ?hgncId ?rxnormId ?uniprotId
            WHERE {{
                OPTIONAL {{ <{resource_uri}> dbo:meshId ?meshId . }}
                OPTIONAL {{ <{resource_uri}> dbp:umlsId ?umlsId . }}
                OPTIONAL {{ <{resource_uri}> dbp:umls ?umlsId . }}
                OPTIONAL {{ <{resource_uri}> dbo:hgncId ?hgncId . }}
                OPTIONAL {{ <{resource_uri}> dbp:hgncId ?hgncId . }}
                OPTIONAL {{ <{resource_uri}> dbp:rxnormId ?rxnormId . }}
                OPTIONAL {{ <{resource_uri}> dbp:uniprotId ?uniprotId . }}
            }}
            LIMIT 1
            """

            sparql_url = "https://dbpedia.org/sparql"
            params = {"query": sparql_query, "format": "json"}

            response = client.get(sparql_url, params=params)

            if response.status_code == 200:
                data = response.json()
                bindings = data.get("results", {}).get("bindings", [])

                if bindings:
                    result = bindings[0]

                    # Determine which authoritative ID to look for based on entity_type
                    authoritative_id_value: Optional[str] = None
                    authoritative_source: Optional[str] = None

                    entity_type_normalized = entity_type.lower()
                    if entity_type_normalized in ("disease", "symptom", "procedure"):
                        # Prefer MeSH, then UMLS
                        if "meshId" in result and result["meshId"].get("value"):
                            authoritative_id_value = result["meshId"]["value"]
                            authoritative_source = "mesh"
                        elif "umlsId" in result and result["umlsId"].get("value"):
                            authoritative_id_value = result["umlsId"]["value"]
                            authoritative_source = "umls"
                    elif entity_type_normalized == "gene":
                        if "hgncId" in result and result["hgncId"].get("value"):
                            authoritative_id_value = result["hgncId"]["value"]
                            authoritative_source = "hgnc"
                    elif entity_type_normalized == "drug":
                        if "rxnormId" in result and result["rxnormId"].get("value"):
                            authoritative_id_value = result["rxnormId"]["value"]
                            authoritative_source = "rxnorm"
                    elif entity_type_normalized == "protein":
                        if "uniprotId" in result and result["uniprotId"].get("value"):
                            authoritative_id_value = result["uniprotId"]["value"]
                            authoritative_source = "uniprot"

                    # If we found an authoritative ID, do a follow-up lookup
                    if authoritative_id_value and authoritative_source:
                        logger.debug(
                            {
                                "message": f"Found {authoritative_source} ID in DBPedia for {dbpedia_id}: {authoritative_id_value}",
                                "dbpedia_id": dbpedia_id,
                                "authoritative_source": authoritative_source,
                                "authoritative_id": authoritative_id_value,
                            },
                            pprint=True,
                        )

                        # Perform follow-up lookup with authoritative source (sync)
                        follow_up_id: Optional[str] = None
                        if authoritative_source == "mesh":
                            follow_up_id = self._lookup_mesh_by_id_sync(authoritative_id_value)
                        elif authoritative_source == "umls":
                            follow_up_id = self._lookup_umls_by_id_sync(authoritative_id_value)
                        elif authoritative_source == "hgnc":
                            follow_up_id = self._lookup_hgnc_by_id_sync(authoritative_id_value)
                        elif authoritative_source == "rxnorm":
                            follow_up_id = self._lookup_rxnorm_by_id_sync(authoritative_id_value)
                        elif authoritative_source == "uniprot":
                            follow_up_id = self._lookup_uniprot_by_id_sync(authoritative_id_value)

                        if follow_up_id:
                            # Cache the result
                            url = build_canonical_url(follow_up_id, entity_type=entity_type)
                            canonical_id = CanonicalId(id=follow_up_id, url=url, synonyms=(original_term,))
                            self._cache.store(cache_key, entity_type, canonical_id)
                            logger.info(
                                {
                                    "message": f"Extracted authoritative ID from DBPedia: {follow_up_id} (from {dbpedia_id})",
                                    "dbpedia_id": dbpedia_id,
                                    "authoritative_id": follow_up_id,
                                    "source": authoritative_source,
                                },
                                pprint=True,
                            )
                            return follow_up_id

            # No authoritative ID found in DBPedia properties
            logger.debug(
                {
                    "message": f"No authoritative ID found in DBPedia properties for {dbpedia_id}",
                    "dbpedia_id": dbpedia_id,
                    "entity_type": entity_type,
                },
                pprint=True,
            )
            # Don't cache as "known bad" - DBPedia properties might be added later
            # Just return None and let the DBPedia ID be used
            return None

        except Exception as e:
            # Log at warning level so failures are visible even without DEBUG logging
            logger.warning(
                {
                    "message": f"Failed to extract authoritative ID from DBPedia for {dbpedia_id}: {e}",
                    "dbpedia_id": dbpedia_id,
                    "error": str(e),
                },
                pprint=True,
            )
            # Don't mark as known bad on exception - might be transient (network, timeout, etc.)
            return None

    def _lookup_mesh_by_id_sync(self, mesh_id: str) -> Optional[str]:
        """Sync version: Look up MeSH ID by known ID."""
        mesh_id_clean = mesh_id.replace("MeSH:", "").strip()
        if mesh_id_clean.startswith("D") and mesh_id_clean[1:].isdigit():
            return f"MeSH:{mesh_id_clean}"
        return None

    def _lookup_umls_by_id_sync(self, umls_id: str) -> Optional[str]:
        """Sync version: Look up UMLS CUI by known ID."""
        umls_id_clean = umls_id.strip()
        if umls_id_clean.startswith("C") and umls_id_clean[1:].isdigit():
            return umls_id_clean
        return None

    def _lookup_hgnc_by_id_sync(self, hgnc_id: str) -> Optional[str]:
        """Sync version: Look up HGNC ID by known ID."""
        hgnc_id_clean = hgnc_id.replace("HGNC:", "").strip()
        if hgnc_id_clean.isdigit():
            return f"HGNC:{hgnc_id_clean}"
        return None

    def _lookup_rxnorm_by_id_sync(self, rxnorm_id: str) -> Optional[str]:
        """Sync version: Look up RxNorm ID by known ID."""
        rxnorm_id_clean = rxnorm_id.replace("RxNorm:", "").strip()
        if rxnorm_id_clean.isdigit():
            return f"RxNorm:{rxnorm_id_clean}"
        return None

    def _lookup_uniprot_by_id_sync(self, uniprot_id: str) -> Optional[str]:
        """Sync version: Look up UniProt ID by known ID."""
        uniprot_id_clean = uniprot_id.replace("UniProt:", "").strip()
        if uniprot_id_clean and (uniprot_id_clean[0].isalpha() or uniprot_id_clean[0].isdigit()):
            return f"UniProt:{uniprot_id_clean}"
        return None

    def lookup_sync(self, term: str, entity_type: str) -> Optional[CanonicalId]:
        """Synchronous lookup (interface method).

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (disease, gene, drug, protein, etc.)

        Returns:
            CanonicalId if found, None otherwise
        """
        canonical_id_str = self.lookup_canonical_id_sync(term, entity_type)
        if canonical_id_str:
            url = build_canonical_url(canonical_id_str, entity_type=entity_type)
            return CanonicalId(id=canonical_id_str, url=url, synonyms=(term,))
        return None

    def lookup_canonical_id_sync(self, term: str, entity_type: str) -> Optional[str]:
        """Synchronous wrapper for use as Ollama tool.

        This is needed because Ollama tool functions must be synchronous.
        Uses the cache first, then makes synchronous HTTP calls if needed.

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (disease, gene, drug, protein, etc.)

        Returns:
            Canonical ID string if found, None otherwise
        """
        import httpx as httpx_sync

        # Normalize inputs
        term_normalized = term.strip().lower()
        entity_type_normalized = entity_type.lower()

        # Never look up generic/type-like terms (same as async path; check before cache)
        if term_normalized in LOOKUP_BLOCKLIST:
            self._cache.mark_known_bad(term, entity_type)
            return None

        # Check cache first (this is synchronous)
        cached = self._cache.fetch(term, entity_type)
        if cached is not None:
            logger.debug(
                {
                    "message": f"Sync cache hit for '{term}' ({entity_type})",
                    "term": term,
                    "entity_type": entity_type,
                    "result": cached.id,
                },
                pprint=True,
            )
            return cached.id

        # Check if known bad
        if self._cache.is_known_bad(term, entity_type):
            return None

        # Cache miss - make synchronous HTTP request
        logger.debug(
            {
                "message": f"Sync cache miss, making HTTP request for '{term}' ({entity_type})",
                "term": term,
                "entity_type": entity_type,
            },
            pprint=True,
        )

        try:
            canonical_id_str: Optional[str] = None

            with httpx_sync.Client(timeout=10.0) as sync_client:
                if entity_type_normalized in ("disease", "symptom", "procedure"):
                    canonical_id_str = self._lookup_umls_sync(sync_client, term)
                elif entity_type_normalized == "gene":
                    canonical_id_str = self._lookup_hgnc_sync(sync_client, term)
                    # Skip DBPedia for genes (same as async path)
                elif entity_type_normalized == "drug":
                    canonical_id_str = self._lookup_rxnorm_sync(sync_client, term)
                elif entity_type_normalized == "protein":
                    canonical_id_str = self._lookup_uniprot_sync(sync_client, term)

                # Fallback to DBPedia if specialized lookup failed (never for gene)
                if canonical_id_str is None and entity_type_normalized != "gene":
                    dbpedia_result = self._lookup_dbpedia_sync(sync_client, term)
                    if dbpedia_result:
                        # Try to extract authoritative ID from DBPedia properties (sync version)
                        authoritative_id = self._extract_authoritative_id_from_dbpedia_sync(sync_client, dbpedia_result, entity_type, term)
                        canonical_id_str = authoritative_id if authoritative_id else dbpedia_result

            # Build CanonicalId object with URL and cache it
            if canonical_id_str:
                url = build_canonical_url(canonical_id_str, entity_type=entity_type)
                canonical_id = CanonicalId(id=canonical_id_str, url=url, synonyms=(term,))
                self._cache.store(term, entity_type, canonical_id)
            else:
                # Mark as known bad
                self._cache.mark_known_bad(term, entity_type)

            self._save_cache()

            # Sanity check: common terms should always resolve
            # This helps catch lookup bugs early
            if term_normalized == "breast cancer" and entity_type_normalized == "disease":
                assert canonical_id_str is not None, "'breast cancer' should always get a MeSH ID! " "Got None. Check MeSH API or normalization logic."

            return canonical_id_str

        except Exception as e:
            logger.warning(
                {
                    "message": f"Sync lookup failed for '{term}' ({entity_type})",
                    "term": term,
                    "entity_type": entity_type,
                    "error": str(e),
                },
                pprint=True,
            )
            return None

    def _lookup_umls_sync(self, client: "httpx.Client", term: str) -> Optional[str]:
        """Synchronous UMLS lookup with MeSH fallback."""
        api_key = os.environ.get("UMLS_API_KEY")

        # Try UMLS first if API key is available
        if api_key:
            try:
                url = "https://uts-ws.nlm.nih.gov/rest/search/current"
                params = {"string": term, "apiKey": api_key, "returnIdType": "concept"}
                response = client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("result", {}).get("results", [])
                    if results:
                        cui = results[0].get("ui")
                        if cui:
                            return cui
            except Exception as e:
                logger.warning(
                    {
                        "message": f"UMLS sync lookup failed for '{term}', trying MeSH fallback",
                        "term": term,
                        "error": str(e),
                    },
                    pprint=True,
                )

        # Fall back to MeSH (no API key required)
        return self._lookup_mesh_sync(client, term)

    def _lookup_mesh_sync(self, client: "httpx.Client", term: str) -> Optional[str]:
        """Synchronous MeSH lookup with term normalization.

        Uses the same multi-term approach as async version.
        """
        # Get all normalized search terms
        search_terms = self._normalize_mesh_search_terms(term)

        # Collect results from all search terms
        all_results = []
        seen_mesh_ids = set()

        try:
            for search_term in search_terms:
                url = "https://id.nlm.nih.gov/mesh/lookup/descriptor"
                params = {"label": search_term, "match": "contains", "limit": "10"}
                response = client.get(url, params=params)

                if response.status_code != 200:
                    continue

                data = response.json()
                if not data:
                    continue

                for result in data:
                    mesh_id = result.get("resource", "").split("/mesh/")[-1] if "/mesh/D" in result.get("resource", "") else None
                    if mesh_id and mesh_id not in seen_mesh_ids:
                        all_results.append(result)
                        seen_mesh_ids.add(mesh_id)
        except Exception as e:
            logger.warning(
                {
                    "message": f"MeSH sync lookup failed for '{term}'",
                    "term": term,
                    "error": str(e),
                },
                pprint=True,
            )
            return None

        if not all_results:
            return None

        # Score all results together, considering all search terms
        return self._extract_mesh_id_from_results(all_results, search_terms)

    def _lookup_hgnc_sync(self, client: "httpx.Client", term: str) -> Optional[str]:
        """Synchronous HGNC lookup with alias fallback."""
        headers = {"Accept": "application/json"}

        # Strategy 1: Try exact symbol match
        url = f"https://rest.genenames.org/fetch/symbol/{term}"
        response = client.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            if docs:
                hgnc_id = docs[0].get("hgnc_id")
                if hgnc_id:
                    return hgnc_id

        # Strategy 2: Try alias search (handles "p53" → "TP53")
        url = f"https://rest.genenames.org/search/alias_symbol/{term}"
        response = client.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            if docs:
                hgnc_id = docs[0].get("hgnc_id")
                if hgnc_id:
                    return hgnc_id

        return None

    def _lookup_rxnorm_sync(self, client: "httpx.Client", term: str) -> Optional[str]:
        """Synchronous RxNorm lookup."""
        url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={term}"
        response = client.get(url)

        if response.status_code == 200:
            data = response.json()
            id_group = data.get("idGroup", {})
            rxnorm_ids = id_group.get("rxnormId", [])
            if rxnorm_ids:
                return f"RxNorm:{rxnorm_ids[0]}"
        return None

    def _lookup_uniprot_sync(self, client: "httpx.Client", term: str) -> Optional[str]:
        """Synchronous UniProt lookup."""
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {"query": f"protein_name:{term}", "format": "json", "size": "1"}
        response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                uniprot_id = results[0].get("primaryAccession")
                return f"UniProt:{uniprot_id}" if uniprot_id else None
        return None

    def _lookup_dbpedia_sync(self, client: "httpx.Client", term: str) -> Optional[str]:
        """Synchronous DBPedia lookup as fallback with validation."""
        try:
            url = "https://lookup.dbpedia.org/api/search"
            params = {"query": term.lower(), "format": "json", "maxResults": "5"}
            response = client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                docs = data.get("docs", [])

                for doc in docs:
                    label_list = doc.get("label", [])
                    label = label_list[0] if label_list else ""

                    if self._dbpedia_label_matches(term, label):
                        resource = doc.get("resource", [])
                        if resource:
                            uri = resource[0] if isinstance(resource, list) else resource
                            return f"DBPedia:{uri.split('/')[-1]}"
            return None
        except Exception:
            return None

    async def close(self) -> None:
        """Close the HTTP client and save cache."""
        self._save_cache(force=True)
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - saves cache and closes client."""
        await self.close()
