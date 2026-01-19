from backend.models.state import WorkflowState, InputData
from backend.models.domain import XAIReport
import sys

print("START_DEBUG")
try:
    data = InputData(history_text="", product_text="", reflection_text="")
    ws = WorkflowState(
        execution_id="test",
        inputs=data,
        step_xai={"foo": "bar"}
    )
    if hasattr(ws, 'step_xai'):
        print("HAS_STEP_XAI: YES")
        print(f"VAL: {ws.step_xai}")
    else:
        print("HAS_STEP_XAI: NO")

except Exception as e:
    print(f"ERROR: {e}")
print("END_DEBUG")
