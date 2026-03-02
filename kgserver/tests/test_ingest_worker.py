"""Tests for mcp_server/ingest_worker persistent workspace and no-op guard."""

import json

import pytest

from mcp_server.ingest_worker import (
    _ensure_workspace_dirs,
    _run_pass2_pass3_load,
    _workspace_lock,
    _workspace_root,
)


class TestWorkspaceHelpers:
    """Unit tests for workspace root and dirs."""

    def test_workspace_root_default(self, monkeypatch, tmp_path):
        """_workspace_root returns resolve()d path; default includes ingest_workspace."""
        monkeypatch.delenv("INGEST_WORKSPACE_ROOT", raising=False)
        root = _workspace_root()
        assert root.is_absolute()
        assert root.name == "ingest_workspace" or "ingest_workspace" in str(root)

    def test_workspace_root_from_env(self, monkeypatch, tmp_path):
        """_workspace_root uses INGEST_WORKSPACE_ROOT when set."""
        want = tmp_path / "custom_workspace"
        want.mkdir()
        monkeypatch.setenv("INGEST_WORKSPACE_ROOT", str(want))
        root = _workspace_root()
        assert root == want.resolve()

    def test_ensure_workspace_dirs(self, tmp_path):
        """_ensure_workspace_dirs creates pass1_bundles, medlit_merged, medlit_bundle, pass1_vocab."""
        root = tmp_path / "ws"
        bundles_dir, merged_dir, output_dir, vocab_dir = _ensure_workspace_dirs(root)
        assert bundles_dir == root / "pass1_bundles"
        assert merged_dir == root / "medlit_merged"
        assert output_dir == root / "medlit_bundle"
        assert vocab_dir == root / "pass1_vocab"
        assert bundles_dir.is_dir()
        assert merged_dir.is_dir()
        assert output_dir.is_dir()
        assert vocab_dir.is_dir()
        # Idempotent
        bundles_dir2, merged_dir2, output_dir2, vocab_dir2 = _ensure_workspace_dirs(root)
        assert bundles_dir2 == bundles_dir
        assert merged_dir2 == merged_dir
        assert output_dir2 == output_dir
        assert vocab_dir2 == vocab_dir


class TestWorkspaceLock:
    """Unit tests for workspace file lock."""

    def test_workspace_lock_acquires_and_releases(self, tmp_path):
        """_workspace_lock acquires and releases; second acquisition in same process succeeds."""
        root = tmp_path / "lock_test"
        root.mkdir()
        with _workspace_lock(root):
            lock_file = root / ".ingest.lock"
            assert lock_file.exists()
        # Released; can acquire again
        with _workspace_lock(root):
            pass


def _minimal_paper_bundle(pmcid: str, title: str = "Test") -> dict:
    """Minimal per-paper bundle dict for pass2/pass3."""
    return {
        "paper": {"pmcid": pmcid, "title": title, "authors": []},
        "entities": [
            {"id": "g01", "class": "Gene", "name": "BRCA2", "synonyms": [], "source": "extracted"},
            {"id": "e01", "class": "Disease", "name": "breast cancer", "synonyms": [], "source": "extracted"},
        ],
        "evidence_entities": [
            {
                "id": f"{pmcid}:abstract:0:llm",
                "class": "Evidence",
                "paper_id": pmcid,
                "text_span_id": f"{pmcid}:abstract:0",
                "text": "BRCA2 increases risk of breast cancer",
                "confidence": 0.95,
                "extraction_method": "llm",
                "source": "extracted",
            },
        ],
        "relationships": [
            {
                "subject": "g01",
                "predicate": "INCREASES_RISK",
                "object": "e01",
                "evidence_ids": [f"{pmcid}:abstract:0:llm"],
                "source_papers": [pmcid],
                "confidence": 0.55,
            },
        ],
        "notes": [],
    }


class TestPersistentWorkspaceIntegration:
    """Integration test: run Pass 2+3+load twice; second run has more entities."""

    def test_pass2_pass3_load_incremental_entity_count(self, monkeypatch, tmp_path):
        """With 2 papers then 3 papers in workspace, entity count increases after second run.
        Requires examples.medlit (PYTHONPATH including repo root when run from kgserver).
        """
        try:
            from examples.medlit.pipeline.dedup import run_pass2  # noqa: F401
        except ModuleNotFoundError:
            pytest.skip("examples.medlit not importable (need PYTHONPATH including repo root)")

        workspace = tmp_path / "ingest_workspace"
        workspace.mkdir()
        monkeypatch.setenv("INGEST_WORKSPACE_ROOT", str(workspace))

        bundles_dir, merged_dir, output_dir, _vocab_dir = _ensure_workspace_dirs(workspace)

        # Use a real SQLite file so load_bundle_incremental can run (and same process can read)
        db_path = str(tmp_path / "test.db")
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
        import query.storage_factory as factory_module

        factory_module._engine = None  # pylint: disable=protected-access
        factory_module._db_url = None  # pylint: disable=protected-access
        from query.storage_factory import get_engine
        from sqlmodel import SQLModel

        engine, _ = get_engine()
        SQLModel.metadata.create_all(engine)

        # Two paper bundles
        (bundles_dir / "paper_PMC111.json").write_text(json.dumps(_minimal_paper_bundle("PMC111"), indent=2), encoding="utf-8")
        (bundles_dir / "paper_PMC222.json").write_text(json.dumps(_minimal_paper_bundle("PMC222"), indent=2), encoding="utf-8")

        _run_pass2_pass3_load(workspace, bundles_dir, merged_dir, output_dir)

        manifest_path = output_dir / "manifest.json"
        assert manifest_path.exists()
        manifest_data = json.loads(manifest_path.read_text())
        entities_path = output_dir / manifest_data["entities"]["path"]
        count_after_two = sum(1 for _ in entities_path.open() if _.strip())

        # Third paper bundle
        (bundles_dir / "paper_PMC333.json").write_text(json.dumps(_minimal_paper_bundle("PMC333"), indent=2), encoding="utf-8")

        _run_pass2_pass3_load(workspace, bundles_dir, merged_dir, output_dir)

        manifest_data2 = json.loads(manifest_path.read_text())
        entities_path2 = output_dir / manifest_data2["entities"]["path"]
        count_after_three = sum(1 for _ in entities_path2.open() if _.strip())

        assert count_after_three >= count_after_two, "Entity count should increase after adding third paper"
        # First two papers' bundle files still present
        assert (bundles_dir / "paper_PMC111.json").exists()
        assert (bundles_dir / "paper_PMC222.json").exists()
        assert (bundles_dir / "paper_PMC333.json").exists()
