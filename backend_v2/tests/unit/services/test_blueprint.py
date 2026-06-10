from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import ExecutionStatus, ScoringStrategy
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, I18nText, RenderedSynthesisCache, ReportDataDTO
from backend_v2.services.blueprint import BlueprintTransformer


def dict_to_obj(d: Any) -> Any:
    if isinstance(d, dict):
        if "translations" in d and "default_locale" in d:
            return I18nText(**d)
        return SimpleNamespace(**{k: dict_to_obj(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_obj(v) for v in d]
    return d


@pytest.fixture
def mock_repo_transformer() -> Any:
    repo = AsyncMock()
    repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}},
            "description": {"default_locale": "en", "translations": {"en": "desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_dddd1111dddd1111",
            "default_strictness_level": 50,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_dddd1111dddd1111": {
                    "name": {"default_locale": "en", "translations": {"en": "Default"}},
                    "synthesis": None,
                    "layouts": [
                        {
                            "preset_view": "1d_metrics",
                            "text_delivery_mode": "full",
                            "title": {"default_locale": "en", "translations": {"en": "Title"}},
                            "target_blocks": ["*"],
                        }
                    ],
                }
            },
        }
    )
    repo.get_all_output_profiles_models.return_value = dict_to_obj(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Title"}},
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
            }
        ]
    )
    repo.get_all_prompt_blocks_models.return_value = dict_to_obj(
        [
            {
                "id": "blk_1234abcd1234abcd",
                "slug": "matrix_logic1234",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"fi": "Kuvaus", "en": "Description"}},
                "label": {"default_locale": "en", "translations": {"fi": "Logiikka", "en": "Logic"}},
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"fi": "Ei mitään", "en": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 100,
                        "name": {"default_locale": "en", "translations": {"fi": "Täysi", "en": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                ],
                "computed_min": 0,
                "computed_max": 100,
                "scale_min": 0,
                "scale_max": 100,
            }
        ]
    )
    return repo


@pytest.mark.asyncio
async def test_build_report_dto_maps_correctly(mock_repo_transformer: Any) -> None:
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000001",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 75.0,
                        "justification": "Very logical.",
                    },
                    "synthesis": "Great job",
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000001", accept_language="en")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 1
    assert len(dto.layouts[0].axes) == 1

    axis = dto.layouts[0].axes[0]
    assert axis.name in ["Mock Workflow", "step_analyst", "matrix_logic1234", "test_k", "Logic", "Logic *"]  # noqa: E501
    assert axis.score == 75.0
    assert axis.row_explanation == "Very logical."


@pytest.mark.asyncio
async def test_graceful_degradation_missing_fields(mock_repo_transformer: Any) -> None:
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000002",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "fi"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000002")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 0


@pytest.fixture
def mock_repo_microcot() -> Any:
    repo = AsyncMock()
    repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234567890abcdef",
            "slug": "mock_workflow",
            "description": {"default_locale": "en", "translations": {"en": "desc"}},
            "status": "published",
            "version": 1,
            "name": {"default_locale": "en", "translations": {"en": "Mock Workflow"}},
            "default_profile_id": "prf_1234567890abcdef",
            "default_strictness_level": 50,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_1234567890abcdef": {
                    "name": {"default_locale": "en", "translations": {"en": "Default Profile"}},
                    "synthesis": None,
                    "layouts": [
                        {
                            "preset_view": "2d_compare",
                            "text_delivery_mode": "full",
                            "title": {"default_locale": "en", "translations": {"en": "Micro-CoT Map"}},
                            "target_blocks": ["*"],
                            "description": None,
                        }
                    ],
                }
            },
        }
    )
    repo.get_all_output_profiles_models.return_value = dict_to_obj(
        [
            {
                "id": "prf_1234567890abcdef",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default Profile"}},
                "workflow_id": "wf_1234567890abcdef",
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Micro-CoT Map"}},
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
            }
        ]
    )
    repo.get_all_prompt_blocks_models.return_value = dict_to_obj(
        [
            {
                "id": "blk_1111222233334444",
                "slug": "kahneman",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Description"}},
                "label": {"default_locale": "en", "translations": {"en": "Kahneman T1", "fi": "Kaksoisprosessiteoria"}},  # noqa: E501
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 3,
                        "name": {"default_locale": "en", "translations": {"en": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                ],
                "computed_min": 0,
                "computed_max": 3,
                "scale_min": 0,
                "scale_max": 3,
            },
            {
                "id": "blk_5555666677778888",
                "slug": "episteeminen",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Description"}},
                "label": {"default_locale": "en", "translations": {"en": "Epistemic", "fi": "Episteeminen Nöyryys"}},  # noqa: E501
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                ],
                "computed_min": 0,
                "computed_max": 5,
                "scale_min": 0,
                "scale_max": 5,
            },
        ]
    )
    return repo


