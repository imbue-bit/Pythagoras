CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, department_id INTEGER, salary INTEGER);
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO departments (id, name) VALUES (1, 'Sales'), (2, 'HR');
INSERT INTO employees (id, name, department_id, salary) VALUES 
(1, 'Alice', 1, 80000), (2, 'Bob', 2, 75000), (3, 'Charlie', 1, 82000);
