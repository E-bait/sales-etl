-- ============================================================
-- REDASH DASHBOARD — Sales Overview
-- ============================================================


-- [Виджет: Line chart — Нарастающая выручка по дням]
-- Показывает накопленный итог — хорошо видно рост
SELECT
    order_date,
    SUM(total_price)                                                     AS daily_revenue,
    SUM(SUM(total_price)) OVER (ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)                AS running_total
FROM orders
GROUP BY order_date
ORDER BY order_date;


-- [Виджет: Bar chart — Выручка по странам]
SELECT
    country,
    SUM(total_price)    AS revenue,
    COUNT(*)            AS orders
FROM orders
GROUP BY country
ORDER BY revenue DESC;


-- [Виджет: Pie chart — Доля категорий в выручке]
SELECT
    category,
    SUM(total_price) AS revenue
FROM orders
GROUP BY category
ORDER BY revenue DESC;


-- [Виджет: Line chart — Выручка по дням]
SELECT
    order_date,
    SUM(total_price)    AS daily_revenue,
    COUNT(*)            AS orders
FROM orders
GROUP BY order_date
ORDER BY order_date;


-- [Виджет: Table — Топ товар в каждой категории по выручке]
-- RANK() внутри категории — сразу видно лидера в каждой группе
SELECT
    category,
    product,
    SUM(total_price)                                                      AS revenue,
    RANK() OVER (PARTITION BY category ORDER BY SUM(total_price) DESC)   AS rank_in_category
FROM orders
GROUP BY category, product
ORDER BY category, rank_in_category;
