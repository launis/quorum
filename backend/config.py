from backend.settings import get_settings

# --- Load Settings via Pydantic ---
settings = get_settings()

# --- Export Constants for Backward Compatibility ---

# Feature Flags
USE_MOCK_LLM = settings.use_mock_llm
USE_MOCK_DB = settings.use_mock_db

# API Keys
GOOGLE_API_KEY = settings.google_api_key

# LLM Configuration
INITIAL_MODEL = settings.initial_model
LLM_DEFAULT_TIMEOUT = settings.llm_default_timeout
LLM_MAX_RETRIES = settings.llm_max_retries
LLM_RETRY_DELAY = settings.llm_retry_delay

# Model Strategies
MODEL_STRATEGIES = settings.model_strategies

# Paths
BASE_DIR = settings.base_dir
DATA_DIR = settings.data_dir
DB_DIR = settings.db_dir
SCRIPTS_DIR = settings.scripts_dir

MOCK_DB_PATH = settings.mock_db_path
PROD_DB_PATH = settings.prod_db_path
SEED_DATA_PATH = settings.seed_data_path
MOCK_RESPONSES_PATH = settings.mock_responses_path

DB_PATH = settings.start_db_path

# Storage
STORAGE_BACKEND = settings.storage_backend

# --- Legacy Help Functions ---
def get_db_path():
    """Returns the path to the database file."""
    return settings.start_db_path

def get_mock_responses_path():
    """Returns the path to the mock responses file."""
    return settings.mock_responses_path
