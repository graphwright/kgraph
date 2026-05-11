"""Tests for scripts/build_code_reference.py."""

from pathlib import Path

from scripts.build_code_reference import build_code_reference


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_code_reference_generates_expected_structure(tmp_path: Path) -> None:
    """Generator writes package/module pages and excludes tests/cache paths."""
    _write(
        tmp_path / "proc.py",
        """def process(source: str) -> str:\n    return source.strip() + "\\n"\n""",
    )

    _write(tmp_path / "kgraph" / "__init__.py", '"""kgraph package docs"""')
    _write(tmp_path / "kgraph" / "module_a.py", '"""module a"""')
    _write(tmp_path / "kgraph" / "tests" / "test_skip.py", '"""skip me"""')
    _write(tmp_path / "kgserver" / "query.py", '"""query docs"""')
    _write(tmp_path / "kgbundle" / "kgbundle" / "__init__.py", '"""bundle docs"""')
    _write(tmp_path / "kgschema" / "__pycache__" / "ignored.py", '"""ignore cache"""')

    output_dir = tmp_path / "docs" / "code-reference" / "generated"
    build_code_reference(repo_root=tmp_path, output_dir=output_dir)

    assert (output_dir / "kgraph" / "__init__.md").exists()
    assert (output_dir / "kgraph" / "module_a.md").exists()
    assert (output_dir / "kgserver" / "query.md").exists()
    assert (output_dir / "kgbundle" / "kgbundle" / "__init__.md").exists()

    assert not (output_dir / "kgraph" / "tests" / "test_skip.md").exists()
    assert not (output_dir / "kgschema" / "__pycache__" / "ignored.md").exists()

    assert (output_dir / "index.md").exists()
    assert (output_dir / "kgraph" / "index.md").exists()
    assert (output_dir / "kgserver" / "index.md").exists()
    assert (output_dir / "kgbundle" / "index.md").exists()
    assert (output_dir / "kgschema" / "index.md").exists()


def test_build_code_reference_module_title_uses_package_name_for_init(tmp_path: Path) -> None:
    """`__init__.py` pages use package module names without __init__ suffix."""
    _write(
        tmp_path / "proc.py",
        """def process(source: str) -> str:\n    return source.strip() + "\\n"\n""",
    )
    _write(tmp_path / "kgraph" / "__init__.py", '"""root package"""')

    output_dir = tmp_path / "docs" / "code-reference" / "generated"
    build_code_reference(repo_root=tmp_path, output_dir=output_dir)

    content = (output_dir / "kgraph" / "__init__.md").read_text(encoding="utf-8")
    assert "# `kgraph`" in content