@pytest.mark.asyncio
async def test_blueprint_crashes_on_naked_microcot_dict(mock_repo_microcot: Any) -> None:
    mock_repo_microcot.get_execution.return_value = ExecutionRecord(
        id="exe_abcdef1234567890",
        workflow_id="wf_1234567890abcdef",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    "blk_5555666677778888": 1.9,
                    "blk_1111222233334444": {
                        "step_1_evidence": "Found 2 valid arguments",
                        "step_4_final_score": 1.8,
                        "extension_confidence": 0.9,
                    },
                },
            )
        ],
        active_profile_id="prf_1234567890abcdef",
        metadata={"target_locale": "en"},
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_microcot,
        workflow_repo=mock_repo_microcot,
        comp_repo=mock_repo_microcot,
        identity_repo=mock_repo_microcot,
    )  # noqa: E501

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto("exe_abcdef1234567890", accept_language="en")

    # Epic 47 Phase 9: Fail-Fast hydration fails immediately on raw matrices
    assert exc_info.value.status_code == 500
    assert "Invalid matrix payload format" in exc_info.value.message


@pytest.fixture
def mock_repo_sdui() -> AsyncMock:
    repo = AsyncMock()
    repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_test",
            "name": {"default_locale": "en", "translations": {"en": "Mock"}},
            "description": {"default_locale": "en", "translations": {"en": "desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_1234abcd1234abcd",
            "default_strictness_level": 50,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
        }
    )
    repo.get_all_output_profiles_models.return_value = dict_to_obj(
        [
            {
                "id": "prf_1234abcd1234abcd",
                "slug": "default",
                "workflow_id": "wf_1234abcd1234abcd",
                "name": {"default_locale": "en", "translations": {"fi": "Oletus", "en": "Default"}},
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Metrics"}},
                        "steps": [],
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
            }
        ]
    )
    repo.get_all_prompt_blocks_models.return_value = dict_to_obj(
        [
            {
                "id": "blk_1234abcd1234abcd",
                "slug": "metric",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Description"}},
                "label": {"default_locale": "en", "translations": {"en": "Metric Category"}},
                "computed_min": 0,
                "computed_max": 5,
                "scale_min": 0,
                "scale_max": 5,
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                ],
            }
        ]
    )
    return repo


