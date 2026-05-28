import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """

    1. Нормализация текстовых полей (trim, регистр)
    2. Исправление форматов дат
    3. Валидация и приведение числовых полей
    4. Удаление дубликатов
    5. Удаление невалидных строк
    6. Добавление вычисляемых полей (total_price, processed_at)
    
    """
    logger.info("[TRANSFORM] Начинаем трансформацию...")
    stats = {"input_rows": len(df), "issues": []}

    df["customer_name"] = df["customer_name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()
    df["product"] = df["product"].str.strip()
    df["category"] = df["category"].str.strip().str.title()  
    df["country"] = df["country"].str.strip().str.title()    
    logger.info("[TRANSFORM] ✓ Нормализация текстовых полей")


    def parse_date(val):
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(val.strip(), fmt).date()
            except (ValueError, AttributeError):
                continue
        return None

    df["order_date"] = df["order_date"].apply(parse_date)
    bad_dates = df["order_date"].isna().sum()
    if bad_dates:
        stats["issues"].append(f"Невалидные даты: {bad_dates} строк")
        logger.warning(f"[TRANSFORM] ⚠ Невалидные даты в {bad_dates} строках")

    def safe_int(val):
        try:
            result = int(str(val).strip())
            return result
        except (ValueError, TypeError):
            return None

    def safe_float(val):
        try:
            return float(str(val).strip())
        except (ValueError, TypeError):
            return None

    df["quantity"] = df["quantity"].apply(safe_int)
    df["price"] = df["price"].apply(safe_float)

    invalid_qty = df["quantity"].isna() | (df["quantity"] <= 0)
    if invalid_qty.sum():
        stats["issues"].append(f"Невалидное quantity: {invalid_qty.sum()} строк")
        logger.warning(f"[TRANSFORM] Невалидное quantity в {invalid_qty.sum()} строках: {df.loc[invalid_qty, 'order_id'].tolist()}")

    mask_valid = (
        df["email"].notna() & (df["email"] != "") &          
        df["order_date"].notna() &                            
        df["quantity"].notna() & (df["quantity"] > 0) &       
        df["price"].notna() & (df["price"] > 0)               
    )
    dropped = (~mask_valid).sum()
    if dropped:
        dropped_ids = df.loc[~mask_valid, "order_id"].tolist()
        stats["issues"].append(f"Удалено невалидных строк: {dropped} (order_id: {dropped_ids})")
        logger.warning(f"[TRANSFORM] Удаляем {dropped} невалидных строк: order_id={dropped_ids}")

    df = df[mask_valid].copy()

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["email", "product", "order_date"], keep="first")
    deduped = before_dedup - len(df)
    if deduped:
        stats["issues"].append(f"Удалено дубликатов: {deduped}")
        logger.warning(f"[TRANSFORM] Удалено {deduped} дубликатов")

    df["total_price"] = (df["quantity"] * df["price"]).round(2)
    df["processed_at"] = datetime.utcnow()

    df["order_id"] = df["order_id"].astype(int)
    df["quantity"] = df["quantity"].astype(int)
    df["price"] = df["price"].astype(float)

    stats["output_rows"] = len(df)
    stats["removed_rows"] = stats["input_rows"] - stats["output_rows"]

    logger.info(f"[TRANSFORM] Трансформация завершена: {stats['input_rows']} → {stats['output_rows']} строк")
    return df, stats
