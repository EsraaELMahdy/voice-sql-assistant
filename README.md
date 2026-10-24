# Voice SQL Assistant

A small web service that lets you ask questions about a CSV file with your voice, in English or Arabic. The speech is turned into text, a language model writes a SQL query, Python runs the query on SQLite, and the result comes back as a table with a short explanation.

## How it works

~~~
voice -> Faster-Whisper -> text -> LLM -> SQL -> validator -> SQLite -> table + explanation
~~~

1. **Speech to text.** Faster-Whisper (`small`, CPU, int8) transcribes the recording. The prompt given to Whisper contains common analysis words and the column names of the loaded table, which helps it hear them correctly.
2. **SQL generation.** The language model receives the question and the database schema only. It never sees the rows. The schema lists the table, the columns with their types, the possible values of short text columns, and three sample rows.
3. **Validation.** Only a single `SELECT` (or `WITH`) statement is accepted. Comments, multiple statements and words such as `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE` and `PRAGMA` are rejected.
4. **Execution.** Python runs the query with `sqlite3` on a read-only connection and returns at most 100 rows. If the query fails, the error is sent back to the model and it tries again, up to three attempts.
5. **Explanation.** The model writes a short explanation of the result.

## Project structure

~~~
main.py              FastAPI app and all endpoints
static/index.html    simple web page with recording button
src/config.py        settings (models, paths, limits)
src/stt.py           speech to text
src/sql_generator.py question to SQL
src/sql_validator.py SQL safety checks
src/database.py      CSV loading, schema, query execution
src/explain.py       explanation of the result
humaneval.csv        sample data
test_validator.py    tests for the validator
test_explain.py      test for the explanation
~~~

## Setup

Requires Python 3.13 (tested on Windows).

~~~
git clone https://github.com/EsraaELMahdy/voice-sql-assistant.git
cd voice-sql-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
~~~

Create a file named `app.env` in the project folder:

~~~
OPENROUTER_API_KEY=your_key_here
~~~

The file is listed in `.gitignore` and is never committed.

## Run

~~~
python -m uvicorn main:app --reload
~~~

Then open:

- `http://127.0.0.1:8000/app` for the web page (upload a CSV, record or type a question)
- `http://127.0.0.1:8000/docs` for the interactive API documentation

The first start downloads the Whisper model, so it can take a while.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/upload-data` | upload a CSV file and load it into SQLite |
| GET | `/schema` | show the current table schema |
| POST | `/transcribe` | audio file to text |
| POST | `/generate-sql` | question to SQL (not executed) |
| POST | `/execute-sql` | validate and run a SQL query |
| POST | `/text-query` | full pipeline from a text question |
| POST | `/voice-query` | full pipeline from a recording |
| GET | `/app` | web page |

## Sample data

`humaneval.csv` is built from the HumanEval dataset (164 programming problems). It has one row per problem with these columns: `task_id`, `task_number`, `entry_point`, `prompt_length`, `solution_lines`, `test_lines`, `has_recursion`.

Example questions:

- How many problems are there?
- What is the average number of solution lines?
- Show the five longest solutions.
- How many problems use recursion?
- - كم عدد المسائل التي تستخدم التكرار الذاتي

Arabic questions work the same way when the language is set to Arabic or Auto.

Any other CSV file can be uploaded from the page. Only one dataset is kept at a time, so uploading a new file replaces the old one.

## Notes and limitations

- The language model is `openrouter/free`, which routes to different free models, so answers can vary slightly between runs. The code removes stray model tokens from the SQL and retries when a query fails.
- Whisper `small` sometimes mishears words, especially in Arabic. The language model usually still understands the intent, but the "What I heard" line should be checked.
- The database is read-only during queries, and all statements other than a single `SELECT` are blocked.