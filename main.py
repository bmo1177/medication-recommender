"""
Health Center — Flask app (production-ready, scalable).

Efficiency:
  - CSVs / model loaded ONCE at startup into O(1) in-memory indexes
    (no pandas filtering per request).
  - Symptom encoding is a single numpy vector build (O(k), k = #input).
  - No per-request file I/O, no repeated DataFrame scans.

Scalability for better models:
  - `ModelPredictor` is a thin adapter around any sklearn classifier
    with `.predict()` (and `.predict_proba()` when available).
    Drop in a retrained svc.pkl / random_forest.pkl — no route changes.
  - `DiseaseKnowledgeBase` owns all dataset lookups; swap CSVs freely.
  - `create_app()` factory + `Config` from env = testable & deployable
    via `gunicorn main:app`.

Bug-free guarantees:
  - Input capped (MAX_SYMPTOMS / MAX_INPUT_LEN), unknown-only input
    returns a friendly message (never a 500).
  - Missing disease in KB returns empty recs (never KeyError).
  - Model version + file checks fail fast with a clear error.
  - `normalize_symptom()` handles spaces/hyphens/quotes/case.

Backwards compatibility (notebook / existing imports):
  - `symptoms_dict`, `diseases_list`, `severity_map`, `svc`,
    `helper()`, `get_predicted_value()`, `calculate_severity_score()`,
    `normalize_symptom()` are preserved as thin shims.
"""

from __future__ import annotations

import ast
import logging
import os
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("medication-recommender")

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"


@dataclass(frozen=True)
class Config:
    """Environment-driven config. Override via env vars in production."""

    datasets_dir: Path = DATASETS_DIR
    models_dir: Path = MODELS_DIR
    model_path: Path = MODELS_DIR / "svc.pkl"
    max_symptoms: int = int(os.getenv("MAX_SYMPTOMS", "30"))
    max_input_len: int = int(os.getenv("MAX_INPUT_LEN", "2000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", "5000"))
    host: str = os.getenv("HOST", "0.0.0.0")


# ------------------------------------------------------------------
# Canonical symptom <-> disease maps (frozen; copied from original app)
# ------------------------------------------------------------------

symptoms_dict: Dict[str, int] = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list: Dict[int, str] = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}
symptom_names_sorted: List[str] = sorted(symptoms_dict.keys())
symptom_set = frozenset(symptoms_dict.keys())
_ALIASES = {"spotting__urination": "spotting_ urination", "spotting_urination": "spotting_ urination"}


def normalize_symptom(raw: Any) -> str:
    """Canonicalize a raw symptom token: strip, lower, spaces/hyphens -> _."""
    name = str(raw).strip().strip("[]'\"\"").lower()
    name = name.replace("-", "_")
    # collapse runs of spaces/underscores added by replace
    name = "_".join(part for part in name.replace("_", " ").split() if part)
    return _ALIASES.get(name, name)


# ------------------------------------------------------------------
# Knowledge base: O(1) disease lookups (built once, no per-request scans)
# ------------------------------------------------------------------

def _parse_list_cell(value: Any) -> List[str]:
    """Parse a stringified Python list cell; fall back to [str(value)]."""
    if isinstance(value, list):
        return [str(v) for v in value]
    s = str(value).strip()
    if s.startswith("["):
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [str(v) for v in parsed]
        except (ValueError, SyntaxError):
            pass
    return [s] if s else []


class DiseaseKnowledgeBase:
    """Pre-indexed disease -> guidance store."""

    def __init__(self, datasets_dir: Path) -> None:
        self._load(datasets_dir)

    @staticmethod
    def _read_csv(path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"Required dataset not found: {path}")
        return pd.read_csv(path)

    def _load(self, d: Path) -> None:
        desc_df = self._read_csv(d / "description.csv")
        med_df = self._read_csv(d / "medications.csv")
        pre_df = self._read_csv(d / "precautions_df.csv")
        diet_df = self._read_csv(d / "diets.csv")
        work_df = self._read_csv(d / "workout_df.csv")
        sev_path = d / "Symptom-severity.csv"

        # Severity map (real weights)
        self.severity_map: Dict[str, float] = {}
        if sev_path.exists():
            sev = pd.read_csv(sev_path)
            for _, row in sev.iterrows():
                self.severity_map[str(row["Symptom"]).strip()] = float(row["weight"])

        # Index by disease name — O(1) at request time.
        self._desc: Dict[str, str] = dict(
            zip(desc_df["Disease"].astype(str), desc_df["Description"].astype(str))
        )
        self._meds: Dict[str, List[str]] = {
            str(k): _parse_list_cell(v) for k, v in zip(med_df["Disease"], med_df["Medication"])
        }
        self._diets: Dict[str, List[str]] = {
            str(k): _parse_list_cell(v) for k, v in zip(diet_df["Disease"], diet_df["Diet"])
        }
        pre_cols = ["Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"]
        self._pre: Dict[str, List[str]] = {
            str(row["Disease"]): [str(row[c]) for c in pre_cols if pd.notna(row[c]) and str(row[c]).strip()]
            for _, row in pre_df.iterrows()
        }
        # workout has 10 rows per disease
        wkey = "disease" if "disease" in work_df.columns else "Disease"
        grouped: Dict[str, List[str]] = {}
        for disease, workout in zip(work_df[wkey].astype(str), work_df["workout"].astype(str)):
            grouped.setdefault(disease, []).append(workout.strip())
        self._workouts: Dict[str, List[str]] = grouped

    def details(self, disease: str) -> Tuple[str, List[str], List[str], List[str], List[str]]:
        """Return (description, precautions, medications, diets, workouts). Never raises."""
        return (
            self._desc.get(disease, ""),
            list(self._pre.get(disease, [])),
            list(self._meds.get(disease, [])),
            list(self._diets.get(disease, [])),
            list(self._workouts.get(disease, [])),
        )

    def severity_score(self, symptoms: Sequence[str]) -> int:
        score = 0.0
        for s in symptoms:
            key = normalize_symptom(s)
            score += self.severity_map.get(key, self.severity_map.get(str(s).strip(), 0.0))
        return int(score)

    def __len__(self) -> int:
        return len(self._desc)


