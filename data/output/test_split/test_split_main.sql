-- File: test_split_main.sql
-- Type: Main Query
-- References CTEs from: test_split_05.sql

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

