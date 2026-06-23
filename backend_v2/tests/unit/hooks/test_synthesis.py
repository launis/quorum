import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from collections.abc import Awaitable
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.synthesis import (
    _build_title_map,
    _compress_synthesis_payload,
    text_consolidation_hook,
)


@pytest.fixture
def valid_workflow_data() -> dict[str, Any]:
    return {
        "id": "wf_1234567890abcdef1234567890abcdef",
        "slug": "test_workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_1234567890abcdef1234567890abcdef",
        "expected_inputs": [],
        "steps": [],
    }


@pytest.fixture
def valid_execution_data() -> dict[str, Any]:
    return {
        "id": "exe_1234567890abcdef1234567890abcdef",
        "workflow_id": "wf_1234567890abcdef1234567890abcdef",
        "organization_id": "org_1",
        "status": "running",
        "output_profile_id": "prof_1234567890abcdef1234567890abcdef",
    }


@pytest.fixture
def valid_output_profile_data() -> dict[str, Any]:
    return {
        "id": "prof_1234567890abcdef1234567890abcdef",
        "slug": "test_profile",
        "workflow_id": "wf_1234567890abcdef1234567890abcdef",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
        "display_scale": "original",
        "synthesis": {
            "system_prompt": "You are a synthesizer.",
            "historical_context_mode": "DISABLED",
            "enable_pii_masking": False,
            "omit_empty_sections": True,
            "allowed_exports": ["pdf", "raw_json"],
            "allowed_mcp_tools": [],
        },
        "layouts": [],
    }


@pytest.mark.asyncio
async def test_synthesis_fails_fast_on_invalid_metadata(
    valid_workflow_data: dict[str, Any],
    valid_execution_data: dict[str, Any],
    valid_output_profile_data: dict[str, Any],  # noqa: E501
) -> None:  # noqa: E501
    """Test that missing target_locale triggers AppException due to strict Pydantic parsing."""
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        workflow_id=valid_workflow_data["id"],
        inputs={},
        metadata={},  # Missing target_locale
        global_context_vars={},
    )
    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_repo.get_execution.return_value = valid_execution_data
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )  # noqa: E501

    from collections.abc import Awaitable

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Strict Fail-Fast Enforced" in exc_info.value.message


@pytest.mark.asyncio
async def test_synthesis_fails_fast_on_invalid_step_data(
    valid_workflow_data: dict[str, Any],
    valid_execution_data: dict[str, Any],
    valid_output_profile_data: dict[str, Any],  # noqa: E501
) -> None:  # noqa: E501
    """Test that non-dict/model step data triggers AppException enforcing Phase 9 logic."""
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        workflow_id=valid_workflow_data["id"],
        inputs={"step_1": 12345},  # Invalid structured data
        metadata={"target_locale": "en", "step_results": [{"invalid": "data"}]},
        global_context_vars={},
    )

    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_repo.get_execution.return_value = valid_execution_data
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data

    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )  # noqa: E501

    from collections.abc import Awaitable

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Strict Fail-Fast Enforced" in exc_info.value.message


@pytest.mark.asyncio
async def test_synthesis_empty_inputs_returns_early(
    valid_workflow_data: dict[str, Any],
    valid_execution_data: dict[str, Any],
    valid_output_profile_data: dict[str, Any],  # noqa: E501
) -> None:  # noqa: E501
    """Test that valid metadata and empty inputs safely return a HookResult without calling the LLM."""
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        workflow_id=valid_workflow_data["id"],
        inputs={"steps": []},
        metadata={
            "target_locale": "en",
            "step_results": [{"step_id": "dummy_step", "block_id": "blk_1", "data_type": "matrix", "payload": {}}],
        },  # noqa: E501
        global_context_vars={},
    )

    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_repo.get_execution.return_value = valid_execution_data
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data

    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )  # noqa: E501

    result = await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "synthesized_markdown" in result.state_delta
    assert result.state_delta["synthesized_markdown"] == "*NO_DATA_AVAILABLE*"


