# query/bundle_loader.py
"""
Bundle loading utilities for the KG server.
Handles loading bundles from directories or ZIP files at startup.
"""

import json
import os
import sys
import logging
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from sqlmodel import Session, SQLModel, delete

from kgbundle import BundleManifestV1
from storage.interfaces import StorageInterface
from storage.backends.sqlite import SQLiteStorage
from storage.backends.postgres import PostgresStorage

from storage.models.bundle import Bundle
from storage.models.entity import Entity
from storage.models.relationship import Relationship

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
FORMAT = "%(levelname)s:     %(asctime)s - %(pathname)s:%(lineno)d - %(message)s"
formatter = logging.Formatter(FORMAT)
ch.setFormatter(formatter)
logger.addHandler(ch)


def load_bundle_at_startup(engine, db_url: str) -> None:
    """
    Load a bundle at server startup if BUNDLE_PATH is set.

    Environment variables:
        BUNDLE_PATH: Path to a bundle directory or ZIP file
    """
    bundle_path_str = os.getenv("BUNDLE_PATH")
    logger.info("bundle_path=%s", bundle_path_str)
    if not bundle_path_str:
        print("BUNDLE_PATH not set, skipping bundle load.")
        return

    bundle_path = Path(bundle_path_str)
    if not bundle_path.exists():
        print(f"Warning: BUNDLE_PATH '{bundle_path}' does not exist, skipping bundle load.")
        return

    logger.info("Loading bundle from: %s", bundle_path)

    # Ensure tables exist
    SQLModel.metadata.create_all(engine)

    # Handle ZIP file vs directory
    if bundle_path.suffix == ".zip":
        _load_from_zip(engine, db_url, bundle_path)
    elif bundle_path.is_dir():
        _load_from_directory(engine, db_url, bundle_path)
    else:
        print(f"Warning: BUNDLE_PATH '{bundle_path}' is not a directory or ZIP file.")


