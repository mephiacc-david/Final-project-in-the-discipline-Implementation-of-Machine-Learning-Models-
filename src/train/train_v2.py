from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from src.train.common import main_summary, train_and_save


def main() -> None:

    estimator = Pipeline(
        steps=[
            (
                "model",
                RandomForestClassifier(
                    class_weight="balanced_subsample",
                    max_depth=8,
                    min_samples_leaf=4,
                    n_estimators=300,
                    random_state=42,
                ),
            )
        ]
    )

    result = train_and_save(
        model_version="v2",
        algorithm="RandomForestClassifier",
        estimator=estimator,
        hyperparameters={
            "class_weight": "balanced_subsample",
            "max_depth": 8,
            "min_samples_leaf": 4,
            "n_estimators": 300,
            "random_state": 42,
        },
    )

    main_summary(result)


if __name__ == "__main__":
    main()
