"""Retrain SVC (linear, probability=True) — real confidence + metadata.

Reproduces notebook pipeline (4920x132, LabelEncoder, 70/30 split)
then refits on full data. Run:

    .venv/bin/python train.py

Writes: models/svc.pkl (Calibrated? no — SVC Platt), models/metadata.json
"""
from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets" / "Training.csv"
OUT_PKL = BASE / "models" / "svc.pkl"
OUT_META = BASE / "models" / "metadata.json"


def main() -> None:
    df = pd.read_csv(DATA)
    print(f"Loaded {DATA}: shape={df.shape}")
    X = df.drop("prognosis", axis=1)
    y = df["prognosis"]

    le = LabelEncoder()
    Y = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.3, random_state=20
    )

    # Validate on holdout first (Platt probabilities need CV internally)
    clf = SVC(kernel="linear", probability=True, random_state=42)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    acc = accuracy_score(y_test, pred)
    try:
        proba = clf.predict_proba(X_test)
        ll = float(log_loss(y_test, proba, labels=list(range(len(le.classes_)))))
    except Exception as exc:  # pragma: no cover
        ll = None
        print(f"log_loss unavailable: {exc}")
    print(f"Holdout accuracy (train-split fit): {acc:.4f} log_loss={ll}")

    # Refit on FULL data for deployment artifact
    clf.fit(X, Y)
    print(f"Refit on full {X.shape[0]} rows.")

    OUT_PKL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PKL.open("wb") as fh:
        pickle.dump(clf, fh)

    meta = {
        "model": "SVC",
        "kernel": "linear",
        "probability": True,
        "random_state": 42,
        "sklearn_version": sklearn.__version__,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "train_file": "datasets/Training.csv",
        "shape_full": list(df.shape),
        "n_features": int(X.shape[1]),
        "n_classes": int(len(le.classes_)),
        "features": list(X.columns),
        "classes_sorted": list(map(str, le.classes_)),
        "split": {"test_size": 0.3, "random_state": 20},
        "holdout_accuracy": float(acc),
        "holdout_log_loss": ll,
        "note": "Refit on full data after holdout validation (same pipeline as notebook + probability=True).",
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Wrote {OUT_PKL} and {OUT_META}")


if __name__ == "__main__":
    main()
