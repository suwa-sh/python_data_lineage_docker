-- File: test_split_01.sql
-- Type: DDL

-- Test SQL file for splitting

-- DDL: Create tables
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    dept_id INT,
    salary DECIMAL(10,2)
);
