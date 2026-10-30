"""Unit tests for backend_v2/api/routers/studio/prompt_blocks.py router."""

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
)
from backend_v2.api.routers.studio.prompt_blocks import (
    delete_prompt_block,
    get_prompt_block,
    router,
    simulate_prompt_block,
)
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.main import app_exception_handler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.studio import (
    PromptBlockSimulationRequest,
    PromptBlockSimulationResponse,
    StepSimulationTraceDTO,
)
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.services.studio.simulation_service import StudioSimulationService

app = FastAPI()
app.include_router(router)


@app.exception_handler(AppException)
async def _test_app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException instances using the production RFC 7807 handler."""
    return await app_exception_handler(request, exc)


client = TestClient(app)


def mock_get_current_user() -> TokenData:
    """Return a root TokenData fixture for router authentication."""
    return TokenData(
        id="usr_0195f3a0000070018234567890abcdef",
        role=UserRole.ROOT,
        organization_id="org_0195f3a0000070018234567890abcdef",
    )


@pytest.fixture(autouse=True)
def setup_overrides() -> Generator[None]:
    """Configure and clean up FastAPI dependency overrides for each test."""
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_services() -> tuple[AsyncMock, AsyncMock]:
    """Provide mocked StudioPromptBlockService and StudioSimulationService instances."""
    mock_prompt_block = AsyncMock()
    mock_simulation = AsyncMock()
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: mock_prompt_block
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_simulation
    return mock_prompt_block, mock_simulation


@pytest.fixture
def sample_block() -> PromptBlock:
    """Provide a valid SystemRulePromptBlock instance."""
    return SystemRulePromptBlock(
        id="blk_0195f3a0000070018234567890abcdef",
        slug="test_block",
        label=I18nText(translations={"fi": "Testi", "en": "Test"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Follow rules strictly.",
    )


@pytest.fixture
def sample_empty_matrix_block() -> MatrixPromptBlock:
    """Provide a MatrixPromptBlock whose scale has zero claims/assertions for boundary testing."""
    return MatrixPromptBlock(
        id="blk_0195f3a00000700a8bcdef1234567890",
        slug="test_matrix_block",
        label=I18nText(translations={"fi": "Matriisi", "en": "Matrix"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        ai_description="Evaluate organizational maturity.",
        scales=[
            MatrixScale(
                score=1,
                ai_label="LEVEL_1",
                claims=[],
            )
        ],
    )


def test_router_initialization() -> None:
    """Verify that the prompt blocks router initializes with expected prefix."""
    assert router is not None
    assert router.prefix == "/prompt-blocks"


@pytest.mark.asyncio
async def test_get_prompt_blocks(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock) -> None:
    """Test GET /prompt-blocks/ retrieves all accessible prompt blocks."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.list_prompt_blocks.return_value = [sample_block]

    response = client.get("/prompt-blocks/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "blk_0195f3a0000070018234567890abcdef"
    mock_prompt_block.list_prompt_blocks.assert_awaited_once_with(mock_get_current_user())


@pytest.mark.asyncio
async def test_create_prompt_block(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock
) -> None:
    """Test POST /prompt-blocks/ creates a new prompt block draft."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.create_prompt_block_draft.return_value = sample_block

    response = client.post("/prompt-blocks/")
    assert response.status_code == 200
    assert response.json()["id"] == "blk_0195f3a0000070018234567890abcdef"
    mock_prompt_block.create_prompt_block_draft.assert_awaited_once_with(
        mock_get_current_user(), category_id=PromptBlockCategory.SYSTEM_RULE
    )


@pytest.mark.asyncio
async def test_get_prompt_block(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock) -> None:
    """Test GET /prompt-blocks/{id} retrieves a specific prompt block."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.get_prompt_block.return_value = sample_block

    response = client.get("/prompt-blocks/blk_0195f3a0000070018234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "blk_0195f3a0000070018234567890abcdef"
    mock_prompt_block.get_prompt_block.assert_awaited_once_with(
        mock_get_current_user(), "blk_0195f3a0000070018234567890abcdef"
    )


@pytest.mark.asyncio
async def test_clone_prompt_block(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock) -> None:
    """Test POST /prompt-blocks/{id}/clone clones an existing prompt block."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.clone_prompt_block.return_value = sample_block

    response = client.post("/prompt-blocks/blk_0195f3a0000070018234567890abcdef/clone")
    assert response.status_code == 200
    assert response.json()["id"] == "blk_0195f3a0000070018234567890abcdef"
    mock_prompt_block.clone_prompt_block.assert_awaited_once_with(
        mock_get_current_user(), "blk_0195f3a0000070018234567890abcdef"
    )


@pytest.mark.asyncio
async def test_save_prompt_block(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock) -> None:
    """Test PUT /prompt-blocks/{id} updates a prompt block."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.save_prompt_block.return_value = sample_block

    response = client.put(
        "/prompt-blocks/blk_0195f3a0000070018234567890abcdef", json=sample_block.model_dump(mode="json")
    )
    assert response.status_code == 200
    assert response.json()["id"] == "blk_0195f3a0000070018234567890abcdef"
    mock_prompt_block.save_prompt_block.assert_awaited_once_with(
        mock_get_current_user(), "blk_0195f3a0000070018234567890abcdef", sample_block
    )


@pytest.mark.asyncio
async def test_delete_prompt_block(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test DELETE /prompt-blocks/{id} deletes a prompt block and returns confirmation DTO."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.delete_prompt_block.return_value = None

    response = client.delete("/prompt-blocks/blk_0195f3a0000070018234567890abcdef?force_delete=true")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "deleted_id": "blk_0195f3a0000070018234567890abcdef"}
    mock_prompt_block.delete_prompt_block.assert_awaited_once_with(
        mock_get_current_user(), "blk_0195f3a0000070018234567890abcdef", force_delete=True
    )


@pytest.mark.asyncio
async def test_simulate_prompt_block(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock
) -> None:
    """Test POST /prompt-blocks/simulate executes prompt block template simulation."""
    mock_prompt_block, _ = mock_studio_services
    real_simulation_service = StudioSimulationService(prompt_block_service=mock_prompt_block)
    app.dependency_overrides[get_studio_simulation_service] = lambda: real_simulation_service

    block_with_var = sample_block.model_copy(update={"instruction_text": "Rule for {company_name}."})
    payload = {
        "block": block_with_var.model_dump(mode="json"),
        "mock_inputs": {"company_name": "Acme Corp"},
    }
    response = client.post("/prompt-blocks/simulate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["rendered_prompt"] == "Rule for Acme Corp."


@pytest.mark.asyncio
async def test_simulate_prompt_block_with_null_context_text_and_locale(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_block: PromptBlock
) -> None:
    """Regression test: simulate_prompt_block accepts null context_text and target_locale."""
    _, mock_simulation = mock_studio_services
    sim_response = PromptBlockSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="Rendered",
        trace=StepSimulationTraceDTO(),
        prompt_context=None,
    )
    mock_simulation.simulate_prompt_block.return_value = sim_response

    payload = {
        "block": sample_block.model_dump(mode="json"),
        "mock_inputs": {},
        "target_scale_score": None,
        "target_locale": None,
        "context_text": None,
    }
    response = client.post("/prompt-blocks/simulate", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["valid"] is True


@pytest.mark.asyncio
async def test_simulate_prompt_block_missing_scale_score_raises_app_exception(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
    sample_empty_matrix_block: MatrixPromptBlock,
) -> None:
    """Negative test: simulate_prompt_block raises AppException (RESOURCE_NOT_FOUND) when target_scale_score is out of bounds."""
    mock_prompt_block, _ = mock_studio_services
    real_simulation_service = StudioSimulationService(prompt_block_service=mock_prompt_block)
    request = PromptBlockSimulationRequest(
        block=sample_empty_matrix_block,
        mock_inputs={},
        target_scale_score=99,
    )

    with pytest.raises(AppException) as exc_info:
        await simulate_prompt_block(
            data=request,
            current_user=mock_get_current_user(),
            studio_simulation_service=real_simulation_service,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_simulate_prompt_block_zero_assertions_raises_app_exception(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
    sample_empty_matrix_block: MatrixPromptBlock,
) -> None:
    """Negative test: simulate_prompt_block raises AppException (VALIDATION_FAILED) when matrix scale has zero assertions."""
    mock_prompt_block, _ = mock_studio_services
    real_simulation_service = StudioSimulationService(prompt_block_service=mock_prompt_block)
    request = PromptBlockSimulationRequest(
        block=sample_empty_matrix_block,
        mock_inputs={},
        target_scale_score=1,
    )

    with pytest.raises(AppException) as exc_info:
        await simulate_prompt_block(
            data=request,
            current_user=mock_get_current_user(),
            studio_simulation_service=real_simulation_service,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_get_prompt_block_not_found_error(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Negative test: GET /prompt-blocks/{id} raises ResourceNotFoundError and maps to HTTP 404."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.get_prompt_block.side_effect = ResourceNotFoundError(
        resource_type="prompt_block", resource_id="blk_0195f3a0000070008000000000000000"
    )

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await get_prompt_block(
            id="blk_0195f3a0000070008000000000000000",
            current_user=mock_get_current_user(),
            prompt_block_service=mock_prompt_block,
        )
    assert exc_info.value.status_code == 404

    response = client.get("/prompt-blocks/blk_0195f3a0000070008000000000000000")
    assert response.status_code == 404
    assert response.json()["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_delete_prompt_block_permission_denied_error(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Negative test: DELETE /prompt-blocks/{id} raises PermissionDeniedError and maps to HTTP 403."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.delete_prompt_block.side_effect = PermissionDeniedError(
        message="Permission denied: delete prompt_block blk_0195f3a0000070018234567890abcdef"
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await delete_prompt_block(
            id="blk_0195f3a0000070018234567890abcdef",
            current_user=mock_get_current_user(),
            prompt_block_service=mock_prompt_block,
            force_delete=False,
        )
    assert exc_info.value.status_code == 403

    response = client.delete("/prompt-blocks/blk_0195f3a0000070018234567890abcdef")
    assert response.status_code == 403
    assert response.json()["extensions"]["error_code"] == ErrorCodes.PERMISSION_DENIED.value


@pytest.mark.asyncio
async def test_simulate_prompt_block_invalid_payload_error() -> None:
    """Negative boundary test: POST /prompt-blocks/simulate returns 422 on malformed request payload."""
    response = client.post("/prompt-blocks/simulate", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_prompt_block_matrix_category(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
    sample_empty_matrix_block: MatrixPromptBlock,
) -> None:
    """Test POST /prompt-blocks/?category_id=matrix creates a MatrixPromptBlock."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.create_prompt_block_draft.return_value = sample_empty_matrix_block

    response = client.post("/prompt-blocks/?category_id=matrix")
    assert response.status_code == 200
    assert response.json()["category_id"] == "matrix"
    mock_prompt_block.create_prompt_block_draft.assert_awaited_once_with(
        mock_get_current_user(), category_id=PromptBlockCategory.MATRIX
    )


def test_get_prompt_block_invalid_id_returns_422() -> None:
    """Negative test: GET /prompt-blocks/{id} with non-opaque ID returns 422."""
    response = client.get("/prompt-blocks/invalid-id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_save_prompt_block_id_mismatch_returns_400(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
    sample_block: PromptBlock,
) -> None:
    """Negative test: PUT /prompt-blocks/{id} with mismatched payload ID returns 400 ID_MISMATCH."""
    response = client.put(
        "/prompt-blocks/blk_0195f3a0000070008000000000000099",
        json=sample_block.model_dump(mode="json"),
    )
    assert response.status_code == 400
    assert response.json()["extensions"]["error_code"] == ErrorCodes.ID_MISMATCH.value


@pytest.mark.asyncio
async def test_delete_protocol_prompt_block_raises_403(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Negative test: DELETE /prompt-blocks/{id} raises 403 SYSTEM_PROTECTED_RESOURCE for PROTOCOL blocks."""
    mock_prompt_block, _ = mock_studio_services
    mock_prompt_block.delete_prompt_block.side_effect = AppException(
        message="Cannot delete protocol prompt block without force_delete.",
        status_code=403,
        details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value},
    )

    response = client.delete("/prompt-blocks/blk_0195f3a0000070018234567890abcdef")
    assert response.status_code == 403
    assert response.json()["extensions"]["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value
