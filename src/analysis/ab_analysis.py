from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.metrics import f1_score
from statsmodels.stats.proportion import proportions_ztest


def bootstrap_f1_delta(
    y_true: np.ndarray,
    control_probabilities: np.ndarray,
    test_probabilities: np.ndarray,
    *,
    control_threshold: float,
    test_threshold: float,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    deltas: list[float] = []
    indices = np.arange(len(y_true))
    for _ in range(n_bootstrap):
        sample_idx = rng.choice(indices, size=len(indices), replace=True)
        sample_y = y_true[sample_idx]
        control_pred = (control_probabilities[sample_idx] >= control_threshold).astype(int)
        test_pred = (test_probabilities[sample_idx] >= test_threshold).astype(int)
        control_f1 = f1_score(sample_y, control_pred, zero_division=0)
        test_f1 = f1_score(sample_y, test_pred, zero_division=0)
        deltas.append(test_f1 - control_f1)
    delta_array = np.array(deltas)
    return (
        float(delta_array.mean()),
        float(np.percentile(delta_array, 2.5)),
        float(np.percentile(delta_array, 97.5)),
    )


def two_proportion_test(successes: Iterable[int], totals: Iterable[int]) -> tuple[float, float]:
    counts = np.array(list(successes))
    observations = np.array(list(totals))
    statistic, p_value = proportions_ztest(counts, observations)
    return float(statistic), float(p_value)
