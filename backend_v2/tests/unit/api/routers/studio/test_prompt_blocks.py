"""Unit tests for backend_v2/api/routers/studio/prompt_blocks.py router."""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
)
from backend_v2.api.routers.studio.prompt_blocks import router
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.prompt_blocks import PromptBlock, SystemRulePromptBlock
from backend_v2.models.dtos.studio import PromptBlockSimulationResponse
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def mock_get_current_user() -> TokenData:
    return TokenData(id="test_usr", role="ROOT", organization_id="root_org")


@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_services():
    mock_prompt_block = AsyncMock()
    mock_simulation = AsyncMock()
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: mock_prompt_block
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_simulation
    return mock_prompt_block, mock_simulation


@pytest.fixture
def sample_block() -> PromptBlock:
    return SystemRulePromptBlock(
        id="blk_1234567890abcdef",
        slug="test_block",
        label=I18nText(translations={"fi": "Testi", "en": "Test"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Follow rules strictly.",
    )


def test_router_initialization() -> None:
    assert router is not None
    assert router.prefix == "/prompt-blocks"


@pytest.mark.asyncio
async def test_get_prompt_blocks(mock_studio_services, sample_block: PromptBlock) -> None:
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.list_prompt_blocks.return_value = [sample_block]

    response = client.get("/prompt-blocks/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "blk_1234567890abcdef"


@pytest.mark.asyncio
async def test_create_prompt_block(mock_studio_services, sample_block: PromptBlock) -> None:
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.create_prompt_block_draft.return_value = sample_block

    response = client.post("/prompt-blocks/")
    assert response.status_code == 200
    assert response.json()["id"] == "blk_1234567890abcdef"


@pytest.mark.asyncio
async def test_get_prompt_block(mock_studio_services, sample_block: PromptBlock) -> None:
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.get_prompt_block.return_value = sample_block

    response = client.get("/prompt-blocks/blk_1234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "blk_1234567890abcdef"


@pytest.mark.asyncio
async def test_clone_prompt_block(mock_studio_services, sample_block: PromptBlock) -> None:
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.clone_prompt_block.return_value = sample_block

    response = client.post("/prompt-blocks/blk_1234567890abcdef/clone")
    assert response.status_code == 200
    assert response.json()["id"] == "blk_1234567890abcdef"


@pytest.mark.asyncio
async def test_save_prompt_block(mock_studio_services, sample_block: PromptBlock) -> None:
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.save_prompt_block.return_value = sample_block

    response = client.put("/prompt-blocks/blk_1234567890abcdef", json=sample_block.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["id"] == "blk_1234567890abcdef"


@pytest.mark.asyncio
async def test_delete_prompt_block(mock_studio_services) -> None:
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.delete_prompt_block.return_value = None

    response = client.delete("/prompt-blocks/blk_1234567890abcdef?force_delete=true")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "deleted_id": "blk_1234567890abcdef"}


@pytest.mark.asyncio
async def test_simulate_prompt_block(mock_studio_services, sample_block: PromptBlock) -> None:
    _, mock_simulation = mock_studio_services
    sim_response = PromptBlockSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="Rendered",
        trace={},
        prompt_context=None,
    )
    mock_simulation.simulate_prompt_block.return_value = sim_response

    payload = {
        "block": sample_block.model_dump(mode="json"),
        "mock_inputs": {},
    }
    response = client.post("/prompt-blocks/simulate", json=payload)
    assert response.status_code == 200
    assert response.json()["valid"] is True
