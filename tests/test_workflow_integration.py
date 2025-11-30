import os
import time
import requests
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
WORKFLOW_ID = "WORKFLOW_MAIN"
SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "scenarios", "workflow")

def wait_for_backend(base_url: str, timeout: int = 60):
    """Polls the backend health endpoint until it returns 200 or timeout."""
    health_url = f"{base_url}/health"
    print(f"[TEST] Waiting for backend at {health_url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print("[TEST] Backend is ready!")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    pytest.fail(f"Backend not ready at {base_url} after {timeout} seconds.")

def test_full_workflow_execution():
    """
    Tests the full workflow execution using PDF files from tests/scenarios/workflow.
    Supports running against local or cloud API via API_BASE_URL.
    """
    # 0. Ensure Backend is Ready
    wait_for_backend(API_BASE_URL)

    print(f"\n[TEST] Running full workflow test against: {API_BASE_URL}")
    
    # 1. Prepare Files
    history_path = os.path.join(SCENARIOS_DIR, "keskusteluhistoria SITRA.pdf")
    product_path = os.path.join(SCENARIOS_DIR, "lopputuote sitra.pdf")
    reflection_path = os.path.join(SCENARIOS_DIR, "Reflektiodokumentti sitra.pdf")
    
    # Verify files exist
    assert os.path.exists(history_path), f"History file not found: {history_path}"
    assert os.path.exists(product_path), f"Product file not found: {product_path}"
    assert os.path.exists(reflection_path), f"Reflection file not found: {reflection_path}"
    
    files = {
        'history_file': ('keskusteluhistoria SITRA.pdf', open(history_path, 'rb'), 'application/pdf'),
        'product_file': ('lopputuote sitra.pdf', open(product_path, 'rb'), 'application/pdf'),
        'reflection_file': ('Reflektiodokumentti sitra.pdf', open(reflection_path, 'rb'), 'application/pdf')
    }
    
    # 2. Start Workflow
    start_url = f"{API_BASE_URL}/orchestrator/run"
    params = {"workflow_id": WORKFLOW_ID}
    
    print(f"[TEST] Sending request to {start_url}...")
    try:
        response = requests.post(start_url, params=params, files=files)
        response.raise_for_status()
        data = response.json()
        execution_id = data.get("execution_id")
        print(f"[TEST] Workflow started. Execution ID: {execution_id}")
        assert execution_id is not None, "Execution ID not returned"
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to start workflow: {e}")
    finally:
        # Close files
        for f in files.values():
            f[1].close()

    # 3. Poll for Completion
    status_url = f"{API_BASE_URL}/orchestrator/status/{execution_id}"
    max_retries = 60 # 60 * 5s = 5 minutes timeout
    
    for i in range(max_retries):
        try:
            status_res = requests.get(status_url)
            status_res.raise_for_status()
            status_data = status_res.json()
            status = status_data.get("status")
            
            print(f"[TEST] Polling status ({i+1}/{max_retries}): {status}")
            
            if status == "COMPLETED":
                print("[TEST] Workflow completed successfully!")
                result = status_data.get("result", {})
                
                # Basic Validation
                assert result is not None, "Result is empty"
                assert "xai_report" in result or "report_content" in result, "XAI Report not found in result"
                
                # Check for timestamp injection (if visible in report or metadata)
                # Note: We might not see the raw metadata in the final report text easily, 
                # but we can check if the report content is substantial.
                report_content = result.get("xai_report") or result.get("report_content")
                assert len(report_content) > 100, "Report content is suspiciously short"
                
                return # Success
                
            elif status == "FAILED":
                error_msg = status_data.get("error", "Unknown error")
                pytest.fail(f"Workflow failed: {error_msg}")
                
            time.sleep(5)
            
        except requests.exceptions.RequestException as e:
            print(f"[TEST] Warning: Status poll failed: {e}")
            time.sleep(5)
            
    pytest.fail("Workflow execution timed out.")

if __name__ == "__main__":
    # Allow running directly with python
    test_full_workflow_execution()
