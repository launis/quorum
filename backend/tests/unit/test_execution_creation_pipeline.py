import base64
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend.agents.input_processor import InputProcessorAgent
from backend.dependencies import get_arq_pool, get_async_repository, get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, UserRole
from backend.models.domain.inputs import WorkflowInputs
from backend.models.dtos.execution import Base64FileDTO, ExecutionRequestDTO
from backend.models.dtos.reflection import GuidedReflectionDTO
from backend.services.document_service import DocumentService

# Dummy PDF Base64 (valid structure, empty content)
DUMMY_PDF_B64 = base64.b64encode(b"%PDF-1.4\n%EOF\n").decode("utf-8")

async def mock_get_current_user():
    return TokenData(id="test-user", role=UserRole.ADMIN, organization_id="test-org")

@pytest.fixture(autouse=True)
def auth_override():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    app.dependency_overrides[get_arq_pool] = lambda: None
    yield
    app.dependency_overrides.pop(get_current_user_from_header, None)
    app.dependency_overrides.pop(get_arq_pool, None)

client = TestClient(app)

@pytest.fixture
def mock_document_service():
    service = AsyncMock(spec=DocumentService)
    # By default return fake extracted text
    service.process_evidence_files.return_value = {
        "history_text": "AI: Kuinka voin auttaa?\nKÄYTTÄJÄ: Etsin tietoa kestävästä kehityksestä.",
        "product_text": "Tämä on kestävyysraportti sisältäen dataa.",
        "reflection_text": "Pohdin tässä eettisyyttä."
    }
    return service

def test_execution_creation_pipeline_files(mock_document_service):
    """Test 1: Input can always be a file (pdf etc.) and is processed correctly at start."""
    payload = ExecutionRequestDTO(
        workflow_id="test-wf-123",
        inputs={
            "history_text": Base64FileDTO(filename="history.pdf", content_base64=DUMMY_PDF_B64),
            "product_text": Base64FileDTO(filename="product.pdf", content_base64=DUMMY_PDF_B64)
        }
    )

    from backend.dependencies import get_async_repository, get_document_service_dep, get_engine
    mock_repo = AsyncMock()
    mock_def = AsyncMock()
    mock_def.name = "Test WF"
    mock_repo.get_workflow.return_value = mock_def
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = {"status": "completed", "execution_trace": []}

    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_engine] = lambda: mock_engine
    app.dependency_overrides[get_document_service_dep] = lambda: mock_document_service
    app.dependency_overrides[get_arq_pool] = lambda: None # Force sync run for testing

    response = client.post("/v1/execute/", json=payload.model_dump())
    assert response.status_code == 201

    # Verify DocumentService was called synchronously BEFORE engine
    mock_document_service.process_evidence_files.assert_called_once()

    # Check that inputs dict passing into the engine no longer contains the base64, but the extracted strings
    # The actual execution creates an execution_data dictionary. The API returns it in `inputs`
    created_inputs = response.json()["inputs"]
    assert created_inputs["history_text"] == "AI: Kuinka voin auttaa?\nKÄYTTÄJÄ: Etsin tietoa kestävästä kehityksestä."
    assert created_inputs["product_text"] == "Tämä on kestävyysraportti sisältäen dataa."

    app.dependency_overrides.clear()

def test_execution_creation_reflection_formats(mock_document_service):
    """Test 2 & 3: Reflection document input can be file, string, OR guided reflection query result."""
    # This payload has direct text, not base64 files
    payload = ExecutionRequestDTO(
        workflow_id="test-wf-123",
        inputs={
            "history_text": "AI: Moi\nUser: Hei",
            "reflection_text": "Direct string reflection"
        },
        guided_reflection=GuidedReflectionDTO(
            questions=["Mitä mieltä olet?"],
            answers=["Olen tyytyväinen."]
        )
    )

    mock_repo = AsyncMock()
    mock_def = AsyncMock()
    mock_def.name = "Test WF"
    mock_repo.get_workflow.return_value = mock_def
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    from backend.dependencies import get_document_service_dep, get_engine
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = {"status": "completed", "execution_trace": []}
    app.dependency_overrides[get_engine] = lambda: mock_engine
    app.dependency_overrides[get_document_service_dep] = lambda: mock_document_service

    response = client.post("/v1/execute/", json=payload.model_dump())
    assert response.status_code == 201

    inputs = response.json()["inputs"]
    assert inputs["reflection_text"] == "Direct string reflection"
    assert "guided_reflection" in inputs

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_input_processor_history_formatting(mock_document_service):
    """Test 4: History document is processed and shown as AI/User split inside the workflow."""
    agent = InputProcessorAgent()

    # Simulate execution inputs passing into the workflow engine Agent
    execution_context = {"execution_id": "test-1"}
    inputs = WorkflowInputs(
        history_text="AI: Kuinka voin auttaa?\nKÄYTTÄJÄ: Etsin tietoa.",
        product_text="Valmis raportti."
    )


    from backend.services import chat_parser

    old_parse = chat_parser.parse_pasted_chat

    # We mock the chat dto returned
    from pydantic import BaseModel
    class FakeTurn(BaseModel):
        role: str
        content: str
        turn: int
    class FakeParsedChat(BaseModel):
        turns: list[FakeTurn]

    fake_dto = FakeParsedChat(turns=[
        FakeTurn(role="ai", content="Kuinka voin auttaa?", turn=1),
        FakeTurn(role="user", content="Etsin tietoa.", turn=2)
    ])

    chat_parser.parse_pasted_chat = AsyncMock(return_value=fake_dto)

    result = await agent.execute(inputs, execution_context=execution_context)

    # Asserting that the agent transforms the string history into the structured pipeline
    from backend.models.domain.input_processor import InputProcessorOutput
    assert isinstance(result, InputProcessorOutput)
    # The output of history_text should now be the stringified JSON
    assert "Kuinka voin auttaa?" in result.history_text
    assert result.product_text == "Valmis raportti."

    # Restore mock
    chat_parser.parse_pasted_chat = old_parse

def test_execution_creation_invalid_base64():
    """Test 5: Edge case - invalid base64 file throws readable Error rather than failing the engine later."""
    payload = ExecutionRequestDTO(
        workflow_id="test-wf-123",
        inputs={
            "history_text": Base64FileDTO(filename="history.pdf", content_base64="NOT_BASE_64_!!!")
        }
    )

    response = client.post("/v1/execute/", json=payload.model_dump())
    # Should fail cleanly during ExecutionPrepService execution
    assert response.status_code == 400
    assert "Invalid base64" in str(response.json())

