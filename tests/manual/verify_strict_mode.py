
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

# Mock dependencies
from backend.core.runner import PipelineRunner
from backend.agents.base import BaseAgent
from backend.exceptions import FatalInterruption
from backend.models.state import WorkflowState, InputData
from pydantic import BaseModel

class DummyAgent(BaseAgent):
    state_field = "dummy"
    async def get_response_schema(self):
        return BaseModel

async def test_pipeline_runner_strict_security():
    print("\n--- Testing PipelineRunner Strict Security ---")
    mock_repo = AsyncMock()
    # Simulate DB failure
    mock_repo.get_banned_phrases.side_effect = Exception("DB Connection Lost")
    
    runner = PipelineRunner(repository=mock_repo, registry=MagicMock(), prompt_builder=MagicMock())
    
    try:
        await runner.initialize_state(
            execution_id="test-exec",
            raw_inputs={"history_text": "foo"}
        )
        print("FAILURE: PipelineRunner swallowed the security error!")
        exit(1)
    except FatalInterruption as e:
        print(f"SUCCESS: PipelineRunner raised FatalInterruption: {e}")
    except Exception as e:
        print(f"FAILURE: Caught unexpected exception: {type(e)} {e}")
        exit(1)

async def test_base_agent_strict_checksum():
    print("\n--- Testing BaseAgent Strict Checksum (Dict) ---")
    agent = DummyAgent()
    
    # Simulate non-serializable object to break json.dumps in checksum calc
    # Force json.dumps to fail
    bad_data = {"key": "value"}
    with patch("json.dumps", side_effect=ValueError("Serialization Crash")):
        try:
            agent._apply_python_authority(bad_data)
            print("FAILURE: BaseAgent swallowed checksum error (Dict)!")
            exit(1)
        except ValueError as e:
            print(f"SUCCESS: BaseAgent raised ValueError: {e}")
            assert "Critical: Failed to calculate authoritative checksum" in str(e)
        except Exception as e:
            print(f"FAILURE: Caught unexpected exception: {type(e)} {e}")
            exit(1)

async def main():
    await test_pipeline_runner_strict_security()
    await test_base_agent_strict_checksum()

if __name__ == "__main__":
    asyncio.run(main())
