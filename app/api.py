from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from uuid import uuid4

from flask import Flask, g, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest

from app.errors import ApiError, validation_error_to_message
from app.logging_config import configure_logging, log_event
from app.model_registry import ModelRegistry, ModelRegistryError
from app.routing import select_model_version
from app.validation import build_predict_request_model
from src.common.constants import MODELS_DIR


def create_app(models_dir: Path | str | None = None) -> Flask:
    registry = ModelRegistry(models_dir or _resolve_models_dir())
    predict_request_model = build_predict_request_model(registry.feature_names)
    logger = configure_logging()

    app = Flask(__name__)
    app.config["MODEL_REGISTRY"] = registry
    app.config["PREDICT_REQUEST_MODEL"] = predict_request_model
    app.config["SERVICE_LOGGER"] = logger

    log_event(
        logger,
        logging.INFO,
        "model_registry.loaded",
        available_models=registry.available_models,
    )

    @app.before_request
    def attach_request_context() -> None:
        g.request_id = request.headers.get("X-Request-ID", str(uuid4()))
        g.request_started = time.perf_counter()
        g.model_version = None
        g.experiment_group = None

    @app.after_request
    def log_response(response):  # type: ignore[no-untyped-def]
        latency_ms = round((time.perf_counter() - g.request_started) * 1000, 3)
        level = logging.INFO
        if response.status_code >= 500:
            level = logging.ERROR
        elif response.status_code >= 400:
            level = logging.WARNING

        log_event(
            logger,
            level,
            "request.completed",
            request_id=g.request_id,
            route=request.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
            model_version=g.model_version,
            experiment_group=g.experiment_group,
        )
        response.headers["X-Request-ID"] = g.request_id
        return response

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):  # type: ignore[no-untyped-def]
        payload = {
            "error_code": error.error_code,
            "message": error.message,
            "request_id": getattr(g, "request_id", str(uuid4())),
        }
        if error.details:
            payload["details"] = error.details
        return jsonify(payload), error.status_code

    @app.errorhandler(BadRequest)
    def handle_bad_request(_: BadRequest):  # type: ignore[no-untyped-def]
        error = ApiError(
            error_code="invalid_json",
            message="Request body must contain valid JSON.",
        )
        return handle_api_error(error)

    @app.errorhandler(ModelRegistryError)
    def handle_registry_error(error: ModelRegistryError):  # type: ignore[no-untyped-def]
        logger.exception(
            "model_registry.error",
            extra={"request_id": getattr(g, "request_id", None)},
        )
        return handle_api_error(
            ApiError(
                error_code="internal_error",
                message="Model registry is unavailable.",
                status_code=500,
            )
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):  # type: ignore[no-untyped-def]
        logger.exception(
            "unhandled_exception",
            extra={
                "request_id": getattr(g, "request_id", None),
                "route": request.path if request else None,
            },
        )
        return handle_api_error(
            ApiError(
                error_code="internal_error",
                message="Internal server error.",
                status_code=500,
            )
        )

    @app.get("/health")
    def health():  # type: ignore[no-untyped-def]
        return jsonify(registry.health_payload())

    @app.post("/predict")
    def predict():  # type: ignore[no-untyped-def]
        if not request.is_json:
            raise ApiError(
                error_code="invalid_content_type",
                message="Content-Type must be application/json.",
            )

        payload = request.get_json(silent=False)
        if payload is None:
            raise ApiError(
                error_code="invalid_json",
                message="Request body must contain valid JSON.",
            )

        try:
            parsed_request = predict_request_model.model_validate(payload)
        except ValidationError as error:
            raise ApiError(
                error_code="invalid_request",
                message=validation_error_to_message(error),
            ) from error

        experiment_key = request.headers.get("X-Experiment-Key")
        routing_decision = select_model_version(
            parsed_request.model_version,
            experiment_key,
        )
        g.model_version = routing_decision.model_version
        g.experiment_group = routing_decision.experiment_group

        prediction = registry.predict(
            parsed_request.features.model_dump(mode="python"),
            routing_decision.model_version,
        )
        return jsonify(
            {
                **prediction,
                "model_version": routing_decision.model_version,
                "experiment_group": routing_decision.experiment_group,
                "request_id": g.request_id,
            }
        )

    return app


def _resolve_models_dir() -> Path:
    return Path(os.getenv("MODELS_DIR", MODELS_DIR))


def main() -> None:
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
