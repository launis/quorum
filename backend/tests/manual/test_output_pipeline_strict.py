
import logging
import sys
from typing import Any
from backend.models.state import WorkflowState, TraceEvent
from backend.models.domain.guard import GuardOutput
from backend.models.domain.xai import XAIOutput
from pydantic import ValidationError

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestOutputPipeline")

def test_strict_accessors():
    logger.info("--- Testing Strict Accessors in WorkflowState ---")

    # 1. Create Empty State
    state = WorkflowState(workflow_id="test_pipeline")
    
    # 2. Test Step Access (Should be None initially)
    print(f"Initial Step Guard: {state.step_guard}")
    assert state.step_guard is None

    # 3. Inject Valid Data (Simulate GraphEngine)
    valid_guard_data = {
        "thought_process": "Input is safe.",
        "conclusion": "Safe",
        "confidence_score": 0.99,
        "security_check": {
            "threat_detected": False,
            "risk_level": "RISK_LOW",
            "risk_score": 1.0,
            "simulation_score": 1.0,
            "simulation_result": "SIM_PASSIVE",
            "anonymized": False,
            "pii_findings": []
        },
        "tainted_data": {
            "chat_history": "clean",
            "product_text": "clean",
            "reflection_text": "clean",
            "safe_data": "clean"
        },
        "metadata": {
            "luontiaika": "2026-02-19T10:00:00Z",
            "muokkausaika": "2026-02-19T10:00:00Z",
            "versio": "1.0",
            "validoija": "system",
            "laatu_pisteet": 0.0,
            "agentti": "step_guard",
            "suoritus_ymparisto": "test"
        },
        "semanttinen_tarkistussumma": "mock_hash"
    }
    
    state.context_variables["step_guard"] = valid_guard_data
    
    # 4. Test Inflation
    guard_output = state.step_guard
    print(f"Inflated Guard Output: {type(guard_output)}")
    assert isinstance(guard_output, GuardOutput)
    assert guard_output.conclusion == "Safe"

    # 5. Inject Invalid Data (Fail Fast Test)
    invalid_data = {
        "is_safe": "maybe", # Should be bool
        "tainted_data": "None" # Should be list or None
    }
    state.context_variables["step_guard"] = invalid_data
    
    # Expect ValidationError or None (depending on pydantic_utils implementation)
    # Mandate says: pydantic_utils.inflate returns None on error and logs it.
    # Let's verify behavior.
    result = state.step_guard
    print(f"Invalid Data Result: {result}")
    
    if result is None:
        logger.info("SUCCESS: Invalid data returned None (Fail Safe for Read/Write split).")
    else:
        logger.error(f"FAILURE: Invalid data resulted in {type(result)}")

    logger.info("--- Test Complete ---")

if __name__ == "__main__":
    try:
        test_strict_accessors()
    except Exception as e:
        logger.error(f"Test Failed: {e}")
        sys.exit(1)
