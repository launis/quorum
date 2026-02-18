
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
import uuid

from pydantic import BaseModel, Field

from backend.core.engine import GraphEngine
from backend.models.workflow import WorkflowDefinition, WorkflowStep
from backend.models.state import WorkflowState, TraceEvent
from backend.models.domain.inputs import WorkflowInputs
from backend.exceptions import AppException, ErrorCodes, WorkflowExecutionError

# --- Mock Models for Typed retrieval ---
class MockInputModel(BaseModel):
    field_a: str
    field_b: int

class MockOutputModel(BaseModel):
    result: str
    score: float

# --- Test Data Fixtures ---

@pytest.fixture
def simple_workflow_def():
    return WorkflowDefinition(
        id="test_flow",
        name="Test Workflow",
        description="A simple mock workflow",
        steps=[
            WorkflowStep(
                id="step_1",
                task_key="mock_task_1",
                inputs={"data": "$inputs.history_text"}
            ),
            WorkflowStep(
                id="step_2",
                task_key="mock_task_2",
                inputs={"prev_result": "$step_1.result"}
            )
        ]
    )

@pytest.fixture
def engine():
    return GraphEngine()

# --- Unit Tests: State & Inputs ---

@pytest.mark.asyncio
async def test_01_initial_state_inflation(engine, simple_workflow_def):
    """Verify state initialization and input inflation."""
    
    # Valid Inputs
    valid_payload = {
        "inputs": {
            "history_text": "History",
            "organization_id": "org-123"
        },
        "extra_context": "foo"
    }

    # We can't call execute_workflow directly easily without mocking everything, 
    # but we can test the logic if we extract it, or just run execute with mocks.
    # Let's run execute with a mocked registry to let it pass the init phase.

    with patch("backend.core.registry.TaskRegistry.get") as mock_get:
        # We assume immediate stop to just test init? 
        # Actually GraphEngine initializes state inside execute_workflow.
        # So we must let it run at least until first step.
        
        # Mock Task 1 to allow execution
        mock_task = MagicMock()
        mock_task.input_schema = MockInputModel # Dummy
        mock_task.handler = AsyncMock(return_value={"result": "pass"})
        mock_get.return_value = mock_task

        # Override step 1 inputs to match MockInputModel
        def_copy = simple_workflow_def.model_copy(update={
            "steps": [
                WorkflowStep(
                    id="step_1", 
                    task_key="mock_task_1", 
                    inputs={"field_a": "A", "field_b": "1"} # Static values as strings
                )
            ]
        })

        # Exec
        result = await engine.execute_workflow(def_copy, valid_payload)
        
        # Assertions
        assert result["status"] == "completed"
        assert result["workflow_id"] == "test_flow"
        # inputs should be inflated and then dumped back to dict
        ctx = result["context_variables"]
        # Since execute_workflow returns model_dump, inputs is now a dict
        assert isinstance(ctx["inputs"], dict)
        # ChatLogParser adds "User: " prefix if missing and it thinks it's a single message
        assert ctx["inputs"]["history_text"] == "User: History"
        assert ctx["inputs"]["organization_id"] == "org-123"
        # extra context preserved
        assert ctx["extra_context"] == "foo"

@pytest.mark.asyncio
async def test_02_input_inflation_failure(engine, simple_workflow_def):
    """Verify that invalid input structure raises 400."""
    
    # GraphEngine.execute_workflow -> inflate(inputs) handling.
    # We'll pass something that causes inflation issues? 
    # WorkflowInputs is pretty permissive (optional fields), but let's try passing a list instead of dict.
    
    invalid_payload = {
        "inputs": ["not", "a", "dict"] 
    }

    with pytest.raises(AppException) as excinfo:
        await engine.execute_workflow(simple_workflow_def, invalid_payload)
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.error_code == ErrorCodes.INVALID_JSON_PAYLOAD

# --- Unit Tests: Dependencies & Resolution ---

