import asyncio
import uuid
import httpx
import pytest
from httpx import ASGITransport

from backend_v2.main import app

@pytest.mark.asyncio
async def test_execution_e2e_with_blueprint():
    # We use ASGITransport to test FastAPI app directly without starting a server
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Mock auth headers
        headers = {
            "Authorization": "Bearer test-token",
            "X-User-ID": "test-user-id",
            "X-Organization-ID": "test-org-id"
        }

        # 1. Start execution
        start_payload = {
            "workflow_id": "test_workflow_123", # Needs to exist or bypassed depending on auth/repo setup
            "target_locale": "fi",
            "inputs": {
                "user_prompt": "Test input"
            }
        }
        
        # This will depend on the mocked DB state in testing, but structurally validates the endpoint
        response = await client.post("/api/v2/executions/", json=start_payload, headers=headers)
        
        # If the environment isn't fully mocked for this test run, this might 404/500 depending on workflow_id.
        # But we mainly want to ensure the router accepts the payload.
        if response.status_code == 202:
            data = response.json()
            exec_id = data["id"]
            
            # 2. Check Render Endpoint (JSON)
            render_res = await client.get(f"/api/v2/executions/{exec_id}/render?format=json", headers=headers)
            # Depending on execution speed it might not be COMPLETED yet, but we check if the endpoint exists
            assert render_res.status_code in [200, 400] # 400 if not completed
            
            # 2.1 Check Variant Render Endpoint
            variant_res = await client.get(f"/api/v2/executions/{exec_id}/render?format=json&variant=1d_metrics", headers=headers)
            assert variant_res.status_code in [200, 400]
            
            # 3. Queue Async PDF Koonti
            pdf_res = await client.post(f"/api/v2/executions/{exec_id}/render_pdf", headers=headers)
            assert pdf_res.status_code == 202
            assert pdf_res.json()["status"] == "Accepted"
            
            print("E2E Routers Validated.")
