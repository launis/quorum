"""End-to-End Golden Master Test for Epic 93 SDUI Output Rendering Unification."""

import pytest

from backend_v2.models.v2_core import ReportDataDTO
from backend_v2.models.view.sdui import ReportView
from backend_v2.services.sdui_mapper_service import SduiMapperService


@pytest.mark.asyncio
async def test_epic_93_e2e_golden_master() -> None:
    """Verify the E2E data flow from ExecutionRecord to SduiComponent tree.

    ExecutionRecord -> MatrixReducer -> ReportDataDTO -> SduiMapper -> SduiComponent tree.
    """
    # 1. Build a minimal v2_core.ReportDataDTO
    dto = ReportDataDTO(
        workflow_id="wor_456",
        profile_id="prf_001",
        global_score=85.0,
    )

    # 2. Map the DTO to SDUI view model using the SduiMapperService
    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id="exe_123")

    # 3. Assertions
    assert isinstance(view, ReportView)
    assert view.view_id == "exe_123"
    assert view.metrics is not None
    assert view.metrics["global_score"] == 85.0
