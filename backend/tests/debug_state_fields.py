from backend.models.state import WorkflowState, InputData
from backend.models.domain import XAIReport
import logging

try:
    # 1. Try initializing with extra field
    data = InputData(history_text="", product_text="", reflection_text="")
    
    try:
        ws = WorkflowState(
            execution_id="test",
            inputs=data,
            step_xai={"some": "data"} 
        )
        print("DEBUG: Initialized WorkflowState with step_xai kwarg.")
        print(f"DEBUG: Has 'step_xai' attribute? {hasattr(ws, 'step_xai')}")
        if hasattr(ws, 'step_xai'):
             print(f"DEBUG: step_xai value: {ws.step_xai}")
    except Exception as e:
        print(f"DEBUG: Failed to init with step_xai: {e}")

    # 2. Try initializing with step_reporter
    try:
        ws_rep = WorkflowState(
            execution_id="test",
            inputs=data,
            step_reporter={"some": "data"}
        )
        print("DEBUG: Initialized with step_reporter.")
    except Exception as e:
        print(f"DEBUG: Failed to init with step_reporter: {e}")

except Exception as main_e:
    print(f"DEBUG: Critical Failure: {main_e}")
