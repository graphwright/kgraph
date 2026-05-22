"""Promotion policy for Sherlock Holmes domain.

Fiction entities don't have external authority APIs like UMLS or HGNC.
Instead we use a curated DBPedia URI map for well-known characters/locations,
and generate synthetic canonical IDs (holmes:<story_slug>:<type>:<SafeName>)
for all others.

Entities are promoted immediately (all fiction entities are inherently real
within the story universe) — there's no provisional/canonical distinction
for fictional entities. The main purpose of this policy is to assign
stable canonical IDs.
"""

from typing import Optional

from kgraph.promotion import PromotionPolicy
from kgschema.entity import BaseEntity, EntityStatus, PromotionConfig

from .domain_spec import make_canonical_id


# Curated DBPedia URIs for well-known Sherlock Holmes entities.
# Used as canonical_ids["dbpedia"] when present.
DBPEDIA_CANONICAL: dict[tuple[str, str], str] = {
    # (entity_type, normalized_name): dbpedia_uri
    ("character", "sherlock holmes"): "http://dbpedia.org/resource/Sherlock_Holmes",
    ("character", "holmes"): "http://dbpedia.org/resource/Sherlock_Holmes",
    ("character", "dr. watson"): "http://dbpedia.org/resource/Dr._Watson",
    ("character", "watson"): "http://dbpedia.org/resource/Dr._Watson",
    ("character", "dr. john h. watson"): "http://dbpedia.org/resource/Dr._Watson",
    ("character", "irene adler"): "http://dbpedia.org/resource/Irene_Adler",
    ("character", "the woman"): "http://dbpedia.org/resource/Irene_Adler",
    ("character", "mycroft holmes"): "http://dbpedia.org/resource/Mycroft_Holmes",
    ("character", "inspector lestrade"): "http://dbpedia.org/resource/Inspector_Lestrade",
    ("character", "mrs. hudson"): "http://dbpedia.org/resource/Mrs._Hudson",
    ("location", "221b baker street"): "http://dbpedia.org/resource/221B_Baker_Street",
    ("location", "baker street"): "http://dbpedia.org/resource/Baker_Street",
    ("location", "bohemia"): "http://dbpedia.org/resource/Bohemia",
    ("location", "london"): "http://dbpedia.org/resource/London",
    ("location", "scotland yard"): "http://dbpedia.org/resource/Scotland_Yard",
    ("organization", "scotland yard"): "http://dbpedia.org/resource/Scotland_Yard",
    ("story", "a scandal in bohemia"): "http://dbpedia.org/resource/A_Scandal_in_Bohemia",
}


class SherlockPromotionPolicy(PromotionPolicy):
    """Promotion policy for Sherlock Holmes fiction domain.

    All fiction entities are promoted (there is no external validation step).
    Canonical IDs are assigned from:
    1. Curated DBPedia map (for well-known entities).
    2. Synthetic holmes:<story_slug>:<type>:<SafeName> IDs for all others.
    """

    def __init__(self, config: PromotionConfig, story_slug: str = "unknown"):
        super().__init__(config)
        self.story_slug = story_slug

    def should_promote(self, entity: BaseEntity) -> bool:
        """All provisional fiction entities are promoted."""
        return entity.status == EntityStatus.PROVISIONAL

    async def assign_canonical_id(self, entity: BaseEntity) -> Optional[object]:
        """Assign a canonical ID for a Sherlock entity.

        Priority:
        1. Already has a canonical ID in canonical_ids → use it.
        2. Curated DBPedia map lookup.
        3. Synthetic holmes: URI from name + type.
        """
        from kgraph.canonical_id import CanonicalId

        # Already resolved
        if entity.canonical_ids:
            for source in ("dbpedia", "holmes"):
                if source in entity.canonical_ids:
                    return CanonicalId(id=entity.canonical_ids[source], source=source)

        entity_type = entity.get_entity_type()
        name_key = entity.name.lower().strip()
        dbpedia_uri = DBPEDIA_CANONICAL.get((entity_type, name_key))
        if not dbpedia_uri:
            # Try synonyms
            for syn in entity.synonyms or []:
                dbpedia_uri = DBPEDIA_CANONICAL.get((entity_type, syn.lower().strip()))
                if dbpedia_uri:
                    break

        if dbpedia_uri:
            return CanonicalId(id=dbpedia_uri, source="dbpedia")

        # Synthetic ID
        safe_name = entity.name.replace(" ", "").replace(".", "").replace("'", "").replace("-", "")
        synthetic = make_canonical_id(entity_type, safe_name, self.story_slug)
        return CanonicalId(id=synthetic, source="holmes")
