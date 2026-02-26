#!/usr/bin/env -S uv run python
"""
Extract documentation from Python source files into Markdown.

Walks the AST to find docstrings, standalone strings, and creates
formatted signatures for classes, methods, and functions.

Includes a portion of each *.md, *.yml, Dockerfile, and shell script
to add more context.

$ git ls-files | uv run python extract_summary.py > summary.md
"""

import ast
import argparse
import glob
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class DocExtractor(ast.NodeVisitor):
    def __init__(self):
        self.sections: List[Tuple[str, str, str, str]] = []  # (type, signature, doc, fields)
        self.current_class = None

    def visit_Module(self, node: ast.Module) -> None:
        """Extract module-level docstring and top-level standalone strings."""
        docstring = ast.get_docstring(node)
        if docstring:
            self.sections.append(("module", "", docstring, ""))

        # Capture other top-level strings (not the docstring)
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                val = stmt.value.value if isinstance(stmt.value, ast.Constant) else stmt.value.s
                if isinstance(val, str) and val != docstring:
                    self.sections.append(("note", "", val, ""))

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = ", ".join(self._format_expr(base) for base in node.bases)
        sig = f"class {node.name}({bases})" if bases else f"class {node.name}"
        docstring = ast.get_docstring(node)

        is_pydantic = self._is_pydantic_model(node)
        fields_md = self._extract_pydantic_fields(node) if is_pydantic else ""

        if docstring or fields_md:
            self.sections.append(("class", sig, docstring or "", fields_md))

        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        args = self._format_arguments(node.args)
        returns = f" -> {self._format_expr(node.returns)}" if node.returns else ""

        if self.current_class:
            sig = f"{prefix}def {self.current_class}.{node.name}({args}){returns}"
            doc_type = "method"
        else:
            sig = f"{prefix}def {node.name}({args}){returns}"
            doc_type = "function"

        docstring = ast.get_docstring(node)
        if docstring:
            self.sections.append((doc_type, sig, docstring, ""))

        self.generic_visit(node)

    def _format_arguments(self, args: ast.arguments) -> str:
        parts = []
        for i, arg in enumerate(args.args):
            annotation = f": {self._format_expr(arg.annotation)}" if arg.annotation else ""
            default_offset = len(args.args) - len(args.defaults)
            if i >= default_offset:
                default = self._format_expr(args.defaults[i - default_offset])
                parts.append(f"{arg.arg}{annotation} = {default}")
            else:
                parts.append(f"{arg.arg}{annotation}")
        if args.vararg:
            parts.append(f"*{args.vararg.arg}")
        if args.kwarg:
            parts.append(f"**{args.kwarg.arg}")
        return ", ".join(parts)

    def _format_expr(self, node) -> str:
        return ast.unparse(node) if node else ""

    def _is_pydantic_model(self, node: ast.ClassDef) -> bool:
        base_names = [self._format_expr(b) for b in node.bases]
        return any("BaseModel" in n or "Entity" in n for n in base_names)

    def _extract_pydantic_fields(self, node: ast.ClassDef) -> str:
        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                name = stmt.target.id
                if not name.startswith("_"):
                    t = self._format_expr(stmt.annotation)
                    fields.append(f"{name}: {t}")
        return "**Fields:**\n\n```python\n" + "\n".join(fields) + "\n```\n" if fields else ""


def _heading_anchor(path: str) -> str:
    s = re.sub(r"[^a-z0-9-]", "", path.lower().replace(" ", "-"))
    return s or "section"


def process_file(path: str) -> str:
    p = Path(path)
    if not p.exists() or p.is_dir():
        return ""

    if p.suffix == ".py":
        try:
            tree = ast.parse(p.read_text())
            extractor = DocExtractor()
            extractor.visit(tree)
            lines = []
            for doc_type, sig, content, fields in extractor.sections:
                if doc_type == "module":
                    lines.append(f"{content}\n")
                elif doc_type == "class":
                    lines.append(f"## `{sig}`\n\n{content}\n{fields}")
                elif doc_type in ("function", "method"):
                    lines.append(f"### `{sig}`\n\n{content}\n")
                elif doc_type == "note":
                    lines.append(f"> {content}\n")
            return "\n".join(lines)
        except Exception as e:
            return f"Error parsing {path}: {e}"

    # Non-python files
    try:
        with open(p) as f:
            lines = [f.readline() for _ in range(10)]
        body = "".join(lines).rstrip()
        ext = p.suffix.lstrip(".")
        lang = "dockerfile" if "Dockerfile" in path else ext if ext in ["yml", "yaml", "sh"] else ""
        return f"```{lang}\n{body}\n\n    ...\n```" if lang else f"{body}\n\n    ..."
    except:
        return f"Could not read {path}"


def main():
    parser = argparse.ArgumentParser(description="Extract documentation and context from files.")
    parser.add_argument("-i", "--include", help="Comma-separated globs (e.g. '*.py,*.md')")
    parser.add_argument("-l", "--list", help="File with list of paths, or '-' for stdin")
    args = parser.parse_args()

    # Default logic: if no arguments provided, act as if -l - was passed
    if args.include is None and args.list is None:
        args.list = "-"

    files = []
    if args.list:
        stream = sys.stdin if args.list == "-" else open(args.list)
        # If reading from stdin and it's a TTY, maybe warn the user?
        # But usually, we just wait for input.
        files = [line.strip() for line in stream if line.strip()]
        if args.list != "-":
            stream.close()
    elif args.include:
        globs = args.include.split(",")
        for g in globs:
            files.extend(glob.glob(g, recursive=True))

    files = sorted(list(set(files)))

    sections = []
    for f in files:
        content = process_file(f)
        if content:
            sections.append((f, content))

    if not sections:
        return

    # Output to stdout
    sys.stdout.write("# Project Summary\n\n## Contents\n\n")
    for path, _ in sections:
        sys.stdout.write(f"- [{path}](#user-content-{_heading_anchor(path)})\n")
    sys.stdout.write("\n---\n\n")

    for path, content in sections:
        sys.stdout.write(f'<span id="user-content-{_heading_anchor(path)}"></span>\n\n# {path}\n\n')
        sys.stdout.write(content)
        sys.stdout.write("\n\n")


if __name__ == "__main__":
    main()
