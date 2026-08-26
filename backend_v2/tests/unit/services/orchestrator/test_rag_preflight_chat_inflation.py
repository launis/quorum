"""Regression test: chat log XML wrappers and AI text inflate preflight character count.

Reproduces the bug from exe_5524d14aaff6426585f8b9ceb6a2be61 where trivial inputs
passed the rag_preflight_min_input_chars threshold because the combined chat_log
(including <user_payload>/<ai_draft_context> XML wrappers and AI-generated responses)
inflated the total character count from ~76 real user chars to ~497.

The circuit breaker MUST evaluate user-authored content quality, not raw file size
including XML tags and AI responses.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.models.v2_core import ExecutionRecord, Step, StepRule, WorkflowInputs
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService


def _make_step_def() -> Step:
    """Creates a valid Step for testing."""
    return Step.model_validate(
        {
            "id": "stp_1234567890abcdef",
            "slug": "test_step",
            "name": {"translations": {"en": "Test Step"}},
            "description": {"translations": {"en": "Desc"}},
            "model_strategy": "fast",
            "criteria_block_ids": ["blk_1234567890abcdef"],
            "extraction_protocol_block_id": "blk_1234567890abcdef",
            "type": "llm",
        }
    )


@pytest.mark.asyncio
async def test_preflight_inflated_by_chat_xml_and_ai_text() -> None:
    """Regression: Trivial user content wrapped in XML with AI text exceeds threshold.

    Scenario from exe_5524d14aaff6426585f8b9ceb6a2be61:
    - product_text: "lopputuote" (10 chars, a label not content)
    - chat_log: combined XML with AI responses (443 chars, but only ~47 user chars)
    - reflection_text: "reflektiodokumentti" (19 chars, a label not content)
    - document_date: "2026-07-22T04:43:36+00:00" (25 chars, metadata)

    Total raw chars = 497 -> passes threshold of 50 -> BUG: atomization proceeds.
    Total ACTUAL user analytical content = ~76 chars of trivial chat ("what time is it").

    Expected: Preflight MUST skip atomization for trivially short user content.
    """
    # Exact reproduction of the buggy inputs
    combined_chat_log = (
        "<user_payload>\npaljon kello on\n</user_payload>\n\n"
        "<ai_draft_context>\nKello on tällä hetkellä 7.43.\n</ai_draft_context>\n\n"
        "<user_payload>\nkiitos\n</user_payload>\n\n"
        "<ai_draft_context>\nOle hyvä! Autan mielelläni, jos sinulla on muuta kysyttävää."
        "\n</ai_draft_context>\n\n"
        "<user_payload>\npaljon kello on\n</user_payload>\n\n"
        "<ai_draft_context>\nKello on tällä hetkellä 7.43.\n</ai_draft_context>\n\n"
        "<user_payload>\nkiitos\n</user_payload>\n\n"
        "<ai_draft_context>\nOle hyvä! Autan mielelläni, jos sinulla on muuta kysyttävää."
        "\n</ai_draft_context>"
    )

    dynamic_inputs: dict[str, str | int] = {
        "product_text": "lopputuote",
        "chat_log": combined_chat_log,
        "reflection_text": "reflektiodokumentti",
        "document_date": "2026-07-22T04:43:36+00:00",
    }

    # Verify the bug precondition: raw total exceeds threshold (50)
    total_raw_chars = sum(len(v) for v in dynamic_inputs.values() if isinstance(v, str))
    assert total_raw_chars > 50, (
        f"Precondition: raw chars ({total_raw_chars}) MUST exceed threshold to prove the inflation bug"
    )

    step_rule = StepRule(
        id="stp_1234567890abcdef",
        task_blueprint="blp_1234567890abcdef",
        input_mappings={},
        depends_on=[],
    )
    step_def = _make_step_def()
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs=dynamic_inputs),
    )

    service = RAGPreflightService(
        workflow_repo=AsyncMock(),
        system_repo=AsyncMock(),
        prompt_compiler=MagicMock(),
    )
    emit_mock = AsyncMock()

    with (
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer,
        patch("backend_v2.services.orchestrator.rag_preflight_service.LLMClient") as mock_llm_client,
    ):
        # If atomizer IS called (the bug), we need to let it return something to avoid crash
        mock_instance = AsyncMock()
        mock_instance.extract_atoms.return_value = []
        mock_atomizer.return_value = mock_instance
        mock_llm_client.from_strategy = AsyncMock(return_value=AsyncMock())

        result = await service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        # BUG ASSERTION: Atomizer should NOT have been called because the actual
        # user-authored content is trivially short (single words + small talk chat).
        # The current code INCORRECTLY allows atomization because the combined
        # chat_log with XML wrappers and AI text inflates the char count above 50.
        assert mock_atomizer.called is False, (
            f"BUG: TwoPassAtomizer was invoked despite trivial user content. "
            f"Raw char count ({total_raw_chars}) passed threshold because "
            f"AI text, XML tags, and metadata inflated the count."
        )
        assert result == {"atoms_by_input": {}, "is_data_starved": True}, (
            "Expected empty blackboard for data-starved inputs"
        )