def _load_from_zip(engine, db_url: str, zip_path: Path) -> None:
    """Extract and load a bundle from a ZIP file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)

        # Find the manifest - could be at root or in a subdirectory
        tmpdir_path = Path(tmpdir)
        manifest_path = _find_manifest(tmpdir_path)
        if not manifest_path:
            print(f"Error: No manifest.json found in ZIP file {zip_path}")
            return

        bundle_dir = manifest_path.parent
        _do_load(engine, db_url, bundle_dir, manifest_path)


def _load_from_directory(engine, db_url: str, bundle_dir: Path) -> None:
    """Load a bundle from a directory."""
    manifest_path = _find_manifest(bundle_dir)
    if not manifest_path:
        print(f"Error: No manifest.json found in {bundle_dir}")
        return

    bundle_dir = manifest_path.parent
    _do_load(engine, db_url, bundle_dir, manifest_path)


def _find_manifest(search_dir: Path) -> Path | None:
    """Find manifest.json in a directory (possibly in a subdirectory)."""
    # Check directly in the directory
    direct = search_dir / "manifest.json"
    if direct.exists():
        return direct

    # Check one level of subdirectories
    for subdir in search_dir.iterdir():
        if subdir.is_dir():
            manifest = subdir / "manifest.json"
            if manifest.exists():
                return manifest

    return None


def _get_docs_destination_path(asset_path: str, app_docs: Path) -> Path | None:
    """Determine the destination path for a documentation asset."""
    # Destination in /app/docs (strip "docs/" prefix if present)
    if asset_path.startswith("docs/"):
        rel_path = asset_path[5:]  # Remove "docs/" prefix
    else:
        rel_path = asset_path

    # Special handling for mkdocs.yml - move to app root
    if rel_path == "mkdocs.yml" or asset_path.endswith("/mkdocs.yml"):
        app_root = os.environ.get("KGSERVER_APP_ROOT", "/app")
        return Path(app_root) / "mkdocs.yml"

    # Regular file - copy to /app/docs preserving structure
    return app_docs / rel_path


def _process_single_doc_asset(line: str, bundle_dir: Path, app_docs: Path) -> bool:
    """Process a single documentation asset entry."""
    try:
        asset = json.loads(line)
        asset_path = asset.get("path")
        if not asset_path:
            logger.warning("Skipping asset entry without path: %s", line)
            return False

        # Source file in bundle
        source_file = bundle_dir / asset_path
        if not source_file.exists():
            logger.warning("Asset file not found: %s", source_file)
            return False

        dest_path = _get_docs_destination_path(asset_path, app_docs)
        if not dest_path:
            logger.warning("Could not determine destination path for asset: %s", asset_path)
            return False

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, dest_path)
        logger.info("Copied %s to %s", source_file, dest_path)
        return True

    except json.JSONDecodeError as e:
        logger.warning("Failed to parse asset entry: %s... Error: %s", line[:100], e)
        return False


def _load_doc_assets(bundle_dir: Path, manifest: BundleManifestV1) -> None:
    """Load documentation assets from doc_assets.jsonl into docs directory.

    Reads the doc_assets.jsonl file (if present) and copies all listed assets
    to the docs directory, preserving directory structure. Special handling for
    mkdocs.yml which is moved to the app root.

    The docs directory defaults to /app/docs (for Docker) but can be overridden
    via the KGSERVER_DOCS_DIR environment variable for local development.

    Note: These are human-readable documentation files (markdown, images, etc.),
    NOT source documents (papers, articles) used for entity extraction.
    """
    if not manifest.doc_assets:
        return

    doc_assets_file = bundle_dir / manifest.doc_assets.path
    if not doc_assets_file.exists():
        logger.warning("Doc assets file %s not found, skipping documentation asset loading", doc_assets_file)
        return

    # Allow override for local development (default: /app/docs for Docker)
    docs_dir = os.environ.get("KGSERVER_DOCS_DIR", "/app/docs")
    app_docs = Path(docs_dir)
    app_docs.mkdir(parents=True, exist_ok=True)

    asset_count = 0
    with open(doc_assets_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if _process_single_doc_asset(line, bundle_dir, app_docs):
                asset_count += 1

    if asset_count > 0:
        logger.info("Loaded %s documentation assets to %s", asset_count, app_docs)
        _build_mkdocs_if_present()


def _build_mkdocs_if_present():
    """Build MkDocs documentation if mkdocs.yml exists and site is not already prebuilt."""
    app_root = Path(os.environ.get("KGSERVER_APP_ROOT", "/app"))
    mkdocs_yml = app_root / "mkdocs.yml"
    site_index = app_root / "site" / "index.html"
    if not mkdocs_yml.exists():
        return
    if site_index.exists():
        logger.info("Using prebuilt site, skipping MkDocs build after doc asset load")
        return
    code_reference_script = app_root / "scripts" / "build_code_reference.py"
    if code_reference_script.exists():
        logger.info("Generating code-reference markdown...")
        code_ref_result = subprocess.run(
            ["uv", "run", "python", str(code_reference_script)],
            cwd=str(app_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if code_ref_result.returncode != 0:
            logger.warning("Code-reference generation failed: %s", code_ref_result.stderr)
    logger.info("Building MkDocs documentation...")
    result = subprocess.run(
        ["uv", "run", "zensical", "build"],
        cwd=str(app_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        logger.info("MkDocs build completed successfully")
    else:
        logger.warning("MkDocs build failed: %s", result.stderr)


def _initialize_storage(session: Session, db_url: str) -> StorageInterface:
    """Initialize and return the appropriate StorageInterface."""
    if db_url.startswith("postgres"):
        return PostgresStorage(session)
    else:
        db_path = db_url.replace("sqlite:///", "")
        if not db_path:
            db_path = ":memory:" if db_url == "sqlite:///:memory:" else "./test.db"
        return SQLiteStorage(db_path)


def _handle_force_reload(session: Session, bundle_id: str, storage: StorageInterface) -> bool:
    """Handle force reload logic, returning True if bundle should be skipped."""
    force = os.getenv("BUNDLE_FORCE_RELOAD", "").lower() in {"1", "true", "yes"}
    if storage.is_bundle_loaded(bundle_id) and not force:
        logger.info("Bundle %s already loaded. Skipping.", bundle_id)
        return True

    if force:
        logger.info("Force reload enabled: clearing Bundle, Relationship, and Entity tables...")
        session.exec(delete(Bundle))
        session.exec(delete(Relationship))
        session.exec(delete(Entity))
        session.commit()
    return False


def _do_load(engine, db_url: str, bundle_dir: Path, manifest_path: Path) -> None:
    """Actually load the bundle into storage."""
    # Parse manifest
    manifest = BundleManifestV1.model_validate_json(manifest_path.read_text())
    logger.info("Loaded manifest for bundle: %s (domain: %s)", manifest.bundle_id, manifest.domain)

    # Load documentation assets if present (NOT source documents)
    _load_doc_assets(bundle_dir, manifest)

    # Use bundle-specific GraphQL examples if provided
    bundle_examples = bundle_dir / "graphql_examples.yml"
    if bundle_examples.exists():
        from query.graphql_examples import load_examples

        load_examples(bundle_examples)
        logger.info("Loaded bundle-specific GraphQL examples from %s", bundle_examples)

    with Session(engine) as session:
        storage = _initialize_storage(session, db_url)
        if _handle_force_reload(session, manifest.bundle_id, storage):
            return

        storage.load_bundle(manifest, str(bundle_dir))
        logger.info("Bundle %s loaded successfully.", manifest.bundle_id)
