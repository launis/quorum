
import logging
import os
from backend.models.state import WorkflowState
from backend.hooks.scoring import enforce_passivity_penalty

# Configure logging to match system
logging.basicConfig(
    filename='backend_debug.log',
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_passivity_penalty():
    print("--- Test 1: Penalty Application ---")
    
    # Mock State with Triggering Data
    state = WorkflowState(
        workflow_id="test_wf",
        context_variables={
            "step_judge": {
                "scale_min": 1.0,
                "scale_max": 4.0,
                "total_score": 3.8,  # High score, should be capped
                "dimensions": [
                    {"dimension_id": "dim1", "score": 1.0}, # Passenger!
                    {"dimension_id": "dim2", "score": 4.0}
                ],
                "critical_findings": []
            }
        }
    )

    # Expected Cap: 1.0 + (3.0 / 3.0) = 2.0
    new_state = enforce_passivity_penalty(state, "step_judge")
    
    result = new_state.context_variables["step_judge"]
    final_score = result["total_score"]
    
    print(f"Original Score: 3.8")
    print(f"Final Score: {final_score}")
    
    if abs(final_score - 2.0) < 0.01:
        print("PASS: Score capped at 2.0")
    else:
        print(f"FAIL: Score {final_score} != 2.0")

    # Verify Findings
    findings = result["critical_findings"]
    if any("PASSIVENESS_CUTTER_ACTIVATED" in f for f in findings):
         print("PASS: Critical finding added.")
    else:
         print(f"FAIL: Findings missing. Got: {findings}")

def test_strict_validation():
    print("\n--- Test 2: Strict Validation (Missing Scale) ---")
    state = WorkflowState(
        workflow_id="test_wf",
        context_variables={
            "step_judge": {
                # scale_min MISSING
                "scale_max": 4.0,
                "dimensions": []
            }
        }
    )
    
    try:
        enforce_passivity_penalty(state, "step_judge")
        print("FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"PASS: Caught expected error: {e}")

def verify_logs():
    print("\n--- Test 3: Log Verification ---")
    try:
        with open("backend_debug.log", "r") as f:
            content = f.read()
            if "Enforcing Passiveness Penalty on step_judge" in content:
                print("PASS: Log entry found.")
            else:
                print("FAIL: Log entry NOT found.")
    except Exception as e:
        print(f"FAIL: Could not read log file: {e}")

if __name__ == "__main__":
    # Clear log first for clean test
    try:
        open("backend_debug.log", "w").close()
    except:
        pass

    test_passivity_penalty()
    test_strict_validation()
    verify_logs()
