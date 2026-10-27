"""V2 PostgreSQL 19 Authoritative Seeder Script.

Reads from backend_v2/seed/seed_data.json, validates 100% of entities in memory
against strict Pydantic V2 domain models and DAGCompilerService, and idempotently
upserts all collections into PostgreSQL 19 via PostgresUnitOfWork.

Usage:
Execute the script from the project root using `uv run python`:

```powershell
uv run python backend_v2/seed/run_seed.py
uv run python backend_v2/seed/run_seed.py postgres --dry-run
```
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.database.factory import create_unit_of_work
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.state import StateProjector as _StateProjector
from backend_v2.seed.seed_registry import SystemConfigUnion
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.settings import get_settings

_ = _StateProjector

SEED_PATH = Path(get_settings().seed_data_path)

TOPOLOGICAL_SEED_ORDER: tuple[str, ...] = (
    "organizations",
    "users",
    "system_config",
    "prompt_blocks",
    "steps",
    "workflows",
    "output_profiles",
    "executions",
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

__all__ = [
    "PROJECT_ROOT",
    "SEED_PATH",
    "TOPOLOGICAL_SEED_ORDER",
    "ValidatedSeedBufferDTO",
    "_seed_postgres",
    "main",
    "seed_database",
    "validate_all_seed_collections",
    "verify_seed_table_counts",
]


class ValidatedSeedBufferDTO(BaseModel):
    """Strongly typed container for validated in-memory seed collections."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    system_config: list[SystemConfigUnion] = Field(default_factory=list)
    workflows: list[Workflow] = Field(default_factory=list)
    prompt_blocks: list[AnyPromptBlock] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)
    output_profiles: list[OutputProfile] = Field(default_factory=list)
    executions: list[ExecutionRecord] = Field(default_factory=list)
    organizations: list[Organization] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)

    def get_collection(self, col_key: str) -> Sequence[BaseModel]:
        """Returns the typed collection list by collection name."""
        match col_key:
            case "system_config" | "system_configs":
                return self.system_config
            case "workflows":
                return self.workflows
            case "prompt_blocks":
                return self.prompt_blocks
            case "steps":
                return self.steps
            case "output_profiles":
                return self.output_profiles
            case "executions":
                return self.executions
            case "organizations":
                return self.organizations
            case "users":
                return self.users
            case _:
                raise KeyError(f"Unknown seed collection: '{col_key}'")

    def __getitem__(self, col_key: str) -> Sequence[BaseModel]:
        """Retrieve seed collection by registry key name."""
        return self.get_collection(col_key)

    def __contains__(self, col_key: object) -> bool:
        """Verify whether a collection key name belongs to standard seed collections."""
        return col_key in {
            "system_config",
            "system_configs",
            "workflows",
            "prompt_blocks",
            "steps",
            "output_profiles",
            "executions",
            "organizations",
            "users",
        }


def _fail_fast(msg: str, error: Exception) -> AppException:
    """Logs a critical error and returns a typed AppException.

    Args:
        msg: The failure message describing the context.
        error: The caught exception instance.

    Returns:
        AppException: Typed application exception with ErrorCodes.VALIDATION_FAILED.
    """
    logger.critical(
        "[Seeder] %s: [CRITICAL FAIL FAST] %s - %s",
        ErrorCodes.VALIDATION_FAILED.name,
        msg,
        str(error),
        exc_info=True,
    )
    print(f"\033[91m[CRITICAL FAIL FAST] {msg}\n{str(error)}\033[0m")
    return AppException(
        message=f"{msg}: {error}",
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED},
    )


def validate_all_seed_collections(seed_data: object) -> ValidatedSeedBufferDTO:
    """Validates 100% of seed items in-memory across all collections before any database operations.

    Phase 1 of Two-Phase Seeding: validates schemas and DAG workflows in memory.
    If ANY item is invalid, triggers Fail-Fast before tables are touched.

    Args:
        seed_data: Raw JSON payload loaded from the seed file.

    Returns:
        ValidatedSeedBufferDTO containing validated domain models per collection.

    Raises:
        AppException: If any validation or processing error occurs.
    """
    try:
        validated_buffer = ValidatedSeedBufferDTO.model_validate(seed_data)
    except ValidationError as ve:
        raise _fail_fast("Seed buffer validation failed", ve) from ve
    except Exception as e:
        raise _fail_fast("Processing error during seed validation", e) from e

    for wf in validated_buffer.workflows:
        try:
            DAGCompilerService.validate_workflow(wf)
        except Exception as e:
            raise _fail_fast(f"Workflow DAG validation failed for '{wf.id}'", e) from e

    return validated_buffer


async def verify_seed_table_counts(
    uow: QuorumUnitOfWork,
    expected_counts: Mapping[str, int],
) -> dict[str, int]:
    """Verify row counts across the 10 core PostgreSQL 19 tables via EntityPersistencePort.

    Args:
        uow: Active QuorumUnitOfWork instance.
        expected_counts: Mapping of collection/table name to minimum expected row count.

    Returns:
        Dictionary mapping canonical table name to actual row count in PostgreSQL 19.
    """
    return await uow.entities.verify_seed_table_counts(expected_counts)


