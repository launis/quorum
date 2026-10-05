"""Script for generating the static OpenAPI schema JSON file from the FastAPI application.

Enables automated Flutter client generation, API documentation, and compliance tests.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from pydantic import JsonValue

# Ensure the root quorum directory is in sys.path BEFORE any backend_v2 imports
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend_v2.exceptions import AppException, ErrorCodes

__all__ = [
    "generate_openapi_schema",
    "main",
    "root_dir",
]

# Configure structured system logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_openapi_schema(output_path: Path | None = None) -> Path:
    """Generate static OpenAPI schema JSON file from FastAPI application.

    Args:
        output_path: Optional destination Path for openapi.json.

    Returns:
        Path to the generated OpenAPI specification file.

    Raises:
        AppException: If file writing or schema extraction fails.
    """
    logger.info("Generating OpenAPI schema from FastAPI app...")

    # Rule 27: Deferred import of FastAPI application instance to prevent premature
    # heavyweight loading of LLM dependencies
    from backend_v2.main import app

    openapi_schema: dict[str, JsonValue] = app.openapi()

    target_path = output_path or (root_dir / "docs" / "swagger" / "openapi.json")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with target_path.open("w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline standard
        logger.info("SUCCESS: TS / Dart Client schemas - OpenAPI JSON generated and saved to %s", target_path)
        return target_path
    except Exception as e:
        error_code = ErrorCodes.STORAGE_ACCESS_FAILED
        logger.error(
            "Failed to write OpenAPI specification to path: %s",
            str(target_path),
            exc_info=True,
            extra={"error_code": error_code.value},
        )
        raise AppException(
            message=f"Failed to write OpenAPI schema file due to: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from e


def main() -> None:
    """Execute the OpenAPI schema generation CLI workflow.

    Raises:
        AppException: If schema generation or persistence fails.
    """
    generate_openapi_schema()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        logger.critical("Fatal exception halted OpenAPI generation script", exc_info=True)
        sys.exit(1)
