import os
from functools import lru_cache
from functools import lru_cache
from typing import Dict, Any, Optional
from pydantic import Field, computed_field, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated

def strip_whitespace(v: Any) -> Any:
    if isinstance(v, str):
        return v.strip()
    return v

MyBool = Annotated[bool, BeforeValidator(strip_whitespace)]

class Settings(BaseSettings):
    """
    Application Settings managed by Pydantic.
    Reads from environment variables and .env file.
    """
    # --- Feature Flags ---
    use_mock_llm: MyBool = Field(default=False, description="Use Mock LLM Service")
    use_mock_db: MyBool = Field(default=True, description="Use Mock Database (TinyDB)")
    
    # --- API Keys ---
    google_api_key: Optional[str] = Field(default=None, description="Google AI Provider API Key")

    # --- LLM Configuration ---
    initial_model: str = Field(default="fast") # Use strategy key, not raw name
    llm_default_timeout: float = Field(default=60.0) # Keep increased timeout
    llm_max_retries: int = Field(default=3)
    llm_retry_delay: float = Field(default=4.0)
    
    # NOTE: Default models are REMOVED to enforce DB-based configuration.
    # gemini_model_fast and gemini_model_deep are deprecated.

    # --- Storage ---
    storage_backend: str = Field(default="LOCAL", description="LOCAL, NONE, or FIRESTORE")

    # --- Paths ---
    # We define base_dir relative to this file (backend/settings.py)
    @computed_field
    def base_dir(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    @computed_field
    def data_dir(self) -> str:
        # Assuming ../data from backend/
        return os.path.join(os.path.dirname(self.base_dir), "data")

    @computed_field
    def db_dir(self) -> str:
        return os.path.join(self.base_dir, "database")
    
    @computed_field
    def scripts_dir(self) -> str:
        return os.path.join(os.path.dirname(self.base_dir), "scripts")

    @computed_field
    def mock_db_path(self) -> str:
        return os.path.join(self.db_dir, "db_mock.json")

    @computed_field
    def prod_db_path(self) -> str:
        return os.path.join(self.data_dir, "db.json")

    @computed_field
    def start_db_path(self) -> str:
        return self.mock_db_path if self.use_mock_db else self.prod_db_path

    @computed_field
    def seed_data_path(self) -> str:
        return os.path.join(self.db_dir, "seed_data.json")

    @computed_field
    def mock_responses_path(self) -> str:
        return os.path.join(self.data_dir, "mock_responses.json")
    
    # --- Complex Configs (Computed) ---
    @computed_field
    def model_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns empty dict by default. 
        Strategies MUST be loaded from 'system_config' table in database.
        """
        return {}

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True, 
        extra="ignore",
        case_sensitive=False
    )

    def model_post_init(self, __context: Any) -> None:
        # Logic to force mock mode if API Key is missing
        if not self.google_api_key and not self.use_mock_llm:
            print("WARNING: GOOGLE_API_KEY not found. Forcing Mock LLM Mode.")
            self.use_mock_llm = True
            
        if self.use_mock_db:
             print(f"CONFIG: Using MOCK DB at {self.mock_db_path}")
        else:
             print(f"CONFIG: Using REAL DB at {self.prod_db_path}")

@lru_cache
def get_settings() -> Settings:
    return Settings()
