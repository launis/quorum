
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend.agents.critics import (
    LogicalFalsifierAgent,
    FactualOverseerAgent,
    CausalAnalystAgent,
    PerformativityDetectorAgent
)
from backend.agents.analyst import AnalystAgent
from backend.agents.profiler import ProfilerAgent
from backend.agents.judge import JudgeAgent
from backend.models.domain import (
    FalsifierDTO, FalsifierOutput, FalsifierInput,
    OverseerDTO, OverseerOutput, OverseerInput,
    CausalDTO, CausalOutput, CausalInput,
    PerformativityDTO, PerformativityOutput, PerformativityInput,
    AnalystDTO, AnalystOutput, AnalystInput,
    ProfilerDTO, ProfilerOutput, ProfilerInput,
    JudgeDTO, JudgeOutput, JudgeInput
)

def test_agent_schemas():
    print("--- Testing Agent Schemas ---")
    
    agents = [
        (LogicalFalsifierAgent, FalsifierDTO, FalsifierOutput),
        (FactualOverseerAgent, OverseerDTO, OverseerOutput),
        (CausalAnalystAgent, CausalDTO, CausalOutput),
        (PerformativityDetectorAgent, PerformativityDTO, PerformativityOutput),
        (AnalystAgent, AnalystDTO, AnalystOutput),
        (ProfilerAgent, ProfilerDTO, ProfilerOutput),
        (JudgeAgent, JudgeDTO, JudgeOutput)
    ]
    
    for AgentClass, DTO, Output in agents:
        print(f"Checking {AgentClass.__name__}...")
        assert AgentClass.DTO_SCHEMA == DTO, f"{AgentClass.__name__} DTO_SCHEMA mismatch"
        assert AgentClass.OUTPUT_SCHEMA == Output, f"{AgentClass.__name__} OUTPUT_SCHEMA mismatch"
        print(f"✅ {AgentClass.__name__} schemas match.")

async def test_agent_execution_mock():
    print("\n--- Testing Agent Execution (Mock) ---")

    # MOCK DATA
    falsifier_dto_mock = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "falsifier_data": {
            "is_falsifiable": True,
            "falsification_attempts": [],
            "stress_test": {"resilience_score": 0.5, "weak_points": []},
            "fidelity": {"score": 0.8, "assessment": "Good"}
        }
    }

    # Helper to test an agent
    async def run_agent_test(agent, input_data, mock_response_dict):
        print(f"Testing execution of {agent.__class__.__name__}...")
        
        # Mock the LLM Client within the agent
        # We need to patch the generate method or similar. 
        # BaseAgent.execute calls self.llm.generate(...)
        
        mock_llm = AsyncMock()
        # The agent expects the LLM to return a Pydantic model (DTO) if strict mode is on?
        # Actually BaseAgent.execute logic:
        # result = await self.llm.generate(..., response_model=self.DTO_SCHEMA)
        # So we mock generate to return the DTO instance.
        
        dto_instance = agent.DTO_SCHEMA(**mock_response_dict)
        mock_llm.generate.return_value = dto_instance
        
        # Inject mock llm
        agent.client = mock_llm 
        
        # ACT
        result = await agent.execute(input_data)
        
        # ASSERT
        assert isinstance(result, agent.OUTPUT_SCHEMA)
        assert isinstance(result, agent.DTO_SCHEMA) # Should inherit
        assert result.metadata is not None # System injected
        assert result.thought_process == mock_response_dict["thought_process"]
        print(f"✅ {agent.__class__.__name__} execution successful. Output type: {type(result)}")

    # 1. LogicalFalsifierAgent
    falsifier = LogicalFalsifierAgent()
    falsifier_input = FalsifierInput(
        history_text="Foo", product_text="Bar", reflection_text="Baz"
    )
    await run_agent_test(falsifier, falsifier_input, falsifier_dto_mock)

    print("\n✅ All mock executions passed.")

if __name__ == "__main__":
    test_agent_schemas()
    asyncio.run(test_agent_execution_mock())