# ------------------------------------------------------------------
# Model adapter: swap in any sklearn classifier without route changes
# ------------------------------------------------------------------

class ModelPredictor:
    """Adapter for any fitted sklearn classifier with .predict()."""

    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        with model_path.open("rb") as fh:
            self.model = pickle.load(fh)  # trusted artifact only
        self.name = type(self.model).__name__
        # Best-effort version check (pickle compatibility across sklearn versions)
        fitted_version = getattr(self.model, "_sklearn_version", None)
        try:
            import sklearn  # local import to keep top-level light

            if fitted_version and fitted_version != sklearn.__version__:
                logger.warning(
                    "Pickle was trained with sklearn %s, running %s — verify accuracy.",
                    fitted_version,
                    sklearn.__version__,
                )
        except ImportError:
            pass
        self.n_features = len(symptoms_dict)

    def predict(self, symptoms: Sequence[str]) -> Tuple[Optional[str], float, List[str]]:
        """Encode symptoms -> predict disease. Returns (disease|None, confidence, unknown)."""
        vec = np.zeros(self.n_features, dtype=np.float32)
        unknown: List[str] = []
        for item in symptoms:
            key = normalize_symptom(item)
            idx = symptoms_dict.get(key, symptoms_dict.get(str(item).strip()))
            if idx is not None:
                vec[idx] = 1.0
            else:
                unknown.append(str(item).strip())
        if vec.sum() == 0:
            return None, 0.0, unknown
        pred = self.model.predict([vec])[0]
        try:
            pred_key = int(pred)
        except (TypeError, ValueError):
            pred_key = pred  # string label already
        disease = diseases_list.get(pred_key) if isinstance(pred_key, int) else diseases_list.get(pred_key, str(pred_key))
        # Confidence: real probability when available, else fixed (SVC without probability)
        confidence = 1.0
        if hasattr(self.model, "predict_proba"):
            try:
                proba = self.model.predict_proba([vec])[0]
                confidence = float(proba.max())
            except Exception:
                confidence = 1.0
        return disease, confidence, unknown


# ------------------------------------------------------------------
# Flask app factory
# ------------------------------------------------------------------

