# Local-first quick commands: make <target>
# No cloud, no Docker required — Python + venv only.

PY := python3
VENV := .venv
VENV_PY := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: help install run dev test docker docker-down check clean

help:  ## Show this help
	@echo ""
	@echo "  Medication Recommender — local first"
	@echo ""
	@echo "  make install     Create venv + install deps (no sudo, no cloud)"
	@echo "  make run         Run on http://127.0.0.1:5000"
	@echo "  make dev         Run with DEBUG=true (auto-reload friendly logs)"
	@echo "  make test        Smoke test: import + /health"
	@echo "  make check       Same as test, explicit name"
	@echo "  make docker      Build + run via Docker (alternative to make run)"
	@echo "  make docker-down Stop docker compose"
	@echo "  make clean       Remove venv + caches"
	@echo ""
	@echo "  Easiest:  git clone https://github.com/bmo1177/medication-recommender.git"
	@echo "            cd medication-recommender && make install && make run"
	@echo "  Or:       docker compose up --build"
	@echo ""

install:  ## Create venv and install requirements
	@echo "==> Creating $(VENV) (uv if available, else python -m venv)..."
	@if command -v uv >/dev/null 2>&1; then \
		uv venv 2>/dev/null || true; \
		uv pip install -r requirements.txt; \
	else \
		$(PY) -m venv $(VENV); \
		$(VENV_PIP) install --upgrade pip; \
		$(VENV_PIP) install -r requirements.txt; \
	fi
	@echo "==> Done. Run: make run"

run:  ## Run app locally (PORT defaults to 5000)
	$(VENV_PY) main.py

dev:  ## Run with DEBUG=true
	DEBUG=true $(VENV_PY) main.py

test:  ## Smoke test: import + health endpoint
	$(VENV_PY) -c "import main; print('OK: app imported')"
	$(VENV_PY) -c "from main import app; c=app.test_client(); r=c.get('/health'); print(r.status_code, r.json); assert r.status_code==200"
	@echo "Smoke test passed."

check: test  ## Alias for test

docker:  ## Docker alternative (needs Docker only)
	docker compose up --build

docker-down:  ## Stop compose
	docker compose down

clean:  ## Remove local artifacts
	rm -rf $(VENV) __pycache__ .pytest_cache
