from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.model_selection import train_test_split

from src.common.constants import (
    DATASET_PATH,
    DROP_COLUMNS,
    FEATURE_NAMES,
    FEATURE_SCHEMA_PATH,
    FEATURE_TYPES,
    RANDOM_SEED,
    TARGET_COLUMN,
)
from src.common.io import write_json


@dataclass(frozen=True)
class DatasetSplits:
    X_train: pd.DataFrame
    X_validation: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series


def load_raw_dataset(path: str | None = None) -> pd.DataFrame:
    dataset_path = DATASET_PATH if path is None else path
    return pd.read_csv(dataset_path)


def build_feature_schema() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "dataset_source": DATASET_PATH.name,
        "target_column": TARGET_COLUMN,
        "drop_columns": list(DROP_COLUMNS),
        "feature_names": FEATURE_NAMES,
        "feature_types": FEATURE_TYPES,
    }


def export_feature_schema() -> dict[str, Any]:
    schema = build_feature_schema()
    write_json(FEATURE_SCHEMA_PATH, schema)
    return schema


def prepare_features_and_target(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    required_columns = set(FEATURE_NAMES) | {TARGET_COLUMN} | set(DROP_COLUMNS)
    missing_columns = sorted(required_columns.difference(frame.columns))
    if missing_columns:
        missing_joined = ", ".join(missing_columns)
        raise ValueError(f"Dataset is missing required columns: {missing_joined}")

    X = frame[FEATURE_NAMES].copy()
    y = frame[TARGET_COLUMN].astype(int).copy()
    return X, y


def create_splits(random_seed: int = RANDOM_SEED) -> DatasetSplits:
    dataset = load_raw_dataset()
    X, y = prepare_features_and_target(dataset)

    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=random_seed,
        stratify=y,
    )

    X_train, X_validation, y_train, y_validation = train_test_split(
        X_train_full,
        y_train_full,
        test_size=0.25,
        random_state=random_seed,
        stratify=y_train_full,
    )

    return DatasetSplits(
        X_train=X_train,
        X_validation=X_validation,
        X_test=X_test,
        y_train=y_train,
        y_validation=y_validation,
        y_test=y_test,
    )


def main() -> None:
    schema = export_feature_schema()
    splits = create_splits()
    print(
        {
            "feature_count": len(schema["feature_names"]),
            "train_rows": len(splits.X_train),
            "validation_rows": len(splits.X_validation),
            "test_rows": len(splits.X_test),
        }
    )


if __name__ == "__main__":
    main()
