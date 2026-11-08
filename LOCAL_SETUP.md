# 💻 Local-First Setup — Clone & Run

> **Local-first = your laptop is the server.** No cloud account, no card, no Docker required. Model + datasets run entirely on your machine (offline after install). Cloud hosting is optional — see [Deployment in README](./README.md#-deployment).

## 30-second start (pick one)

### A) `make` (recommended)

```bash
git clone https://github.com/bmo1177/medication-recommender.git
cd medication-recommender
make install
make run
```

Open **http://127.0.0.1:5000** — verify **http://127.0.0.1:5000/health** → `{"status":"ok","symptoms":132,"diseases":41,"model":"SVC","kb_diseases":41}`

### B) One-script (no `make` needed)

```bash
git clone https://github.com/bmo1177/medication-recommender.git
cd medication-recommender
./scripts/bootstrap.sh
```

`bootstrap.sh` does: Python check → `.venv` → `pip install -r requirements.txt` → smoke test → starts app. Stop with `Ctrl+C`. Re-run with `./scripts/run.sh`.

### C) Docker (no local Python needed)

```bash
git clone https://github.com/bmo1177/medication-recommender.git
cd medication-recommender
docker compose up --build
# or: make docker
```

Open **http://localhost:5000**. Stop: `docker compose down` / `make docker-down`.

---

## Requirements

| Need | Version | Check |
|---|---|---|
| Python | 3.11+ (3.12 works) | `python3 --version` |
| pip | latest | inside `.venv` (bootstrap handles) |
| Disk | ~800 MB (venv + pandas/sklearn) | `df -h .` |
| Port | 5000 free (or set `PORT=8080`) | `PORT=8080 make run` |

Windows: use PowerShell/WSL + `make` (Git Bash) or run `python -m venv venv`, `pip install -r requirements.txt`, `python main.py` manually. macOS: same as Linux.

## What `make install` actually does

1. Creates `.venv` in the repo (git-ignored — never committed).
2. Installs pinned deps from [`requirements.txt`](./requirements.txt): `Flask==3.0.3`, `gunicorn==22.0.0`, `numpy==1.26.4`, `pandas==2.2.2`, `scikit-learn==1.3.2` (match `models/svc.pkl`).
3. Leaves `datasets/*.csv` + `models/svc.pkl` untouched (already in the clone).

After that everything is local: inference never leaves your machine, no keys, no DB.

## Day-to-day commands

```bash
make run          # http://127.0.0.1:5000
make dev          # DEBUG=true (verbose logs)
PORT=8080 make run
make test         # import + /health smoke test (also runs in CI)
make docker       # alternative via Docker
make clean        # delete .venv + caches
```

Env overrides (optional — copy [`.env.example`](./.env.example) to `.env` if your shell loads it):

| Var | Default | Effect |
|---|---|---|
| `PORT` | `5000` | Listen port |
| `DEBUG` | `false` | Flask debug mode (local only!) |
| `MAX_SYMPTOMS` | `30` | Max symptoms per request |
| `MAX_INPUT_LEN` | `2000` | Max input chars |

## Voice input

Works in **Chrome/Edge** (Web Speech API) only. Other browsers show: *"Speech input is not supported — please type"*. Manual input always works.

## Troubleshooting (local)

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Venv not active: use `make run` (uses `.venv/bin/python`) or `source .venv/bin/activate` |
| `Address already in use :5000` | `lsof -i :5000` → kill, or `PORT=8080 make run` |
| `InconsistentVersionWarning` from sklearn | You're on non-1.3.2: `uv pip install scikit-learn==1.3.2` / `pip install scikit-learn==1.3.2` |
| `FileNotFoundError: models/svc.pkl` | You didn't clone fully — re-clone, check `ls models/` |
| `X does not have valid feature names` warning | Harmless — SVC was fit with column names. Ignore. |
| Windows `make: command not found` | Use `./scripts/bootstrap.sh` via Git Bash/WSL, or manual venv steps above |
| Very slow first run | `make install` downloads ~80 MB (numpy/pandas/sklearn). One-time. |

## Updating locally

```bash
git pull origin main
make install   # picks up new pins if any
make run
```

## Privacy

All predictions run in-process (`main.py` → `ModelPredictor` → CSV lookups). No symptom data is logged, stored, or sent anywhere. The only outbound calls are CDN assets (Bootstrap, FontAwesome, Google Fonts) — block them and the app still works (un-styled).
