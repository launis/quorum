import json
import asyncio
import httpx
import sys
import os

API_URL = "http://127.0.0.1:8000/executions"

async def main():
    print("Loading input payload...")
    with open("backend_v2/tests/test_data/exe_c0bc_inputs.json", "r", encoding="utf-8") as f:
        raw_inputs = json.load(f)
    
    # Haetaan DB:stä viimeisin workflow_id (Epic 51 workflow)
    with open("data/db_v2.json", "r", encoding="utf-8") as f:
        db_data = json.load(f)
        workflows = db_data.get("workflows", {})
        if not workflows:
            workflow_id = "wf_d653170e174847559e08af42b938d826" # Fallback
        else:
            workflow_id = list(workflows.keys())[0]

    payload = {
        "workflow_id": workflow_id,
        "target_locale": "fi",
        "raw_inputs": raw_inputs
    }

    print(f"Triggering execution for Workflow {workflow_id}...")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(f"{API_URL}/", json=payload)
            response.raise_for_status()
            execution_record = response.json()
            execution_id = execution_record["id"]
            print(f"Execution started! ID: {execution_id}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to start execution: {e.response.text}")
            sys.exit(1)
        
        print("Connecting to SSE stream to monitor progress and verify SSE-Heartbeat...")
        
        # Listen to SSE
        async with client.stream("GET", f"{API_URL}/{execution_id}/stream", timeout=None) as stream:
            async for line in stream.aiter_lines():
                if not line.strip():
                    continue
                if line.startswith("data: "):
                    data_str = line[len("data: "):]
                    try:
                        record = json.loads(data_str)
                        status = record.get("status")
                        print(f"SSE Heartbeat received. Current status: {status}")
                        if status in ["COMPLETED", "FAILED"]:
                            print(f"\nExecution finished with status: {status}")
                            if status == "FAILED":
                                print(f"Error: {record.get('error')}")
                            
                            trace_path = record.get("execution_trace_storage_path")
                            print(f"Execution trace saved at: {trace_path}")
                            print(f"\nCommand to diff:\npython scratch/diff_executions.py {execution_id}")
                            break
                    except json.JSONDecodeError:
                        print(f"Received raw SSE line: {line}")

if __name__ == "__main__":
    asyncio.run(main())
