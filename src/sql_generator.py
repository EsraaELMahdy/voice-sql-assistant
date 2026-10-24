import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src import config, example_store

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
- Use single quotes for text values.
- Return only the SQL query, with no explanation and no markdown.

Solved examples of similar requests. They use a different schema, so only follow their query pattern and adapt the table and column names to the schema below:
{examples}

Database schema:
{schema}"""),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()


def get_examples_text(question):
    try:
        found = example_store.find_examples(question)
    except Exception:
        return "No examples available."
    return "\n".join(
        "Request: " + item["question"] + "\nSQL: " + item["sql"] for item in found
    )


def clean_sql(text):
    text = re.split(r"<\|", text)[0]
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    start = re.search(r"\b(select|with)\b", text, re.IGNORECASE)
    if start:
        text = text[start.start():]
    return text.strip().rstrip(";").strip()


def generate_sql(question, schema, previous_sql=None, error=None):
    request = question
    if previous_sql and error:
        request = (
            question
            + "\n\nThe previous query failed.\nQuery: " + previous_sql
            + "\nError: " + str(error)
            + "\nWrite a corrected query."
        )
    output = chain.invoke({
        "question": request,
        "schema": schema,
        "examples": get_examples_text(question),
    })
    return clean_sql(output)