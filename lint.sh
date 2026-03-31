#!/bin/bash -e

fixes_needed() {
    echo "Something needs fixing, trying to fix it"
    set -x
    uv run black kgraph kgbundle kgserver examples
    uv run ruff check --fix kgraph kgbundle kgserver examples
    exit 1
}

mypy_fix_needed() {
    echo "Something mypy-ish needs fixing, You need to do that"
    exit 1
}

echo "=========================================="
echo "Running Linters and Tests"
echo "=========================================="

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Please install uv first."
    echo "See: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo ""
echo "UV Version:"
uv --version

# Only list .py files that exist (git ls-files includes deleted-but-unstaged files)
PYTHONFILES=$(git ls-files -- kgraph kgbundle kgschema kgserver examples | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)

echo ""
echo "=========================================="
echo "Running ruff check..."
echo "=========================================="
uv run ruff check ${PYTHONFILES} || fixes_needed

echo ""
echo "=========================================="
echo "Running mypy..."
echo "=========================================="
# Exclude chainlit app: Chainlit has no type stubs and uses dynamic decorators
MYPY_FILES=$(echo "${PYTHONFILES}" | tr ' ' '\n' | grep -v 'kgserver/chainlit/app\.py' | tr '\n' ' ')
uv run mypy ${MYPY_FILES} || mypy_fix_needed

echo ""
echo "=========================================="
echo "Running black check..."
echo "=========================================="
uv run black --check ${PYTHONFILES} || fixes_needed

echo ""
echo "=========================================="
echo "Running flake8..."
echo "=========================================="
# Use -j 1 to avoid multiprocessing (avoids PermissionError in sandbox/CI)
uv run flake8 ${PYTHONFILES} --count --show-source --statistics -j 1 || fixes_needed

# echo ""
# echo "=========================================="
# echo "Running pylint..."
# echo "=========================================="
# # Exclude chainlit app: Chainlit uses dynamic decorators and has no static introspection
# PYLINT_FILES=$(echo "${PYTHONFILES}" | tr ' ' '\n' | grep -v 'kgserver/chainlit/app\.py' | tr '\n' ' ')
# uv run pylint ${PYLINT_FILES}

echo ""
echo "=========================================="
echo "Running tests..."
echo "=========================================="
# Root tests: tests/ + examples/medlit/tests/ (includes provenance, export, ingestion, etc.)
uv run pytest -q

# Run kgbundle tests from repo root so the root venv (kgbundle + pydantic) is used.
# Do not "cd kgbundle && uv run pytest": that can use a venv without pydantic.
if [ -d "kgbundle/tests" ]; then
    echo ""
    echo "Running kgbundle tests..."
    uv run pytest kgbundle/tests/ -q
fi

# Run kgserver tests from kgserver/ so uv uses kgserver's pyproject (sqlalchemy, etc.).
# Do not run "pytest kgserver/tests/" from root: that uses the root venv, which lacks kgserver deps.
# PYTHONPATH adds root kgbundle so kgserver can import it (kgserver does not list kgbundle as a dep).
if [ -d "kgserver/tests" ]; then
    echo ""
    echo "Running kgserver tests..."
    ROOT_DIR="$(pwd)"
    # (cd kgserver && PYTHONPATH="${ROOT_DIR}/kgbundle:${ROOT_DIR}:${PYTHONPATH}" uv run pytest tests/ -m "not playwright" --full-trace -q)
    (cd kgserver && PYTHONPATH="${ROOT_DIR}/kgbundle:${ROOT_DIR}:${PYTHONPATH}" uv run pytest tests/ -m "not playwright" -q)
fi
