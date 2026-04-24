# Data

Источник: `Default of Credit Card Clients Dataset` из UCI.

- Файл: `data/UCI_Credit_Card.csv`
- Target: `default.payment.next.month`
- Исключённый столбец: `ID`
- Feature schema экспортируется в `models/feature_schema.json`

Команда подготовки данных:

```bash
python -m src.data.make_dataset
```