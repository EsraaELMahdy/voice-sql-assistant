from src import database, explain

sql = "SELECT category, SUM(quantity * price) AS total_sales FROM sales GROUP BY category"
result = database.run_query(sql)

print(explain.explain_result("Show me total sales by category", sql, result))
print()
print(explain.explain_result("???? ?? ?????? ???????? ??? ???", sql, result))
