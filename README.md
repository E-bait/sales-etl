# ETL Demo — Продажи интернет-магазина

Простой ETL-пайплайн: CSV → Python → PostgreSQL.

## Структура проекта

```
etl_project/
├── data/
│   └── orders_raw.csv      # сырые данные с намеренными проблемами
├── etl/
│   ├── extract.py          # чтение CSV
│   ├── transform.py        # очистка и обогащение
│   └── load.py             # запись в PostgreSQL
├── main.py                 # запуск пайплайна
├── requirements.txt
└── queries.sql             # полезные запросы для проверки
```

## Установка

```bash
pip install -r requirements.txt
```

## Настройка БД

Создай базу в PostgreSQL:

```sql
CREATE DATABASE etl_demo;
```

Затем укажи свои параметры подключения в `main.py`:

```python
DB_PARAMS = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "etl_demo",
    "user":     "postgres",
    "password": "your_password",
}
```

## Запуск

```bash
python main.py
```

## Что делает пайплайн

**Extract** — читает `orders_raw.csv` как есть, без изменений.

**Transform** — очищает данные:
- нормализует регистр (ANNA → Anna, "electronics" → "Electronics")
- приводит даты к единому формату (15.01.2024 и 17-01-2024 → 2024-01-15)
- удаляет строки с пустым email или невалидными числами
- удаляет дубликаты (по email + product + date)
- добавляет `total_price = quantity × price` и `processed_at`

**Load** — создаёт таблицу `orders` (если нет) и делает upsert — можно запускать повторно без дубликатов в БД.

## Проблемы в сырых данных

| order_id | Проблема |
|---|---|
| 1002 | Капслок в имени, "electronics" в нижнем регистре, дата "15.01.2024" |
| 1003 | Пустой email → удаляется |
| 1004 | quantity = -1 → удаляется |
| 1005 | Дубликат строки 1001 → удаляется |
| 1008 | Дата "17-01-2024" (нестандартный формат) |
| 1009 | Лишние пробелы в category: "  Electronics  " |
| 1010 | quantity = 0 → удаляется |
| 1014 | quantity = "abc" → удаляется |
| 1015 | Дубликат строки 1008 → удаляется |
