import pandas as pd
import logging

logger = logging.getLogger(__name__)


def extract(filepath: str) -> pd.DataFrame:

    logger.info(f"[EXTRACT] Читаем файл: {filepath}")

    df = pd.read_csv(filepath, dtype=str)

    logger.info(f"[EXTRACT] Загружено строк: {len(df)}, колонок: {len(df.columns)}")
    logger.info(f"[EXTRACT] Колонки: {list(df.columns)}")

    return df
