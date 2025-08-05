-- Test SQL file with complex subqueries

-- DDL
CREATE TABLE sales (
    sale_id INT PRIMARY KEY,
    product_id INT,
    customer_id INT,
    sale_date DATE,
    amount DECIMAL(10,2)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    region VARCHAR(50)
);

-- Main query with complex subqueries
SELECT 
    p.category,
    p.product_name,
    monthly_sales.total_amount,
    monthly_sales.sale_month,
    regional_avg.avg_amount
FROM products p
JOIN (
    -- Complex subquery that could be extracted
    SELECT 
        s.product_id,
        DATE_FORMAT(s.sale_date, '%Y-%m') as sale_month,
        SUM(s.amount) as total_amount,
        COUNT(DISTINCT s.customer_id) as unique_customers
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    WHERE s.sale_date >= DATE_SUB(CURRENT_DATE, INTERVAL 6 MONTH)
    GROUP BY s.product_id, DATE_FORMAT(s.sale_date, '%Y-%m')
    HAVING SUM(s.amount) > 1000
) monthly_sales ON p.product_id = monthly_sales.product_id
LEFT JOIN (
    -- Another complex subquery
    SELECT 
        c.region,
        p.category,
        AVG(s.amount) as avg_amount,
        STDDEV(s.amount) as stddev_amount
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    JOIN products p ON s.product_id = p.product_id
    GROUP BY c.region, p.category
) regional_avg ON p.category = regional_avg.category
WHERE monthly_sales.unique_customers > 10
ORDER BY monthly_sales.total_amount DESC;