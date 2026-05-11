#!/usr/bin/env python3
"""
Poor man's literate programming preprocessor.

Processes a Python file in source order, emitting:
  - Top-level string literals verbatim as markdown
  - Markdown summaries (signature + docstring) for top-level functions and classes

Example usage:
$ docker run -it --rm -v "$(pwd):/work" python:3.13-bookworm \
    python3 /work/proc.py /work/example.py > example.md
"""

import ast
import sys
import textwrap
from pathlib import Path


def _type_str(node: ast.expr | None) -> str:
    return ast.unparse(node) if node is not None else ""


def _render_function(node: ast.FunctionDef | ast.AsyncFunctionDef, level: int = 2) -> str:
    args = node.args
    defaults = args.defaults
    default_offset = len(args.args) - len(defaults)

    params: list[str] = []
    for i, arg in enumerate(args.args):
        if arg.arg == "self":
            continue
        part = arg.arg
        if arg.annotation:
            part += f": {_type_str(arg.annotation)}"
        if i >= default_offset:
            part += f" = {ast.unparse(defaults[i - default_offset])}"
        params.append(part)

    # *args
    if args.vararg:
        part = f"*{args.vararg.arg}"
        if args.vararg.annotation:
            part += f": {_type_str(args.vararg.annotation)}"
        params.append(part)

    # keyword-only args
    kw_defaults = args.kw_defaults
    for i, arg in enumerate(args.kwonlyargs):
        part = arg.arg
        if arg.annotation:
            part += f": {_type_str(arg.annotation)}"
        if kw_defaults[i] is not None:
            part += f" = {ast.unparse(kw_defaults[i])}"
        params.append(part)

    # **kwargs
    if args.kwarg:
        part = f"**{args.kwarg.arg}"
        if args.kwarg.annotation:
            part += f": {_type_str(args.kwarg.annotation)}"
        params.append(part)

    ret = f" -> {_type_str(node.returns)}" if node.returns else ""
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    signature = f"`{prefix}def {node.name}({', '.join(params)}){ret}`"

    hashes = "#" * level
    chunks = [f"{hashes} `{node.name}`", "", signature]

    docstring = ast.get_docstring(node)
    if docstring:
        chunks += ["", textwrap.dedent(docstring).strip()]

    return "\n".join(chunks)


def _render_class(node: ast.ClassDef) -> str:
    chunks = [f"## Class `{node.name}`"]

    bases = [ast.unparse(b) for b in node.bases]
    if bases:
        chunks.append(f"\nInherits from: {', '.join(f'`{b}`' for b in bases)}")

    docstring = ast.get_docstring(node)
    if docstring:
        chunks += ["", textwrap.dedent(docstring).strip()]

    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunks += ["", _render_function(item, level=3)]

    return "\n".join(chunks)


def process(source: str) -> str:
    tree = ast.parse(source)
    sections: list[str] = []

    for node in tree.body:
        match node:
            case ast.Expr(value=ast.Constant(value=str() as s)):
                sections.append(textwrap.dedent(s).strip())
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                sections.append(_render_function(node, level=2))
            case ast.ClassDef():
                sections.append(_render_class(node))
            # Everything else (imports, assignments, etc.) is silently skipped.

    return "\n\n---\n\n".join(sections) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.py>", file=sys.stderr)
        sys.exit(1)
    print(process(Path(sys.argv[1]).read_text()))
