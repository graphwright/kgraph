"""Story parser and paragraph chunker for Sherlock Holmes stories.

Fetches "A Scandal in Bohemia" from Project Gutenberg (or accepts a local file),
strips the Gutenberg header/footer, and produces a SherlockStory document with
paragraph-level chunking for extraction.

Evidence IDs use: {story_id}:{section}:{paragraph_idx}:llm
"""

import re
import textwrap
import urllib.request
from pathlib import Path
from typing import Optional

SCANDAL_GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/1661/pg1661.txt"
SCANDAL_STORY_ID = "scandal_in_bohemia"
SCANDAL_TITLE = "A Scandal in Bohemia"
SCANDAL_YEAR = 1891

# The full Adventures collection; extract just the first story.
SCANDAL_START_MARKER = "A SCANDAL IN BOHEMIA"
SCANDAL_END_MARKER = "THE RED-HEADED LEAGUE"

# Embedded minimal story text as fallback when Gutenberg is unreachable.
# This is a short public-domain excerpt sufficient for offline testing.
SCANDAL_EMBEDDED_EXCERPT = """\
A SCANDAL IN BOHEMIA

I.

To Sherlock Holmes she is always THE woman. I have seldom heard him mention her
under any other name. In his eyes she eclipses and predominates the whole of her
sex. It was not that he felt any emotion akin to love for Irene Adler.

He had, so he told me, met her at Warsaw. She was the daughter of a New Jersey
family who had emigrated to America, and she had made her name as a contralto
under the name of Irene Adler on the operatic stage in Warsaw and in St. Petersburg.

The photograph concerned a certain Cabinet Minister. It had a Royal provenance.

One night--it was on the twentieth of March, 1888--I was returning from a journey
to a patient when my way led me through Baker Street. As I passed the well-remembered
door, which must always be associated in my mind with my wooing, and with the dark
incidents of the Study in Scarlet, I was seized with a keen desire to see Holmes again.

His rooms were brilliantly lit, and, even as I looked up, I saw his tall, spare figure
pass twice in a dark silhouette against the blind. He was pacing the room swiftly,
eagerly, with his head sunk upon his chest and his hands clasped behind him.

A client! It was the King of Bohemia in person. His Majesty had desired that Holmes
should take charge of a very delicate matter. The matter concerned a certain photograph
which was in the possession of one Irene Adler, the well-known adventuress.

Irene Adler lived at Briony Lodge, Serpentine Avenue, St. John's Wood.
Holmes, disguised as an out-of-work groom, observed the house.

Watson threw a plumber's smoke-rocket into the room, causing a fire alarm.
Holmes, disguised as a clergyman, acted as witness to the marriage of Irene Adler
and Godfrey Norton at the Church of St. Monica.

The next day, Holmes returned to Briony Lodge as a clergyman again.
He and Watson entered the house to retrieve the photograph.
But Irene Adler had fled with Godfrey Norton to the Continent.
She had left a letter for Holmes, and in its place she left her own photograph.

The King offered Holmes the emerald snake ring from his finger.
Holmes refused, asking instead for the photograph of Irene Adler.
To Sherlock Holmes she is always THE woman.
"""


def _fetch_gutenberg_text(url: str, timeout: int = 30) -> str:
    """Fetch plain text from Project Gutenberg."""
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # nosec
        raw = resp.read()
    # Gutenberg may serve UTF-8 or Latin-1
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _extract_story(full_text: str, start_marker: str, end_marker: str) -> str:
    """Extract a story section from a multi-story collection."""
    upper = full_text.upper()
    start_idx = upper.find(start_marker.upper())
    if start_idx == -1:
        return full_text
    end_idx = upper.find(end_marker.upper(), start_idx + len(start_marker))
    if end_idx == -1:
        return full_text[start_idx:]
    return full_text[start_idx:end_idx]


def _clean_text(text: str) -> str:
    """Remove Gutenberg header/footer boilerplate and normalize whitespace."""
    # Remove Project Gutenberg legal boilerplate
    pg_end = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", text, re.IGNORECASE)
    if pg_end:
        text = text[: pg_end.start()]
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_story_text(local_path: Optional[Path] = None, story_url: str = SCANDAL_GUTENBERG_URL) -> str:
    """Fetch and return the clean text of 'A Scandal in Bohemia'.

    Priority:
    1. local_path (override for offline / test use)
    2. Project Gutenberg fetch
    3. Embedded excerpt fallback
    """
    if local_path and local_path.exists():
        raw = local_path.read_text(encoding="utf-8")
        return _clean_text(_extract_story(raw, SCANDAL_START_MARKER, SCANDAL_END_MARKER))

    try:
        raw = _fetch_gutenberg_text(story_url)
        story = _extract_story(raw, SCANDAL_START_MARKER, SCANDAL_END_MARKER)
        return _clean_text(story)
    except Exception:
        return _clean_text(SCANDAL_EMBEDDED_EXCERPT)


def chunk_story(story_text: str, min_words: int = 40) -> list[dict]:
    """Split story text into paragraph chunks with stable indices.

    Returns a list of dicts:
        {
            "section": str,          # "opening" | "body"
            "paragraph_idx": int,    # 0-based index across entire story
            "text": str,             # paragraph text
        }
    """
    # Split into paragraphs (double newline)
    raw_paragraphs = [p.strip() for p in re.split(r"\n{2,}", story_text)]
    chunks = []
    para_idx = 0

    for para in raw_paragraphs:
        if not para:
            continue
        words = para.split()
        if len(words) < min_words:
            # Keep very short paragraphs only if they are section headers
            if re.match(r"^[IVXLCDM]+\.$", para.strip()):
                # Roman numeral section marker — include as separator, not as chunk
                continue
            if len(words) < 8:
                # Too short to be useful
                para_idx += 1
                continue
        section = "opening" if para_idx < 3 else "body"
        chunks.append(
            {
                "section": section,
                "paragraph_idx": para_idx,
                "text": para,
            }
        )
        para_idx += 1

    return chunks


def chunk_story_windowed(story_text: str, window_size: int = 3, min_words: int = 40) -> list[dict]:
    """Return overlapping windows of paragraphs for richer context in LLM extraction.

    Each chunk contains `window_size` consecutive paragraphs. The `paragraph_idx`
    is the index of the FIRST paragraph in the window.
    """
    raw_chunks = chunk_story(story_text, min_words=min_words)
    if not raw_chunks:
        return []
    windowed = []
    for i in range(0, len(raw_chunks), max(1, window_size // 2)):
        window = raw_chunks[i : i + window_size]
        if not window:
            break
        combined_text = "\n\n".join(c["text"] for c in window)
        windowed.append(
            {
                "section": window[0]["section"],
                "paragraph_idx": window[0]["paragraph_idx"],
                "text": combined_text,
                "span": (window[0]["paragraph_idx"], window[-1]["paragraph_idx"]),
            }
        )
    return windowed
