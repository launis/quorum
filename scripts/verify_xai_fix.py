
import json
import logging
import os
import sys
import time

from fastapi.testclient import TestClient

# Ensure backend in path
sys.path.append(os.getcwd())

# Mock Environment
os.environ["OPENAI_API_KEY"] = "mock-key"
os.environ["GOOGLE_API_KEY"] = "mock-key"
os.environ["GOOGLE_SEARCH_API_KEY"] = "mock-key"
os.environ["GOOGLE_SEARCH_CX"] = "mock-cx"
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "false"
os.environ["STORAGE_BACKEND"] = "LOCAL"

# Import app after env vars
# Import app and dependencies
from backend.dependencies import get_arq_pool
from backend.main import app


# Force Synchronous Mode (Bypass Arq)
async def mock_get_arq_pool():
    return None

app.dependency_overrides[get_arq_pool] = mock_get_arq_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_xai")

def verify_report_generation():
    with TestClient(app) as client:
        # 1. Start Workflow
        workflow_id = "sequential_audit_chain_dual"
        logger.info(f"Starting workflow '{workflow_id}'...")

        # DEBUG: List workflows first
        resp = client.get("/builder/workflows", headers={"Authorization": "Bearer mock-token:root_master"})
        if resp.status_code != 200:
             logger.error(f"Failed to list workflows: {resp.status_code}")
             print(f"RESPONSE ERROR (LIST): {resp.text}", flush=True)
             sys.exit(1)
        else:
             logger.info("Successfully listed workflows.")

        resp = client.post(
            "/executions",
            json={
                "workflowId": workflow_id,
                "inputs": {
                    "history_text": "Test History " * 20,
                    "product_text": "Test Product " * 20,
                    "reflection_text": "Test Reflection " * 20
                }
            },
            headers={"Authorization": "Bearer mock-token:root_master"}
        )

        if resp.status_code != 201:
            logger.error(f"Failed to start execution: {resp.status_code}")
            with open("verification_error.log", "w") as f:
                f.write(resp.text)
            sys.exit(1)

        if resp.status_code != 201:
            logger.error(f"Failed to start execution: {resp.status_code}")
            print(f"RESPONSE ERROR: {resp.text}", flush=True)
            sys.exit(1)

        execution_id = resp.json()["execution_id"]
        logger.info(f"Execution started: {execution_id}")

        # 2. Poll for Completion
        max_retries = 20
        for i in range(max_retries):
            time.sleep(1)
            status_resp = client.get(f"/executions/{execution_id}", headers={"Authorization": "Bearer mock-token:root_master"})
            state = status_resp.json()
            status = state.get("status")
            logger.info(f"Poll {i+1}: Status={status}")

            if status in ["completed", "failed"]:
                break
        else:
            logger.error("Timed out waiting for completion")
            sys.exit(1)

        with open("verification_state.json", "w") as f:
            json.dump(state, f, indent=2)

        if status == "failed":
            logger.error(f"Execution failed: {state.get('error')}")
            sys.exit(1)

        # 3. Verify Report Content
        results = state.get("result", {})

        # Check Top-Level Field (The Fix)
        # Result is WorkflowState dump, so we check context_variables
        context_vars = results.get("context_variables", {})
        report_top = context_vars.get("xai_report_formatted")

        # Check Nested Field (The Original)
        step_reporter = context_vars.get("step_reporter", {})
        report_nested = step_reporter.get("xai_report_formatted") if step_reporter else None

        logger.info(f"Top-Level Report: {'FOUND' if report_top else 'MISSING'}")
        logger.info(f"Nested Report:    {'FOUND' if report_nested else 'MISSING'}")

        if report_top and len(report_top) > 10:
            logger.info("SUCCESS: XAI Report is present in top-level state!")
            print("VERIFICATION_SUCCESS")
        else:
            logger.error("FAILURE: XAI Report is missing or empty.")
            print("VERIFICATION_FAILURE")
            sys.exit(1)

if __name__ == "__main__":
    import traceback
    try:
        verify_report_generation()
    except Exception:
        traceback.print_exc()
