import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# --- Configuration & Constants ---

# Target Execution ID from Requirements (Files)
FILE_EXECUTION_ID = "1e205b2c-c907-45a1-a5e5-3fa4cc10952f"
# Target Execution ID from Requirements (DB) - Found in db.json
DB_EXECUTION_ID = "1eb1fbc6-0ab0-4514-8cce-d92ab63f6031"

# Paths relative to project root
DB_PATH = Path("data/db.json")
FILES_DIR = Path(f"data/files/{FILE_EXECUTION_ID}")
SERVICE_ACCOUNT_PATH = Path("service-account.json")

# Helper to verify DB path resolution
if not DB_PATH.exists():
    # Try looking in root if test passed from wrong cwd
    pass # Assume pytest runs from root

# --- Tests ---

def test_sitra_files_exist():
    """Requirement 1: Verify specific physical files exist for the target execution."""
    # Check if primary directory exists for FILE_EXECUTION_ID
    assert FILES_DIR.exists(), f"Files directory not found for ID {FILE_EXECUTION_ID}"

    expected_files = [
        "Reflektiodokumentti sitra.pdf",
        "keskusteluhistoria SITRA.pdf"
    ]

    for fname in expected_files:
        fpath = FILES_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname} in {FILES_DIR}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty."


def test_sitra_db_record():
    """Requirement 2: Verify database metadata for the execution."""
    assert DB_PATH.exists(), "Database not found."

    with open(DB_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert "executions" in data, "No 'executions' table in DB."
    table = data["executions"]

    # TinyDB stores as dict of dicts
    found_record = None

    records = table
    if "_default" in table:
        records = table["_default"]

    for key, record in records.items():
        if record.get("id") == DB_EXECUTION_ID:
            found_record = record
            break

    assert found_record is not None, f"Execution {DB_EXECUTION_ID} not found in DB."

    # Assertion: Status is completed or valid inputs
    status = found_record.get("status")
    inputs = found_record.get("inputs")

    # Status might be 'failed' in the provided JSON, but inputs exist.
    # Requirement: "status is 'completed' (if applicable) OR has valid 'inputs'"
    # So if status is failed but inputs exist, it PASSES.

    has_valid_inputs = inputs and len(inputs) > 0
    assert status == "completed" or has_valid_inputs, \
        f"Execution state invalid. Status: {status}, Inputs: {inputs}"


@pytest.mark.asyncio
async def test_llm_connectivity():
    """Requirement 3: Verify LLM Connectivity using Database Configuration."""
    from backend.llm.provider import LiteLLMProvider
    from backend.models.llm import LLMResponse

    if not SERVICE_ACCOUNT_PATH.exists():
        pytest.skip("No service-account.json found. Skipping live LLM test.")

    # 1. Load Model Config from DB
    assert DB_PATH.exists(), "Database not found."
    with open(DB_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Navigate to system_config -> model_registry
    sys_config = data.get("system_config", {})
    # TinyDB structure check
    if "_default" in sys_config:
        sys_config = sys_config["_default"]

    model_registry = None
    for key, record in sys_config.items():
        if record.get("id") == "model_registry":
            model_registry = record
            break

    if not model_registry:
        pytest.skip("No 'model_registry' found in system_config. Cannot determine model.")

    # Extract 'fast' model for connectivity test
    try:
        models = model_registry.get("models", {})
        google_conf = models.get("google", {})
        fast_conf = google_conf.get("fast", {})
        model_name = fast_conf.get("model_name")

        if not model_name:
             pytest.fail("[Test] Error: 'fast' model config not found in DB sistem_config. No fallback allowed.")
        else:
             print(f"[Test] Using Model from DB: {model_name}")

    except Exception as e:
        pytest.fail(f"Failed to parse model registry from DB: {e}")

    # Load environment variables (e.g. from .env)
    load_dotenv()

    # Verify required environment variables are present
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        # As a fallback for local testing, if the file exists in root, we can hint it,
        # but per user request "no default values", we should respect the env.
        # However, to be helpful while strict: check if set.
        if SERVICE_ACCOUNT_PATH.exists():
             # If env var is missing but file exists, we *could* set it, but user said "no default values".
             # So we will standardly fail or skip if the library can't find auth.
             pass

    if not os.getenv("VERTEX_LOCATION"):
        # User said "no default values", so we do NOT set 'us-central1'.
        # We assume the environment or the provider default is sufficient.
        pass

    print(f"[Test] Initializing LiteLLMProvider with {model_name}...")

    provider = LiteLLMProvider(
        model_name=model_name,
        usage_service=None,
        organization_id="test_org"
    )

    # Lightweight Prompt
    print("[Test] Sending 'Hello World' to Vertex AI...")
    try:
        response: LLMResponse = await provider.generate(
            prompt="Hello",
            max_tokens=10,
            temperature=0.0
        )

        content = response.content.strip()
        print(f"[Test] Output: {content}")

        assert content is not None, "LLM returned None content."

    except Exception as e:
        pytest.fail(f"LLM Connectivity Failed: {e}")
