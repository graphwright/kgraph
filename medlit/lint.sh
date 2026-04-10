#!/bin/bash -e

fixes_needed() {
    echo "Something needs fixing, trying to fix it"
    set -x
    uv run black medlit medlit_schema domain_service pipeline.py tests
    uv run ruff check --fix medlit medlit_schema domain_service pipeline.py tests
    exit 1
}

mypy_fix_needed() {
    echo "Something mypy-ish needs fixing, you need to do that"
    exit 1
}

echo "=========================================="
echo "Running Linters and Tests"
echo "=========================================="

if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Please install uv first."
    echo "See: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo ""
echo "UV Version:"
uv --version

# Only list .py files that exist (git ls-files includes deleted-but-unstaged files)
PYTHONFILES=$(git ls-files -- medlit medlit_schema domain_service pipeline.py tests | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)

echo ""
echo "=========================================="
echo "Running ruff check..."
echo "=========================================="
uv run ruff check ${PYTHONFILES} || fixes_needed

echo ""
echo "=========================================="
echo "Running mypy..."
echo "=========================================="
uv run mypy ${PYTHONFILES} || mypy_fix_needed

echo ""
echo "=========================================="
echo "Running black check..."
echo "=========================================="
uv run black --check ${PYTHONFILES} || fixes_needed

echo ""
echo "=========================================="
echo "Running flake8..."
echo "=========================================="
uv run flake8 ${PYTHONFILES} --count --show-source --statistics -j 1 || fixes_needed

echo ""
echo "=========================================="
echo "Running tests..."
echo "=========================================="
uv run pytest -q
