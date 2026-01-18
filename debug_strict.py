
import os
import sys
import logging

# Configure logging to see PromptBuilder output
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.settings import get_settings
from backend.agents.profiler import ProfilerAgent
from backend.models.state import InputData
# Let's wait for view_file result to be sure.
# Actually, I will defer this edit until I see the file content.


async def main():
    print("--- STRICT EXECUTION AUDIT ---")
    settings = get_settings()
    print(f"USE_MOCK_LLM: {settings.use_mock_llm}")
    # print(f"USE_VERTEX_LLM: {settings.use_vertex_llm}") # Attribute does not exist

    # Force strict
    if settings.use_mock_llm:
        print("ERROR: Mock LLM is ENABLED! This script requires STRICT execution.")
        return

    # Create Agent
    try:
        agent = ProfilerAgent()
        # Configure Agent explicitly
        agent.set_model(model_name="gemini-1.5-pro", provider="vertex_ai")
        print(f"Agent initialized: {agent}")
    except Exception as e:
        print(f"Agent init failed: {e}")
        return

    # Logic from latest_execution.json (inputs)
    # The input in latest_execution.json was product_text (Sitra)
    # But profiler usually looks at history_text or reflection_text?
    # Let's see what inputs it takes.
    
    # Create Inputs
    input_data = InputData(
        history_text="", # Emulate the empty history issue
        product_text="Testing Strict Execution. This is not an angry email.",
        reflection_text="Just a test."
    )

    # Create State
    from backend.models.state import WorkflowState
    state = WorkflowState(
        execution_id="debug_exec_id",
        inputs=input_data,
        organization_id="org_debug",
        user_id="user_debug"
    )

    print("Running Agent...")
    try:
        # Pass state as first argument
        result = await agent.execute(state, context={})
        print("--- RESULT ---")
        print(result)
        
        if "negatiivissävytteinen sähköposti" in str(result):
            print("\n[CRITICAL] CANNED DATA DETECTED!")
        else:
            print("\n[OK] No canned data detected.")
            
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
