-- Test file for DELETE and TRUNCATE statements

-- Simple DELETE statement
DELETE FROM emp WHERE empno = 7369;

-- DELETE with subquery
DELETE FROM emp 
WHERE deptno IN (
    SELECT deptno 
    FROM dept 
    WHERE loc = 'BOSTON'
);

-- DELETE with JOIN syntax (SQL Server style)
DELETE e
FROM emp e
JOIN dept d ON e.deptno = d.deptno
WHERE d.loc = 'BOSTON';

-- TRUNCATE statement
TRUNCATE TABLE temp_table;

-- TRUNCATE with schema
TRUNCATE TABLE scott.emp;