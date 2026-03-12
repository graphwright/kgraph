#!/bin/bash -e

cd kgserver
uv run pytest -m playwright -v -p no:playwright
