
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.agents.judge import JudgeAgent
from backend.exceptions import AgentExecutionError

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StrictScaleVerifier")

async def test_strict_scale():
    print("\n--- TEST 1: SUCCESS CASE (DB Has Scale) ---")
    repo = AsyncMock()
    mock_matrix = MagicMock()
    mock_matrix.content = {"scale": {"min": 10, "max": 100}, "name": "StrictMatrix"}
    repo.get_component_by_id.return_value = mock_matrix
    
    # Initialize without model to bypass Factory validation
    agent = JudgeAgent(model=None)
    # Mock Provider
    agent.llm_provider = AsyncMock()
    # Mock return value of generate() to have .content and .parsed_content
    mock_resp = MagicMock()
    mock_resp.content = '{"pisteet": {}}'
    mock_resp.parsed_content = {"pisteet": {}}
    mock_resp.token_usage = {}
    agent.llm_provider.generate.return_value = mock_resp
    
    context = {"matrix_id": "matrix_strict_v1"}
    
    try:
        # Running execute via the agent
        result = await agent.execute(input_data={"history_text": "foo"}, execution_context=context, repository=repo)
        
        print(f"Result Matrix ID: {result.get('matrix_id')}")
        print(f"Result Scale: {result.get('scale_min')} - {result.get('scale_max')}")
        
        if result.get("scale_min") == 10 and result.get("scale_max") == 100:
            print("✅ SUCCESS: Scale matches DB (10-100).")
        else:
             print("❌ FAILURE: Scale mismatch.")
             
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- TEST 2: FAILURE CASE (Missing Scale) ---")
    mock_matrix_broken = MagicMock()
    mock_matrix_broken.content = {"name": "BrokenMatrix"} # No scale
    repo.get_component_by_id.return_value = mock_matrix_broken
    
    try:
        await agent.execute(input_data={"history_text": "foo"}, execution_context=context, repository=repo)
        print("❌ FAILURE: Agent should have raised error but didn't.")
    except AgentExecutionError as e:
        print(f"✅ SUCCESS: Agent raised expected error: {e}")
    except Exception as e:
        print(f"⚠️  SUCCESS (Sort of): Agent raised generic error: {e}")

if __name__ == "__main__":
    asyncio.run(test_strict_scale())
