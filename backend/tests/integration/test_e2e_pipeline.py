from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

# Import application tasks so the TaskRegistry gets populated during the test
from backend.dependencies import get_arq_pool, get_async_repository, get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, UserRole
from backend.models.workflow import WorkflowDefinition, WorkflowStep


async def mock_get_current_user() -> TokenData:
    return TokenData(id=str(uuid4()), role=UserRole.ADMIN, email="admin@example.com", organization_id="test_org")

@pytest.mark.asyncio
async def test_full_pipeline_ingestion_to_bff():
    """End-to-end test simulating exactly what the Flutter client does:
    1. Uploads files and metadata to /v1/execute using multipart/form-data.
    2. Wait for execution to complete (mocking the LLM paths).
    3. Fetches the execution output through the BFF layer /executions/{id}/view.
    """
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    app.dependency_overrides[get_arq_pool] = lambda: None

    # 0. ISOLATE DATABASE (Prevent overwriting data/db.json)
    import os
    import tempfile

    import backend.dependencies as deps
    from backend.database.wrapper import TinyDBClient
    from backend.dependencies import get_db_client_dep

    fd, temp_db_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    test_db = TinyDBClient(temp_db_path)

    # CRITICAL: Reset the Singleton instances to ensure the test uses the temporary DB
    # instead of the live DB that may have already been loaded into memory.
    deps._db_client_instance = test_db
    deps._repository_instance = None
    deps._engine_instance = None

    from backend.agents.analyst import AnalystAgent
    from backend.core.registry import TaskRegistry
    from backend.models.domain import AnalystOutput
    TaskRegistry.register_agent(task_keys=["analyst"], agent_cls=AnalystAgent, output_model=AnalystOutput)

    app.dependency_overrides[get_db_client_dep] = lambda: test_db

    # Extract the repository safely mapped to the test_db
    repository = await get_async_repository()

    # 1. Setup a dummy workflow in the database so the engine has something to run
    wf_id = str(uuid4())
    step_id = str(uuid4())
    dummy_wf = WorkflowDefinition(
        id=wf_id,
        name="E2E Pipeline Test Workflow",
        description="Testing the entire chain",
        organization_id="test_org",
        steps=[step_id]
    )

    # Register the step in the mocked repository so GraphEngine finds it
    step_model = WorkflowStep(
        id=step_id,
        name="step_analyzer",
        task_key="analyst",
        inputs={
            "history_text": "This is a sufficiently long and heavily padded history text string designed strictly to bypass the Pydantic field validation requirements of the AnalystAgent, ensuring it does not crash.",
            "product_text": "This is a sufficiently long and heavily padded product text string designed strictly to bypass the Pydantic field validation requirements of the AnalystAgent, ensuring it does not crash."
        },
        config={"model_strategy": "fast", "llm_prompts": ["mock_prompt_1"]}
    )

    # 1. Provide Real Database Seed Mock via API
    await repository.create_workflow(dummy_wf.model_dump(mode="json"))
    await repository.driver.upsert("steps", step_model.model_dump(mode="json"), step_id)

    # 1.2 Inject Mock Prompt for Strict Mode
    await repository.driver.upsert("components", {"id": "mock_prompt_1", "type": "prompt", "content": "You are a test analyst.", "name": "Mock Prompt"}, "mock_prompt_1")

    # 1.5 Inject Model Registry to satisfy Zero-Fallback mandate
    model_registry_data = {
        "id": "model_registry",
        "models": {
            "test_provider": {
                "fast": {
                    "model_name": "openai/gpt-4o-mini",
                    "tpm_limit": 100000,
                    "rpm_limit": 1000
                },
                "AnalystAgent": {"model_name": "fast"}
            }
        }
    }
    await repository.driver.upsert("system_config", model_registry_data, "model_registry")

    from backend.models.dtos.chat_history import ChatHistoryDTO, ChatMessageDTO, ChatRole
    from backend.models.llm import LLMResponse

    with patch("backend.llm.provider.LiteLLMProvider.generate", new_callable=AsyncMock) as mock_agent, \
         patch("backend.services.chat_parser.parse_pasted_chat", new_callable=AsyncMock) as mock_chat_parser:

        # Mock chat parsing response
        mock_chat_parser.return_value = ChatHistoryDTO(
            conversation=[ChatMessageDTO(order=1, role=ChatRole.USER, text="Mocked history")]
        )

        # Provide a valid mock response representing an Agent's parsed output
        mock_agent.return_value = LLMResponse(
            content='{"thought_process": "Mocked", "conclusion": "Mocked conclusion", "confidence_score": 0.9, "hypotheses": [{"id": "HYP-001", "claim_text": "The system is robust.", "evidence_found": true, "quotes": ["Testing passed explicitly."], "search_query": "robustness testing"}]}',
            parsed_content={
                "thought_process": "This is a mocked RAG analysis.",
                "conclusion": "The product strategy is sound.",
                "confidence_score": 0.95,
                "hypotheses": [
                    {
                        "id": "HYP-001",
                        "claim_text": "The system is robust.",
                        "evidence_found": True,
                        "quotes": ["Testing passed explicitly."],
                        "search_query": "robustness testing"
                    }
                ]
            },
            reasoning_token="none",
            token_usage={"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10, "cost_usd": 0.05},
            system_fingerprint="mock_fp_123"
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Construct the strict JSON payload matching ExecutionRequestDTO
            json_payload = {
                "workflow_id": wf_id,
                "organization_id": "test_org",
                "inputs": {
                    "history_text": "Simulated chat history content.",
                    "target_audience": "stakeholders"
                },
                "guided_reflection": None
            }

            response = await ac.post("/v1/execute/", json=json_payload)
            assert response.status_code == 201, f"Execution creation failed: {response.text}"
            exec_data = response.json()
            execution_id = exec_data["id"]

            # 4. Wait for the engine to mark the execution as completed
            # The execute_workflow_route triggers arq, but in tests arq might run sync or we poll repo.
            # If arq isn't running, we might need to directly trigger the job or wait.
            # Actually, in testing environment `get_arq_pool` is usually mocked to None, forcing sync execution!
            # Let's verify status.
            exec_record_dict = await repository.get_execution(execution_id)
            assert exec_record_dict is not None
            assert exec_record_dict.status == "completed", f"Status was {exec_record_dict.status}. Trace: {exec_record_dict.results}"

            # 5. Hit the BFF View Endpoint (ReportView DTO)
            view_response = await ac.get(f"/executions/{execution_id}/view")
            assert view_response.status_code == 200, f"BFF view failed: {view_response.text}"

            sdui_payload = view_response.json()
            assert "title" in sdui_payload
            assert "sections" in sdui_payload

            # Check that SDUI generated sections for us
            assert len(sdui_payload["sections"]) > 0, "BFF did not produce any UI sections"
            assert sdui_payload["sections"][0]["type"] in ["markdown_block", "score_card", "data_grid", "USAGE_STATS"]

    # Cleanup
    app.dependency_overrides.clear()

    try:
        os.remove(temp_db_path)
    except Exception:
        pass

