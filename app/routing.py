from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.common.constants import DEFAULT_MODEL_VERSION, EXPERIMENT_GROUP_BY_VERSION


@dataclass(frozen=True)
class RoutingDecision:
    model_version: str
    experiment_group: str


def select_model_version(
    explicit_model_version: str | None,
    experiment_key: str | None,
) -> RoutingDecision:
    if explicit_model_version is not None:
        return RoutingDecision(
            model_version=explicit_model_version,
            experiment_group=EXPERIMENT_GROUP_BY_VERSION[explicit_model_version],
        )

    if experiment_key:
        digest = hashlib.sha256(experiment_key.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % 2
        model_version = "v1" if bucket == 0 else "v2"
        return RoutingDecision(
            model_version=model_version,
            experiment_group=EXPERIMENT_GROUP_BY_VERSION[model_version],
        )

    return RoutingDecision(
        model_version=DEFAULT_MODEL_VERSION,
        experiment_group="default_control",
    )
