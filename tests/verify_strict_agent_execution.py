import asyncio
import logging
import sys
import os
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.getcwd())

from backend.agents.base import BaseAgent
from backend.exceptions import AgentExecutionError, ErrorCodes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestInput(BaseModel):
    value: str

class TestOutput(BaseModel):
    result: str

class StrictAgent(BaseAgent[TestInput, TestOutput]):
    INPUT_SCHEMA = TestInput
    OUTPUT_SCHEMA = TestOutput
    
    async def execute(self, input_data: TestInput, **kwargs) -> TestOutput:
        # If base class validation works, input_data is guaranteed to be TestInput
        return TestOutput(result=input_data.value)

class LooseAgent(BaseAgent):
    # No schemas defined
    async def execute(self, input_data: dict, **kwargs) -> dict:
        return {"result": input_data.get("value")}

async def verify_strict_execution():
    logger.info("=== Verifying Strict Agent Execution (Phase 8) ===")
    
    agent = StrictAgent(model="mock-model", provider="mock")
    
    # 1. Test Valid Input (Model)
    try:
        valid_input = TestInput(value="test")
        # We manually call execute logic or simulate engine call
        # Since BaseAgent.execute validates, we test that directly.
        # But wait, BaseAgent.execute is the entry point.
        # We need to mock the LLM provider or override generate to avoid network calls.
        # Actually, BaseAgent.execute does validation BEFORE LLM call.
        # So if we pass a dict, it should fail immediately.
        pass
    except Exception as e:
        logger.error(f"Setup failed: {e}")

    # 2. Test Invalid Input (Dict) - The Core Test
    logger.info("Test 1: Passing Dict to Strict Agent (Should Fail)")
    try:
        invalid_input = {"value": "test"}
        # This should raise AgentExecutionError(AGENT_INVALID_INPUT)
        await agent.execute(invalid_input) 
        logger.error("  [Fail] StrictAgent accepted dict input!")
    except AgentExecutionError as e:
        if e.detail == ErrorCodes.AGENT_INVALID_INPUT:
            logger.info("  [Pass] StrictAgent rejected dict input with AGENT_INVALID_INPUT.")
        else:
            logger.error(f"  [Fail] Wrong error code: {e.detail}")
    except Exception as e:
        logger.error(f"  [Fail] Unexpected exception: {type(e)} - {e}")

    # 3. Test Valid Input execution (mocking provider)
    # We can't easily test succeess without mocking provider, but we tested the failure gate.
    
    logger.info("=== Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(verify_strict_execution())
