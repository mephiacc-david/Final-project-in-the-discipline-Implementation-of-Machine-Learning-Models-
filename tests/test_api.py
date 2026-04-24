import json
import logging
from io import StringIO

import pytest

from app.logging_config import JsonFormatter


def test_health_returns_loaded_models(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.get_json()["available_models"] == ["v1", "v2"]


def test_predict_returns_contract_fields(client, sample_request):
    response = client.post("/predict", json=sample_request)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["model_version"] == "v1"
    assert payload["experiment_group"] == "default_control"
    assert set(payload) == {
        "prediction",
        "probability",
        "model_version",
        "experiment_group",
        "request_id",
    }
    assert payload["prediction"] in {0, 1}
    assert 0.0 <= payload["probability"] <= 1.0


def test_predict_returns_400_for_missing_feature(client, sample_request):
    invalid_request = {"features": sample_request["features"].copy()}
    invalid_request["features"].pop("PAY_AMT6")

    response = client.post("/predict", json=invalid_request)
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error_code"] == "invalid_request"
    assert "features.PAY_AMT6" in payload["message"]


def test_predict_returns_400_for_extra_feature(client, sample_request):
    invalid_request = {"features": sample_request["features"].copy()}
    invalid_request["features"]["UNEXPECTED"] = 1

    response = client.post("/predict", json=invalid_request)
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error_code"] == "invalid_request"
    assert "Extra inputs are not permitted" in payload["message"]


def test_predict_returns_400_for_invalid_content_type(client):
    response = client.post("/predict", data="plain-text")

    assert response.status_code == 400
    assert response.get_json()["error_code"] == "invalid_content_type"


def test_predict_returns_400_for_invalid_json(client):
    response = client.post(
        "/predict",
        data="{bad json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json()["error_code"] == "invalid_json"


def test_predict_supports_explicit_model_version(client, sample_request):
    sample_request["model_version"] = "v2"

    response = client.post("/predict", json=sample_request)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["model_version"] == "v2"
    assert payload["experiment_group"] == "test"


def test_predict_uses_stable_experiment_key(client, sample_request):
    headers = {"X-Experiment-Key": "customer-123"}

    first_response = client.post("/predict", json=sample_request, headers=headers)
    second_response = client.post("/predict", json=sample_request, headers=headers)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.get_json()["model_version"] == second_response.get_json()["model_version"]
    assert (
        first_response.get_json()["experiment_group"]
        == second_response.get_json()["experiment_group"]
    )


def test_predict_ignores_input_key_order(client, sample_request):
    reversed_features = dict(reversed(list(sample_request["features"].items())))
    ordered_request = {"model_version": "v1", "features": sample_request["features"]}
    reversed_request = {"model_version": "v1", "features": reversed_features}

    ordered_response = client.post("/predict", json=ordered_request)
    reversed_response = client.post("/predict", json=reversed_request)

    assert ordered_response.status_code == 200
    assert reversed_response.status_code == 200
    assert reversed_response.get_json()["probability"] == pytest.approx(
        ordered_response.get_json()["probability"],
        abs=1e-6,
    )


def test_predict_emits_json_log_line(client, sample_request):
    logger = logging.getLogger("credit_default_service")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    try:
        client.post("/predict", json=sample_request)
    finally:
        logger.removeHandler(handler)

    captured_lines = [line for line in stream.getvalue().splitlines() if line.strip()]
    log_record = json.loads(captured_lines[-1])

    assert log_record["route"] == "/predict"
    assert log_record["status_code"] == 200
    assert "request_id" in log_record
