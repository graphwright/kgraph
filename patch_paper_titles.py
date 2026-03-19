#!/usr/bin/env python3
"""Patch cited-paper names in an existing bundle by fetching titles from NCBI esummary.

Usage:
    uv run python patch_paper_titles.py [--bundle-dir medlit_bundle]
"""
import argparse
import json
import logging
import time
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 200
NCBI_DELAY = 0.34  # seconds between batches (NCBI: max 3 req/s without API key)


def fetch_pmc_titles(pmc_ids: list[str]) -> dict[str, str]:
    """Return {PMC-prefixed-id -> title} for as many IDs as NCBI knows about."""
    titles: dict[str, str] = {}
    numeric_ids = []
    id_map: dict[str, str] = {}
    for pid in pmc_ids:
        numeric = pid[3:] if pid.upper().startswith("PMC") else pid
        if numeric.isdigit():
            numeric_ids.append(numeric)
            id_map[numeric] = pid

    for i in range(0, len(numeric_ids), BATCH_SIZE):
        batch = numeric_ids[i : i + BATCH_SIZE]
        url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pmc&id={','.join(batch)}&retmode=json"
        )
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read())
            result = data.get("result", {})
            found = 0
            for numeric_id in batch:
                doc = result.get(numeric_id)
                if doc and isinstance(doc, dict):
                    title = doc.get("title", "").strip()
                    if title:
                        titles[id_map[numeric_id]] = title
                        found += 1
            logger.info("Batch %d-%d: %d/%d titles found", i + 1, i + len(batch), found, len(batch))
        except Exception:
            logger.warning("esummary fetch failed for batch %d", i // BATCH_SIZE + 1, exc_info=True)
        if i + BATCH_SIZE < len(numeric_ids):
            time.sleep(NCBI_DELAY)

    return titles


def patch_bundle(bundle_dir: Path) -> None:
    entities_path = bundle_dir / "entities.jsonl"
    if not entities_path.exists():
        raise FileNotFoundError(f"{entities_path} not found")

    lines = entities_path.read_text(encoding="utf-8").splitlines()
    entities = [json.loads(l) for l in lines if l.strip()]

    # Find paper entities whose name == entity_id (bare PMC ID)
    to_patch = [e for e in entities if e.get("entity_type") == "paper" and e.get("name") == e.get("entity_id")]
    logger.info("Found %d cited-paper entities with bare PMC ID as name", len(to_patch))

    if not to_patch:
        logger.info("Nothing to patch.")
        return

    pmc_ids = [e["entity_id"] for e in to_patch]
    titles = fetch_pmc_titles(pmc_ids)
    logger.info("Retrieved %d titles total", len(titles))

    patched = 0
    for entity in entities:
        if entity.get("entity_type") == "paper" and entity["entity_id"] in titles:
            entity["name"] = titles[entity["entity_id"]]
            patched += 1

    with open(entities_path, "w", encoding="utf-8") as f:
        for entity in entities:
            f.write(json.dumps(entity) + "\n")

    logger.info("Patched %d entity names. Wrote %s", patched, entities_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch cited-paper titles in a kgbundle entities.jsonl")
    parser.add_argument("--bundle-dir", default="medlit_bundle", type=Path)
    args = parser.parse_args()
    patch_bundle(args.bundle_dir)


if __name__ == "__main__":
    main()
