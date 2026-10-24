import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src import config

llm = ChatOpenAI(
    model=config.LLM_MODEL,
    base_url=config.LLM_BASE_URL,
    api_key=config.openrouter_api_key,
    temperature=config.LLM_TEMPERATURE,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert SQLite data analyst.
Convert the user's request into exactly one SQLite SELECT query.
The request comes from speech transcription, so it may contain spelling mistakes, extra commas, and may be in Arabic or English.
Understand the intent and map it to the table and column names in the schema below.

Rules:
- Use only the tables and columns that exist in the schema.
- Write exactly one SELECT statement in SQLite syntax.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or PRAGMA.
- If a value must be calculated from several columns, calculate it inside the query.
- Use clear English aliases for calculated columns.
- Compare text values case-insensitively, for example: WHERE city = 'Austin' COLLATE NOCASE.
- Return only the SQL query, with no explanation and no markdown.

Examples (for a different schema: employees with name, department, salary):
Request: average salary per department
SQL: SELECT department, AVG(salary) AS avg_salary FROM employees GROUP BY department
Request: ???? ???? 3 ?????? ?? ??? ??????
SQL: SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3

Database schema:
{schema}"""),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()


def clean_sql(text):
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    start = re.search(r"\b(select|with)\b", text, re.IGNORECASE)
    if start:
        text = text[start.start():]
    return text.strip().rstrip(";").strip()


def generate_sql(question, schema):
    output = chain.invoke({"question": question, "schema": schema})
    return clean_sql(output)

