import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from backend.agents.analyst import AnalystAgent
from backend.agents.critics import (
    CausalAnalystAgent,
    FactualOverseerAgent,
    LogicalFalsifierAgent,
    PerformativityDetectorAgent,
)
from backend.agents.judge import JudgeAgent
from backend.agents.profiler import ProfilerAgent
from backend.models.domain import (
    AnalystDTO,
    AnalystOutput,
    CausalDTO,
    CausalOutput,
    FalsifierDTO,
    FalsifierInput,
    FalsifierOutput,
    JudgeDTO,
    JudgeOutput,
    OverseerDTO,
    OverseerOutput,
    PerformativityDTO,
    PerformativityOutput,
    ProfilerDTO,
    ProfilerOutput,
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
        (JudgeAgent, JudgeDTO, JudgeOutput),
    ]

    for AgentClass, DTO, Output in agents:
        print(f"Checking {AgentClass.__name__}...")
        assert getattr(AgentClass, "DTO_SCHEMA") == DTO, f"{AgentClass.__name__} DTO_SCHEMA mismatch"
        assert getattr(AgentClass, "OUTPUT_SCHEMA") == Output, f"{AgentClass.__name__} OUTPUT_SCHEMA mismatch"
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
            "stress_test_findings": [{"question": "Q", "evidence_held": False, "observation": "O"}],
            "fidelity_audit": {"fidelity_score": "High", "justification": "Mock fidelity audit"},
            "stress_test": {"resilience_score": 0.5, "weak_points": []},
            "fidelity": {"score": 0.8, "assessment": "Good"},
        },
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
        mock_response = MagicMock()
        mock_response.parsed_content = dto_instance
        mock_llm.generate.return_value = mock_response

        # Inject mock llm
        agent.llm_provider = mock_llm

        # ACT
        result = await agent.execute(input_data)

        # ASSERT
        assert isinstance(result, agent.OUTPUT_SCHEMA)
        assert isinstance(result, agent.DTO_SCHEMA)  # Should inherit
        assert result.metadata is not None  # System injected
        assert result.thought_process == mock_response_dict["thought_process"]
        print(f"✅ {agent.__class__.__name__} execution successful. Output type: {type(result)}")

    # 1. LogicalFalsifierAgent
    falsifier = LogicalFalsifierAgent()
    falsifier_input = FalsifierInput(
        history_text="Foo",
        step_analyst={"thought_process": "tp", "conclusion": "c", "confidence_score": 0.9, "hypotheses": ["Test hypothesis 1"]}
    )
    await run_agent_test(falsifier, falsifier_input, falsifier_dto_mock)

    print("\n✅ All mock executions passed.")


if __name__ == "__main__":
    test_agent_schemas()
    asyncio.run(test_agent_execution_mock())
