-- Simple test for subquery extraction
CREATE TABLE test1 (id INT, name VARCHAR(50));
CREATE TABLE test2 (id INT, value DECIMAL(10,2));

SELECT t1.name, sub.total_value 
FROM test1 t1
JOIN (
    SELECT id, SUM(value) as total_value 
    FROM test2 
    GROUP BY id
) sub ON t1.id = sub.id;