async def _seed_postgres(
    seed_data: object,
    dry_run: bool = False,
    uow: QuorumUnitOfWork | None = None,
) -> dict[str, int]:
    """Seeds the PostgreSQL 19 database with validated V2 domain models.

    Enforces Two-Phase Pre-Flight In-Memory Validation:
    Phase 1: Validates 100% of seed items in-memory via validate_all_seed_collections.
    Phase 2: Executes transactional idempotent UPSERT across all collections in topological order
        and verifies row counts across all 10 tables via SELECT count(*).

    Args:
        seed_data: Raw JSON payload loaded from the seed file.
        dry_run: If True, validate in memory and bypass database modifications.
        uow: Optional QuorumUnitOfWork instance for dependency injection in tests.

    Returns:
        Mapping of table name to verified row count.
    """
    validated_buffers = validate_all_seed_collections(seed_data)
    print("[Seeder V2] Pre-flight in-memory validation passed for all collections.")

    expected_counts: dict[str, int] = {
        "organizations": max(1, len(validated_buffers.organizations)),
        "users": max(1, len(validated_buffers.users)),
        "system_configs": max(1, len(validated_buffers.system_config)),
        "prompt_blocks": max(1, len(validated_buffers.prompt_blocks)),
        "steps": max(1, len(validated_buffers.steps)),
        "workflows": max(1, len(validated_buffers.workflows)),
        "output_profiles": max(1, len(validated_buffers.output_profiles)),
        "executions": len(validated_buffers.executions),
        "report_artifacts": 0,
        "report_binaries": 0,
    }

    if dry_run:
        print("[Seeder V2] DRY-RUN ACTIVE: Completed validation without modifying PostgreSQL 19.")
        return expected_counts

    resolved_uow: QuorumUnitOfWork = uow if uow is not None else create_unit_of_work(get_settings())
    try:
        async with resolved_uow as active_uow:
            for col_key in TOPOLOGICAL_SEED_ORDER:
                items = validated_buffers.get_collection(col_key)
                upserted_count = await active_uow.entities.seed_collection_batch(col_key, items)
                print(f"[Seeder V2] Upserted {upserted_count} items to '{col_key}'.")

            actual_counts = await verify_seed_table_counts(active_uow, expected_counts)
    except AppException:
        raise
    except Exception as exc:
        raise _fail_fast("PostgreSQL 19 transactional seeding failed", exc) from exc

    print(f"[Seeder V2] Verified PostgreSQL 19 table counts: {actual_counts}")
    return actual_counts


async def seed_database(
    target: str = "postgres",
    dry_run: bool = False,
    uow: QuorumUnitOfWork | None = None,
) -> dict[str, int]:
    """Orchestrates the seeding process for PostgreSQL 19.

    Args:
        target: Target database environment ('postgres', 'local', or 'all').
        dry_run: If True, bypass database modifications.
        uow: Optional QuorumUnitOfWork override for testing.

    Returns:
        Mapping of table name to verified row count.

    Raises:
        AppException: If target is invalid or seeding fails.
        SystemExit: If seed file is missing on disk.
    """
    normalized_target = target.strip().lower()
    if normalized_target not in ("postgres", "postgresql", "local", "all"):
        raise _fail_fast(
            f"Unsupported seed target '{target}'. Only PostgreSQL 19 ('postgres') is supported",
            ValueError(f"Invalid target: {target}"),
        )

    print(f"--- V2 SEEDING TARGET: POSTGRESQL 19 ({normalized_target.upper()}) ---")

    if not SEED_PATH.exists():
        logger.critical("[Seeder] %s: Seed file not found at %s", ErrorCodes.FILE_NOT_FOUND.name, SEED_PATH)
        print(f"\033[91mCRITICAL: Seed file not found at {SEED_PATH}\033[0m")
        sys.exit(1)

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    counts = await _seed_postgres(data, dry_run=dry_run, uow=uow)
    print("[SUCCESS] V2 Seeded PostgreSQL 19 Database.")
    return counts


def main(argv: list[str] | None = None) -> None:
    """Parses command line arguments and initializes the async PostgreSQL 19 seeding loop.

    Args:
        argv: Optional list of argument strings for invocation.

    Raises:
        SystemExit: If parsing fails or an unhandled seeding error occurs.
    """
    parser = argparse.ArgumentParser(description="Unified V2 PostgreSQL 19 Database Seeder")
    parser.add_argument(
        "targets",
        nargs="*",
        default=["postgres"],
        choices=["postgres", "postgresql", "local", "all"],
        help="Target environment (defaults to 'postgres').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate seed data in memory without modifying PostgreSQL 19.",
    )

    args = parser.parse_args(argv)
    target_list: list[str] = list(args.targets)
    if not target_list:
        target_list = ["postgres"]

    try:
        asyncio.run(seed_database(target_list[0], dry_run=args.dry_run))
    except (OSError, RuntimeError, ValueError, AppException) as e:
        logger.critical(
            "[Seeder] %s: Failed to seed PostgreSQL 19: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            e,
            exc_info=True,
        )
        print(f"\033[91m[ERROR] Failed to seed PostgreSQL 19: {e}\033[0m")
        raise SystemExit(1) from e

    print("\n[SUCCESS] All requested targets completed successfully.")


if __name__ == "__main__":
    main()
