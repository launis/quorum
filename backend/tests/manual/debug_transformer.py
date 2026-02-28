import os
import sys

# Ensure cwd is in path
sys.path.append(os.getcwd())

from backend.api.transformers.report_transformer import ReportTransformer
from backend.models.state import WorkflowState

try:
    print("Testing Fail Fast...")
    import uuid

    from backend.models.domain.execution import ExecutionRecord
    state = WorkflowState(workflow_id="fail_test", execution_id=uuid.uuid4())
    record = ExecutionRecord(id=str(state.execution_id), results=state, status="failed")
    ReportTransformer().transform(record)
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
