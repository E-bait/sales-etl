-- Общая выручка и количество заказов
SELECT
    COUNT(*)         AS total_orders,
    SUM(total_price) AS total_revenue
FROM orders;
 
 
-- Выручка по странам
SELECT
    country,
    SUM(total_price) AS revenue
FROM orders
GROUP BY country
ORDER BY revenue DESC;
 
 
-- Выручка по категориям
SELECT
    category,
    SUM(total_price) AS revenue
FROM orders
GROUP BY category
ORDER BY revenue DESC;
 
 
-- Нарастающая выручка по дням
SELECT
    TO_CHAR(order_date, 'DD Mon') AS day,
    SUM(total_price) AS daily_revenue,
    SUM(SUM(total_price)) OVER (ORDER BY order_date) AS running_total
FROM orders
GROUP BY order_date
ORDER BY order_date;
 
 
-- Топ товар в каждой категории по выручке
SELECT
    category,
    product,
    SUM(total_price)                                                    AS revenue,
    RANK() OVER (PARTITION BY category ORDER BY SUM(total_price) DESC) AS rank_in_category
FROM orders
GROUP BY category, product
ORDER BY category, rank_in_category;
 
