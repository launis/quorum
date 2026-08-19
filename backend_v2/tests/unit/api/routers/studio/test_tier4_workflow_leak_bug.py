from unittest.mock import AsyncMock

import pytest

# Create a FastAPI app to mount the router
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.routers.studio.workflows import router as api_router
from backend_v2.models.auth import TokenData
from backend_v2.models.dtos.studio import WorkflowResponseDTO

app = FastAPI()
app.include_router(api_router)
client = TestClient(app)

from collections.abc import Generator

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_workflow_service,
)
from backend_v2.models.auth import UserRole
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.v2_core import I18nText


def mock_get_current_user() -> TokenData:
    return TokenData(id="test", role=UserRole.ROOT, organization_id="root_org")


@pytest.fixture(autouse=True)
def setup_overrides() -> Generator[None]:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    mock_service = AsyncMock()
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_service
    return mock_service


@pytest.mark.asyncio
async def test_workflow_does_not_leak_metric_mappings(mock_studio_service: AsyncMock) -> None:
    """Ensure that the API response explicitly omits metric_mappings."""
    from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO

    mock_profile_dto = OutputProfileResponseDTO.model_validate(
        {
            "id": "prof_0123456789abcdef0123456789abcdef",
            "workflow_id": "wf_0123456789abcdef0123456789abcdef",
            "slug": "test-profile",
            "name": {"default_locale": "en", "translations": {"en": "test"}},
            "layouts": [],
        },
        strict=False,
    )

    mock_workflow = WorkflowResponseDTO(
        id="wf_0123456789abcdef0123456789abcdef",
        slug="test-wf",
        name=I18nText(default_locale="en", translations={"en": "test wf"}),
        description="test",
        status="draft",
        version=1,
        default_profile_id="prof_0123456789abcdef0123456789abcdef",
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        organization_id="root_org",
        output_profiles={"prof_0123456789abcdef0123456789abcdef": mock_profile_dto},
    )

    mock_studio_service.list_workflows.return_value = [mock_workflow]

    response = client.get("/workflows/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1

    wf_data = data[0]
    profiles = wf_data.get("output_profiles", {})
    assert "prof_0123456789abcdef0123456789abcdef" in profiles
    profile_data = profiles["prof_0123456789abcdef0123456789abcdef"]

    # Dual-Axis Localization contract requires metric_mappings to be retained in responses
    assert "metric_mappings" in profile_data
    assert "score_display_label" not in profile_data
