import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id     INTEGER PRIMARY KEY,
    customer_name VARCHAR(200),
    email        VARCHAR(200),
    product      VARCHAR(300),
    category     VARCHAR(100),
    quantity     INTEGER,
    price        NUMERIC(12, 2),
    total_price  NUMERIC(12, 2),
    order_date   DATE,
    country      VARCHAR(100),
    processed_at TIMESTAMP
);
"""

UPSERT_SQL = """
INSERT INTO orders (
    order_id, customer_name, email, product, category,
    quantity, price, total_price, order_date, country, processed_at
)
VALUES %s
ON CONFLICT (order_id) DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    email         = EXCLUDED.email,
    product       = EXCLUDED.product,
    category      = EXCLUDED.category,
    quantity      = EXCLUDED.quantity,
    price         = EXCLUDED.price,
    total_price   = EXCLUDED.total_price,
    order_date    = EXCLUDED.order_date,
    country       = EXCLUDED.country,
    processed_at  = EXCLUDED.processed_at;
"""


def load(df: pd.DataFrame, conn_params: dict) -> int:
    """
    Создаёт таблицу (если не существует) и загружает данные через upsert.
    Возвращает количество загруженных строк.
    """
    logger.info("[LOAD] Подключаемся к PostgreSQL...")

    conn = psycopg2.connect(**conn_params)
    conn.autocommit = False  

    try:
        with conn.cursor() as cur:
            
            cur.execute(CREATE_TABLE_SQL)
            logger.info("[LOAD] ✓ Таблица orders готова")

            columns = [
                "order_id", "customer_name", "email", "product", "category",
                "quantity", "price", "total_price", "order_date", "country", "processed_at"
            ]
            rows = [tuple(row[col] for col in columns) for _, row in df.iterrows()]

            execute_values(cur, UPSERT_SQL, rows)
            count = cur.rowcount

        conn.commit()
        logger.info(f"[LOAD] Загружено {count} строк в таблицу orders")
        return count

    except Exception as e:
        conn.rollback()
        logger.error(f"[LOAD] Ошибка при загрузке: {e}")
        raise

    finally:
        conn.close()
