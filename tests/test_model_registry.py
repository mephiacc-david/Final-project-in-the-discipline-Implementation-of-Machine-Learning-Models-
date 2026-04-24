import pytest

from app.model_registry import ModelRegistry, ModelRegistryError
from src.common.constants import FEATURE_NAMES
from src.common.io import write_json


def test_registry_loads_all_models():
    registry = ModelRegistry()

    assert registry.available_models == ["v1", "v2"]
    assert registry.feature_names == FEATURE_NAMES


def test_registry_predict_is_stable(sample_features):
    registry = ModelRegistry()

    first = registry.predict(sample_features, "v1")
    second = registry.predict(sample_features, "v1")

    assert first["prediction"] == second["prediction"]
    assert first["probability"] == pytest.approx(second["probability"], abs=1e-6)


def test_registry_fails_fast_when_artifact_is_missing(tmp_path):
    write_json(
        tmp_path / "feature_schema.json",
        {
            "feature_names": FEATURE_NAMES,
            "schema_version": 1,
        },
    )

    with pytest.raises(ModelRegistryError, match="Missing model artifact for v1"):
        ModelRegistry(tmp_path)
