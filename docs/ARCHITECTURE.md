# Architecture

## Chosen Architecture

Выбран stateless монолитный inference-сервис на Flask с отдельным offline training pipeline.

Почему не микросервисы:

- один bounded context: credit default inference;
- один API и один runtime process;
- нет независимых сервисов, которые нужно масштабировать отдельно;
- учебный production-like кейс выигрывает от простоты, а не от инфраструктурной сложности.

## Components

1. `src/data`
   Подготовка датасета, исключение `ID`, фиксация feature schema и deterministic split.
2. `src/train`
   Обучение `v1` и `v2`, подбор threshold на validation, сериализация `.joblib` и metadata.
3. `models/`
   Runtime-ready артефакты и `feature_schema.json`.
4. `app/`
   Flask API, validation, model registry, routing, JSON logging.
5. Docker + GitHub Actions
   Воспроизводимый runtime и quality gates.

## Request Flow

1. Клиент отправляет `POST /predict` с `application/json`.
2. Сервис создаёт `request_id`.
3. Payload валидируется строго по `models/feature_schema.json`.
4. Версия модели выбирается по правилу:
   - explicit `model_version`;
   - иначе `X-Experiment-Key`;
   - иначе default `v1`.
5. `ModelRegistry` загружает нужный artifact и вызывает `predict_proba`.
6. Вероятность сравнивается с threshold из metadata.
7. Ответ возвращается клиенту, а access log уходит в `stdout` как JSON.

## Feature Contract

Feature order берётся только из `models/feature_schema.json`.

Сервис не:

- сортирует JSON keys;
- не угадывает missing fields;
- не игнорирует extra fields;
- не переобучает модель на старте.

## Runtime Reliability

- На старте загружаются обе модели.
- Отсутствие schema, metadata или `.joblib` вызывает fail-fast через `ModelRegistryError`.
- Полный payload не логируется.
- Ошибки клиента возвращаются как управляемые `400`.
- Внутренние ошибки возвращаются как `500` без traceback в HTTP-ответе.

## Logging

Каждый запрос к `/health` и `/predict` пишет JSON line в `stdout`.

Минимальные поля:

- `timestamp`
- `level`
- `request_id`
- `route`
- `status_code`
- `latency_ms`
- `model_version`
- `experiment_group`

## Future Evolution

`RabbitMQ`, `DVC`, `MLflow`, `ONNX`, `uWSGI + NGINX` описаны отдельно в [MLOPS-CONCEPTS.md](MLOPS-CONCEPTS.md) как следующий шаг, но не добавлены в runtime MVP.

