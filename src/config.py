from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
env_values = dotenv_values(ROOT / "app.env")
openrouter_api_key = env_values["OPENROUTER_API_KEY"]

DATA_DIR = ROOT / "data"
UPLOAD_DIR = ROOT / "uploads"
DB_PATH = DATA_DIR / "analysis.db"

LLM_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "openrouter/free"
LLM_TEMPERATURE = 0

WHISPER_MODEL = "small"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

MAX_ROWS = 100

WHISPER_BEAM_SIZE = 1


