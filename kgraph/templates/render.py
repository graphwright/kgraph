"""Render extraction prompts from config and Jinja2 templates."""

from pathlib import Path
from typing import Any, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


def _format_from_domain_spec(domain_spec: Any) -> tuple[str, str, str]:
    """Build entity_types_str, predicates_str, domain_instructions from domain_spec module."""
    bundle_to_entity = getattr(domain_spec, "BUNDLE_CLASS_TO_ENTITY", {})
    # Exclude metadata_only entities from extraction prompt (Paper, Author, Institution)
    entity_types_for_prompt = [k for k, cls in bundle_to_entity.items() if not getattr(getattr(cls, "spec", None), "metadata_only", False)]
    entity_types_str = ", ".join(sorted(entity_types_for_prompt)) if entity_types_for_prompt else "Disease, Gene, Drug, etc."
    predicates = getattr(domain_spec, "PREDICATES", {})
    predicates_str = ", ".join(sorted(predicates.keys())) if predicates else "TREATS, INCREASES_RISK, etc."
    domain_instructions = (getattr(domain_spec, "PROMPT_INSTRUCTIONS", "") or "").strip() + "\n\n"
    return entity_types_str, predicates_str, domain_instructions


def _load_config(config_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Load entity_types, predicates, domain_instructions from config_dir."""
    if not config_dir.exists():
        return {}, {}, ""

    def _load_yaml(name: str, key: str) -> dict:
        p = config_dir / name
        if not p.exists():
            return {}
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get(key, {}) if isinstance(data, dict) else {}

    entity_types = _load_yaml("entity_types.yaml", "types")
    predicates = _load_yaml("predicates.yaml", "predicates")
    domain_path = config_dir / "domain_instructions.md"
    domain = domain_path.read_text(encoding="utf-8") if domain_path.exists() else ""
    return entity_types, predicates, domain


def _format_entity_types_for_prompt(entity_types: dict[str, Any]) -> str:
    """Pre-format entity_types into comma-separated bundle_class list for prompt."""
    classes: list[str] = []
    for val in entity_types.values():
        if isinstance(val, dict) and "bundle_class" in val:
            classes.append(val["bundle_class"])
    if not classes:
        return "Disease, Gene, Drug, Hormone, Enzyme, Evidence, etc."
    return ", ".join(sorted(classes)) + ", Evidence"


def _format_predicates_for_prompt(predicates: dict[str, Any]) -> str:
    """Pre-format predicates into comma-separated list for prompt."""
    if not predicates:
        return "TREATS, INCREASES_RISK, INDICATES, ASSOCIATED_WITH, SAME_AS, SUBTYPE_OF, etc."
    return ", ".join(sorted(predicates.keys()))


def _format_vocab_section(vocab_entries: list[dict[str, Any]]) -> str:
    """Format vocab entries for prompt appendix."""
    if not vocab_entries:
        return ""
    subset = sorted(vocab_entries, key=lambda e: (e.get("name") or "").lower())[:500]
    lines = [f"- {e.get('name', '')} ({e.get('type', '')})" for e in subset if e.get("name")]
    vocab_text = "\n".join(lines) if lines else "(none)"
    return "\n\n---\n\nThe following entities have already been identified across the corpus. " "Use these exact names and types where applicable rather than creating new variants:\n\n" + vocab_text


def render_extraction_prompt(
    config_dir: Optional[Path] = None,
    vocab_entries: Optional[list[dict[str, Any]]] = None,
    domain_spec: Optional[Any] = None,
) -> str:
    """Render entity/relationship extraction prompt from config and optional vocab.

    When domain_spec is provided, uses it as single source of truth (ENTITY_CLASSES,
    PREDICATES, PROMPT_INSTRUCTIONS). Otherwise loads from config_dir.

    Args:
        config_dir: Directory containing entity_types.yaml, predicates.yaml,
            domain_instructions.md. Ignored when domain_spec is provided.
        vocab_entries: Optional list of {"name", "type", ...} for corpus vocab.
        domain_spec: Optional module with ENTITY_CLASSES, PREDICATES, PROMPT_INSTRUCTIONS.

    Returns:
        Full prompt string for LLM.
    """
    template_dir = Path(__file__).resolve().parent
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default=False),
    )
    template = env.get_template("entity_relationship_extraction.j2")

    if domain_spec is None and config_dir is None:
        raise ValueError("Either domain_spec or config_dir must be provided")

    if domain_spec is not None:
        entity_types_str, predicates_str, domain_instructions = _format_from_domain_spec(domain_spec)
    else:
        assert config_dir is not None  # validated above
        entity_types, predicates, domain = _load_config(config_dir)
        entity_types_str = _format_entity_types_for_prompt(entity_types)
        predicates_str = _format_predicates_for_prompt(predicates)
        domain_instructions = domain.strip() + "\n\n" if domain.strip() else ""
    vocab_section = _format_vocab_section(vocab_entries or [])

    return template.render(
        entity_types=entity_types_str,
        predicates=predicates_str,
        domain_instructions=domain_instructions,
        vocab_section=vocab_section,
    )
