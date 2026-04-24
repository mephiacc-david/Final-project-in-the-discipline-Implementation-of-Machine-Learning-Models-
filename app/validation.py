from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictInt, create_model


def build_predict_request_model(feature_names: list[str]) -> type[BaseModel]:
    feature_model = create_model(
        "CustomerFeatures",
        __config__=ConfigDict(extra="forbid"),
        **{feature_name: (StrictInt, ...) for feature_name in feature_names},
    )
    return create_model(
        "PredictRequest",
        __config__=ConfigDict(extra="forbid"),
        model_version=(Literal["v1", "v2"] | None, None),
        features=(feature_model, ...),
    )