def test_resolve_inputs_strict(engine):
    """Test _resolve_inputs logic strictly."""
    
    # Setup State
    state = WorkflowState(
        workflow_id="test",
        context_variables={
            "inputs": WorkflowInputs(history_text="Official History"),
            "step_1": {"nested": {"val": 42}},
            "step_typed": MockOutputModel(result="Success", score=0.9)
        }
    )

    # 1. Simple Mapping
    mapping = {"text": "$inputs.history_text"}
    res = engine._resolve_inputs(mapping, state)
    assert res["text"] == "Official History"

    # 2. Nested Dict Mapping
    mapping = {"num": "$step_1.nested.val"}
    res = engine._resolve_inputs(mapping, state)
    assert res["num"] == 42

    # 3. Model Attribute Mapping
    mapping = {"sc": "$step_typed.score"}
    res = engine._resolve_inputs(mapping, state)
    assert res["sc"] == 0.9

    # 4. Strict Typed Retrieval (Whole Object)
    # Target field expects MockOutputModel
    class ConsumerModel(BaseModel):
        source: MockOutputModel

    # Engine needs input_schema to do strict typed retrieval
    mapping = {"source": "$step_typed"} # Maps root to root
    res = engine._resolve_inputs(mapping, state, input_schema=ConsumerModel)
    assert isinstance(res["source"], MockOutputModel)
    assert res["source"].result == "Success"

# --- Integration Tests: Execution Flow ---

@pytest.mark.asyncio
async def test_03_execute_workflow_success(engine, simple_workflow_def):
    """Full execution of a 2-step workflow."""
    
    with patch("backend.core.registry.TaskRegistry.get") as mock_get:
        # Mock Task 1
        task1 = MagicMock()
        class Input1(BaseModel):
            data: str
        task1.input_schema = Input1
        task1.handler = AsyncMock(return_value={"result": "step1_data", "reasoning": "thought1"})
        
        # Mock Task 2
        task2 = MagicMock()
        class Input2(BaseModel):
            prev_result: str
        task2.input_schema = Input2
        task2.handler = AsyncMock(return_value={"final": "done", "reasoning": "thought2"})

        # Registry Logic
        def get_task(key):
            if key == "mock_task_1": return task1
            if key == "mock_task_2": return task2
            return None
        mock_get.side_effect = get_task

        # Input Payload
        payload = {"inputs": {"history_text": "Start"}}

        # Execute
        final_state_dump = await engine.execute_workflow(simple_workflow_def, payload)
        
        # Verify State
        assert final_state_dump["status"] == "completed"
        trace = final_state_dump["execution_trace"]
        assert len(trace) == 2
        
        # Step 1 Event
        e1 = trace[0]
        assert e1["step_name"] == "step_1"
        assert e1["content"] == {"result": "step1_data"} # Reasoning popped
        assert e1["reasoning"]["thought_process"] == "thought1"

        # Step 2 Event
        e2 = trace[1]
        assert e2["step_name"] == "step_2"
        assert e2["content"] == {"final": "done"}
        assert e2["reasoning"]["thought_process"] == "thought2"

        # Verify Context Variables
        cv = final_state_dump["context_variables"]
        assert cv["step_1"]["result"] == "step1_data"
        assert cv["step_2"]["final"] == "done"

@pytest.mark.asyncio
async def test_04_execute_fail_fast_validation(engine, simple_workflow_def):
    """Verify execution stops if input validation fails."""
    
    with patch("backend.core.registry.TaskRegistry.get") as mock_get:
        # Mock Task 1 expecting Integer, but we pass String
        task1 = MagicMock()
        class IntInput(BaseModel):
            idx: int
        task1.input_schema = IntInput
        
        mock_get.return_value = task1

        # Def mapping matches input schema
        bad_def = simple_workflow_def.model_copy(update={
            "steps": [
                 WorkflowStep(
                    id="step_1", 
                    task_key="mock_task_1", 
                    inputs={"idx": "NOT_AN_INT"} # Static string
                )
            ]
        })

        with pytest.raises(AppException) as exc:
            await engine.execute_workflow(bad_def, {"inputs": {}})
        
        assert exc.value.status_code == 400
        assert exc.value.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED

