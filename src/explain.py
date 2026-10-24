import json

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
    ("system", """You explain data analysis results to a non-technical user.
You get the user's question, the SQL query that was run, and the result table.
Write 2 to 3 short sentences that answer the question using the real numbers from the result.
Reply in the same language as the question (Arabic or English).
Do not invent numbers that are not in the result.
Do not repeat the SQL query.
Do not add currency symbols or units that are not in the data."""),
    ("human", "Question: {question}\n\nSQL: {sql}\n\nResult:\n{result}"),
])

chain = prompt | llm | StrOutputParser()


def explain_result(question, sql, result):
    if not result["rows"]:
        return "No rows matched this question."
    shown = {"columns": result["columns"], "rows": result["rows"][:20]}
    text = json.dumps(shown, ensure_ascii=False)
    return chain.invoke({"question": question, "sql": sql, "result": text}).strip()

