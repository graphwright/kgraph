"""Config loader for medlit schema. Loads entity_types, predicates, domain_instructions from config dir.

TODO: migrate to domain_spec. Full migration: (1) Switch pass1_extract, pass1a_vocab,
dedup to use NORMALIZED_TO_BUNDLE and entity data from domain_spec. (2) Replace
get_schema_version with a hash of domain_spec module source (e.g.
hashlib.sha256(inspect.getsource(domain_spec).encode()).hexdigest()[:8]). (3) Delete
entity_types.yaml, predicates.yaml, domain_instructions.md and this module.
"""

import hashlib
from pathlib import Path
from typing import Any

import yaml


def _config_path(config_dir: Path, name: str) -> Path:
    """Return path to config file."""
    return config_dir / name


def load_entity_types(config_dir: Path) -> dict[str, Any]:
    """Load entity_types.yaml. Returns dict suitable for template injection."""
    path = _config_path(config_dir, "entity_types.yaml")
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("types", {})


def load_predicates(config_dir: Path) -> dict[str, Any]:
    """Load predicates.yaml."""
    path = _config_path(config_dir, "predicates.yaml")
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("predicates", {})


def load_domain_instructions(config_dir: Path) -> str:
    """Load domain_instructions.md as string."""
    path = _config_path(config_dir, "domain_instructions.md")
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def get_schema_version(config_dir: Path) -> str:
    """SHA256 of sorted concatenation of the three config files' contents, 8-char hex prefix."""
    filenames = ["domain_instructions.md", "entity_types.yaml", "predicates.yaml"]
    parts: list[str] = []
    for name in sorted(filenames):
        p = _config_path(config_dir, name)
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
        else:
            parts.append("")
    combined = "\n".join(parts)
    digest = hashlib.sha256(combined.encode("utf-8")).hexdigest()
    return digest[:8]
