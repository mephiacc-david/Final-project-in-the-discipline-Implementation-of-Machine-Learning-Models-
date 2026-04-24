from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
DOCS_DIR = ROOT_DIR / "docs"
DATASET_PATH = DATA_DIR / "UCI_Credit_Card.csv"
FEATURE_SCHEMA_PATH = MODELS_DIR / "feature_schema.json"

PYTHON_VERSION = "3.12"
RANDOM_SEED = 42
DEFAULT_MODEL_VERSION = "v1"
SUPPORTED_MODEL_VERSIONS = ("v1", "v2")
TARGET_COLUMN = "default.payment.next.month"
DROP_COLUMNS = ("ID",)

FEATURE_NAMES = [
    "LIMIT_BAL",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
]

FEATURE_TYPES = {feature_name: "integer" for feature_name in FEATURE_NAMES}
EXPERIMENT_GROUP_BY_VERSION = {
    "v1": "control",
    "v2": "test",
}
