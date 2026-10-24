from src.sql_validator import validate_sql, UnsafeSQLError

tests = [
    "SELECT * FROM sales;",
    "DROP TABLE sales",
    "SELECT 1; DELETE FROM sales",
    "DELETE FROM sales",
    "SELECT * FROM sales -- hello",
    "SELECT * FROM sales WHERE product = 'delete'",
    "WITH t AS (SELECT * FROM sales) SELECT COUNT(*) FROM t",
]

for sql in tests:
    try:
        print("OK   ", validate_sql(sql))
    except UnsafeSQLError as error:
        print("BLOCK", sql, "->", error)
