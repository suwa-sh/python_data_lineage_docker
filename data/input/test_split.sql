-- Test SQL file for splitting

-- DDL: Create tables
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    dept_id INT,
    salary DECIMAL(10,2)
);

CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(100)
);

-- Create index
CREATE INDEX idx_emp_dept ON employees(dept_id);

-- Create temporary table
CREATE TEMPORARY TABLE temp_high_salaries AS
SELECT emp_id, emp_name, salary
FROM employees
WHERE salary > 100000;

-- Main query with CTE
WITH dept_summary AS (
    SELECT 
        d.dept_id,
        d.dept_name,
        COUNT(e.emp_id) as emp_count,
        AVG(e.salary) as avg_salary
    FROM departments d
    LEFT JOIN employees e ON d.dept_id = e.dept_id
    GROUP BY d.dept_id, d.dept_name
),
high_earners AS (
    SELECT 
        emp_id,
        emp_name,
        salary,
        dept_id
    FROM employees
    WHERE salary > (SELECT AVG(salary) FROM employees)
)
SELECT 
    ds.dept_name,
    ds.emp_count,
    ds.avg_salary,
    he.emp_name as top_earner,
    he.salary as top_salary
FROM dept_summary ds
LEFT JOIN high_earners he ON ds.dept_id = he.dept_id
WHERE ds.avg_salary > 50000
ORDER BY ds.avg_salary DESC;