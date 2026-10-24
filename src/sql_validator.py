import re

FORBIDDEN = (
    "insert", "update", "delete", "drop", "alter", "create",
    "attach", "detach", "pragma", "vacuum", "reindex", "truncate",
)


class UnsafeSQLError(ValueError):
    pass


def strip_strings(sql):
    sql = re.sub(r"'(?:[^']|'')*'", "''", sql)
    sql = re.sub(r'"(?:[^"]|"")*"', '""', sql)
    return sql


def validate_sql(sql):
    sql = sql.strip().rstrip(";").strip()
    if not sql:
        raise UnsafeSQLError("The query is empty.")
    body = strip_strings(sql)
    if ";" in body:
        raise UnsafeSQLError("Only one statement is allowed.")
    if "--" in body or "/*" in body:
        raise UnsafeSQLError("Comments are not allowed.")
    if not re.match(r"(select|with)\b", body, re.IGNORECASE):
        raise UnsafeSQLError("Only SELECT queries are allowed.")
    for word in FORBIDDEN:
        if re.search(r"\b" + word + r"\b", body, re.IGNORECASE):
            raise UnsafeSQLError("The keyword " + word.upper() + " is not allowed.")
    return sql
