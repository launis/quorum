import logging
import os
import sys

# Redirect stdout/stderr to file for reliable capture
log_file = os.path.join(os.path.dirname(__file__), "test_output.txt")
sys.stdout = open(log_file, "w", encoding="utf-8")
sys.stderr = sys.stdout

print(f"--- TEST START: {os.path.abspath(__file__)} ---")

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(root_dir)
print(f"Added to sys.path: {root_dir}")

try:
    from backend.exceptions import AppException
    from backend.hooks.reporting import generate_report
    from backend.hooks.scoring import apply_scoring_logic
    from backend.models.state import WorkflowState

    print("Imports successful.")
except Exception as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

# Configure logging to capture output
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("fail_fast_test")


def test_scoring_fail_fast():
    print("\n--- Testing ScoringHook Fail Fast ---")
    # specific empty state (no judge)
    state = WorkflowState(workflow_id="test-scoring-fail", context_variables={})

    try:
        apply_scoring_logic(state)
        print("❌ FAILED: callback swallowed error! Expected crash.")
        return False
    except AppException as e:
        if e.error_code == "SCORING_MISSING_JUDGE_OUTPUT":
            print(f"✅ PASSED: Caught expected error: {e.error_code}")
            return True
        else:
            print(f"❌ FAILED: Caught wrong error code: {e.error_code}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Caught wrong exception type: {type(e)}")
        # Print traceback for debugging
        import traceback

        traceback.print_exc()
        return False


def test_reporting_fail_fast():
    print("\n--- Testing ReportingHook Fail Fast ---")
    # specific invalid context (missing required fields for ReportContext)

    mock_xai = {"some_data": "value"}  # minimal to pass first check
    state = WorkflowState(workflow_id="test-reporting-fail", context_variables={"step_xai": mock_xai})

    try:
        generate_report(state)
        print("❌ FAILED: callback swallowed error! Expected crash.")
        return False
    except AppException as e:
        if e.error_code == "REPORT_GENERATION_FAILED":
            print(f"✅ PASSED: Caught expected error: {e.error_code}")
            return True
        else:
            print(f"❌ FAILED: Caught wrong error code: {e.error_code}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Caught wrong exception type: {type(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True
    if not test_scoring_fail_fast():
        success = False
    if not test_reporting_fail_fast():
        success = False

    if success:
        print("\n🎉 ALL TESTS PASSED: Fail Fast Architecture Verified.")
        sys.exit(0)
    else:
        print("\n💥 TESTS FAILED.")
        sys.exit(1)
