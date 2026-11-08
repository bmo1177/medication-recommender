<div align="center">

# 🩺 Personalized Medical Recommendation System

### AI-powered symptom-based disease prediction with medications, diet, workouts & precautions

> **Disclaimer:** Educational Flask demo. Symptom-based disease prediction with medication and diet suggestions. **Not medical advice.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Railway](https://img.shields.io/badge/Railway-Deploy-CFC3F3?style=for-the-badge&logo=railway&logoColor=black)](https://railway.app/)
[![CI](https://img.shields.io/badge/CI-Passing-brightgreen?style=for-the-badge&logo=githubactions)](https://github.com/bmo1177/medication-recommender/actions)
[![License](https://img.shields.io/badge/License-Academic-blue?style=for-the-badge)](./README.md)

**[Live Demo](https://github.com/bmo1177/medication-recommender#deployment)** · **[Quick Start](#-quick-start)** · **[How It Works](#-how-it-works)** · **[Deployment](#-deployment)** · **[Contributing](#-contributing)**

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🖼️ Screenshots](#️-screenshots)
- [⚙️ How It Works](#-how-it-works)
- [🧰 Tech Stack](#-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [☁️ Deployment](#-deployment)
- [📁 Project Structure](#-project-structure)
- [🔌 Endpoints](#-endpoints)
- [📊 Datasets & Model](#-datasets--model)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [🗺️ Roadmap](#️-roadmap)
- [⚠️ Disclaimer](#️-important-disclaimer)
- [📄 License](#-license)
- [👥 Authors](#-authors)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Symptom-based prediction** | Enter comma-separated symptoms → instant disease prediction (132 symptoms, 41 diseases) |
| **Voice input** | Mic-enabled symptom entry on supported browsers |
| **Personalized recommendations** | Medications, precautions, diet plan and workout routine per predicted disease |
| **Severity scoring** | Weighted score from `Symptom-severity.csv` (real weights, not index sums) |
| **Input validation** | Unknown / misspelled symptoms are reported instead of crashing |
| **Production-ready** | `$PORT` / `DEBUG` env handling, `/health` check, Gunicorn + Docker, Railway/Render blueprints |
| **CI** | GitHub Actions on every push/PR (import + health check) |
| **Privacy-focused** | All inference runs locally on the server — no symptom data is stored |

**Sample inputs** (see `tests.txt`):

```text
fatigue, weight_loss, restlessness, lethargy
chills, fatigue, cough, high_fever
itching, skin_rash, burning_micturition
```

---

## 🖼️ Screenshots

| Homepage | Prediction result |
|---|---|
| ![Homepage](screenshots/screencapture-127-0-0-1-5000-2025-06-09-05_36_49.png) | ![Prediction](screenshots/screencapture-127-0-0-1-5000-predict-2025-06-09-05_37_17.png) |

| About | Blog |
|---|---|
| ![About](screenshots/screencapture-127-0-0-1-5000-about-2025-06-09-05_40_36.png) | ![Blog](screenshots/screencapture-127-0-0-1-5000-blog-2025-06-09-05_45_15.png) |

> More screenshots are in [`screenshots/`](./screenshots).

---

## ⚙️ How It Works

```text
User symptoms  →  normalize (lowercase, _-separated, strip)
                 →  binary vector of length 132
                 →  SVC model (models/svc.pkl, scikit-learn 1.3.2)
                 →  predicted disease (41 classes)
                 →  lookup in datasets/*.csv
                      ├─ description.csv       → description
                      ├─ medications.csv       → medications
                      ├─ precautions_df.csv    → precautions
                      ├─ diets.csv             → diet plan
                      └─ workout_df.csv        → workout plan
                 →  severity score = Σ weight(symptom) from Symptom-severity.csv
                 →  rendered in templates/index.html
```

- **Model:** `Support Vector Classifier` trained in `Medicine Recommendation System.ipynb`, exported as `models/svc.pkl`
- **Training data:** `datasets/Training.csv` + `datasets/symtoms_df.csv`
- **Routes:** `/` · `/predict` (POST) · `/about` · `/contact` · `/developer` · `/blog` · `/health`

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0, Gunicorn |
| ML | scikit-learn 1.3.2 (SVC), pandas, numpy |
| Frontend | Jinja2 templates, vanilla HTML/CSS/JS, Font Awesome |
| Container | Docker (`python:3.11-slim`) |
| Hosting | Railway (Dockerfile / Procfile), Render (`render.yaml`) |
| CI | GitHub Actions (`.github/workflows/python-app.yml`) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (3.12 also works locally) and `pip`
- Or Docker (no local Python needed)

### 1. Clone & install

```bash
git clone https://github.com/bmo1177/medication-recommender.git
cd medication-recommender

python3 -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run locally

```bash
python main.py
```

Open **http://127.0.0.1:5000** — health check at **http://127.0.0.1:5000/health**.

Production-like (Gunicorn):

```bash
gunicorn main:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
```

Custom port:

```bash
PORT=8080 python main.py
```

### 3. Docker

```bash
docker build -t medication-recommender .
docker run -e PORT=5000 -p 5000:5000 medication-recommender
```

---

## ☁️ Deployment

### Railway (recommended)

Railway auto-detects the `Dockerfile` — it binds to `$PORT`, so no env vars are required.

1. Go to [railway.app](https://railway.app) → **Login with GitHub** (`bmo1177`)
2. **+ New Project** → **Deploy from GitHub Repo** → `bmo1177/medication-recommender` → branch `main`
3. Click the service → **Settings** → **Networking** → **Generate Domain** → copy your live URL
4. Verify: `<your-domain>/health` → `{"status":"ok","symptoms":132,"diseases":41}`

Optional env var:

| Key | Value | Notes |
|---|---|---|
| `DEBUG` | `false` | Default. Set `true` only for local debugging |
| `PORT` | *(auto)* | Set by Railway — do not hardcode |

### Render

1. [render.com](https://render.com) → **New → Web Service** → connect `bmo1177/medication-recommender`
2. `render.yaml` auto-fills: Build `pip install -r requirements.txt`, Start `gunicorn main:app --bind 0.0.0.0:$PORT`, Health `/health`
3. Deploy → live at `https://medication-recommender.onrender.com`

### Docker (any host)

```bash
docker build -t medication-recommender .
docker run -d --name medication-recommender -p 5000:5000 medication-recommender
curl http://localhost:5000/health
```

---

## 📁 Project Structure

```text
medication-recommender/
├── main.py                     # Flask app (routes, prediction, severity)
├── requirements.txt            # Pinned dependencies (ml pickle-compatible)
├── Dockerfile                  # Railway-ready, binds to $PORT
├── Procfile                    # gunicorn main:app
├── render.yaml                 # Render blueprint
├── .python-version             # 3.11.9
├── .github/workflows/python-app.yml
├── datasets/                   # Canonical data (runtime + training)
│   ├── symtoms_df.csv
│   ├── Training.csv
│   ├── description.csv
│   ├── medications.csv
│   ├── diets.csv
│   ├── precautions_df.csv
│   ├── workout_df.csv
│   └── Symptom-severity.csv
├── models/
│   └── svc.pkl                 # Trained SVC (sklearn 1.3.2)
├── templates/                  # Flask templates (runtime)
│   ├── index.html              # Symptom form + results modal
│   ├── about.html
│   ├── contact.html
│   ├── developer.html
│   └── blog.html
├── static/                     # Static assets
├── diagrams/                   # UML diagrams
├── screenshots/
├── Medicine Recommendation System.ipynb
└── tests.txt                   # Sample symptom inputs
```

---

## 🔌 Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Symptom form (index) |
| `POST` | `/predict` | Predict disease from `symptoms` form field (comma-separated) |
| `GET` | `/health` | `{"status":"ok","symptoms":132,"diseases":41}` |
| `GET` | `/about` `/contact` `/developer` `/blog` | Static pages |

---

## 📊 Datasets & Model

| File | Rows* | Purpose |
|---|---|---|
| `datasets/symtoms_df.csv` | 4921 | Symptom list / encoding source |
| `datasets/Training.csv` | 4921 | Training matrix (symptoms → disease) |
| `datasets/description.csv` | 41 | Disease descriptions |
| `datasets/medications.csv` | 41 | Medication per disease |
| `datasets/precautions_df.csv` | 41 | 4 precautions per disease |
| `datasets/diets.csv` | 41 | Diet plan per disease |
| `datasets/workout_df.csv` | 410 | Workout routine per disease |
| `datasets/Symptom-severity.csv` | 133 | Symptom → severity weight |

\*Row counts from the committed files; training notebook rebuilds `models/svc.pkl`.

> ⚠️ `models/svc.pkl` is loaded with `pickle`. It is **trusted-only** — never load a pickle from an untrusted source. The version-matched `scikit-learn==1.3.2` pin (see `requirements.txt`) avoids pickle version warnings.

---

## 🧪 Testing

- **Local smoke test** (also run in CI):

  ```bash
  python -c "import main; print('OK: app imported')"
  python -c "from main import app; c=app.test_client(); print(c.get('/health').json)"
  ```

- **Sample inputs:** [`tests.txt`](./tests.txt)
- **CI:** `.github/workflows/python-app.yml` — install + import + `/health` on every push/PR to `main`

---

## 🤝 Contributing

Contributions are welcome!

1. Fork `bmo1177/medication-recommender`
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit with a clear message and push
4. Open a Pull Request against `main` (CI runs automatically)

Please try to keep changes focused and update `README.md` when behavior changes.

---

## 🗺️ Roadmap

- [x] Production-ready Flask (`$PORT`, `/health`, input validation)
- [x] Severity scoring from weights file
- [x] Docker + Railway + Render + GitHub Actions CI
- [ ] `POST /api/predict` JSON endpoint (currently form-only)
- [ ] Confidence via `probability=True` retraining
- [ ] Unit tests (`pytest` for `helper` + routes)
- [ ] Frontend polish (loading states, error toasts, mobile layout)

---

## ⚠️ Important Disclaimer

> **Warning:** This system is for **educational purposes only**. It is **not** intended to replace professional medical advice. Always consult a qualified healthcare provider for medical decisions.

---

## 📄 License

Academic / educational project. No warranty. See repository history for attribution.

---

## 👥 Authors

- **Mohamed Oussama Belalia** ([@bmo1177](https://github.com/bmo1177)) — creator
- Educational project only.

<div align="center">

Made with Flask, scikit-learn & ❤️ · <a href="https://github.com/bmo1177/medication-recommender">⭐ Star on GitHub</a>

</div>
