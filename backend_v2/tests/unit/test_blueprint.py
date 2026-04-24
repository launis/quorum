from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, RenderedSynthesisCache, ReportDataDTO
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.fixture
def mock_repo_transformer() -> Any:
    repo = AsyncMock()
    repo.get_workflow_by_id.return_value = {
        "id": "wf_1234abcd1234abcd",
        "slug": "wf_1",
        "name": {"default_locale": "en", "translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_dddd1111dddd1111",
        "output_profiles": {
            "prf_dddd1111dddd1111": {
                "name": {"default_locale": "en", "translations": {"en": "Default"}},
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "title": {"default_locale": "en", "translations": {"en": "Title"}},
                        "target_blocks": ["*"],
                        "show_text": True,
                    }
                ],
            }
        },
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_dddd1111dddd1111",
            "slug": "default",
            "name": {"default_locale": "en", "translations": {"en": "Default"}},
            "workflow_id": "wf_1234abcd1234abcd",
            "layouts": [
                {
                    "preset_view": "1d_metrics",
                    "title": {"default_locale": "en", "translations": {"en": "Title"}},
                    "target_blocks": ["*"],
                    "show_text": True,
                }
            ],
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1234abcd1234abcd",
            "slug": "matrix_logic1234",
            "category_id": "matrix",
            "label": {"translations": {"fi": "Logiikka", "en": "Logic"}},
            "scales": [
                {"score": 0, "name": {"translations": {"fi": "Nolla", "en": "Zero"}}},
                {"score": 100, "name": {"translations": {"fi": "Täysi", "en": "Full"}}},
            ],
            "computed_min": 0.0,
            "computed_max": 100.0,
        }
    ]
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
                    "blk_1234abcd1234abcd": 75.0,
                    "blk_1234abcd1234abcd_justification": "Very logical",
                    "synthesis": "Great job",
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(mock_repo_transformer)
    dto = await transformer.build_report_dto("exe_0000000000000001", accept_language="en")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 1
    assert len(dto.layouts[0].axes) == 1

    axis = dto.layouts[0].axes[0]
    assert axis.name in ["Mock Workflow", "step_analyst", "matrix_logic1234", "test_k", "Logic"]
    assert axis.score == 75.0
    assert axis.justification == "Very logical"


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
    transformer = BlueprintTransformer(mock_repo_transformer)
    dto = await transformer.build_report_dto("exe_0000000000000002")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 0


