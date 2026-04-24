# A/B Test Plan

## Experiment Setup

- Control: `v1`
- Test: `v2`
- Split: `50/50`
- Assignment rule: `SHA-256(X-Experiment-Key) % 2`
- Endpoint: один и тот же `POST /predict`
- Runtime contract: обе версии доступны через один сервис


## Duration

Минимальная длительность: `4 недели` после достижения достаточного числа mature cohorts.

Причина:

- target по дефолту имеет задержку;
- ранние online данные нельзя использовать как финальный критерий без labels.

## Metrics

Primary metric:

- `F1-score` по классу дефолта

Secondary metric:

- `Precision` по классу дефолта

Guardrails:

- доля позитивных предсказаний не должна расти больше чем на 10% относительно control;
- error rate API (`5xx`) не должна ухудшаться;
- p95 latency не должна превышать `500 ms`.

## Statistical Analysis

- Для `delta F1` используется `bootstrap 95% CI`.
- Для долевых secondary и guardrail metrics допускается `two-proportion z-test`.
- Анализ выполняется по matured cohorts, а не по всем свежим запросам.

Шаблон расчёта вынесен в `src/analysis/ab_analysis.py`.

## Success Criterion

Эксперимент считается успешным, если одновременно выполнены условия:

1. Нижняя граница `95% CI` для `delta F1 = F1(v2) - F1(v1)` больше `0`.
2. `Precision(v2)` не ухудшается более чем на `0.01` относительно `Precision(v1)`.
3. Guardrail-метрики не нарушены.

Если хотя бы одно условие не выполнено, `v2` не переводится в default path.

## Risks

- delayed labels могут дать ложный ранний сигнал;
- user mix в control и test должен быть сопоставим по стабильному `X-Experiment-Key`;
- метрики нужно считать отдельно по сегментам, если появится выраженный skew по клиентским группам.

