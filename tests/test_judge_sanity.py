"""Judge Agent Sanity Tests."""

import unittest
from unittest.mock import AsyncMock, MagicMock

from backend.agents.judge import JudgeAgent
from backend.llm.provider import LLMProvider
from backend.models.llm import LLMResponse
from backend.models.state import InputData, WorkflowState


class TestJudgeSanity(unittest.IsolatedAsyncioTestCase):
    """Judge sanity test suite."""

    async def test_judge_sanity_execution(self):
        """Sanity check for JudgeAgent V2.

        Ensures input injection and result parsing works.
        """
        # 1. Setup Input Data
        inputs = InputData(
            history_text="User: Hello\nAI: Hi",
            product_text="This is a product draft.",
            reflection_text="I did my best.",
        )

        state = WorkflowState(execution_id="sanity_check", inputs=inputs)

        # 2. Mock LLM Response
        valid_json = """{
            "metadata": {
                "luontiaika": "2023-01-01",
                "agentti": "SanityMock",
                "vaihe": 1
            },
            "matrix_id": "sanity_matrix",
            "scale_min": 1,
            "scale_max": 5,
            "total_score": 5,
            "dimensions": [
                {
                    "dimension_id": "test_dim",
                    "label": "Test Dimension",
                    "score": 5,
                    "reasoning": "Excellent output.",
                    "quote": "product draft"
                }
            ],
            "critical_findings": [],
            "metodologinen_loki": "Log",
            "edellisen_vaiheen_validointi": "Valid",
            "semanttinen_tarkistussumma": "Hash"
        }"""

        mock_llm = MagicMock(spec=LLMProvider)
        mock_llm.generate = AsyncMock(
            return_value=LLMResponse(content=valid_json, reasoning_token=None, token_usage={}, provider_metadata={})
        )

        # 3. Setup Agent
        agent = JudgeAgent(model="mock", provider="mock")
        agent.llm_provider = mock_llm

        # 4. Execute
        mock_repo = MagicMock()
        mock_repo.get_component_by_id = AsyncMock(return_value={"content": {"name": "Sanity Matrix", "criteria": []}})

        await agent.execute(state, execution_config={"matrix_id": "sanity_matrix"}, repository=mock_repo)

        # 5. Verify State
        self.assertIn("step_judge", state.audit_results)
        result = state.audit_results["step_judge"]

        self.assertEqual(result.total_score, 5)
        self.assertEqual(result.dimensions[0].reasoning, "Excellent output.")

        # 6. Verify Context Injection
        call_args = mock_llm.generate.call_args
        kwargs = call_args.kwargs
        system_instr = kwargs.get("system_instruction", "")

        self.assertIn("### CHAT HISTORY TO EVALUATE:", system_instr)
        self.assertIn("User: Hello", system_instr)
        self.assertIn("### PRODUCT TO EVALUATE:", system_instr)
