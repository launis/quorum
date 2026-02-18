
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import BaseModel, Field

from backend.core.engine import GraphEngine
from backend.models.workflow import WorkflowDefinition, WorkflowStep
from backend.models.state import WorkflowState
from backend.models.domain.inputs import WorkflowInputs

class Step1Output(BaseModel):
    summary: str
    score: float

class Step2Input(BaseModel):
    previous_summary: str
    original_input: str

class Step2Output(BaseModel):
    final_verdict: str

@pytest.mark.asyncio
async def test_data_flow_integrity():
    """
    Verifies that data flows correctly from Inputs -> Step 1 -> Step 2.
    Ensures no data loss or corruption during state transitions.
    """
    engine = GraphEngine()

    # Define Workflow
    wf_def = WorkflowDefinition(
        id="flow_integrity_test",
        name="Data Flow Test",
        description="Verifies variable resolution",
        steps=[
            # Step 1: Takes raw input, produces structured output
            WorkflowStep(
                id="step_1",
                task_key="task_1",
                inputs={
                    "text": "$inputs.history_text"
                }
            ),
            # Step 2: Takes Step 1 output AND original input
            WorkflowStep(
                id="step_2",
                task_key="task_2",
                inputs={
                    "previous_summary": "$step_1.summary",
                    "original_input": "$inputs.history_text"
                }
            )
        ]
    )

    # Mock Task Registry
    with patch("backend.core.registry.TaskRegistry.get") as mock_get:
        
        # Task 1 Handler
        task1 = MagicMock()
        class Input1(BaseModel):
            text: str
        task1.input_schema = Input1
        # Returns specific data we want to trace
        task1.handler = AsyncMock(return_value={"summary": "Processed Data", "score": 0.95})
        
        # Task 2 Handler
        task2 = MagicMock()
        task2.input_schema = Step2Input
        # We verify inputs received here
        async def handler2(ctx, **kwargs):
            # Verify data inside the handler execution
            assert ctx.previous_summary == "Processed Data"
            assert ctx.original_input == "User: Original User Input"
            return {"final_verdict": "Verified"}
        
        task2.handler = AsyncMock(side_effect=handler2)

        def get_task(key):
            if key == "task_1": return task1
            if key == "task_2": return task2
            return None
        mock_get.side_effect = get_task

        # Execute
        payload = {"inputs": {"history_text": "Original User Input"}}
        final_state_dump = await engine.execute_workflow(wf_def, payload)
        
        # Verify Final State Persistence
        ctx = final_state_dump["context_variables"]
        
        # 1. Inputs Preserved (Note: ChatLogParser modifies inputs in place in strict mode)
        assert ctx["inputs"]["history_text"] == "User: Original User Input"
        
        # 2. Step 1 Output Preserved
        assert ctx["step_1"]["summary"] == "Processed Data"
        assert ctx["step_1"]["score"] == 0.95
        
        # 3. Step 2 Output Preserved
        assert ctx["step_2"]["final_verdict"] == "Verified"

        print("\nData Flow Verified Successfully:")
        print(f"  Inputs -> Step 1: {ctx['inputs']['history_text']} -> {ctx['step_1']['summary']}")
        print(f"  Step 1 -> Step 2: {ctx['step_1']['summary']} -> (Verified in Handler)")