def test_compress_synthesis_payload_strips_heavy_keys() -> None:
    """Test that _compress_synthesis_payload removes log-heavy keys but preserves lite evaluations."""
    import json

    payload = {
        "step_1": {
            "result": "success",
            "evaluations": [
                {
                    "atom_id": "atm_001",
                    "exact_quotes": ["Tämä on suora lainaus käyttäjän tekstistä."],
                    "semantic_reasoning": "Lause viittaa selkeään väitteeseen.",
                    "score": 4,
                    "shuffled_atoms": ["x"],
                },
                {
                    "atom_id": "atm_002",
                    "exact_quotes": None,
                    "semantic_reasoning": "No evidence found.",
                    "score": 1,
                },
                {
                    "atom_id": "atm_003",
                    "exact_quotes": ["[CONTEXTUAL_OVERRIDE_APPLIED]"],
                    "semantic_reasoning": "Override applied.",
                    "score": 0,
                },
                {
                    "atom_id": "atm_004",
                    "exact_quotes": ["[SKIPPED]"],
                    "semantic_reasoning": "Junk",
                    "score": 0,
                },
                {
                    "atom_id": "atm_005",
                    "exact_quotes": ["   "],
                    "semantic_reasoning": "Empty string",
                    "score": 0,
                },
            ],
            "shuffled_atoms": ["a", "b"],
            "quote": "test",
            "reasoning": "because",
            "nested": {"evaluations": "remove me too", "keep_me": True},
        }
    }

    compressed_str = _compress_synthesis_payload(payload)
    compressed = json.loads(compressed_str)

    # Lite evaluations preserved: only atm_001 has a valid exact_quote
    step1 = compressed["step_1"]
    assert "evaluations" in step1
    assert len(step1["evaluations"]) == 1
    assert step1["evaluations"][0]["atom_id"] == "atm_001"
    assert step1["evaluations"][0]["exact_quotes"] == ["Tämä on suora lainaus käyttäjän tekstistä."]
    assert step1["evaluations"][0]["semantic_reasoning"] == "Lause viittaa selkeään väitteeseen."

    # Heavy keys still stripped
    assert "shuffled_atoms" not in step1
    assert "quote" in step1
    assert "reasoning" in step1

    # Nested non-list evaluations still stripped
    assert "evaluations" not in step1["nested"]
    assert step1["nested"]["keep_me"] is True


@pytest.mark.skip("Legacy architecture obsolete")
def test_compress_synthesis_strips_heavy_anchors() -> None:
    """Verify that _compress_synthesis_payload compresses localized_anchors_found and strips post_quote_anchor."""
    import json

    payload = {
        "step_1": {
            "exact_quotes": ["This must survive"],
            "semantic_reasoning": "So must this",
            "localized_anchors_found": [
                "anchor_one",
                "anchor_two",
                "anchor_three_is_the_longest_by_far",
                "anchor_four",
                "anchor_five",
            ],
            "post_quote_anchor": "should be removed",
        }
    }

    compressed_str = _compress_synthesis_payload(payload)
    compressed = json.loads(compressed_str)
    step1 = compressed["step_1"]

    # Anchor compression: 5 anchors → 2-element hybrid signal
    assert "localized_anchors_found" in step1
    assert len(step1["localized_anchors_found"]) == 2
    assert "anchor_three_is_the_longest_by_far" in step1["localized_anchors_found"][0]
    assert step1["localized_anchors_found"][1] == "[+4 additional anchors found]"

    # post_quote_anchor must be stripped
    assert "post_quote_anchor" not in step1

    # Critical fields must survive
    assert step1["exact_quotes"] == "This must survive"
    assert step1["semantic_reasoning"] == "So must this"


