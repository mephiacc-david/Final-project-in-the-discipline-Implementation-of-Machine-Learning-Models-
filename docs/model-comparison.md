# Model Comparison

## Holdout Results

Общая схема:

- dataset: `UCI_Credit_Card.csv`
- feature count: `23`
- split: `60% train / 20% validation / 20% test`
- random seed: `42`

| Model | Algorithm | Threshold | F1 | Precision | Recall |
| --- | --- | ---: | ---: | ---: | ---: |
| v1 | LogisticRegression | 0.56 | 0.500939 | 0.499251 | 0.502638 |
| v2 | RandomForestClassifier | 0.54 | 0.541096 | 0.546503 | 0.535795 |

## Baseline vs Candidate

`v1` выбран baseline, потому что:

- модель проще и лучше интерпретируется;
- её легче объяснить;
- она задаёт минимально достаточную точку отсчёта.

`v2` выбран candidate, потому что:

- на том же holdout split показывает лучший `F1`;
- улучшает `Precision`;
- улучшает `Recall`;
- остаётся в пределах допустимого семейства моделей из PDR.

## Rollout Rationale

Несмотря на лучший офлайн-результат `v2`, baseline остаётся `v1`, а `v2` идёт в A/B как experimental model.

Причина:

- офлайн uplift не равен production uplift;
- labels дефолта delayed;
- необходимо проверить, что улучшение сохраняется на mature cohorts и не ведёт к нежелательному росту операционной нагрузки.

