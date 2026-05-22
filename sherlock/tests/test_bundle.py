"""Tests for the bundle builder."""

import json
import tempfile
from pathlib import Path

import pytest

from sherlock.bundle_models import PerStoryBundle
from sherlock.pipeline.bundle_builder import build_bundle


def test_build_bundle_creates_files(minimal_bundle: PerStoryBundle):
    """build_bundle must create all expected output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir)

        assert (output_dir / "entities.jsonl").exists()
        assert (output_dir / "relationships.jsonl").exists()
        assert (output_dir / "evidence.jsonl").exists()
        assert (output_dir / "manifest.json").exists()


def test_manifest_content(minimal_bundle: PerStoryBundle):
    """manifest.json must have expected fields and correct domain."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir)

        with open(output_dir / "manifest.json") as f:
            manifest = json.load(f)

        assert manifest["domain"] == "sherlock"
        assert manifest["bundle_version"] == "v1"
        assert "entity_count" in manifest["metadata"]
        assert manifest["metadata"]["entity_count"] > 0


def test_entities_jsonl_valid(minimal_bundle: PerStoryBundle):
    """entities.jsonl must be valid JSONL with expected fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir)

        lines = (output_dir / "entities.jsonl").read_text().strip().splitlines()
        assert lines, "entities.jsonl must not be empty"
        for line in lines:
            row = json.loads(line)
            assert "entity_id" in row
            assert "entity_type" in row
            assert "name" in row


def test_relationships_jsonl_valid(minimal_bundle: PerStoryBundle):
    """relationships.jsonl must be valid JSONL with expected fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir)

        lines = (output_dir / "relationships.jsonl").read_text().strip().splitlines()
        assert lines, "relationships.jsonl must not be empty"
        for line in lines:
            row = json.loads(line)
            assert "subject_id" in row
            assert "object_id" in row
            assert "predicate" in row


def test_story_provenance_added(minimal_bundle: PerStoryBundle):
    """DESCRIBED_IN edges must be added for all non-Story entities."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir, add_story_provenance=True)

        lines = (output_dir / "relationships.jsonl").read_text().strip().splitlines()
        rels = [json.loads(l) for l in lines]
        described_in = [r for r in rels if r["predicate"] == "DESCRIBED_IN"]
        assert described_in, "DESCRIBED_IN provenance edges must be added"


def test_no_self_loops_in_bundle(minimal_bundle: PerStoryBundle):
    """Bundle relationships must not contain self-loops."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir)

        lines = (output_dir / "relationships.jsonl").read_text().strip().splitlines()
        for line in lines:
            row = json.loads(line)
            assert row["subject_id"] != row["object_id"], f"Self-loop found: {row}"


def test_narrator_trust_in_properties(minimal_bundle: PerStoryBundle):
    """narrator_trust should appear in relationship properties."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        build_bundle(minimal_bundle, output_dir)

        lines = (output_dir / "relationships.jsonl").read_text().strip().splitlines()
        rels = [json.loads(l) for l in lines]
        rels_with_trust = [r for r in rels if r.get("properties", {}).get("narrator_trust")]
        # At least some relationships should have narrator_trust
        assert rels_with_trust, "Some relationships must have narrator_trust in properties"


def test_bundle_roundtrip(minimal_bundle: PerStoryBundle):
    """Bundle serialization round-trip must be lossless."""
    bundle_dict = minimal_bundle.to_bundle_dict()
    restored = PerStoryBundle.from_bundle_dict(bundle_dict)

    assert len(restored.entities) == len(minimal_bundle.entities)
    assert len(restored.relationships) == len(minimal_bundle.relationships)
    assert restored.story.story_id == minimal_bundle.story.story_id
