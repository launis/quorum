import json
import os
import sys
import logging

# Add the current directory to sys.path so we can import the backend module
sys.path.append(os.getcwd())

# FORCE MOCK MODE to bypass credential checks in Settings
os.environ["USE_MOCK_LLM"] = "True"
os.environ["USE_MOCK_DB"] = "True"
os.environ["DISABLE_LOGFIRE"] = "true"

from backend.logging_config import setup_logging
from backend.exceptions import AppException, ErrorCodes
from fastapi import status

# Initialize logging immediately
setup_logging()
logger = logging.getLogger("backend.utils.generate_openapi")

try:
    from backend.main import app
except Exception as e:
    logger.critical(f"CRITICAL ERROR importing backend.main: {e}", exc_info=True)
    sys.exit(1)


def generate_openapi():
    """Generates the OpenAPI JSON schema and saves it to docs/swagger/openapi.json.
    
    Fail Fast: Raises AppException if schema generation fails or IO error.
    """
    logger.info("Generating OpenAPI spec...")
    
    try:
        openapi_schema = app.openapi()
        if not openapi_schema:
             raise ValueError("Generated OpenAPI schema is empty.")
             
        # Validate schema structure (basic check)
        if "openapi" not in openapi_schema or "paths" not in openapi_schema:
             raise ValueError("Result does not look like a valid OpenAPI schema.")
             
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI schema: {e}", exc_info=True)
        # We wrap in known exception for consistent exit code pattern if this were a service,
        # but here we log and likely exit non-zero.
        raise AppException(
            message=f"Schema Generation Failed: {e}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR}
        ) from e

    output_dir = os.path.join("docs", "swagger")
    output_path = os.path.join(output_dir, "openapi.json")
    
    try:
        os.makedirs(output_dir, exist_ok=True)

        # Consolidate: Remove legacy docs/openapi.json if it exists
        legacy_path = os.path.join("docs", "openapi.json")
        if os.path.exists(legacy_path):
            logger.info(f"Removing legacy file: {legacy_path}")
            os.remove(legacy_path)

        with open(output_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)

        logger.info(f"Successfully saved OpenAPI spec to {output_path}")
        
    except OSError as e:
        logger.error(f"IO Error saving spec: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to save OpenAPI spec: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        ) from e


if __name__ == "__main__":
    try:
        generate_openapi()
    except AppException as e:
        # Expected failure path
        logger.critical(f"Execution Failed: {e.message} (Code: {e.details.get('error_code')})")
        sys.exit(1)
    except Exception as e:
        # Unexpected
        logger.critical(f"Unexpected Crash: {e}", exc_info=True)
        sys.exit(1)
