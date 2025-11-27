import os
from dotenv import load_dotenv

load_dotenv()

# Project Root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(DATA_DIR, 'db')
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')
DB_PATH = os.path.join(DB_DIR, 'db.json')

# Ensure DB Directory Exists
os.makedirs(DB_DIR, exist_ok=True)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")
