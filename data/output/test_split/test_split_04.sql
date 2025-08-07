-- File: test_split_04.sql
-- Type: Temporary Table

-- Create temporary table
CREATE TEMPORARY TABLE temp_high_salaries AS
SELECT emp_id, emp_name, salary
FROM employees
WHERE salary > 100000;
