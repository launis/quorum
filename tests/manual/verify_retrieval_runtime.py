
import asyncio
import logging
from unittest.mock import AsyncMock, patch

from backend.agents.retrieval import RetrievalAgent
from backend.models.state import InputData, WorkflowState

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_retrieval_runtime():
    print("\n--- Testing RetrievalAgent Runtime (Metadata Injection) ---")

    # 1. Setup Mock State
    input_data = InputData(
        conversation_id="test-conv",
        history_text="Some history",
        product_text="Some product",
        reflection_text="Some reflection"
    )
    state = WorkflowState(
        execution_id="test-exec-1",
        organization_id="org-123",
        inputs=input_data
    )

    # 2. Mock Dependency Injection
    # We strip out the DB calls for this unit test
    mock_repo = AsyncMock()
    # Mock get_all_executions return value
    mock_repo.get_all_executions.return_value = [
        {
            "execution_id": "prev-1",
            "status": "completed",
            "end_time": "2025-01-01T12:00:00Z",
            "trace": {
                "step_judge": {
                    "pisteet": {
                        "analyysi": {"arvosana": 3},
                        "arviointi": {"arvosana": 4},
                        "synteesi": {"arvosana": 3}
                    },
                    "kriittiset_havainnot_yhteenveto": "Good job."
                }
            }
        }
    ]

    # Patch modules
    with patch("backend.agents.retrieval.get_repository", new=AsyncMock(return_value=mock_repo)):
        with patch("backend.agents.retrieval.get_db_client"):
            with patch("backend.agents.retrieval.get_settings"):

                # 3. Instantiate Agent
                agent = RetrievalAgent()

                # 4. Execute
                print("Executing Agent...")
                new_state = await agent.execute(state)

                # 5. Verify Output
                print("Verifying Output...")
                result = new_state.step_context

                if not result:
                    print("FAILURE: step_context is None!")
                    exit(1)

                print(f"Result Type: {type(result)}")
                # Pydantic items usually print nicely
                # print(result.model_dump_json(indent=2))

                # 6. Verify Metadata
                if hasattr(result, "metadata") and result.metadata:
                    print(f"Metadata Found: {result.metadata}")
                    print(f"Luontiaika: {result.metadata.luontiaika}")
                    print(f"Agentti: {result.metadata.agentti}")

                    if result.metadata.agentti == "RetrievalAgent":
                         print("SUCCESS: Metadata correctly injected with Agent Name.")
                    else:
                         print(f"FAILURE: Agent name mismatch. Got {result.metadata.agentti}")
                         exit(1)
                else:
                    print("FAILURE: Metadata missing from result!")
                    exit(1)

if __name__ == "__main__":
    asyncio.run(test_retrieval_runtime())