def test_build_title_map() -> None:
    """Test that _build_title_map successfully resolves localized Step and Input names."""
    from backend_v2.models.v2_core import I18nText, Step, Workflow

    wf = Workflow(
        id="wf_1234567890abcdef1234567890abcdef",
        slug="test",
        name=I18nText(default_locale="en", translations={"en": "Test", "fi": "Test"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        status="draft",
        version=1,
        default_profile_id="prof_1234567890abcdef1234567890abcdef",
        steps=cast(
            Any,
            [
                {
                    "id": "node_1111111111abcdef1111111111abcdef",
                    "task_blueprint": "step_2222222222abcdef2222222222abcdef",
                }
            ],
        ),
        expected_inputs=cast(
            Any,
            [
                {
                    "input_key": "input_x",
                    "label": I18nText(default_locale="en", translations={"en": "Input X", "fi": "Syöte X"}),
                    "required": True,
                    "input_modes": ["text"],
                    "description": I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
                }
            ],
        ),
    )

    step = Step(
        id="step_2222222222abcdef2222222222abcdef",
        slug="test_step",
        type="llm",
        model_strategy="standard",
        name=I18nText(default_locale="en", translations={"en": "Test Step", "fi": "Testi Vaihe"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        extraction_protocol_block_id="blk_573802341db9d68c",
        criteria_block_ids=["block_1"],
    )

    title_map = _build_title_map(wf, [step], language="fi")

    assert title_map["node_1111111111abcdef1111111111abcdef"] == "Testi Vaihe"
    assert title_map["input_x"] == "Syöte X"


"""Unit tests for the Synthesis Hook."""


import pytest

from backend_v2.core.hook_registry import hook_registry
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.services.mcp.mcp_tool_loop import MCPToolLoopResult  # type: ignore


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_workflow_by_id = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def base_state() -> HookState:
    return HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_1",
        inputs={
            "steps": {
                "step_1": {
                    "reasoning_trace": {
                        "thought_process": "test text",
                        "conclusion": "abc@example.com",
                        "confidence_score": 0.9,
                    }
                },
                "step_2": {
                    "reasoning_trace": {
                        "thought_process": "localization test",
                        "conclusion": "en",
                        "confidence_score": 1.0,
                    }
                },
            }
        },
        global_context_vars={"language": "en"},
        metadata={
            "target_locale": "en",
            "step_results": [
                {
                    "step_id": "step_1",
                    "block_id": "b1",
                    "data_type": "text",
                    "payload": {
                        "reasoning_trace": {
                            "thought_process": "test text",
                            "conclusion": "abc@example.com",
                            "confidence_score": 0.9,
                        }
                    },
                },  # noqa: E501
                {
                    "step_id": "step_2",
                    "block_id": "b2",
                    "data_type": "text",
                    "payload": {
                        "reasoning_trace": {
                            "thought_process": "localization test",
                            "conclusion": "en",
                            "confidence_score": 1.0,
                        }
                    },
                },
            ],
        },
    )


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.get_pii_service")
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_success(
    mock_llm_client_class: AsyncMock,
    mock_execute_tool_loop: AsyncMock,
    mock_get_pii_service: AsyncMock,
    mock_repo: AsyncMock,
    base_state: HookState,
) -> None:
    from unittest.mock import MagicMock

    mock_pii_service = MagicMock()

    def mock_mask_pii(text: str, language: str) -> str:
        return text.replace("abc@example.com", "[REDACTED_EMAIL]")

    mock_pii_service.mask_pii.side_effect = mock_mask_pii
    mock_get_pii_service.return_value = mock_pii_service
    """Test that synthesis hook injects config constraints correctly and calls LLM."""
    mock_repo.get_workflow_by_id = AsyncMock()
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "output_profile_id": "prf_test",
        }
    )
    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "name": {"default_locale": "en", "translations": {"en": "Profile Test", "fi": "Profile Test"}},
                "strictness_level": 85,
                "scoring_strategy": "WATERFALL",
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 500,
                    "preamble_text": {
                        "default_locale": "en",
                        "translations": {"en": "Always be concise.", "fi": "Always be concise."},
                    },
                    "omit_empty_sections": True,
                    "enable_pii_masking": True,
                },
            }
        },
    }
    mock_repo.get_workflow_by_id.return_value = mock_workflow
    prof_data = dict(mock_workflow["output_profiles"]["prf_test"])
    prof_data.update({"id": "prf_test", "slug": "profile-test", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    # Setup the mock LLM Client Instance
    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)

    # Return MCPToolLoopResult
    mock_dto_dict = {
        "content_blocks": [],
        "cited_sources": ["source1"],
        "section_syntheses": [],
        "xai_highlights": [],
    }
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data=mock_dto_dict,
        audit_traces=[],
        usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=100),
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # Verify that LLM tools loop was called
    mock_execute_tool_loop.assert_called_once()

    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    call_args = mock_execute_tool_loop.call_args
    messages = call_args.kwargs.get("messages", [])
    user_msg: dict[str, Any] = next((m for m in messages if m["role"] == "user"), {})
    sys_msg: dict[str, Any] = next((m for m in messages if m["role"] == "system"), {})

    assert "[REDACTED_EMAIL]" in user_msg.get("content", "")
    assert "abc@example.com" not in user_msg.get("content", "")

    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    assert "<global_length_constraint_chars>500</global_length_constraint_chars>" in sys_msg.get("content", "")

    assert "content_blocks" in delta
    assert delta["cited_sources"] == ["source1"]
    assert "token_usage" in delta["step_metadata_updates"]
    assert delta["step_metadata_updates"]["token_usage"]["total_tokens"] == 100


