> **Disclaimer:** Educational Flask demo: symptom-based disease prediction with medication and diet suggestions. Not medical advice.

# Personalized Medical Recommendation System

An AI-powered health assistant that helps users identify potential diseases based on symptoms and provides personalized recommendations for medications, diet, workouts, and precautions.

**Live demo:** Deploy to Render or Railway from this repo (see [Deployment](#deployment)).

## 🚀 Features

- **Symptom-Based Disease Prediction** – Input symptoms to get instant disease predictions
- **Voice Recognition Support** – Describe symptoms using voice input (mic-enabled devices)
- **Personalized Recommendations** – Get suggestions for:
  - Top medications
  - Precautionary measures
  - Diet plans
  - Workout routines
- **Web Interface** – User-friendly Flask web application
- **Severity Scoring** – Weighted score from `datasets/Symptom-severity.csv`
- **Privacy Focused** – User data is processed locally and securely

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ (3.11 recommended for hosting)
- pip (Python package manager)

### 2. Clone & Setup
```bash
git clone https://github.com/bmo1177/medication-recommender.git
cd medication-recommender

# Create virtual environment (Recommended)
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Locally
```bash
python main.py
```
Then open your browser to: `http://127.0.0.1:5000`

Health check: `http://127.0.0.1:5000/health`

Or with Gunicorn (production-like):
```bash
gunicorn main:app --bind 0.0.0.0:5000
```

## ☁️ Deployment

### Render (Recommended, free tier)
1. Push to GitHub: `bmo1177/medication-recommender`
2. Go to [render.com](https://render.com) → **New → Web Service** → connect this repo
3. Render auto-detects `render.yaml`:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app --bind 0.0.0.0:$PORT`
4. Deploy → live at `https://medication-recommender.onrender.com`

### Railway
1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub Repo**
2. Select `bmo1177/medication-recommender`
3. Use `Procfile`: `web: gunicorn main:app --bind 0.0.0.0:$PORT`
4. Deploy → live URL generated automatically

### Docker
```bash
docker build -t medication-recommender .
docker run -p 5000:5000 medication-recommender
```

## 📁 Project Structure
```
medication-recommender/
├── main.py                      # Flask app (production-ready)
├── requirements.txt             # Python dependencies
├── Procfile                     # Railway/Heroku-style start command
├── render.yaml                  # Render blueprint (auto-deploy)
├── Dockerfile                   # Container build
├── .github/workflows/python-app.yml  # CI (import + health check)
├── datasets/                    # Canonical CSV data
│   ├── symtoms_df.csv
│   ├── precautions_df.csv
│   ├── workout_df.csv
│   ├── description.csv
│   ├── medications.csv
│   ├── diets.csv
│   └── Symptom-severity.csv
├── models/
│   └── svc.pkl                  # Trained SVM model
├── templates/                   # Flask templates (used at runtime)
│   ├── index.html
│   ├── about.html
│   ├── contact.html
│   ├── developer.html
│   └── blog.html
├── static/                      # Static assets
├── diagrams/                    # UML diagrams
├── screenshots/
├── Medicine Recommendation System.ipynb
└── tests.txt                    # Sample symptom inputs
```

## 🧪 Testing
Use `tests.txt` with sample symptoms:
```
fatigue, weight_loss, restlessness, lethargy
chills, fatigue, cough, high_fever
itching, skin_rash, burning_micturition
```

CI runs on every push/PR to `main` (see `.github/workflows/python-app.yml`).

## 👥 Developers
Educational project only.

## ⚠️ Important Disclaimer
> **Warning**: This system is for **educational purposes only**. Not intended to replace professional medical advice. Always consult healthcare providers for medical decisions.

## 📄 License
Academic project (educational use).
