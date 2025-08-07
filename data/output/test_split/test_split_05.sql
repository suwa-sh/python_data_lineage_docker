-- File: test_split_05.sql
-- Type: CTE (Common Table Expression)
-- Note: This will be combined with main query

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
