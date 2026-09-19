"""Unit tests for worker proxy module verifying PEP 484 re-exports and Arq settings."""

import backend_v2.worker as worker_mod
from backend_v2.worker import WorkerSettings


def test_worker_exports_all_symbols() -> None:
    """Verify that every symbol declared in __all__ exists and is accessible."""
    assert hasattr(worker_mod, "__all__")
    expected_symbols = [
        "WorkerSettings",
        "health_check",
        "shutdown",
        "startup",
    ]
    assert set(worker_mod.__all__) == set(expected_symbols)
    for symbol in expected_symbols:
        assert hasattr(worker_mod, symbol)
        assert getattr(worker_mod, symbol) is not None

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
    registered_fn_names = [getattr(f, "name", getattr(f, "__name__", str(f))) for f in WorkerSettings.functions]
    assert "execute_workflow_job" in registered_fn_names
    assert "generate_report_artifact_job" in registered_fn_names
    assert "render_profile_job" in registered_fn_names
    assert "generate_pdf_job" in registered_fn_names


def test_run_worker_imports_worker_settings() -> None:
    """Verify that run_worker imports WorkerSettings cleanly."""
    import backend_v2.run_worker as rw

    assert hasattr(rw, "WorkerSettings")
    assert rw.WorkerSettings is WorkerSettings
