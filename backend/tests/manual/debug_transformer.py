
import sys
import os

# Ensure cwd is in path
sys.path.append(os.getcwd())

from backend.models.state import WorkflowState
from backend.api.transformers.report_transformer import ReportTransformer
from backend.exceptions import AppException

try:
    print("Testing Fail Fast...")
    state = WorkflowState(workflow_id="fail_test")
    ReportTransformer.transform(state)
    print("Did not raise exception!")
    sys.exit(1)
except Exception as e:
    print(f"Caught exception type: {type(e)}")
    print(f"Caught exception message: {e}")
    if "Report generation pending or failed" in str(e):
        print("MATCH: Exception message correct.")
        sys.exit(0)
    else:
        print("NO MATCH: Exception message incorrect.")
        sys.exit(1)