@pytest.mark.asyncio
async def test_synthesis_hook_workflow_not_found(mock_repo: AsyncMock, base_state: HookState) -> None:
    """Test that missing workflow throws an AppException."""
    mock_repo.get_workflow_by_id.return_value = None
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    with pytest.raises(AppException) as exc_info:
        await text_consolidation_hook(base_state, deps)  # type: ignore[misc]

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_multi_profile_routing(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test that synthesis routes to requested target_profile_id and uses its distinct rules."""
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "output_profile_id": "prof_b",
        }
    )

    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prof_a",
        "output_profiles": {
            "prof_a": {
                "name": {"default_locale": "en", "translations": {"en": "A", "fi": "A"}},
                "strictness_level": 85,
                "scoring_strategy": "WATERFALL",
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 100,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Alpha", "fi": "Alpha"}},
                },
            },
            "prof_b": {
                "name": {"default_locale": "en", "translations": {"en": "B", "fi": "B"}},
                "strictness_level": 85,
                "scoring_strategy": "WATERFALL",
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 900,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Beta", "fi": "Beta"}},
                },
            },
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)
    prof_data = dict(mock_workflow["output_profiles"]["prof_b"])
    prof_data.update({"id": "prof_b", "slug": "prof-b", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    # Force the hook to use prof_b
    base_state.metadata["target_profile_id"] = "prof_b"

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data={
            "content_blocks": [],
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        },
        audit_traces=[],
        usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=50),
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    call_args = mock_execute_tool_loop.call_args
    sys_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "system"), {})

    # Assert Prof B's constraints are found, NOT Prof A's
    assert "<global_length_constraint_chars>900</global_length_constraint_chars>" in sys_msg.get("content", "")
    assert "<global_length_constraint_chars>100</global_length_constraint_chars>" not in sys_msg.get("content", "")


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_target_blocks_wildcard_bypass(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test the dual-layer filter: AI traces are included by *, explicit Python variables bypass the check."""
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "output_profile_id": "prof_a",
        }
    )

    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prof_a",
        "steps": [
            {"id": "stp_1111111111111111", "task_blueprint": "sb_1111111111111111", "depends_on": []},
            {"id": "stp_2222222222222222", "task_blueprint": "sb_2222222222222222", "depends_on": []},
            {"id": "stp_3333333333333333", "task_blueprint": "sb_3333333333333333", "depends_on": []},
        ],
        "output_profiles": {
            "prof_a": {
                "name": {"default_locale": "en", "translations": {"en": "A", "fi": "A"}},
                "strictness_level": 85,
                "scoring_strategy": "WATERFALL",
                "layouts": [
                    {"target_blocks": ["stp_2222222222222222"], "preset_view": "default"},
                    {"target_blocks": ["*"], "preset_view": "default"},
                ],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 100,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Alpha", "fi": "Alpha"}},
                },
            }
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)
    prof_data = dict(mock_workflow["output_profiles"]["prof_a"])
    prof_data.update({"id": "prof_a", "slug": "prof-a", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    mock_repo.get_all_steps = AsyncMock(
        return_value=[
            {
                "id": "sb_1111111111111111",
                "slug": "step-1",
                "type": "logic",
                "hook": "some_hook",
                "name": {"default_locale": "en", "translations": {"en": "Step 1", "fi": "Step 1"}},
                "role_block_id": None,
                "extraction_protocol_block_id": None,
                "criteria_block_ids": [],
            },
            {
                "id": "sb_2222222222222222",
                "slug": "step-2",
                "type": "logic",
                "hook": "some_hook",
                "name": {"default_locale": "en", "translations": {"en": "Step 2", "fi": "Step 2"}},
                "role_block_id": None,
                "extraction_protocol_block_id": None,
                "criteria_block_ids": [],
            },
            {
                "id": "sb_3333333333333333",
                "slug": "step-3",
                "type": "logic",
                "hook": "some_hook",
                "name": {"default_locale": "en", "translations": {"en": "Step 3", "fi": "Step 3"}},
                "role_block_id": None,
                "extraction_protocol_block_id": None,
                "criteria_block_ids": [],
            },
        ]
    )
    mock_repo.get_all_prompt_blocks = AsyncMock(return_value=[])
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    base_state = base_state.model_copy(
        update={
            "inputs": {
                "steps": {
                    "stp_1111111111111111": {
                        "reasoning_trace": {
                            "thought_process": "AI says hello",
                            "conclusion": "test",
                            "confidence_score": 1.0,
                        }
                    },
                    "stp_2222222222222222": {"result": 1337},
                    "stp_3333333333333333": {"value": "this should be blocked by wildcard"},
                }
            },
            "metadata": {
                "target_locale": "en",
                "step_results": [
                    {
                        "step_id": "stp_1111111111111111",
                        "block_id": "b1",
                        "data_type": "text",
                        "payload": {
                            "reasoning_trace": {
                                "thought_process": "AI says hello",
                                "conclusion": "test",
                                "confidence_score": 1.0,
                            }
                        },
                    },  # noqa: E501
                    {
                        "step_id": "stp_2222222222222222",
                        "block_id": "b2",
                        "data_type": "text",
                        "payload": {"result": 1337},
                    },
                    {
                        "step_id": "stp_3333333333333333",
                        "block_id": "b3",
                        "data_type": "text",
                        "payload": {"value": "this should be blocked by wildcard"},
                    },  # noqa: E501
                ],
            },
        }
    )

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data={
            "content_blocks": [],
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        },
        audit_traces=[],
        usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=10),
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    call_args = mock_execute_tool_loop.call_args
    user_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "user"), {})
    content = user_msg.get("content", "")

    # Assert AI trace is in
    assert "stp_1111111111111111" in content
    assert "AI says hello" in content

    # Assert python math bypassed the wildcard shield
    assert "stp_2222222222222222" in content
    assert "1337" in content

    # Assert garbage metadata was properly shielded
    assert "stp_3333333333333333" not in content
    assert "this should be blocked" not in content


