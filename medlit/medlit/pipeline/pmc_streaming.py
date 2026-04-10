"""Streaming PMC XML chunker for full-paper extraction.

Yields overlapping text windows from a PMC/JATS XML document without loading
the entire body into a single string. Uses iterparse so the parser does not
hold the full tree in memory; sections are yielded and then cleared.

Use for:
- Entity extraction: run NER on each window, then merge/dedupe mentions.
- Relationship extraction: run relationship extraction on each window with
  the full entity list, then merge relationships.
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from typing import Iterator

# Default window size and overlap for LLM prompts (chars).
# Override via medlit.toml [chunker] or MEDLIT_CONFIG.
DEFAULT_WINDOW_SIZE = 1536
DEFAULT_OVERLAP = 400


def _local_tag(tag: str) -> str:
    """Strip XML namespace from tag for comparison."""
    if tag and "}" in tag:
        return tag.split("}", 1)[1]
    return tag or ""


def iter_pmc_sections(raw_content: bytes) -> Iterator[tuple[str, str]]:
    """Yield (section_id, text) for abstract and each body section.

    Uses iterparse so we do not build a full DOM for the body. After
    yielding each element's text we clear it to free memory. Yields:
    - ("abstract", abstract_text) first if present
    - ("sec_<id>", section_text) for each <sec> (full text of that section,
      including nested secs and paragraphs)

    Namespaces in JATS are stripped so we match "abstract", "body", "sec".
    """
    context = ET.iterparse(io.BytesIO(raw_content), events=("start", "end"))
    in_body = False

    for event, elem in context:
        tag = _local_tag(elem.tag)
        if event == "start" and tag == "body":
            in_body = True
            continue
        if event != "end":
            continue
        if tag == "abstract":
            text = "".join(elem.itertext()).strip()
            if text:
                yield ("abstract", text)
            elem.clear()
        elif in_body and tag == "sec":
            text = "".join(elem.itertext()).strip()
            if text:
                sec_id = elem.get("id", "") if hasattr(elem, "get") else ""
                yield (f"sec_{sec_id}" if sec_id else "sec", text)
            elem.clear()


def iter_overlapping_windows(
    sections: Iterator[tuple[str, str]],
    window_size: int = DEFAULT_WINDOW_SIZE,
    overlap: int = DEFAULT_OVERLAP,
    *,
    include_abstract_separately: bool = True,
) -> Iterator[tuple[int, str]]:
    """Turn a stream of (section_id, text) into overlapping windows.

    Concatenates section texts. When accumulated length reaches window_size,
    yields (window_index, text). Then slides by (window_size - overlap) so
    consecutive windows overlap by `overlap` characters. This helps the LLM
    see context across boundaries and avoids splitting entities.

    If include_abstract_separately is True, the first yielded window is
    always the abstract alone (if any section has section_id == "abstract").
    Subsequent windows are from body content only. Only one window-sized
    buffer is kept in memory.

    Args:
        sections: Iterator of (section_id, text).
        window_size: Target size of each window in characters.
        overlap: Number of characters to overlap between consecutive windows.
        include_abstract_separately: If True, yield abstract as window 0.

    Yields:
        (window_index, text) for each window.
    """
    if overlap >= window_size:
        overlap = max(0, window_size - 500)
    step = window_size - overlap

    buffer = ""
    window_index = 0

    for section_id, text in sections:
        if not text:
            continue
        if include_abstract_separately and section_id == "abstract":
            yield (window_index, text)
            window_index += 1
            continue
        buffer += text + "\n\n"
        while len(buffer) >= window_size:
            yield (window_index, buffer[:window_size].strip())
            window_index += 1
            buffer = buffer[step:]
    if buffer.strip():
        yield (window_index, buffer.strip())


def iter_pmc_windows(
    raw_content: bytes,
    window_size: int = DEFAULT_WINDOW_SIZE,
    overlap: int = DEFAULT_OVERLAP,
    include_abstract_separately: bool = True,
) -> Iterator[tuple[int, str]]:
    """Yield overlapping text windows from PMC XML for full-paper extraction.

    Convenience generator: iter_pmc_sections(raw_content) -> iter_overlapping_windows(...).
    Use when you have raw PMC/XML bytes and want a sequence of prompts (e.g. for
    entity or relationship extraction) without loading the whole paper into one string.

    Args:
        raw_content: Raw bytes of the PMC/JATS XML document.
        window_size: Target characters per window.
        overlap: Overlap between consecutive windows.
        include_abstract_separately: If True, first window is the abstract alone.

    Yields:
        (window_index, text) for each window.
    """
    sections = iter_pmc_sections(raw_content)
    return iter_overlapping_windows(
        sections,
        window_size=window_size,
        overlap=overlap,
        include_abstract_separately=include_abstract_separately,
    )
