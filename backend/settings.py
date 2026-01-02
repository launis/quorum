import os
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
    use_mock_llm: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Mock LLM Service")] = False
    use_mock_db: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Mock Database (TinyDB)")] = True
    
    # --- API Keys ---
    google_api_key: Annotated[Optional[str], Field(description="Google AI Provider API Key")] = None

    # --- LLM Configuration ---
    initial_model: Annotated[str, Field(description="Initial Model Strategy")] = "fast"
    llm_default_timeout: Annotated[float, Field(description="LLM Timeout in seconds")] = 60.0
    llm_max_retries: Annotated[int, Field(description="Max retries for LLM calls")] = 3
    llm_retry_delay: Annotated[float, Field(description="Delay between retries in seconds")] = 4.0
    
    # NOTE: Default models are REMOVED to enforce DB-based configuration.
    # gemini_model_fast and gemini_model_deep are deprecated.

    # --- Storage ---
    storage_backend: Annotated[str, Field(description="LOCAL, NONE, or FIRESTORE")] = "LOCAL"

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
        # Check for EITHER Google AI Studio Key OR Vertex AI Credentials
        has_vertex = os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT")
        
        # STRICT: If not in mock mode, require credentials.
        if not self.use_mock_llm:
             if not self.google_api_key and not has_vertex:
                  raise ValueError("CRITICAL: No LLM Credentials found (GOOGLE_API_KEY or VERTEX_PROJECT_ID/Credentials). Cannot proceed in Production Mode.")
            
        if self.use_mock_db:
             pass 
        elif self.storage_backend == "FIRESTORE":
             pass
        else:
             pass

@lru_cache
def get_settings() -> Settings:
    return Settings()