@pytest.mark.asyncio
async def test_blueprint_zero_math_rounding(mock_repo_sdui: AsyncMock) -> None:
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_sdui, workflow_repo=mock_repo_sdui, comp_repo=mock_repo_sdui, identity_repo=mock_repo_sdui
    )  # noqa: E501

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 3.14159,
                        "justification": "ok.",
                    },
                    "scoring_result": {
                        "total_score": 4.567  # Should become 4.6
                    },
                },
            )
        ],
    )
    mock_repo_sdui.get_execution.return_value = mock_execution
    mock_repo_sdui.get_workflow.return_value = dict_to_obj(
        {
            "id": "wor_1234abcd1234abcd",
            "slug": "mock-workflow",
            "name": {"default_locale": "en", "translations": {"en": "Mock"}},
            "description": {"default_locale": "en", "translations": {"en": "Mock"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_1234abcd1234abcd",
            "default_strictness_level": 50,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
        }
    )

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.global_score == 4.6

    assert len(dto.layouts) > 0
    axis = next(a for a in dto.layouts[0].axes if a.name in ["Metric Category", "Metric Category *"])
    assert axis.score == 3.1


@pytest.mark.asyncio
async def test_blueprint_synthesis_markdown_packaging(mock_repo_sdui: AsyncMock) -> None:
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_sdui, workflow_repo=mock_repo_sdui, comp_repo=mock_repo_sdui, identity_repo=mock_repo_sdui
    )  # noqa: E501

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        profile_syntheses={
            "prf_1234abcd1234abcd": RenderedSynthesisCache(
                synthesized_markdown="### Title\\n<script>alert('xss');</script>Some content."
            )
        },
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "has_warning": True,
                },
            )
        ],
    )
    mock_repo_sdui.get_execution.return_value = mock_execution
    mock_repo_sdui.get_workflow.return_value = dict_to_obj(
        {
            "id": "wor_1234abcd1234abcd",
            "slug": "mock-workflow",
            "name": {"default_locale": "en", "translations": {"en": "Mock"}},
            "description": {"default_locale": "en", "translations": {"en": "Mock"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_1234abcd1234abcd",
            "default_strictness_level": 50,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
        }
    )

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.has_warning is True

    assert dto.synthesized_markdown is not None
    assert "<script>" not in dto.synthesized_markdown
    assert "Some content." in dto.synthesized_markdown


# ---------------------------------------------------------------------------
# Phase 2: Suffix-based flat key extraction (no isinstance(v, dict) fallback)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_xai_extraction_works_for_nested_dict(mock_repo_transformer: Any) -> None:
    """Phase 9: Verify XAI metadata is extracted from nested dicts."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000003",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 85.0,
                        "justification": "Strictly suffix-based justification.",
                        "extensions": {"coaching": "Keep it up"},
                    }
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000003", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.score == 85.0
    assert axis.row_explanation == "Strictly suffix-based justification."
    assert axis.coaching == "Keep it up"


# ---------------------------------------------------------------------------
# Phase 4: MCPAuditTrace strict model access & deduplication
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mcp_audit_deduplication_uses_strict_model_attrs(mock_repo_transformer: Any) -> None:
    """Phase 4: Verifies that MCPAuditTrace items are accessed via strict attribute access
    (audit.tool_id, audit.query) and that duplicates are deduplicated by hash.
    """
    from backend_v2.models.v2_core import FrozenContext, MCPAuditTrace

    frozen = FrozenContext(
        mcp_tool_audit=[
            MCPAuditTrace(tool_id="mcp_tavily_search", step_name="step_1", query="AI ethics"),
            MCPAuditTrace(tool_id="mcp_tavily_search", step_name="step_1", query="AI ethics"),  # duplicate
            MCPAuditTrace(tool_id="mcp_tavily_search", step_name="step_2", query="Bias detection"),
        ]
    )
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000004",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        frozen_context=frozen,
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000004")

    # 3 items in, 1 duplicate must be removed → 2 unique
    assert len(dto.mcp_tool_audit) == 2
    tool_ids = {a.tool_id for a in dto.mcp_tool_audit}
    assert "mcp_tavily_search" in tool_ids


@pytest.mark.asyncio
async def test_mcp_audit_fails_fast_on_incomplete_data() -> None:
    """Phase 4: Negative Test verifying Pydantic boundary fails on missing query/tool_id.
    Ensures that raw dicts or incomplete schemas are rejected immediately.
    """
    from pydantic import ValidationError

    from backend_v2.models.v2_core import ExecutionRecord

    # Missing "query"
    invalid_mcp_audit = {
        "tool_id": "mcp_tavily_search",
        "step_name": "step_1",
        # query missing
    }

    with pytest.raises(ValidationError) as exc_info:
        ExecutionRecord(
            id="exe_0000000000000005",
            workflow_id="wf_1234abcd1234abcd",
            status=ExecutionStatus.COMPLETED,
            active_profile_id="prf_dddd1111dddd1111",
            frozen_context={"mcp_tool_audit": [invalid_mcp_audit]},  # type: ignore
            metadata={"target_locale": "en"},
        )

    # Must raise an error specifically indicating that query is missing
    assert "Field required" in str(exc_info.value)
    assert "query" in str(exc_info.value)


@pytest.mark.asyncio
async def test_blueprint_scoring_payload_validation_succeeds_with_extra_fields(mock_repo_sdui: AsyncMock) -> None:
    """TDD Fix (Green) for Epic 47 Phase 2: TraceScoringPayloadDTO handles final_score and aggregation_status.
    BlueprintTransformer attempts to extract final_score and aggregation_status from scoring_result
    and TraceScoringPayloadDTO strictly validates them according to Phase 9 schema rules.
    """
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_sdui, workflow_repo=mock_repo_sdui, comp_repo=mock_repo_sdui, identity_repo=mock_repo_sdui
    )

    mock_execution = ExecutionRecord(
        id="exe_3333333344444444",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_scoring",
                content={
                    "scoring_result": {
                        "total_score": 4.5,
                        "final_score": 4.5,
                        "penalties_applied": [],
                        "aggregation_status": "V2 Commensurate Average of 2 matrices",
                    }
                },
            )
        ],
    )
    mock_repo_sdui.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_3333333344444444")

    assert dto.global_score == 4.5


@pytest.mark.asyncio
async def test_blueprint_virtual_matrix_allows_missing_justification(mock_repo_transformer: Any) -> None:
    """Tier 4 Bug Hunting: Reproduce bug where mathematically generated matrix blocks lack justification."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000006",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_virtual_math",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 50.0,
                        # NO justification field provided (e.g., from Waterfall engine)
                    }
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )

    # This should NOT raise an exception, it should handle missing justification gracefully.
    dto = await transformer.build_report_dto("exe_0000000000000006", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.score == 50.0
    assert axis.row_explanation == ""  # Should default to empty string, not crash


@pytest.mark.asyncio
async def test_blueprint_xai_extensions_type_coercion(mock_repo_transformer: Any) -> None:
    """Verifies that invalid/empty types inside LLM dynamic extensions are coerced cleanly."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000007",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_xai_coercion",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 90.0,
                        "justification": "Checked with coercions.",
                        "extensions": {
                            "confidence": "",  # Empty string float coercion test
                            "risk_flag": "OWASP LLM09 (Overreliance) - Warning here.",  # Text description boolean coercion test  # noqa: E501
                            "remediation_steps": ["Step 1", "Step 2"],  # List array string coercion test
                            "coaching": None,
                        },
                    }
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )
    # This should succeed without raising any Pydantic ValidationError.
    dto = await transformer.build_report_dto("exe_0000000000000007", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.confidence is None
    assert axis.risk_flag is True
    assert axis.remediation_steps == "Step 1\nStep 2"


@pytest.mark.asyncio
async def test_blueprint_quotes_and_row_explanation_visibility(mock_repo_transformer: Any) -> None:
    """Tier 4 Bug Hunting: Reproduce bug where row_explanation is suppressed when quotes are shown,
    and quotes are not deduplicated.
    """
    from backend_v2.models.v2_core import RenderedSynthesisCache

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000008",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                synthesized_markdown="Global MD", row_explanations={"blk_1234abcd1234abcd": "This should not be empty!"}
            )
        },
        execution_trace=[
            TraceEvent(
                step_name="step_test",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 100.0,
                    },
                    "atom_quotes": {
                        "blk_1234abcd1234abcd": [
                            "This is a duplicated quote.",
                            "This is a duplicated quote.",
                            "This is a unique quote.",
                        ]
                    },
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
    )

    dto = await transformer.build_report_dto("exe_0000000000000008", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]

    # 1. row_explanation MUST NOT be suppressed when quotes are visible
    assert axis.row_explanation == "This should not be empty!"

    # 2. Duplicate quotes MUST be removed
    assert axis.quotes_list is not None
    assert len(axis.quotes_list) == 2
    assert "This is a duplicated quote." in axis.quotes_list
    assert "This is a unique quote." in axis.quotes_list