def test_synthesis_hook_is_registered() -> None:
    """Test that text_consolidation_hook is correctly registered in the HookRegistry to prevent regressions."""
    # Ensure hooks are initialized (this triggers decorators in tests if not already done)
    import backend_v2.hooks  # noqa: F401

    hook = hook_registry.get_hook("text_consolidation_hook")
    assert hook is not None
    assert hook == text_consolidation_hook


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_historical_context_mode(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test that SLIDING_WINDOW_3 fetches valid past executions and ignores failed ones."""
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "output_profile_id": "prf_test",
        }
    )

    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "name": {"default_locale": "en", "translations": {"en": "Profile Test", "fi": "Profile Test"}},
                "strictness_level": 85,
                "scoring_strategy": "WATERFALL",
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "historical_context_mode": "SLIDING_WINDOW_3",
                    "system_prompt": "Test sys prompt",
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Alpha", "fi": "Alpha"}},
                    "length_constraint": 100,
                },
            }
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)

    # Mocking past executions
    from datetime import datetime, timezone

    mock_past_exec = AsyncMock()
    mock_past_exec.id = "exe_past_1"
    mock_past_exec.status.value = "completed"
    mock_past_exec.created_at = datetime.now(timezone.utc)
    mock_past_exec.completed_at = datetime.now(timezone.utc)

    mock_cache = AsyncMock()
    mock_cache.synthesized_markdown = "Past history text"
    mock_cache.content_blocks = [{"block_type": "text", "text": "Past history text"}]
    mock_past_exec.profile_syntheses = {"prf_test": mock_cache}

    mock_failed_exec = AsyncMock()
    mock_failed_exec.id = "exe_past_2"
    mock_failed_exec.status.value = "failed"

    mock_repo.get_all_executions = AsyncMock(return_value=[mock_failed_exec, mock_past_exec])
    prof_data = dict(mock_workflow["output_profiles"]["prf_test"])
    prof_data.update({"id": "prf_test", "slug": "profile-test", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)

    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data={
            "content_blocks": [],
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        },
        audit_traces=[],
        usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=10),
    )

    base_state = base_state.model_copy(
        update={
            "inputs": {
                "steps": {
                    "step_1": {
                        "reasoning_trace": {
                            "thought_process": "AI says hello",
                            "conclusion": "test",
                            "confidence_score": 1.0,
                        }
                    }
                }
            },
            "global_context_vars": {"user_id": "usr_123"},
            "metadata": {
                "target_locale": "en",
                "step_results": [
                    {
                        "step_id": "step_1",
                        "block_id": "b1",
                        "data_type": "text",
                        "payload": {
                            "reasoning_trace": {
                                "thought_process": "AI says hello",
                                "conclusion": "test",
                                "confidence_score": 1.0,
                            }
                        },
                    }
                ],
            },  # noqa: E501
        }
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    # Verify historical context was fetched
    mock_repo.get_all_executions.assert_called_once()

    call_args = mock_execute_tool_loop.call_args
    user_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "user"), {})
    content = user_msg.get("content", "")

    # Assert valid past text was included
    assert "Past history text" in content
    assert "<HistoricalContext>" in content


def test_row_exp_prompt_contains_human_centric_focus() -> None:
    """Test that text_consolidation_hook contains the human-centric focus directive."""
    import inspect

    from backend_v2.hooks import synthesis

    source = inspect.getsource(synthesis.text_consolidation_hook)
    assert "HUMAN-CENTRIC FOCUS (CRITICAL)" in source