@pytest.fixture
def mock_repo_microcot() -> Any:
    repo = AsyncMock()
    repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567890abcdef",
        "slug": "mock_workflow",
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "status": "published",
        "version": 1,
        "name": {"default_locale": "en", "translations": {"en": "Mock Workflow"}},
        "default_profile_id": "prf_1234567890abcdef",
        "output_profiles": {
            "prf_1234567890abcdef": {
                "name": {"default_locale": "en", "translations": {"en": "Default Profile"}},
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "title": {"default_locale": "en", "translations": {"en": "Micro-CoT Map"}},
                        "target_blocks": ["*"],
                        "show_text": True,
                    }
                ],
            }
        },
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_1234567890abcdef",
            "slug": "default",
            "name": {"default_locale": "en", "translations": {"en": "Default Profile"}},
            "workflow_id": "wf_1234567890abcdef",
            "layouts": [
                {
                    "preset_view": "2d_compare",
                    "title": {"default_locale": "en", "translations": {"en": "Micro-CoT Map"}},
                    "target_blocks": ["*"],
                    "show_text": True,
                }
            ],
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "matrix_kahneman123",
            "slug": "kahneman",
            "category_id": "matrix",
            "label": {"translations": {"en": "Kahneman T1", "fi": "Kaksoisprosessiteoria"}},
            "scales": [
                {"score": 0, "name": {"translations": {"en": "Zero"}}},
                {"score": 3, "name": {"translations": {"en": "Full"}}},
            ],
            "computed_min": 0.0,
            "computed_max": 3.0,
        },
        {
            "id": "matrix_episteeminen123",
            "slug": "episteeminen",
            "category_id": "matrix",
            "label": {"translations": {"en": "Epistemic", "fi": "Episteeminen Nöyryys"}},
            "scales": [
                {"score": 0, "name": {"translations": {"en": "Zero"}}},
                {"score": 5, "name": {"translations": {"en": "Full"}}},
            ],
            "computed_min": 0.0,
            "computed_max": 5.0,
        },
    ]
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
                    "matrix_episteeminen123": 1.9,
                    "matrix_kahneman123": {
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

    transformer = BlueprintTransformer(mock_repo_microcot)

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto("exe_abcdef1234567890", accept_language="en")

    assert exc_info.value.status_code == 400
    assert "Invalid numeric score" in exc_info.value.message


@pytest.fixture
def mock_repo_sdui() -> AsyncMock:
    repo = AsyncMock(spec=AbstractWorkflowRepository)
    repo.get_workflow_by_id.return_value = {
        "id": "wf_1234abcd1234abcd",
        "slug": "wf_test",
        "name": {"default_locale": "en", "translations": {"en": "Mock"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_1234abcd1234abcd",
        "steps": [],
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_1234abcd1234abcd",
            "slug": "default",
            "workflow_id": "wf_1234abcd1234abcd",
            "name": {"default_locale": "en", "translations": {"fi": "Oletus", "en": "Default"}},
            "layouts": [
                {
                    "preset_view": "1d_metrics",
                    "title": {"default_locale": "en", "translations": {"en": "Metrics"}},
                    "steps": [],
                    "target_blocks": ["*"],
                    "show_text": True,
                }
            ],
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1234abcd1234abcd",
            "slug": "metric",
            "category_id": "matrix",
            "label": {"default_locale": "en", "translations": {"en": "Metric Category"}},
            "computed_min": 0.0,
            "computed_max": 5.0,
            "scales": [
                {"score": 0, "name": {"translations": {"en": "Zero"}}},
                {"score": 5, "name": {"translations": {"en": "Full"}}},
            ],
        }
    ]
    return repo


@pytest.mark.asyncio
async def test_blueprint_zero_math_rounding(mock_repo_sdui: AsyncMock) -> None:
    transformer = BlueprintTransformer(repo=mock_repo_sdui)

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "blk_1234abcd1234abcd": 3.14159,  # Should become 3.1
                    "scoring_result": {
                        "total_score": 4.567  # Should become 4.6
                    },
                },
            )
        ],
    )
    mock_repo_sdui.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.global_score == 4.6

    assert len(dto.layouts) > 0
    axis = next(a for a in dto.layouts[0].axes if a.name == "Metric Category")
    assert axis.score == 3.1


@pytest.mark.asyncio
async def test_blueprint_synthesis_markdown_packaging(mock_repo_sdui: AsyncMock) -> None:
    transformer = BlueprintTransformer(repo=mock_repo_sdui)

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

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.has_warning is True

    assert dto.synthesized_markdown is not None
    assert "<script>" not in dto.synthesized_markdown
    assert "Some content." in dto.synthesized_markdown


# ---------------------------------------------------------------------------
# Phase 2: Suffix-based flat key extraction (no isinstance(v, dict) fallback)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suffix_xai_extraction_works_for_flat_scalars(mock_repo_transformer: Any) -> None:
    """Phase 2: Verify suffix-based XAI metadata is extracted from flat step keys.
    After removing the isinstance(v, dict) branch, the ONLY valid lookup path
    for justification/coaching/etc. is via `{block_id}_justification` suffix keys.
    """
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000003",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": 85.0,
                    "blk_1234abcd1234abcd_justification": "Strictly suffix-based justification",
                    "blk_1234abcd1234abcd_coaching": "Keep it up",
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(mock_repo_transformer)
    dto = await transformer.build_report_dto("exe_0000000000000003", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.score == 85.0
    assert axis.justification == "Strictly suffix-based justification"
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
    transformer = BlueprintTransformer(mock_repo_transformer)
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
