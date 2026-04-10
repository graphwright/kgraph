# medlit/scripts/parse_pmc_xml.py
"""Parse PMC JATS-XML files directly to Paper schema JSON format.

This script combines XML parsing and schema conversion into a single step,
converting JATS-XML files directly to the format expected by JournalArticleParser.
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import Any
import argparse


def parse_pmc_xml_to_paper_schema(xml_path: Path) -> dict:
    """Parse PMC XML file directly into Paper schema JSON format.

    Args:
        xml_path: Path to the PMC XML file

    Returns:
        Dictionary in Paper schema format with:
        - paper_id: PMC ID (from filename)
        - title: Article title
        - abstract: Dict with "text" key containing abstract
        - full_text: Full body text (if available)
        - authors: List of author names
        - metadata: Dict with keywords (if available)
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract basic metadata
    article_meta = root.find(".//article-meta")

    # Use pmc_id as paper_id (from filename, e.g., PMC10759991)
    paper_id = xml_path.stem

    # Title
    title = ""
    title_elem = article_meta.find(".//article-title") if article_meta else None
    if title_elem is not None:
        title = "".join(title_elem.itertext()).strip()

    # Abstract - convert to object with "text" key
    abstract_text = ""
    abstract_elem = root.find(".//abstract")
    if abstract_elem is not None:
        abstract_text = "".join(abstract_elem.itertext()).strip()
    abstract = {"text": abstract_text} if abstract_text else {"text": ""}

    # Body text - use as "full_text"
    full_text = ""
    body_elem = root.find(".//body")
    if body_elem is not None:
        full_text = "".join(body_elem.itertext()).strip()

    # Authors
    authors: list[str] = []
    for contrib in root.findall('.//contrib[@contrib-type="author"]'):
        name_elem = contrib.find(".//name")
        if name_elem is not None:
            surname = name_elem.find("surname")
            given = name_elem.find("given-names")
            if surname is not None:
                author = surname.text or ""
                if given is not None and given.text:
                    author = f"{given.text} {author}"
                authors.append(author)

    # Keywords
    keywords: list[str] = []
    for kwd in root.findall(".//kwd"):
        if kwd.text:
            keywords.append(kwd.text.strip())

    # Build Paper schema structure
    paper: dict[str, Any] = {
        "paper_id": paper_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
    }

    # Add full_text if it exists
    if full_text:
        paper["full_text"] = full_text

    # Add metadata if keywords exist
    if keywords:
        paper["metadata"] = {"keywords": keywords}

    return paper


def main():
    parser = argparse.ArgumentParser(description="Parse PMC JATS-XML files directly to Paper schema JSON format")
    parser.add_argument("--input-dir", required=True, help="Directory with XML files")
    parser.add_argument("--output-dir", required=True, help="Output directory for JSON files")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    xml_files = list(input_dir.glob("*.xml"))
    print(f"Found {len(xml_files)} XML files")

    converted_count = 0
    for xml_file in xml_files:
        try:
            paper = parse_pmc_xml_to_paper_schema(xml_file)
            json_file = output_dir / f"{xml_file.stem}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(paper, f, indent=2, ensure_ascii=False)
            converted_count += 1
            if converted_count % 10 == 0:
                print(f"Converted {converted_count} files...")
        except Exception as e:
            print(f"Error parsing {xml_file.name}: {e}")

    print(f"\nConverted {converted_count} files to {output_dir}")


if __name__ == "__main__":
    main()