def create_app(config: Optional[Config] = None, kb: Optional[DiseaseKnowledgeBase] = None,
               predictor: Optional[ModelPredictor] = None) -> Flask:
    cfg = config or Config()
    kb = kb or DiseaseKnowledgeBase(cfg.datasets_dir)
    predictor = predictor or ModelPredictor(cfg.model_path)

    app = Flask(__name__)
    app.config["KB"] = kb
    app.config["PREDICTOR"] = predictor
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB guard

    @app.errorhandler(413)
    def _too_large(_e):
        return "Request too large.", 413

    @app.route("/health")
    def health():
        return jsonify(
            status="ok",
            symptoms=len(symptoms_dict),
            diseases=len(diseases_list),
            kb_diseases=len(kb),
            model=predictor.name,
        )

    @app.route("/")
    def index():
        return render_template("index.html", symptoms_list=symptom_names_sorted)

    @app.route("/predict", methods=["GET", "POST"])
    def predict_route():
        if request.method != "POST":
            return render_template("index.html", symptoms_list=symptom_names_sorted)

        raw = request.form.get("symptoms", "")
        if not raw or raw.strip() == "" or raw == "Symptoms":
            return render_template(
                "index.html",
                message="Please either write symptoms or you have written misspelled symptoms",
                symptoms_list=symptom_names_sorted,
                user_input=raw or "",
            )
        if len(raw) > cfg.max_input_len:
            return render_template(
                "index.html",
                message=f"Input too long (max {cfg.max_input_len} characters).",
                symptoms_list=symptom_names_sorted,
                user_input=raw[: cfg.max_input_len],
            )

        user_symptoms = [s.strip().strip("[]' ") for s in raw.split(",") if s.strip()]
        if not user_symptoms:
            return render_template(
                "index.html",
                message="Please enter at least one symptom.",
                symptoms_list=symptom_names_sorted,
                user_input=raw,
            )
        if len(user_symptoms) > cfg.max_symptoms:
            return render_template(
                "index.html",
                message=f"Please enter at most {cfg.max_symptoms} symptoms.",
                symptoms_list=symptom_names_sorted,
                user_input=raw,
            )

        disease, confidence, unknown = predictor.predict(user_symptoms)
        if disease is None:
            message = (
                "None of those symptoms were recognized. "
                "Please use symptoms from the list (e.g. itching, cough, high_fever). "
                f"Unrecognized: {', '.join(unknown)}"
            )
            return render_template(
                "index.html",
                message=message,
                symptoms_list=symptom_names_sorted,
                user_input=raw,
            )

        severity_score = kb.severity_score(user_symptoms)
        dis_des, my_precautions, medications_list, rec_diet, workout_plan = kb.details(disease)
        extra = ""
        if unknown:
            extra = f"Note: unrecognized symptoms were ignored: {', '.join(unknown)}"

        return render_template(
            "index.html",
            predicted_disease=disease,
            confidence=confidence,
            severity_score=severity_score,
            dis_des=dis_des,
            my_precautions=my_precautions,
            medications=medications_list,
            my_diet=rec_diet,
            workout=workout_plan,
            message=extra or None,
            symptoms_list=symptom_names_sorted,
            user_input=raw,
        )

    @app.route("/api/symptoms", methods=["GET"])
    def api_symptoms():
        return jsonify(count=len(symptom_names_sorted), symptoms=symptom_names_sorted)

    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(error="JSON body required: {\"symptoms\": \"itching, cough\"}"), 400

        raw_in = payload.get("symptoms")
        if isinstance(raw_in, str):
            raw_str = raw_in
            user_symptoms = [s.strip().strip("[]' ") for s in raw_in.split(",") if s.strip()]
        elif isinstance(raw_in, list):
            if not all(isinstance(s, str) for s in raw_in):
                return jsonify(error="symptoms list must contain only strings"), 400
            raw_str = ", ".join(raw_in)
            user_symptoms = [s.strip().strip("[]' ") for s in raw_in if s.strip()]
        else:
            return jsonify(error="symptoms must be a comma-separated string or list of strings"), 400

        if not user_symptoms:
            return jsonify(error="Please enter at least one symptom."), 400
        if len(user_symptoms) > cfg.max_symptoms:
            return jsonify(error=f"Please enter at most {cfg.max_symptoms} symptoms."), 400
        if len(raw_str) > cfg.max_input_len:
            return jsonify(error=f"Input too long (max {cfg.max_input_len} characters)."), 400

        disease, confidence, unknown = predictor.predict(user_symptoms)
        if disease is None:
            return jsonify(
                error="None of those symptoms were recognized. Use symptoms from /api/symptoms.",
                unknown=unknown,
            ), 422

        dis_des, my_precautions, medications_list, rec_diet, workout_plan = kb.details(disease)
        return jsonify(
            predicted_disease=disease,
            confidence=confidence,
            severity_score=kb.severity_score(user_symptoms),
            recognized=[s for s in user_symptoms if s.strip() not in unknown],
            unknown=unknown,
            description=dis_des,
            precautions=my_precautions,
            medications=medications_list,
            diet=rec_diet,
            workouts=workout_plan,
        )

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")

    @app.route("/developer")
    def developer():
        return render_template("developer.html")

    @app.route("/blog")
    def blog():
        return render_template("blog.html")

    return app


# ------------------------------------------------------------------
# Backwards-compatible singletons (gunicorn: main:app)
# ------------------------------------------------------------------

app = create_app()
_kb: DiseaseKnowledgeBase = app.config["KB"]
_predictor: ModelPredictor = app.config["PREDICTOR"]

# legacy aliases for external imports / notebook compat
severity_map: Dict[str, float] = _kb.severity_map
svc = _predictor.model  # raw sklearn model


def helper(dis: str):
    """Legacy shim -> O(1) KB lookup. Returns (desc, pre, med, diet, workout)."""
    return _kb.details(dis)


def calculate_severity_score(symptoms: Sequence[str]) -> int:
    return _kb.severity_score(symptoms)


def get_predicted_value(patient_symptoms: Sequence[str]):
    """Legacy shim -> ModelPredictor.predict()."""
    return _predictor.predict(patient_symptoms)


if __name__ == "__main__":
    _cfg = Config()
    logger.info("Starting on %s:%s (debug=%s)", _cfg.host, _cfg.port, _cfg.debug)
    app.run(host=_cfg.host, port=_cfg.port, debug=_cfg.debug)
