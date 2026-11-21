#!/usr/bin/env bash
# Convenience wrapper: python -m scraper.run --properties all
set -euo pipefail
cd "$(dirname "$0")/.."
python -m scraper.run --properties all --max-pages 20 --export-json data/sample_reviews.json "$@"
