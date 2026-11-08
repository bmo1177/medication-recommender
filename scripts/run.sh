#!/usr/bin/env bash
# Run the app (assumes ./scripts/bootstrap.sh or `make install` ran first).
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv/bin/python ]]; then
  echo "ERROR: .venv not found. Run ./scripts/bootstrap.sh or 'make install' first." >&2
  exit 1
fi
echo "==> Starting on http://127.0.0.1:${PORT:-5000}  (Ctrl+C to stop)"
exec .venv/bin/python main.py
