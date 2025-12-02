import os
import sys
import pytest
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force Mock Configuration
os.environ["USE_MOCK_LLM"] = "True"
os.environ["USE_MOCK_DB"] = "True"

from backend.engine import WorkflowEngine
from backend.config import get_db_path

def test_mock_workflow_execution():
    """
    Verifies that a workflow can run end-to-end using the Mock LLM and Mock DB.
    """
    print("\n--- Starting Mock Workflow Test ---")
    
    # 1. Initialize Engine (should pick up Mock DB)
    engine = WorkflowEngine(get_db_path())
    print(f"Using DB: {engine.db_path}")
    assert "db_mock.json" in engine.db_path
    
    # 2. Get the Main Workflow
    # Assuming 'WORKFLOW_MAIN' exists in seed data
    workflow = engine.workflows_table.get(doc_id=1) # Or query by name/ID
    if not workflow:
        # Fallback: Create a simple test workflow if main is missing
        print("Main workflow not found, creating test workflow.")
        workflow_id = engine.create_workflow("Test Mock Workflow", [
            {"id": "STEP_1_GUARD", "component": "GuardAgent"},
            {"id": "STEP_2_ANALYST", "component": "AnalystAgent"}
        ])
    else:
        workflow_id = workflow.doc_id
        print(f"Found workflow: {workflow['name']} (ID: {workflow_id})")

    # 3. Create Execution
    inputs = {
        "history_text": "Test History",
        "product_text": "Test Product",
        "reflection_text": "Test Reflection"
    }
    execution_id = engine.create_execution(workflow_id, inputs)
    print(f"Created Execution ID: {execution_id}")
    
    # 4. Run Execution
    try:
        engine.run_execution(execution_id)
    except Exception as e:
        pytest.fail(f"Execution failed: {e}")

    # 5. Verify Results
    status = engine.get_execution_status(execution_id)
    print(f"Execution Status: {status['status']}")
    
    assert status['status'] == 'COMPLETED'
    assert 'result' in status
    result = status['result']
    
    # Check for mock data signatures
    # Guard Agent should produce 'safe_data'
    assert 'safe_data' in result or 'data' in result
    
    # Analyst Agent should produce 'todistuskartta' (if included in workflow)
    # Check step results
    step_results = status.get('step_results', [])
    assert len(step_results) > 0
    
    print("Test Passed: Workflow completed successfully with mock data.")

if __name__ == "__main__":
    test_mock_workflow_execution()
