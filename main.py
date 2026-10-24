import sqlite3
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src import config, database, explain, sql_generator, stt
from src.sql_validator import UnsafeSQLError, validate_sql

app = FastAPI(title="Voice SQL Assistant")

config.UPLOAD_DIR.mkdir(exist_ok=True)
stt.get_model()

ARABIC_WORDS = "اعرض، احسب، إجمالي، متوسط، أكبر، أقل، عدد، المجموع، لكل"
ENGLISH_WORDS = "show, total, average, maximum, minimum, count, sum, per, by, top"


class QuestionRequest(BaseModel):
    question: str


class SQLRequest(BaseModel):
    sql: str


def save_upload(file):
    suffix = Path(file.filename or "").suffix
    path = config.UPLOAD_DIR / (uuid.uuid4().hex + suffix)
    path.write_bytes(file.file.read())
    return path


def build_stt_prompt(language):
    columns = ", ".join(name.replace("_", " ") for name in database.get_columns())
    if language == "ar":
        return ARABIC_WORDS + "، " + columns
    if language == "en":
        return ENGLISH_WORDS + ", " + columns
    return columns


def clean_language(language):
    if language in ("ar", "en"):
        return language
    return None


def speech_to_text(file, language):
    language = clean_language(language)
    path = save_upload(file)
    try:
        return stt.transcribe(path, language=language, prompt=build_stt_prompt(language))
    except Exception as error:
        raise HTTPException(status_code=400, detail="Could not read the audio: " + str(error))
    finally:
        path.unlink(missing_ok=True)


def make_sql(question):
    try:
        sql = sql_generator.generate_sql(question, database.get_schema())
    except Exception as error:
        raise HTTPException(status_code=502, detail="The language model failed: " + str(error))
    try:
        return validate_sql(sql)
    except UnsafeSQLError as error:
        raise HTTPException(status_code=400, detail={"message": str(error), "sql": sql})


def execute(sql):
    sql = validate_sql_or_400(sql)
    try:
        return database.run_query(sql)
    except sqlite3.Error as error:
        raise HTTPException(status_code=400, detail={"message": str(error), "sql": sql})


def validate_sql_or_400(sql):
    try:
        return validate_sql(sql)
    except UnsafeSQLError as error:
        raise HTTPException(status_code=400, detail={"message": str(error), "sql": sql})


def answer(question):
    sql = make_sql(question)
    result = execute(sql)
    try:
        explanation = explain.explain_result(question, sql, result)
    except Exception:
        explanation = None
    return {
        "question": question,
        "sql": sql,
        "columns": result["columns"],
        "rows": result["rows"],
        "explanation": explanation,
    }


@app.get("/")
def home():
    return {"status": "running", "docs": "/docs"}


@app.post("/upload-data")
def upload_data(file: UploadFile = File(...)):
    name = Path(file.filename or "").name
    if not name.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    path = config.UPLOAD_DIR / name
    path.write_bytes(file.file.read())
    try:
        database.load_csv(path)
    except Exception as error:
        raise HTTPException(status_code=400, detail="Could not read the CSV: " + str(error))
    return {"message": "Data loaded.", "schema": database.get_schema()}


@app.get("/schema")
def schema():
    return {"schema": database.get_schema()}


@app.post("/transcribe")
def transcribe(audio: UploadFile = File(...), language: str = Form("auto")):
    return speech_to_text(audio, language)


@app.post("/generate-sql")
def generate_sql(request: QuestionRequest):
    return {"question": request.question, "sql": make_sql(request.question)}


@app.post("/execute-sql")
def execute_sql(request: SQLRequest):
    sql = validate_sql_or_400(request.sql)
    result = execute(sql)
    return {"sql": sql, "columns": result["columns"], "rows": result["rows"]}


@app.post("/text-query")
def text_query(request: QuestionRequest):
    return answer(request.question)


@app.post("/voice-query")
def voice_query(audio: UploadFile = File(...), language: str = Form("auto")):
    heard = speech_to_text(audio, language)
    if not heard["text"]:
        raise HTTPException(
            status_code=400,
            detail="I could not hear any speech. Please try again and speak a little closer to the microphone.",
        )
    response = answer(heard["text"])
    response["transcript"] = heard["text"]
    response["language"] = heard["language"]
    return response


@app.get("/app")
def web_app():
    return FileResponse(config.ROOT / "static" / "index.html")