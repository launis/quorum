import asyncio
import logging
import os
import sys
import uuid
from unittest.mock import MagicMock

# Add current CWD to path
sys.path.append(os.getcwd())

# Mock LLMFactory BEFORE internal imports to bypass auth
sys.modules["backend.llm.factory"] = MagicMock()
from backend.llm.factory import LLMFactory

LLMFactory.create_provider.return_value = MagicMock()

from backend.agents.archivist import ArchivistAgent
from backend.core.engine import GraphEngine
from backend.core.registry import TaskRegistry
from backend.models.domain import ArchivistOutput
from backend.models.workflow import WorkflowDefinition, WorkflowStep

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_archivist")

# Register Agent
TaskRegistry.register_agent(task_keys=["archivist_task"], agent_cls=ArchivistAgent, output_model=ArchivistOutput)


async def run_test():
    engine = GraphEngine()

    # Define step with the HOOK
    step_archivist = WorkflowStep(
        id="step_archivist",
        name="Archivist Step",
        description="Desc",
        task_key="archivist_task",
        inputs={
            "history_text": "History",
            "product_text": "Product",
            "reflection_text": "Reflection",
            # This input relies on the hook populating it in context_variables!
            "archivist_precedents": "$archivist_precedents",
        },
        config={"pre_hooks": ["retrieve_precedent"], "llm_prompts": []},
    )

    workflow = WorkflowDefinition(
        id="test_archivist_workflow",
        name="Test Workflow",
        description="Test desc",
        status="draft",
        version=1,
        is_public=False,
        organization_id="org-123",
        steps=["step_archivist"]
    )

    inputs = {"inputs": {"history_text": "History", "product_text": "Product", "reflection_text": "Reflection"}}

    # Mock Repository for the Hook
    mock_repo = MagicMock()
    # Hook calls: await repository.get_all_executions()
    # It returns list of dicts
    mock_executions = [
        {
            "execution_id": str(uuid.uuid4()),
            "status": "completed",
            "end_time": "2026-01-01T12:00:00",
            "trace": {
                "step_judge": {
                    "pisteet": {"analyysi": {"arvosana": 9}, "arviointi": {"arvosana": 8}, "synteesi": {"arvosana": 9}},
                    "kriittiset_havainnot_yhteenveto": "Good job.",
                }
            },
        }
    ]

    async def get_all_executions():
        return mock_executions

    async def get_step_by_id(step_id):
        if step_id == "step_archivist":
             return step_archivist.model_dump()
        return None

    mock_repo.get_all_executions = get_all_executions
    mock_repo.get_step_by_id = get_step_by_id

    # Mock Provider Response
    mock_provider = MagicMock()
    LLMFactory.create_provider.return_value = mock_provider

    import json

    valid_response = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "model_name": "mock-model",
        "relevant_cases": [],
        "consistency_analysis": "Consistent.",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Aligned",
        "description": "Aligned description",  # Bypass localization
        "token_usage": {"total": 100},
    }

    mock_response_obj = MagicMock()
    mock_response_obj.content = json.dumps(valid_response)
    mock_response_obj.parsed_content = None  # Force parsing path or use it? BaseAgent checks this.
    mock_response_obj.token_usage = {"total": 100}
    mock_response_obj.messages = [{"role": "user", "content": "prompt"}]

    async def mock_generate(*args, **kwargs):
        return mock_response_obj

    mock_provider.generate = mock_generate

    logger.info("Starting Archivist Verification...")
    try:
        # Pass mock repo and provider

        result = await engine.execute_workflow(definition=workflow, initial_input=inputs, repository=mock_repo)

        # Verify that precedents were injected and used
        # We can inspect the trace or the result
        logger.info("Workflow Finished!")
        # Access the context_variables from the returned dump?
        # engine.execute_workflow returns state.model_dump()

        # Check if precedents found their way into context vars
        ctx = result.get("context_variables", {})
        precedents = ctx.get("archivist_precedents")

        if precedents and "ENNAKKOTAPAUKSET" in precedents:
            logger.info(f"SUCCESS: Precedents injected: {precedents[:50]}...")
        else:
            logger.error(f"FAILURE: Precedents NOT found in context variables. Context keys: {ctx.keys()}")
            raise Exception("Hook failed to inject data.")

    except Exception as e:
        import traceback

        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        logger.error(f"Workflow Failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except Exception:
        import traceback

        traceback.print_exc()
