# Credit Default Inference Service

Production-like ML-сервис для прогноза дефолта по кредитным картам на датасете UCI `Default of Credit Card Clients`.

Сервис реализован как stateless Flask-монолит с двумя версиями модели:

- `v1` — baseline `LogisticRegression`
- `v2` — candidate `RandomForestClassifier`

Сервис принимает JSON с признаками одного клиента, валидирует payload по фиксированной feature schema, выбирает модель по `model_version` или `X-Experiment-Key`, возвращает бинарный прогноз и вероятность дефолта, а также пишет JSON-логи в `stdout`.

Кратко по слоям проекта:

- `app/` — online-часть сервиса: Flask API, валидация входного запроса, выбор версии модели и настройка логирования.
- `src/` — offline-код для подготовки данных, обучения моделей и анализа результатов A/B-эксперимента.
- `models/` — готовые артефакты для inference: сериализованные модели, metadata и схема признаков.
- `tests/` — unit- и integration-тесты для API, routing и загрузки моделей.
- `docs/` — документация по архитектуре, API-контракту и сравнению моделей.
- `data/` — исходный датасет.

Поток работы в репозитории такой: `src/` подготавливает данные и обучает модели, артефакты сохраняются в `models/`, после чего `app/` использует их для online-predict в API.

## Local Run

Установка и подготовка:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m src.data.make_dataset
python -m src.train.train_all
```

Локальный запуск API:

```bash
python -m app.api
```

Smoke checks:

```bash
curl http://127.0.0.1:5000/health
```

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "LIMIT_BAL": 20000,
      "SEX": 2,
      "EDUCATION": 2,
      "MARRIAGE": 1,
      "AGE": 24,
      "PAY_0": 2,
      "PAY_2": 2,
      "PAY_3": -1,
      "PAY_4": -1,
      "PAY_5": -2,
      "PAY_6": -2,
      "BILL_AMT1": 3913,
      "BILL_AMT2": 3102,
      "BILL_AMT3": 689,
      "BILL_AMT4": 0,
      "BILL_AMT5": 0,
      "BILL_AMT6": 0,
      "PAY_AMT1": 0,
      "PAY_AMT2": 689,
      "PAY_AMT3": 0,
      "PAY_AMT4": 0,
      "PAY_AMT5": 0,
      "PAY_AMT6": 0
    }
  }'
```

Явный вызов candidate-модели:

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_version": "v2",
    "features": {
      "LIMIT_BAL": 20000,
      "SEX": 2,
      "EDUCATION": 2,
      "MARRIAGE": 1,
      "AGE": 24,
      "PAY_0": 2,
      "PAY_2": 2,
      "PAY_3": -1,
      "PAY_4": -1,
      "PAY_5": -2,
      "PAY_6": -2,
      "BILL_AMT1": 3913,
      "BILL_AMT2": 3102,
      "BILL_AMT3": 689,
      "BILL_AMT4": 0,
      "BILL_AMT5": 0,
      "BILL_AMT6": 0,
      "PAY_AMT1": 0,
      "PAY_AMT2": 689,
      "PAY_AMT3": 0,
      "PAY_AMT4": 0,
      "PAY_AMT5": 0,
      "PAY_AMT6": 0
    }
  }'
```

Детерминированный A/B routing:

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -H "X-Experiment-Key: customer-123" \
  -d @request.json
```

## Docker Run

Сборка:

```bash
docker build -t credit-default-service:local .
```

Запуск:

```bash
docker run --rm -p 5000:5000 credit-default-service:local
```

Bonus-compose сценарий:

```bash
docker compose up --build
```

## Model Artifacts

Артефакты хранятся в `models/`:

- `feature_schema.json`
- `model_v1.joblib`
- `model_v1.metadata.json`
- `model_v2.joblib`
- `model_v2.metadata.json`

Метрики:

- `v1`: `F1=0.500939`, `Precision=0.499251`, `Recall=0.502638`, `threshold=0.56`
- `v2`: `F1=0.541096`, `Precision=0.546503`, `Recall=0.535795`, `threshold=0.54`

## Quality Checks

Основные команды:

```bash
make test
make quality-check
make docker-build
```

`quality-check` включает:

- `ruff`
- `black --check`
- `pytest --cov`
- `bandit`
- `pip-audit`

GitHub Actions:

- `.github/workflows/ci.yml` — lint, tests, coverage, security, docker build
- `.github/workflows/release.yml` — build and push to Docker Hub on tag/manual trigger

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API.md](docs/API.md)
- [docs/openapi.yaml](docs/openapi.yaml)
- [docs/MLOPS-CONCEPTS.md](docs/MLOPS-CONCEPTS.md)
- [docs/model-comparison.md](docs/model-comparison.md)
- [ab_test_plan.md](ab_test_plan.md)
