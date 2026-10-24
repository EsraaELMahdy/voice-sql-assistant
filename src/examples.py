PAIRS = [
    ("How many rows are there", "SELECT COUNT(*) AS total_rows FROM employees"),
    ("What is the average salary", "SELECT AVG(salary) AS average_salary FROM employees"),
    ("Show the five highest salaries", "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 5"),
    ("Total sales per region", "SELECT region, SUM(price * quantity) AS total_sales FROM orders GROUP BY region"),
    ("How many employees are in each department", "SELECT department, COUNT(*) AS employee_count FROM employees GROUP BY department"),
    ("Average salary in Cairo", "SELECT AVG(salary) AS average_salary FROM employees WHERE city = 'Cairo' COLLATE NOCASE"),
    ("Which department has the highest average salary", "SELECT department, AVG(salary) AS average_salary FROM employees GROUP BY department ORDER BY average_salary DESC LIMIT 1"),
    ("How many employees are older than 30", "SELECT COUNT(*) AS employee_count FROM employees WHERE age > 30"),
    ("What is the maximum price", "SELECT MAX(price) AS max_price FROM orders"),
    ("كم عدد الصفوف", "SELECT COUNT(*) AS total_rows FROM employees"),
    ("ما هو متوسط الراتب", "SELECT AVG(salary) AS average_salary FROM employees"),
    ("اعرض أعلى خمسة رواتب", "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 5"),
    ("إجمالي المبيعات لكل منطقة", "SELECT region, SUM(price * quantity) AS total_sales FROM orders GROUP BY region"),
    ("كم عدد الموظفين في كل قسم", "SELECT department, COUNT(*) AS employee_count FROM employees GROUP BY department"),
    ("متوسط الراتب في القاهرة", "SELECT AVG(salary) AS average_salary FROM employees WHERE city = 'Cairo' COLLATE NOCASE"),
    ("أي قسم لديه أعلى متوسط راتب", "SELECT department, AVG(salary) AS average_salary FROM employees GROUP BY department ORDER BY average_salary DESC LIMIT 1"),
    ("كم عدد الموظفين الذين أعمارهم أكبر من 30", "SELECT COUNT(*) AS employee_count FROM employees WHERE age > 30"),
    ("ما هو أعلى سعر", "SELECT MAX(price) AS max_price FROM orders"),
]

EXAMPLES = [{"question": question, "sql": sql} for question, sql in PAIRS]