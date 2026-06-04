"""Script for generating the static OpenAPI schema JSON file from the FastAPI application.

Enables automated Flutter client generation, API documentation, and compliance tests.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Ensure the root quorum directory is in sys.path BEFORE any backend_v2 imports
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend_v2.exceptions import AppException, ErrorCodes

# Configure structured system logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Generates the static OpenAPI schema JSON file from the FastAPI application instance.

    This schema is used for automated Flutter client generation, documentation,
    and API compliance checks. Resolves output directory structurally and writes
    using standard UTF-8 encoding patterns.

    Raises:
        AppException: If file writing or generation fails due to file system or structural blocks.
    """
    logger.info("Generating OpenAPI schema from FastAPI app...")

    # Rule 27: Deferred import of FastAPI application instance to prevent premature
    # heavyweight loading of LLM dependencies
    from backend_v2.main import app

    openapi_schema: dict[str, Any] = app.openapi()

    output_dir = root_dir / "docs" / "swagger"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "openapi.json"

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline standard
        logger.info(f"SUCCESS: TS / Dart Client schemas - OpenAPI JSON generated and saved to {output_path}")
    except Exception as e:
        error_code = ErrorCodes.STORAGE_ACCESS_FAILED
        logger.error(
            "Failed to write OpenAPI specification to path: %s",
            str(output_path),
            exc_info=True,
            extra={"error_code": error_code},
        )
        raise AppException(
            message=f"Failed to write OpenAPI schema file due to: {e}",
            status_code=500,
            details={"error_code": error_code},
        ) from e


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.critical("Fatal exception halted OpenAPI generation script", exc_info=True)
        sys.exit(1)
