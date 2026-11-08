#!/usr/bin/env bash
# Local-first bootstrap: clone-ready -> running app (no cloud, no Docker needed).
#
# Usage (inside the cloned repo):
#   ./scripts/bootstrap.sh          # venv + install + smoke test + run
#   ./scripts/bootstrap.sh --help
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--help" ]]; then
  echo "Local-first bootstrap for Medication Recommender"
  echo ""
  echo "  ./scripts/bootstrap.sh"
  echo "  Creates .venv, installs requirements.txt, runs smoke test, starts app."
  echo "  Open http://127.0.0.1:${PORT:-5000} when ready."
  exit 0
fi

# --- 1. Python check ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3.11+ first:" >&2
  echo "  https://www.python.org/downloads/" >&2
  exit 1
fi
echo "==> Python: $(python3 --version)"

# --- 2. venv + install (uv if available) ---
if [[ ! -x .venv/bin/python ]]; then
  echo "==> Creating .venv ..."
  if command -v uv >/dev/null 2>&1; then
    uv venv
  else
    python3 -m venv .venv
  fi
fi

echo "==> Installing requirements.txt ..."
if command -v uv >/dev/null 2>&1; then
  uv pip install -r requirements.txt
else
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
fi

# --- 3. Smoke test ---
echo "==> Smoke test (import + /health) ..."
.venv/bin/python -c "import main; print('OK: app imported')"
.venv/bin/python -c "from main import app; c=app.test_client(); r=c.get('/health'); print('health:', r.status_code, r.json); assert r.status_code==200"
echo "==> Smoke test passed."

# --- 4. Run ---
echo ""
echo "==> Starting app on http://127.0.0.1:${PORT:-5000}  (Ctrl+C to stop)"
echo ""
exec .venv/bin/python main.py
