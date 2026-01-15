
import sys
import os

sys.path.append(os.getcwd())

# Mock env
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "true"

from backend.models.domain import TodistusKartta, Hypoteesi, RagTodiste, Metadata
from backend.models.state import WorkflowState, InputData, TaintedData
from backend.llm.mock_data import MOCK_ANALYST_OUTPUT

try:
    print("1. Validating MOCK_ANALYST_OUTPUT directly...")
    # This should pass if mock object is valid
    print(f"Mock Object: {type(MOCK_ANALYST_OUTPUT)}")
    
    # Check fields
    if hasattr(MOCK_ANALYST_OUTPUT, "rag_todisteet"):
        print(f"rag_todisteet present: {len(MOCK_ANALYST_OUTPUT.rag_todisteet)}")
    else:
        print("rag_todisteet MISSING on mock object!")

    print("\n2. Creating WorkflowState...")
    state = WorkflowState(
        execution_id="test_exec",
        inputs=InputData(
            history_text="test",
            product_text="test",
            reflection_text="test"
        )
    )
    
    print("\n3. Assigning step_analyst...")
    # This mimics BaseAgent._update_state
    state.step_analyst = MOCK_ANALYST_OUTPUT
    print("Assignment SUCCESS!")
    
    print("\n4. Checking validation assignment...")
    try:
        state.step_analyst = MOCK_ANALYST_OUTPUT.model_copy(deep=True)
        print("Deep copy assignment SUCCESS!")
    except Exception as e:
        print(f"Deep copy assignment FAILED: {e}")
        raise e

except Exception as e:
    print(f"\nCRASH: {e}")
