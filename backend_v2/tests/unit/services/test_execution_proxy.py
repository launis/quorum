import importlib.util

import backend_v2.services.execution as exec_pkg
from backend_v2.services.execution import (
    ExecutionService,
    create_execution_record,
)


def test_execution_pkg_exports_all_symbols() -> None:
    """Verify that every symbol declared in __all__ exists and is accessible."""
    exec_pkg_dir = dir(exec_pkg)
    assert "__all__" in exec_pkg_dir
    expected = [
        "ExecutionContextService",
        "ExecutionCreate",
        "ExecutionIngressService",
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
        assert symbol in exec_pkg_dir

    banned_borrowed_symbols = [
        "BlueprintTransformer",
        "DocumentExtractionService",
        "ExecutionLegacyRenderService",
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

    assert importlib.util.find_spec("backend_v2.services.execution.legacy_render_service") is None
    assert importlib.util.find_spec("backend_v2.models.dtos.render") is None


def test_execution_service_facade_instantiation() -> None:
    """Verify that ExecutionService class exists and has decomposed subservice properties/methods."""
    assert isinstance(ExecutionService, type)
    assert callable(create_execution_record)
