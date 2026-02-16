import asyncio
import json
import logging
import uuid

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports
try:
    from pydantic import BaseModel

    from backend.core.engine import GraphEngine
    from backend.core.registry import TaskDefinition, TaskRegistry
    from backend.models.state import WorkflowState
    from backend.models.workflow import WorkflowDefinition, WorkflowStep
except ImportError as e:
    logger.error(f"Import Error: {e}")
    exit(1)

async def run_integration_test():
    logger.info("Starting Integration Test for Metrics...")

    # 1. Load Workflow Definition from Seed Data (or Mock it to match)
    # To be sure, let's construct a definition that matches strict schema
    # We use step_analyst configuration exactly as in seed_data

    step_analyst = WorkflowStep(
        id="step_analyst",
        task_key="analyst",
        config={
            "pre_hooks": ["calculate_text_metrics", "calculate_control_ratio"],
            # "model": "gpt-4o" # Optional
        },
        inputs={
            "history_text": "$inputs.history_text",
            "product_text": "$inputs.product_text",
            "reflection_text": "$inputs.reflection_text"
        }
    )

    wf_def = WorkflowDefinition(
        id="test_workflow_metrics",
        name="Test Workflow",
        description="Integration Test for Metrics",
        steps=[step_analyst],
        ui_schema={}
    )

    # 2. Mock the Analyst Task (to avoid calling real LLM)
    class AnalystInput(BaseModel):
        history_text: str | None = None
        product_text: str | None = None
        reflection_text: str | None = None

    @TaskRegistry.register_task(
        name="analyst",
        input_schema=AnalystInput,
        output_schema=BaseModel,
        description="Mock Analyst"
    )
    async def mock_analyst_handler(inputs: AnalystInput, execution_config=None):
        logger.info(f"Mock Analyst Running with inputs: {inputs}")
        return {"analysis": "Mock analysis complete."}

    # 3. Prepare Inputs
    repo_inputs = {
        "inputs": {
            "history_text": "User: This is a test.\nAI: Indeed it is.",
            "product_text": "Product sample.",
            "reflection_text": "Reflection sample."
        }
    }

    # 4. Execute
    engine = GraphEngine()
    try:
        final_state_dict = await engine.execute_workflow(
            definition=wf_def,
            initial_input=repo_inputs,
            execution_id=str(uuid.uuid4())
        )

        # 5. Verify Metrics
        # GraphEngine returns dict dump of state
        ctx = final_state_dict.get("context_variables", {})
        metrics = ctx.get("audit_metrics")

        if metrics:
            logger.info("SUCCESS: Audit Metrics Found!")
            logger.info(json.dumps(metrics, indent=2))
        else:
            logger.error("FAILURE: Audit Metrics MISSING in final state.")
            logger.error(f"Context Variables Keys: {list(ctx.keys())}")

    except Exception as e:
        logger.error(f"Execution Failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_integration_test())
