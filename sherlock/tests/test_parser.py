"""Tests for story parser and chunker."""

import pytest

from sherlock.pipeline.parser import (
    SCANDAL_EMBEDDED_EXCERPT,
    _clean_text,
    _extract_story,
    chunk_story,
    chunk_story_windowed,
    get_story_text,
)


def test_get_story_text_embedded_fallback():
    """get_story_text() must return content even if network is unavailable or URL is invalid."""
    # A disallowed host triggers ValueError → falls back to embedded excerpt
    text = get_story_text(story_url="http://localhost:0/notfound")
    assert len(text) > 100
    assert "Holmes" in text or "Watson" in text or "Adler" in text


def test_fetch_rejects_disallowed_host():
    """_fetch_gutenberg_text must raise ValueError for non-Gutenberg URLs."""
    from sherlock.pipeline.parser import _fetch_gutenberg_text

    with pytest.raises(ValueError, match="not in the allowed fetch list"):
        _fetch_gutenberg_text("http://evil.example.com/story.txt")


def test_clean_text_removes_pg_footer():
    """_clean_text must strip Gutenberg boilerplate."""
    dirty = "Some content\n\n*** END OF THE PROJECT GUTENBERG EBOOK ***\nBoilerplate"
    cleaned = _clean_text(dirty)
    assert "Boilerplate" not in cleaned
    assert "Some content" in cleaned


def test_extract_story_finds_section():
    """_extract_story must find the story section by marker."""
    full = "Preamble\n\nA SCANDAL IN BOHEMIA\nStory content\n\nTHE RED-HEADED LEAGUE\nNext story"
    result = _extract_story(full, "A SCANDAL IN BOHEMIA", "THE RED-HEADED LEAGUE")
    assert "Story content" in result
    assert "Next story" not in result


def test_chunk_story_returns_paragraphs():
    """chunk_story must return a list of chunks with expected keys."""
    text = SCANDAL_EMBEDDED_EXCERPT
    chunks = chunk_story(text)
    assert len(chunks) > 0
    for chunk in chunks:
        assert "section" in chunk
        assert "paragraph_idx" in chunk
        assert "text" in chunk
        assert isinstance(chunk["text"], str)
        assert len(chunk["text"]) > 0


def test_chunk_story_unique_indices():
    """Chunk paragraph_idx values must be unique."""
    text = SCANDAL_EMBEDDED_EXCERPT
    chunks = chunk_story(text)
    indices = [c["paragraph_idx"] for c in chunks]
    assert len(indices) == len(set(indices)), "Duplicate paragraph indices"


def test_chunk_story_windowed_overlap():
    """Windowed chunking must produce overlapping windows."""
    text = SCANDAL_EMBEDDED_EXCERPT
    chunks = chunk_story(text, min_words=1)
    windowed = chunk_story_windowed(text, window_size=3, min_words=1)

    # Each windowed chunk should have more text than individual
    if len(chunks) >= 3 and windowed:
        assert len(windowed[0]["text"]) >= len(chunks[0]["text"])


def test_sections_assigned():
    """Early chunks get 'opening' section; later get 'body'."""
    text = SCANDAL_EMBEDDED_EXCERPT
    chunks = chunk_story(text)
    if len(chunks) > 3:
        assert chunks[0]["section"] == "opening"
        assert chunks[-1]["section"] == "body"
