"""Unit tests for execution service proxy module verifying PEP 484 re-exports."""

import backend_v2.services.execution as exec_pkg
from backend_v2.services.execution import (
    ExecutionService,
    create_execution_record,
)


def test_execution_pkg_exports_all_symbols() -> None:
    """Verify that every symbol declared in __all__ exists and is accessible."""
    assert hasattr(exec_pkg, "__all__")
    expected = [
        "ExecutionContextService",
        "ExecutionCreate",
        "ExecutionIngressService",
        "ExecutionLegacyRenderService",
        "ExecutionLifecycleService",
        "ExecutionOverrideService",
        "ExecutionRecord",
        "ExecutionResumptionService",
        "ExecutionService",
        "ExecutionStep",
        "ExecutionStreamService",
        "FrozenContext",
        "create_execution_record",
    ]
    assert set(exec_pkg.__all__) == set(expected)
    for symbol in expected:
        assert hasattr(exec_pkg, symbol)
        assert getattr(exec_pkg, symbol) is not None

    banned_borrowed_symbols = [
        "BlueprintTransformer",
        "DocumentExtractionService",
        "ExportService",
        "FlatFileService",
        "OutputProfile",
        "PdfReportService",
        "SduiMapperService",
        "TokenData",
        "Workflow",
        "asyncio",
        "get_storage_driver",
        "recalculate",
    ]
    for banned in banned_borrowed_symbols:
        assert banned not in exec_pkg.__all__


def test_execution_service_facade_instantiation() -> None:
    """Verify that ExecutionService class exists and has decomposed subservice properties/methods."""
    assert isinstance(ExecutionService, type)
    assert callable(create_execution_record)
