#!/usr/bin/env python3
"""Build MkDocs-ready code-reference markdown from Python source files."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import types
from collections import defaultdict
from pathlib import Path

SOURCE_ROOTS = ("kgraph", "kgserver", "kgbundle", "kgschema")
EXCLUDED_DIR_NAMES = {
    "__pycache__",
    "tests",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


def _load_proc_module(repo_root: Path) -> types.ModuleType:
    proc_path = repo_root / "proc.py"
    if not proc_path.exists():
        raise FileNotFoundError(f"Expected proc.py at {proc_path}")
    spec = importlib.util.spec_from_file_location("proc", proc_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {proc_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_excluded(rel_path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in rel_path.parts)


def discover_python_sources(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for source_root in SOURCE_ROOTS:
        root_path = repo_root / source_root
        if not root_path.exists():
            continue
        for source_file in sorted(root_path.rglob("*.py")):
            rel_path = source_file.relative_to(repo_root)
            if _is_excluded(rel_path):
                continue
            files.append(source_file)
    return files


def _module_name(rel_path: Path) -> str:
    parts = list(rel_path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _render_module_page(processor: types.ModuleType, rel_path: Path, source_text: str) -> str:
    module_name = _module_name(rel_path)
    lines = [
        f"# `{module_name}`",
        "",
        f"_Generated from `{rel_path.as_posix()}`._",
        "",
    ]
    body = processor.process(source_text).strip()
    if body:
        lines.append(body)
    else:
        lines.append("_No top-level markdown literals, function docstrings, or class docstrings found._")
    lines.append("")
    return "\n".join(lines)


def _write_package_indexes(output_root: Path, grouped: dict[str, list[Path]]) -> None:
    root_index_lines = [
        "# Generated Code Reference",
        "",
        "This index is generated at build time by `scripts/build_code_reference.py`.",
        "",
    ]

    for source_root in SOURCE_ROOTS:
        package_docs = sorted(grouped.get(source_root, []))
        package_dir = output_root / source_root
        package_dir.mkdir(parents=True, exist_ok=True)
        package_index_path = package_dir / "index.md"

        package_lines = [
            f"# `{source_root}`",
            "",
            f"Generated from Python files under `{source_root}/`.",
            "",
        ]

        if package_docs:
            for rel_path in package_docs:
                rel_md = rel_path.with_suffix(".md")
                module_name = _module_name(rel_path)
                link = rel_md.relative_to(Path(source_root)).as_posix()
                package_lines.append(f"- [`{module_name}`]({link})")
        else:
            package_lines.append("_No Python modules were found in this source tree._")

        package_lines.append("")
        package_index_path.write_text("\n".join(package_lines), encoding="utf-8")
        root_index_lines.append(f"- [`{source_root}`]({source_root}/index.md)")

    root_index_lines.append("")
    (output_root / "index.md").write_text("\n".join(root_index_lines), encoding="utf-8")


def build_code_reference(repo_root: Path, output_dir: Path) -> None:
    processor = _load_proc_module(repo_root)
    output_root = output_dir if output_dir.is_absolute() else repo_root / output_dir

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[Path]] = defaultdict(list)
    for source_file in discover_python_sources(repo_root):
        rel_path = source_file.relative_to(repo_root)
        grouped[rel_path.parts[0]].append(rel_path)
        out_path = output_root / rel_path.with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(_render_module_page(processor, rel_path, source_file.read_text(encoding="utf-8")), encoding="utf-8")

    _write_package_indexes(output_root, grouped)


def parse_args() -> argparse.Namespace:
    default_repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root,
        help=f"Repository root (default: {default_repo_root})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/code-reference/generated"),
        help="Directory for generated markdown, relative to repo root by default",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_code_reference(repo_root=args.repo_root.resolve(), output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
