import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Mock Configuration ---
# Set to True to use the Mock LLM Service (no API costs)
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "False").lower() == "true"

# Set to True to use the Mock Database (TinyDB)
# Set to False to use the Real Database (Firebase - Future Implementation)
USE_MOCK_DB = os.getenv("USE_MOCK_DB", "True").lower() == "true"

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

MOCK_DB_PATH = os.path.join(DATA_DIR, "db_mock.json")
PROD_DB_PATH = os.path.join(DATA_DIR, "db.json")

if USE_MOCK_DB:
    DB_PATH = MOCK_DB_PATH
    print(f"CONFIG: Using MOCK DB at {DB_PATH}")
else:
    DB_PATH = PROD_DB_PATH
    print(f"CONFIG: Using REAL DB at {DB_PATH}")
MOCK_RESPONSES_PATH = os.path.join(DATA_DIR, "mock_responses.json")

def get_db_path():
    """Returns the path to the database file."""
    return DB_PATH

def get_mock_responses_path():
    """Returns the path to the mock responses file."""
    return MOCK_RESPONSES_PATH
