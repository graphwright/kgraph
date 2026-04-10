"""Load medlit pipeline config from TOML (e.g. medlit.toml).

Config file is looked up in order:
  1. Path in MEDLIT_CONFIG env var (if set)
  2. medlit.toml in the medlit package directory
  3. medlit.toml in the current working directory

If no file is found, built-in defaults are used (window_size=1536, overlap=400).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore[assignment, misc]

# Built-in defaults (smaller windows to reduce LLM context and timeouts)
DEFAULT_WINDOW_SIZE = 1536
DEFAULT_OVERLAP = 400


def _default_config_paths() -> list[Path]:
    """Return paths to check for medlit.toml (first existing wins)."""
    paths: list[Path] = []
    if os.environ.get("MEDLIT_CONFIG"):
        paths.append(Path(os.environ["MEDLIT_CONFIG"]))
    # Package dir: .../medlit/pipeline/config.py -> .../medlit
    pkg_dir = Path(__file__).resolve().parent.parent
    paths.append(pkg_dir / "medlit.toml")
    paths.append(Path.cwd() / "medlit.toml")
    return paths


def load_medlit_config() -> dict[str, Any]:
    """Load medlit config from TOML file.

    Returns:
        Config dict with at least "chunker" key containing window_size and overlap.
        Uses DEFAULT_WINDOW_SIZE and DEFAULT_OVERLAP if no file or [chunker] section.
    """
    out: dict[str, Any] = {
        "chunker": {
            "window_size": DEFAULT_WINDOW_SIZE,
            "overlap": DEFAULT_OVERLAP,
        }
    }
    if tomllib is None:
        return out
    for path in _default_config_paths():
        if path.is_file():
            try:
                with open(path, "rb") as f:
                    data = tomllib.load(f)
            except (OSError, ValueError):
                continue
            chunker = data.get("chunker")
            if isinstance(chunker, dict):
                if "window_size" in chunker and isinstance(chunker["window_size"], int):
                    out["chunker"]["window_size"] = chunker["window_size"]
                if "overlap" in chunker and isinstance(chunker["overlap"], int):
                    out["chunker"]["overlap"] = chunker["overlap"]
            break
    return out
