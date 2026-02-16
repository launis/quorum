import asyncio
import logging

from backend.core.engine import GraphEngine
from backend.models.domain import WorkflowStep
from backend.models.workflow import WorkflowDefinition

logging.basicConfig(level=logging.DEBUG) # DEBUG to see hook logs
logger = logging.getLogger(__name__)

async def run_test():
    engine = GraphEngine()

    # Minimal Definition with step_analyst and global inputs
    step_analyst = WorkflowStep(
        id="step_analyst",
        task_key="analyst", # Mock this?
        config={
            "pre_hooks": ["calculate_text_metrics"],
            "model": "gpt-mock"
        },
        inputs={
            "history_text": "$inputs.history_text"
        }
    )

    wf_def = WorkflowDefinition(
        id="test_metrics_wf",
        name="Test Metrics",
        steps=[step_analyst],
        ui_schema={}
    )

    initial_input = {
        "inputs": {
            "history_text": "User: Hello.\nAI: Hi there.",
            "product_text": "Product content.",
            "reflection_text": "Reflection content."
        }
    }

    # We need to mock TaskRegistry.get("analyst") because real one needs LLM
    from backend.core.registry import TaskDefinition, TaskRegistry

    async def mock_handler(inputs, execution_config=None):
        return {"analysis": "done"}

    TaskRegistry.register(
        TaskDefinition(
            task_key="analyst",
            handler=mock_handler,
            description="Mock Analyst",
            # schema... (skip validation by mocking?)
        )
    )
    # Actually TaskRegistry validation might fail if we don't provide schema.
    # Let's hope Pydantic validation is lenient or we provide valid mock schema.
    # But wait, `task_def.input_schema` is used in `engine.py`.
    # Let's define a simple one.
    from pydantic import BaseModel
    class MockInput(BaseModel):
        history_text: str

    TaskRegistry.register(
        TaskDefinition(
            task_key="analyst",
            handler=mock_handler,
            description="Mock Analyst",
            input_schema=MockInput,
            output_schema=BaseModel
        )
    )

    try:
        final_state = await engine.execute_workflow(wf_def, initial_input)

        ctx = final_state.get("context_variables", {})
        metrics = ctx.get("audit_metrics")

        if metrics:
            print("SUCCESS: Found audit_metrics!")
            print(metrics)
        else:
            print("FAILURE: audit_metrics MISSING.")

    except Exception:
        logger.exception("Execution Failed")

if __name__ == "__main__":
    asyncio.run(run_test())
