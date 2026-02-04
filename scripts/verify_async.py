
import asyncio
import sys

import aiohttp

BASE_URL = "http://localhost:8000"

async def main():
    print("--- Verifying Async Execution (Polling) ---")

    async with aiohttp.ClientSession() as session:
        # 1. Start Execution
        payload = {
            "workflowId": "sequential_audit_chain",
            "inputs": {"text": "Test input for async verification"}
        }

        print(f"POST /executions with payload: {payload}")
        async with session.post(f"{BASE_URL}/executions", json=payload) as resp:
            if resp.status != 201:
                print(f"FAILED to create execution: {resp.status} {await resp.text()}")
                return

            data = await resp.json()
            execution_id = data.get("execution_id") or data.get("id")
            print(f"Execution Created! ID: {execution_id}")
            print(f"Initial Status: {data.get('status')}") # Should be 'pending'

        if not execution_id:
            print("No Execution ID returned.")
            return

        # 2. Poll for Updates
        print("\n--- POLLING START ---")
        status = "pending"
        last_step = None

        while status not in ["completed", "failed"]:
            await asyncio.sleep(1.0) # Poll every 1s

            async with session.get(f"{BASE_URL}/executions/{execution_id}") as resp:
                if resp.status != 200:
                    print(f"Polling Error: {resp.status}")
                    continue

                state = await resp.json()
                status = state.get("status")
                current_step = state.get("current_step") # This field is added by our Engine refactor

                # Check for updates
                if current_step != last_step:
                     print(f"Step Completed: {current_step}")
                     last_step = current_step

                if status == "completed":
                    print("\n--- EXECUTION COMPLETED ---")
                    print(f"Final Result Keys: {list(state.get('results', {}).keys())}")
                elif status == "failed":
                    print("\n--- EXECUTION FAILED ---")
                    print(f"Error: {state.get('error')}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
