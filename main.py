import logging
from etl.extract import extract
from etl.transform import transform
from etl.load import load

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Параметры подключения к PostgreSQL — замени на свои
DB_PARAMS = {
    "host":     "redash-local-postgres-1",
    "port":     5432,
    "dbname":   "postgres",
    "user":     "postgres",
    "password": "redash_password",
}

CSV_PATH = "data/orders_raw.csv"


def run_pipeline():
    logger.info("=" * 50)
    logger.info("ETL PIPELINE STARTED")
    logger.info("=" * 50)

    # --- Extract ---
    raw_df = extract(CSV_PATH)

    # --- Transform ---
    clean_df, stats = transform(raw_df)

    # Вывод итогов трансформации
    logger.info("-" * 50)
    logger.info(f"Строк на входе:  {stats['input_rows']}")
    logger.info(f"Строк на выходе: {stats['output_rows']}")
    logger.info(f"Удалено:         {stats['removed_rows']}")
    if stats["issues"]:
        logger.info("Найденные проблемы:")
        for issue in stats["issues"]:
            logger.info(f"  • {issue}")
    logger.info("-" * 50)

    # Превью чистых данных
    print("\nЧистые данные (превью):")
    print(clean_df[["order_id", "customer_name", "product", "quantity", "total_price", "order_date"]].to_string(index=False))
    print()

    # --- Load ---
    loaded = load(clean_df, DB_PARAMS)

    logger.info("=" * 50)
    logger.info(f"ETL PIPELINE DONE — загружено {loaded} строк")
    logger.info("=" * 50)


if __name__ == "__main__":
    run_pipeline()
