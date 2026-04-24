from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.train.common import main_summary, train_and_save


def main() -> None:

    estimator = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                    solver="liblinear",
                ),
            ),
        ]
    )

    result = train_and_save(
        model_version="v1",
        algorithm="LogisticRegression",
        estimator=estimator,
        hyperparameters={
            "class_weight": "balanced",
            "max_iter": 2000,
            "random_state": 42,
            "solver": "liblinear",
        },
    )
    main_summary(result)


if __name__ == "__main__":
    main()
