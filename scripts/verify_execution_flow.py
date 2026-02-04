
import json
import logging
import os
import sys
import time

# Ensure backend in path
sys.path.append(os.getcwd())

# Mock keys to avoid errors if they are checked
os.environ["OPENAI_API_KEY"] = "mock-key"
os.environ["GOOGLE_API_KEY"] = "mock-key"
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "true"
os.environ["STORAGE_BACKEND"] = "LOCAL"

from fastapi.testclient import TestClient

from backend.main import app

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_execution(client):
    logger.info("Starting Verification of POST /executions...")

    # 1. Get Authentication Token
    headers = {"Authorization": "Bearer mock-token:root_master"}

    # 2. List Workflows to find a valid ID
    logger.info("Fetching workflows...")
    try:
        resp = client.get("/builder/workflows", headers=headers)
        if resp.status_code != 200:
            logger.error(f"Failed to list workflows: {resp.status_code} - {resp.text}")
            return

        workflows = resp.json()
        if not workflows:
            logger.error("No workflows found in Mock DB. Seeding might be needed.")
            workflow_id = "fused_audit_chain_dual"
        else:
            target_wf = next((w for w in workflows if "fused" in w.get("id", "").lower()), workflows[0])
            workflow_id = target_wf["id"]

        logger.info(f"Selected Workflow: {workflow_id}")

        # 3. Prepare Payload
        inputs = {
            "history_text": "Mock history content",
            "product_text": "Mock product content",
            "reflection_text": "Mock reflection content"
        }

        json_payload = json.dumps({
            "workflowId": workflow_id,
            "inputs": inputs
        })

        files = {
            "dummy": ("dummy.txt", b"content", "text/plain")
        }

        data = {
            "json_payload": json_payload
        }

        # 4. Execute
        logger.info(f"Sending POST /executions with workflowId={workflow_id}...")
        resp = client.post(
            "/executions",
            data=data,
            files=files,
            headers=headers
        )

        execution_id = None
        if resp.status_code == 201:
            logger.info(f"SUCCESS: Workflow '{workflow_id}' execution started.")
            res_json = resp.json()
            execution_id = res_json.get("execution_id")
            logger.info(f"Execution ID: {execution_id}")
        else:
            logger.error(f"FAILURE: {resp.status_code} - {resp.text}")
            return

        # 5. Poll for Completion
        if execution_id:
            logger.info(f"Polling for completion of execution {execution_id}...")
            for i in range(20):
                time.sleep(1)
                check = client.get(f"/executions/{execution_id}", headers=headers)
                if check.status_code == 200:
                    status = check.json().get("status")
                    logger.info(f"Poll {i+1}: Status = {status}")
                    if status in ["completed", "failed"]:
                        break
            else:
                logger.warning("Polling timed out.")

    except Exception as e:
        logger.error(f"Verification crashed: {e}", exc_info=True)

if __name__ == "__main__":
    with TestClient(app) as client:
        verify_execution(client)
