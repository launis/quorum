from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_arq_pool, get_current_user_from_header, get_repo
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    I18nText,
    OutputLayoutBlock,
    OutputProfile,
    RenderedSynthesisCache,
    SynthesisConfigDTO,
)


def mock_get_current_user_admin() -> Any:
    return TokenData(email="admin@test.com", id="usr_1111222233334444", role=UserRole.ADMIN, organization_id="org_1111222233334444")


@pytest.fixture
def mock_repository() -> Any:
    """Mock repository with complete SSOT representation of an Execution and Profile."""
    repo = AsyncMock()

    # 1. Output Profile
    mock_profile = OutputProfile(
        id="prf_2233445566778899",
        workflow_id="wf_1234567812345678",
        name=I18nText(default_locale="en", translations={"en": "Executive Report"}),
        slug="exec_report",
        description=I18nText(default_locale="en", translations={"en": "desc"}),
        visible_metadata=[],  # Specifically filtering out standard fields if needed, but [] is OK.
        layouts=[
            OutputLayoutBlock(
                preset_view="1d_metrics",
                title=I18nText(default_locale="en", translations={"en": "Main Metric"}),
                description=I18nText(default_locale="en", translations={"en": "Main Description"}),
                target_blocks=["blk_1111111111111111"],
                show_text=True,
                synthesis=SynthesisConfigDTO(),
            )
        ],
    )
    repo.get_output_profile.return_value = mock_profile
    repo.get_all_output_profiles.return_value = [mock_profile.model_dump(mode="json")]

    # 2. Workflow
    repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "output_profiles": {"prf_2233445566778899": "Executive Report"},
        "steps": [
            {
                "id": "step_1",
                "task_blueprint": "step_rule_1",
            }
        ],
    }

    # 3. Prompt Blocks
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1111111111111111",
            "type": "slider",
            "slug": "main_metric",
            "label": {"default_locale": "en", "translations": {"en": "Metric Label"}},
            "description": {"default_locale": "en", "translations": {}},
            "category_id": "test",
        }
    ]

    # Compute exactly what BlueprintTransformer computes
    title_obj = I18nText(default_locale="en", translations={"en": "Main Metric"})
    computed_layout_id = f"layout_1d_metrics_{hash(str(title_obj.model_dump()))}"

    # 4. Execution Record (Fully Cached via Epic 14 extraction)
    mock_execution = ExecutionRecord(
        id="exe_1010101010101010",
        workflow_id="wf_1234567812345678",
        created_by="usr_1111222233334444",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            {
                "step_name": "step_1",
                "event_type": "output",
                "content": {
                    "blk_1111111111111111": 88.0,
                    "blk_1111111111111111_justification": "Analyysi perustelu..."
                }
            }
        ],
        profile_syntheses={
            "prf_2233445566778899": RenderedSynthesisCache(
                synthesized_markdown="Global Executive Synthesis from worker.",
                section_syntheses={computed_layout_id: "This is block specific context."},
            )
        },
        metadata={"target_locale": "en"},
    )
    repo.get_execution.return_value = mock_execution

    return repo


@pytest.fixture
def mock_arq() -> Any:
    arq = AsyncMock()
    return arq


@pytest.fixture
def client_e2e(mock_repository: Any, mock_arq: Any) -> Any:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_admin
    app.dependency_overrides[get_repo] = lambda: mock_repository
    app.dependency_overrides[get_arq_pool] = lambda: mock_arq

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_e2e_json_render_mapping(client_e2e: Any, mock_repository: Any) -> None:
    """Test that GET /render?format=json correctly resolves profile synthesis and formats the ReportDataDTO."""
    # Action
    response = client_e2e.get(
        "/api/v2/execution/executions/exe_1010101010101010/render?format=json&profile_id=prf_2233445566778899",
        headers={"Accept-Language": "en"},
    )

    # Assert HTTP success
    assert response.status_code == 200, response.text
    data = response.json()

    # Assert DTO mappings from BlueprintTransformer
    assert data["profile_id"] == "prf_2233445566778899"
    assert data["synthesized_markdown"] == "Global Executive Synthesis from worker."

    # Assert layout generation
    assert len(data["layouts"]) == 1
    layout = data["layouts"][0]
    assert layout["preset_view"] == "1d_metrics"
    assert layout["synthesis_md"] == "This is block specific context."


@pytest.mark.asyncio
async def test_e2e_pdf_generation_bytes(mock_repository: Any) -> None:
    """Test the physical generation of PDF directly bypassing the routing layer."""
    from backend_v2.services.blueprint import BlueprintTransformer
    from backend_v2.services.pdf_generator import PdfReportService

    # Use BlueprintTransformer to build DTO exactly as API would
    transformer = BlueprintTransformer(mock_repository)
    dto = await transformer.build_report_dto(
        execution_id="exe_1010101010101010", profile_id="prf_2233445566778899", accept_language="en"
    )

    assert dto.synthesized_markdown == "Global Executive Synthesis from worker."

    # Send DTO directly to PDF Generator Service
    pdf_service = PdfReportService(mock_repository)
    pdf_bytes = await pdf_service.generate_execution_pdf(execution_id="exe_1010101010101010", report_dto=dto)

    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 100  # Ensure we actually have binary content

    # Write physical file as requested
    import os

    out_dir = os.path.join("backend_v2", "tests", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "test_report.pdf")

    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 100
