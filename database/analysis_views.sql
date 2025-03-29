/*
E-commerce Database - Analysis Views
-----------------------------------
This script creates SQL views for common analysis tasks and reporting.
These views simplify data access for visualization tools like Tableau and Power BI.
*/

-- 1. Daily Sales View - Aggregates sales by day
CREATE OR REPLACE VIEW vw_daily_sales AS
SELECT
    DATE(order_date) AS sale_date,
    COUNT(DISTINCT order_id) AS num_orders,
    COUNT(DISTINCT customer_id) AS num_customers,
    SUM(total_amount) AS total_revenue,
    SUM(total_amount) / COUNT(DISTINCT order_id) AS average_order_value
FROM orders
GROUP BY DATE(order_date)
ORDER BY sale_date;

-- 2. Monthly Sales View - Aggregates sales by month
CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(DISTINCT order_id) AS num_orders,
    COUNT(DISTINCT customer_id) AS num_customers,
    SUM(total_amount) AS total_revenue,
    SUM(total_amount) / COUNT(DISTINCT order_id) AS average_order_value
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- 3. Product Sales View - Aggregates sales by product
CREATE OR REPLACE VIEW vw_product_sales AS
SELECT
    p.product_id,
    p.description,
    p.category,
    COUNT(DISTINCT oi.order_id) AS num_orders,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.total_price) AS total_revenue,
    AVG(oi.unit_price) AS average_unit_price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.description, p.category
ORDER BY total_revenue DESC;

-- 4. Country Sales View - Aggregates sales by country
CREATE OR REPLACE VIEW vw_country_sales AS
SELECT
    o.country,
    COUNT(DISTINCT o.order_id) AS num_orders,
    COUNT(DISTINCT o.customer_id) AS num_customers,
    SUM(o.total_amount) AS total_revenue,
    AVG(o.total_amount) AS average_order_value
FROM orders o
GROUP BY o.country
ORDER BY total_revenue DESC;

-- 5. Customer Purchase History - Customer purchase details
CREATE OR REPLACE VIEW vw_customer_purchase_history AS
SELECT
    c.customer_id,
    c.country,
    c.first_purchase_date,
    c.last_purchase_date,
    EXTRACT(DAY FROM NOW() - c.last_purchase_date) AS days_since_last_purchase,
    c.total_purchases,
    c.total_spent,
    c.total_spent / NULLIF(c.total_purchases, 0) AS average_order_value,
    cs.segment
FROM customers c
LEFT JOIN customer_segments cs ON c.customer_id = cs.customer_id;

-- 6. RFM Analysis View - Detailed RFM metrics for customers
CREATE OR REPLACE VIEW vw_rfm_analysis AS
SELECT
    cs.customer_id,
    c.country,
    EXTRACT(DAY FROM NOW() - c.last_purchase_date) AS recency_days,
    c.total_purchases AS frequency,
    c.total_spent AS monetary,
    cs.recency_score,
    cs.frequency_score,
    cs.monetary_score,
    cs.rfm_score,
    cs.segment
FROM customer_segments cs
JOIN customers c ON cs.customer_id = c.customer_id;

-- 7. Product Category Analysis - Aggregates sales by product category
CREATE OR REPLACE VIEW vw_category_analysis AS
SELECT
    p.category,
    COUNT(DISTINCT p.product_id) AS num_products,
    COUNT(DISTINCT oi.order_id) AS num_orders,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.total_price) AS total_revenue,
    SUM(oi.total_price) / SUM(oi.quantity) AS average_unit_price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 8. Customer-Product Affinity - Which customers buy which products
CREATE OR REPLACE VIEW vw_customer_product_affinity AS
SELECT
    o.customer_id,
    p.category,
    COUNT(DISTINCT o.order_id) AS num_orders,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.total_price) AS total_spent
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.customer_id, p.category
ORDER BY o.customer_id, total_spent DESC;

-- 9. Time-based Analysis - Hour of day and day of week analysis
CREATE OR REPLACE VIEW vw_time_analysis AS
SELECT
    EXTRACT(DOW FROM order_date) AS day_of_week,
    EXTRACT(HOUR FROM order_date) AS hour_of_day,
    COUNT(DISTINCT order_id) AS num_orders,
    SUM(total_amount) AS total_revenue
FROM orders
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;

-- 10. Customer Segment Performance - Performance metrics by customer segment
CREATE OR REPLACE VIEW vw_segment_performance AS
SELECT
    cs.segment,
    COUNT(DISTINCT cs.customer_id) AS num_customers,
    AVG(c.total_purchases) AS avg_purchase_frequency,
    AVG(c.total_spent) AS avg_customer_spend,
    SUM(c.total_spent) AS total_segment_revenue,
    MIN(c.first_purchase_date) AS earliest_purchase,
    MAX(c.last_purchase_date) AS latest_purchase
FROM customer_segments cs
JOIN customers c ON cs.customer_id = c.customer_id
GROUP BY cs.segment
ORDER BY total_segment_revenue DESC;