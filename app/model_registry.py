from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.common.constants import MODELS_DIR, SUPPORTED_MODEL_VERSIONS
from src.common.io import read_json


class ModelRegistryError(RuntimeError):
    """Raised when model artifacts are missing or inconsistent."""


@dataclass(frozen=True)
class LoadedModel:
    version: str
    model: Any
    metadata: dict[str, Any]


class ModelRegistry:
    def __init__(self, models_dir: Path | str = MODELS_DIR) -> None:
        self.models_dir = Path(models_dir)
        self.feature_schema = self._load_feature_schema()
        self.models = self._load_models()

    @property
    def available_models(self) -> list[str]:
        return sorted(self.models.keys())

    @property
    def feature_names(self) -> list[str]:
        return list(self.feature_schema["feature_names"])

    def health_payload(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "available_models": self.available_models,
            "models": {
                version: {
                    "algorithm": loaded_model.metadata["algorithm"],
                    "threshold": loaded_model.metadata["threshold"],
                }
                for version, loaded_model in self.models.items()
            },
        }

    def predict(self, features: dict[str, int], model_version: str) -> dict[str, Any]:
        try:
            loaded_model = self.models[model_version]
        except KeyError as exc:
            raise ModelRegistryError(f"Unsupported model version: {model_version}") from exc

        row = [[features[name] for name in self.feature_names]]
        frame = pd.DataFrame(row, columns=self.feature_names)
        probability = float(loaded_model.model.predict_proba(frame)[0, 1])
        prediction = int(probability >= loaded_model.metadata["threshold"])
        return {
            "prediction": prediction,
            "probability": round(probability, 6),
        }

    def _load_feature_schema(self) -> dict[str, Any]:
        schema_path = self.models_dir / "feature_schema.json"
        if not schema_path.exists():
            raise ModelRegistryError(f"Missing feature schema file: {schema_path}")

        schema = read_json(schema_path)
        feature_names = schema.get("feature_names")
        if not isinstance(feature_names, list) or not feature_names:
            raise ModelRegistryError(
                "feature_schema.json must contain a non-empty feature_names list"
            )
        return schema

    def _load_models(self) -> dict[str, LoadedModel]:
        loaded: dict[str, LoadedModel] = {}
        for version in SUPPORTED_MODEL_VERSIONS:
            model_path = self.models_dir / f"model_{version}.joblib"
            metadata_path = self.models_dir / f"model_{version}.metadata.json"
            if not model_path.exists():
                raise ModelRegistryError(f"Missing model artifact for {version}: {model_path}")
            if not metadata_path.exists():
                raise ModelRegistryError(f"Missing metadata for {version}: {metadata_path}")

            metadata = read_json(metadata_path)
            self._validate_metadata(version, metadata)
            loaded[version] = LoadedModel(
                version=version,
                model=joblib.load(model_path),
                metadata=metadata,
            )
        return loaded

    def _validate_metadata(self, version: str, metadata: dict[str, Any]) -> None:
        required_fields = {
            "model_version",
            "algorithm",
            "feature_schema",
            "threshold",
            "training_date",
            "metrics",
            "random_seed",
        }
        missing_fields = sorted(required_fields.difference(metadata))
        if missing_fields:
            missing_joined = ", ".join(missing_fields)
            raise ModelRegistryError(f"Metadata for {version} is missing fields: {missing_joined}")
        if metadata["model_version"] != version:
            raise ModelRegistryError(
                f"Metadata version mismatch for {version}: {metadata['model_version']}"
            )
        if metadata["feature_schema"] != self.feature_names:
            raise ModelRegistryError(f"Feature schema mismatch for {version}")
