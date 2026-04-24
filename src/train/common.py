from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score

from src.common.constants import FEATURE_NAMES, MODELS_DIR, RANDOM_SEED
from src.common.io import write_json
from src.data.make_dataset import create_splits, export_feature_schema


@dataclass(frozen=True)
class TrainingResult:
    metadata: dict[str, Any]
    model_path: Path
    metadata_path: Path


def choose_threshold(y_true: np.ndarray, probabilities: np.ndarray) -> float:
    thresholds = np.arange(0.05, 0.951, 0.01)
    best_threshold = 0.5
    best_score = -1.0
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)
        score = f1_score(y_true, predictions, zero_division=0)
        if score > best_score:
            best_score = score
            best_threshold = float(threshold)
    return round(best_threshold, 2)


def build_metrics(
    y_true: np.ndarray, probabilities: np.ndarray, threshold: float
) -> dict[str, float]:
    predictions = (probabilities >= threshold).astype(int)
    return {
        "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 6),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 6),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 6),
    }


def train_and_save(
    *,
    model_version: str,
    algorithm: str,
    estimator: Any,
    hyperparameters: dict[str, Any],
) -> TrainingResult:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    schema = export_feature_schema()
    splits = create_splits()

    estimator.fit(splits.X_train, splits.y_train)

    validation_probabilities = estimator.predict_proba(splits.X_validation)[:, 1]
    threshold = choose_threshold(
        splits.y_validation.to_numpy(),
        validation_probabilities,
    )
    test_probabilities = estimator.predict_proba(splits.X_test)[:, 1]
    metrics = build_metrics(
        splits.y_test.to_numpy(),
        test_probabilities,
        threshold,
    )

    model_path = MODELS_DIR / f"model_{model_version}.joblib"
    metadata_path = MODELS_DIR / f"model_{model_version}.metadata.json"

    joblib.dump(estimator, model_path)

    metadata = {
        "model_version": model_version,
        "algorithm": algorithm,
        "feature_schema": schema["feature_names"],
        "feature_schema_path": str(schema["dataset_source"]).replace(
            schema["dataset_source"],
            "models/feature_schema.json",
        ),
        "threshold": threshold,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "random_seed": RANDOM_SEED,
        "hyperparameters": hyperparameters,
        "artifact_path": f"models/{model_path.name}",
        "train_rows": len(splits.X_train),
        "validation_rows": len(splits.X_validation),
        "test_rows": len(splits.X_test),
    }
    write_json(metadata_path, metadata)

    return TrainingResult(
        metadata=metadata,
        model_path=model_path,
        metadata_path=metadata_path,
    )


def main_summary(result: TrainingResult) -> None:
    print(
        {
            "model_version": result.metadata["model_version"],
            "algorithm": result.metadata["algorithm"],
            "threshold": result.metadata["threshold"],
            "metrics": result.metadata["metrics"],
            "feature_count": len(FEATURE_NAMES),
            "artifact_path": str(result.model_path),
        }
    )
