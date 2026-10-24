import re
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from src import config

MAX_CATEGORY_VALUES = 15


def clean_name(name):
    name = re.sub(r"\W+", "_", str(name).strip()).strip("_")
    if not name or name[0].isdigit():
        name = "t_" + name
    return name


def unique_names(names):
    seen = {}
    result = []
    for name in names:
        count = seen.get(name, 0)
        seen[name] = count + 1
        result.append(name if count == 0 else name + "_" + str(count + 1))
    return result


def read_csv(csv_path):
    try:
        return pd.read_csv(csv_path, sep=None, engine="python", encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(csv_path, sep=None, engine="python", encoding="latin-1")


def load_csv(csv_path):
    csv_path = Path(csv_path)
    df = read_csv(csv_path)
    df.columns = unique_names([clean_name(column) for column in df.columns])
    table = clean_name(csv_path.stem)
    config.DATA_DIR.mkdir(exist_ok=True)
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        old = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        for (name,) in old:
            if not name.startswith("sqlite_"):
                conn.execute('DROP TABLE IF EXISTS "' + name + '"')
        df.to_sql(table, conn, index=False)
        conn.commit()
    return table


def get_table(conn):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name LIMIT 1"
    ).fetchone()
    return row[0] if row else None


def get_columns():
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        table = get_table(conn)
        if table is None:
            return []
        info = conn.execute('PRAGMA table_info("' + table + '")').fetchall()
    return [row[1] for row in info]


def get_schema():
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        table = get_table(conn)
        if table is None:
            return "No data loaded."
        info = conn.execute('PRAGMA table_info("' + table + '")').fetchall()
        lines = ["Table: " + table, "Columns:"]
        for row in info:
            name, kind = row[1], row[2] or "TEXT"
            line = "- " + name + " (" + kind + ")"
            if kind == "TEXT":
                query = (
                    'SELECT DISTINCT "' + name + '" FROM "' + table + '" WHERE "'
                    + name + '" IS NOT NULL LIMIT ' + str(MAX_CATEGORY_VALUES + 1)
                )
                values = [str(item[0])[:40] for item in conn.execute(query)]
                if len(values) <= MAX_CATEGORY_VALUES:
                    line += " possible values: " + ", ".join(values)
            lines.append(line)
        lines.append("Sample rows:")
        for row in conn.execute('SELECT * FROM "' + table + '" LIMIT 3'):
            lines.append(str([str(item)[:40] for item in row]))
    return "\n".join(lines)


def run_query(sql):
    uri = config.DB_PATH.as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        cursor = conn.execute(sql)
        columns = [item[0] for item in cursor.description]
        rows = [list(row) for row in cursor.fetchmany(config.MAX_ROWS)]
    return {"columns": columns, "rows": rows}


def get_text_values(max_values=15):
    values = []
    with sqlite3.connect(config.DB_PATH.as_uri() + "?mode=ro", uri=True) as connection:
        table = get_table(connection)
        if not table:
            return values
        for _, name, kind, *_ in connection.execute('PRAGMA table_info("' + table + '")'):
            if kind.upper() != "TEXT":
                continue
            rows = connection.execute(
                'SELECT DISTINCT "' + name + '" FROM "' + table + '" LIMIT ' + str(max_values + 1)
            ).fetchall()
            if len(rows) <= max_values:
                values += [str(row[0]) for row in rows if row[0] is not None]
    return values