@pytest.mark.asyncio
async def test_05_execute_task_not_found(engine, simple_workflow_def):
    """Verify 404 if task key missing from registry."""
    
    with patch("backend.core.registry.TaskRegistry.get", return_value=None):
        with pytest.raises(AppException) as exc:
            await engine.execute_workflow(simple_workflow_def, {"inputs": {}})
        
        assert exc.value.status_code == 404
        assert exc.value.error_code == ErrorCodes.TASK_NOT_FOUND

@pytest.mark.asyncio
async def test_06_halting_signal(engine, simple_workflow_def):
    """Verify execution stops when finding stop_execution=True."""
    
    with patch("backend.core.registry.TaskRegistry.get") as mock_get:
        # Task 1 returns stop signal
        task1 = MagicMock()
        task1.input_schema = MockInputModel # irrelevant, we overwrite inputs
        task1.handler = AsyncMock(return_value={"stop_execution": True, "reason": "guard triggered"})
        
        mock_get.return_value = task1

        # Just 1 step needed to test halt, but let's keep 2 to prove 2nd didn't run
        def_halt = simple_workflow_def.model_copy(update={
             "steps": [
                WorkflowStep(
                    id="step_1", 
                    task_key="mock_task_1", 
                    inputs={"field_a": "x", "field_b": "1"}
                ),
                WorkflowStep(
                    id="step_2", 
                    task_key="mock_task_2", # Should not run
                    inputs={}
                )
            ]
        })

        final_state = await engine.execute_workflow(def_halt, {"inputs": {}})
        
        assert final_state["status"] == "stopped"
        trace = final_state["execution_trace"]
        assert len(trace) == 1
        assert trace[0]["step_name"] == "step_1"
        # content has stop signal
        assert trace[0]["content"]["stop_execution"] is True

@pytest.mark.asyncio
async def test_07_hook_execution(engine):
    """Verify hooks are mapped and executed."""
    
    # We define a workflow with pre_hooks
    wf = WorkflowDefinition(
        id="hook_test",
        name="Hook Test",
        description="Testing hooks",
        steps=[
            WorkflowStep(
                id="step_h",
                task_key="mock_task",
                config={"pre_hooks": ["mock_hook"]} # Configured hook
            )
        ]
    )

    # Patch HOOK_MAPPING to include our mock
    with patch.dict("backend.core.engine.HOOK_MAPPING", {"mock_hook": ("tests.test_workflow_engine_comprehensive", "mock_hook_func")}):
        with patch("backend.core.registry.TaskRegistry.get") as mock_get:
            
            # Task Mock
            task = MagicMock()
            task.input_schema = BaseModel
            # Task Mock
            task = MagicMock()
            class MockSchema(BaseModel):
                pass
            task.input_schema = MockSchema
            task.handler = AsyncMock(return_value={"ok": True})
            mock_get.return_value = task

            # We need to ensure importlib imports this module to find the func
            # But the mapping points to "tests.test_workflow_engine_comprehensive"
            # So we must mock importlib or define the func here.
            
            # The engine uses: module = importlib.import_module(module_path)
            # func = getattr(module, func_name)
            
            # It's easier to mock _execute_hook directly? 
            # OR patch importlib.
            
            # Let's mock _execute_hook method of the engine instance to verify call
            with patch.object(engine, '_execute_hook', side_effect=engine._execute_hook) as spy_hook:
                 # But we need the ACTUAL execution to work or fail.
                 # Let's mock importlib.import_module 
                 
                 mock_module = MagicMock()
                 # Define the hook function
                 mock_hook_fn = MagicMock(return_value=WorkflowState(workflow_id="hooked", context_variables={"hook_ran": True}))
                 mock_module.mock_hook_func = mock_hook_fn

                 with patch("importlib.import_module", return_value=mock_module):
                      result = await engine.execute_workflow(wf, {"inputs": {}})
                      
                      # Assertions
                      # State passed to task should have hook_ran=True?
                      # engine execution_state is updated by hooks.
                      # Since we mocked hook return to replace state...
                      assert result["context_variables"].get("hook_ran") is True
