"""Unit tests for worker proxy module verifying PEP 484 re-exports and Arq settings."""

import sys
from unittest.mock import patch

import pytest

import backend_v2.run_worker as rw
import backend_v2.worker as worker_mod
from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.worker import WorkerSettings, health_check, startup
from backend_v2.workers import execute_workflow_job, generate_report_artifact_job


def test_worker_exports_all_symbols() -> None:
    """Verify that every symbol declared in __all__ exists and is accessible."""
    assert "__all__" in dir(worker_mod)
    expected_symbols = [
        "WorkerSettings",
        "health_check",
        "shutdown",
        "startup",
    ]
    assert set(worker_mod.__all__) == set(expected_symbols)
    mod_dir = set(dir(worker_mod))
    for symbol in expected_symbols:
        assert symbol in mod_dir

    banned_coroutine_symbols = [
        "VarianceExplanationResult",
        "execute_workflow_job",
        "generate_pdf_job",
        "generate_pdf_task",
        "generate_profile_synthesis_and_pdf_task",
        "generate_report_artifact_job",
        "render_profile_job",
    ]
    for banned in banned_coroutine_symbols:
        assert banned not in worker_mod.__all__


def test_worker_settings_functions_registered() -> None:
    """Verify that WorkerSettings correctly registers all decoupled worker jobs."""
    assert tuple(WorkerSettings.functions) == (
        health_check,
        execute_workflow_job,
        generate_report_artifact_job,
    )


def test_run_worker_imports_worker_settings() -> None:
    """Verify that run_worker imports WorkerSettings cleanly."""
    assert "WorkerSettings" in dir(rw)
    assert "backend_v2.worker" in sys.modules


def test_worker_entrypoint_registers_mandatory_hooks_in_registry() -> None:
    """Verify that importing the Arq worker entrypoint registers all mandatory DAG hooks."""
    mandatory_hooks = (
        "input_processing",
        "atom_flattening_hook",
        "matrix_scoring_hook",
        "normalize_matrix_scores",
        "verify_structure",
        "synthesis_distiller_hook",
    )
    for hook_name in mandatory_hooks:
        hook_fn = hook_registry.get_hook(hook_name)
        assert callable(hook_fn)
    assert "backend_v2.hooks" in sys.modules


# Phase 1, Step 1.1: ISTQB negative partition tests for worker HookRegistry contracts
def test_worker_hook_registry_missing_hook_failure() -> None:
    """ISTQB negative partition: requesting an unregistered hook raises RESOURCE_NOT_FOUND."""
    with pytest.raises(AppException) as exc_info:
        hook_registry.get_hook("nonexistent_hook_xyz")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_worker_hook_registry_empty_name_invalid() -> None:
    """ISTQB boundary value negative partition: empty string hook name raises RESOURCE_NOT_FOUND."""
    with pytest.raises(AppException) as exc_info:
        hook_registry.get_hook("")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_worker_startup_missing_input_processing_hook_failure() -> None:
    """ISTQB negative partition: startup fails fast with CONFIGURATION_ERROR if input_processing is missing."""
    with (
        patch("backend_v2.worker.setup_logging"),
        patch("backend_v2.worker.configure_telemetry"),
        patch("backend_v2.worker.log_startup_system_parameters"),
        patch("backend_v2.worker.hook_registry.get_all_hooks", return_value={}),
        pytest.raises(AppException) as exc_info,
    ):
        await startup({})
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
