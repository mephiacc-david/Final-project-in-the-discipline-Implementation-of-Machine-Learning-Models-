# MLOps Concepts

## DVC

В текущем проекте raw CSV хранится прямо в репозитории, потому что объём небольшой и это упрощает воспроизводимость для учебного кейса.

Если проект перерастёт MVP, `DVC` нужен для:

- versioning больших датасетов и промежуточных train artifacts;
- привязки конкретного model artifact к конкретному snapshot данных;
- репликации данных между разработчиками и CI без хранения бинарных blobs в Git.

## MLflow

Сейчас metadata каждой модели лежит рядом с artifact в JSON. Это минимально достаточно для MVP.

`MLflow` имеет смысл добавить, если понадобятся:

- experiment tracking для множества train runs;
- сравнение параметров и метрик без ручного markdown-отчёта;
- централизованный model registry c promotion stage.

## ONNX-ML

В проекте сохранены native scikit-learn artifacts через `joblib`, потому что это минимальный путь без лишней конверсии.

`ONNX-ML` можно рассматривать, если нужны:

- runtime вне Python;
- более строгая portability между средами;
- унифицированный inference-формат для нескольких сервисов.

Пока выгода от конверсии ниже её операционной цены.

## uWSGI + NGINX

В MVP Docker-образ поднимает Flask через Gunicorn.

В production `NGINX + uWSGI/Gunicorn` нужен для:

- reverse proxy и SSL termination;
- rate limiting;
- buffering и управление timeouts;
- разделения edge concerns и WSGI runtime.

## RabbitMQ

Текущий сервис синхронный и stateless. Message broker ему не нужен в core online path.

`RabbitMQ` станет полезен, если появятся:

- асинхронный inference audit log;
- batch scoring;
- fan-out событий в несколько downstream consumers;
- декуплинг между online inference и тяжёлой постобработкой.

## JSON Logging and ELK-like Stack

Сервис уже пишет структурированные JSON-логи в `stdout`.

Дальнейший production path:

1. Docker runtime пишет `stdout`.
2. Агент сбора логов читает контейнерный stream.
3. Логи отправляются в Elasticsearch/OpenSearch.
4. Kibana/OpenSearch Dashboards используются для поиска и дашбордов.

Текущие поля логов уже пригодны для этого:

- `request_id`
- `route`
- `status_code`
- `latency_ms`
- `model_version`
- `experiment_group`

## Business Metrics

Для этого кейса практичны минимум две бизнес-метрики.

1. Default capture rate
   Прокси-метрика на основе `Recall` по классу дефолта. Показывает, какую долю реальных дефолтов система успевает подсветить.
2. Manual review load
   Доля клиентов, которых модель отправляет в positive class. Это прокси для объёма ручной проверки или ужесточённых risk actions.

Явные допущения:

- cost matrix банка в задании не дана;
- labels могут приходить с задержкой;
- поэтому итоговая оценка rollout должна делаться по matured cohorts, а не по сырым свежим данным.

