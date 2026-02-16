"""Application Settings Module."""

import os
from enum import Enum
from functools import lru_cache
from typing import Annotated, Any

from backend.exceptions import AppException, ErrorCodes

from dotenv import load_dotenv
from pydantic import BeforeValidator, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Explicitly load .env to ensure environment variables are populated
# independent of Pydantic's internal loader (which seems brittle here)
load_dotenv()


def strip_whitespace(v: Any) -> Any:
    """Validator to strip whitespace from strings."""
    if isinstance(v, str):
        return v.strip()
    return v


MyBool = Annotated[bool, BeforeValidator(strip_whitespace)]


class StorageBackend(str, Enum):
    """Enumeration for Storage Backends."""

    FIRESTORE = "FIRESTORE"
    LOCAL = "LOCAL"  # Legacy/Dev modes. Production target is FIRESTORE.
    MOCK = "MOCK"  # Legacy/Dev modes. Production target is FIRESTORE.


class Settings(BaseSettings):
    """Application Settings managed by Pydantic.

    Reads from environment variables and .env file.
    """

    # --- Feature Flags ---
    use_mock_llm: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Mock LLM Service")] = False
    use_vertex_llm: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Vertex AI for LLM")] = False
    use_mock_db: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Mock Database (TinyDB)")] = (
        False
    )
    use_firebase_auth: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Firebase Auth (vs Mock)")] = True
    cors_origins: Annotated[list[str], Field(description="Allowed CORS Origins")] = ["*"]

    # --- Logging ---
    use_json_logging: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Force structured JSON logging in any environment")] = False

    # --- API Keys ---
    google_api_key: Annotated[str | None, Field(description="Google AI Provider API Key")] = None
    openai_api_key: Annotated[str | None, Field(description="OpenAI API Key (Optional)")] = None
    anthropic_api_key: Annotated[str | None, Field(description="Anthropic API Key (Optional)")] = None
    vertex_location: Annotated[str | None, Field(description="Google Cloud Region (e.g. europe-north1)")] = None
    discovery_location: Annotated[str | None, Field(description="Source Region for Model Discovery (e.g. us-west1)")] = None

    # --- LLM Configuration ---
    # initial_model REMOVED per Zero-Fallback Policy
    default_model_strategy: Annotated[str | None, Field(description="Default LLM strategy key (Optional). If None, explicit strategy is required.")] = None
    llm_default_timeout: Annotated[float, Field(description="LLM Timeout in seconds")] = 120.0
    llm_max_retries: Annotated[int, Field(description="Max retries for LLM calls")] = 2
    llm_retry_delay: Annotated[float, Field(description="Delay between retries in seconds")] = 5.0
    
    # --- Rate Limits (Strict Mode) ---
    llm_default_tpm: Annotated[int, Field(description="Default Tokens Per Minute if not specified by caller")] = 10000
    llm_default_rpm: Annotated[int, Field(description="Default Requests Per Minute if not specified by caller")] = 10

    # --- Redis & Arq ---
    redis_host: Annotated[str, Field(description="Redis Host")] = "localhost"
    redis_port: Annotated[int, Field(description="Redis Port")] = 6379

    # NOTE: Default models are REMOVED to enforce DB-based configuration.
    # gemini_model_fast and gemini_model_deep are deprecated.

    # --- Storage ---
    storage_backend: Annotated[
        str, BeforeValidator(strip_whitespace), Field(description="LOCAL, NONE, or FIRESTORE")
    ] # REMOVED DEFAULT = "LOCAL". Must be explicit.
    environment: Annotated[str, Field(description="development, staging, or production")] = "production" # Default to production for safety? No, make explicit.
    storage_bucket_name: Annotated[str | None, Field(description="Firebase Storage Bucket Name")] = None

    # URL for generating public links in Local mode
    api_url: Annotated[str | None, Field(description="Public API Base URL")] = "http://localhost:8000"

    # --- Paths ---
    log_file_name: Annotated[str, Field(description="Name of the debug log file")] = "backend_debug.log"

    # We define base_dir relative to this file (backend/settings.py)
    @computed_field  # type: ignore[prop-decorator]
    @property
    def base_dir(self) -> str:
        """Returns the base directory of the backend application."""
        return os.path.dirname(os.path.abspath(__file__))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def data_dir(self) -> str:
        """Returns the path to the persistent data directory."""
        # Assuming ../data from backend/
        return os.path.join(os.path.dirname(self.base_dir), "data")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def files_dir(self) -> str:
        """Returns the path to the central files directory."""
        return os.path.join(self.data_dir, "files")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_dir(self) -> str:
        """Returns the path to the database directory."""
        return os.path.join(self.base_dir, "database")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def scripts_dir(self) -> str:
        """Returns the path to the scripts directory."""
        return os.path.join(os.path.dirname(self.base_dir), "scripts")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mock_db_path(self) -> str:
        """Returns the path to the mock database file."""
        return os.path.join(self.db_dir, "db_mock.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def prod_db_path(self) -> str:
        """Returns the path to the production database file."""
        return os.path.join(self.data_dir, "db.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def start_db_path(self) -> str:
        """Returns the path to the database file to be used at startup (Prod or Mock)."""
        return self.mock_db_path if self.use_mock_db else self.prod_db_path

    @computed_field  # type: ignore[prop-decorator]
    @property
    def seed_data_path(self) -> str:
        """Returns the path to the seed data file."""
        return os.path.join(self.base_dir, "seed", "seed_data.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mock_responses_path(self) -> str:
        """Returns the path to the mock responses file."""
        return os.path.join(self.data_dir, "mock_responses.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def log_file_path(self) -> str:
        """Absolute path to the log file in the project root."""
        # Using base_dir parent (project root) + log_file_name
        return os.path.join(os.path.dirname(self.base_dir), self.log_file_name)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_backend(self) -> StorageBackend:
        """Determines the active storage backend based on configuration.

        Priority 1: Explicit FIRESTORE backend.
        Priority 2: Mock mode.
        Default: Local storage.
        """
        if self.use_mock_db:
            return StorageBackend.MOCK

        # Strict matching
        value = self.storage_backend.upper()
        if value == "FIRESTORE":
            return StorageBackend.FIRESTORE
        if value == "LOCAL":
            return StorageBackend.LOCAL

        raise AppException(
            message=f"CRITICAL: Invalid STORAGE_BACKEND '{self.storage_backend}'. Must be LOCAL or FIRESTORE (or set USE_MOCK_DB=True).",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_cloud_storage(self) -> bool:
        """Returns True if active_backend is FIRESTORE."""
        return self.active_backend == StorageBackend.FIRESTORE

    # --- Complex Configs (Computed) ---
    @computed_field
    def model_strategies(self) -> dict[str, dict[str, Any]]:
        """Returns empty dict by default.

        Strategies MUST be loaded from 'system_config' table in database.
        """
        return {}

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore", case_sensitive=False)

    def model_post_init(self, __context: Any) -> None:
        """Validates settings after initialization."""
        # Check for EITHER Google AI Studio Key OR Vertex AI Credentials
        if not self.use_mock_llm:
            # Auto-discovery for service-account.json (Resilience against launcher issues)
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                root_dir = os.path.dirname(self.base_dir)
                sa_path = os.path.join(root_dir, "service-account.json")
                if os.path.exists(sa_path):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
                    # logger.info not available here easily, but we proceed silently or could print
                    print(f"Settings: Auto-detected service-account.json at {sa_path}")

            has_vertex = (
                os.getenv("VERTEX_PROJECT_ID")
                or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                or os.getenv("GOOGLE_CLOUD_PROJECT")
            )

            if not self.google_api_key and not has_vertex:
                raise AppException(
                    message="CRITICAL: No LLM Credentials found (GOOGLE_API_KEY or VERTEX_PROJECT_ID/Credentials). "
                    "Cannot proceed in Production Mode. Ensure 'service-account.json' exists in root or set env vars.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                )

        if self.use_mock_db:
            pass
        elif self.storage_backend == "FIRESTORE":
            pass
        else:
            pass

    @computed_field
    def enabled_providers(self) -> list[str]:
        """Returns list of enabled LLM providers based on configuration.
        
        Hardcoded source of truth for UI and Discovery.
        """
        providers = []
        # Google / Vertex
        if self.google_api_key or (not self.use_mock_llm and (os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))):
             providers.append("google")
        
        # OpenAI
        if self.openai_api_key:
            providers.append("openai")

        # Mock override (if enabled, ensuring it appears for dev)
        if self.use_mock_llm and "mock" not in providers:
             providers.append("mock")

        # Fallback/Safety: If empty but not mock, maybe we should warn? 
        # But for now, returning what is explicitly configured is strict.
        return providers

@lru_cache
def get_settings() -> Settings:
    """Singleton getter for Settings."""
    return Settings()
