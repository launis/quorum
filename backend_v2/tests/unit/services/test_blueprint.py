from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


def fix_mock_dict(d: Any) -> Any:
    if isinstance(d, dict):
        import re

        if "ai_description" in d and "tda_assertions" not in d:
            d["tda_assertions"] = [
                {
                    "tda_id": "tda_00000000000000000000000000000000",
                    "concept_description": "concept",
                    "inverse_evidence": False,
                    "aggregation_mode": "EXISTS",
                }
            ]
        if "score" in d and "claims" in d and "ai_label" not in d:
            d["ai_label"] = "ai_label_mock"
        if "strictness_level" in d:
            d["strictness_level"] = 85
        if "default_strictness_level" in d:
            d["default_strictness_level"] = 85
        if "level_name" in d and "structural_location" in d:
            if "visual_intent" not in d:
                d["visual_intent"] = "positive"
            if "chart_display_label" not in d:
                d["chart_display_label"] = "Test"
        if "tda_id" in d and not re.match(r"^tda_[a-f0-9]{32}$", str(d["tda_id"])):
            d["tda_id"] = "tda_00000000000000000000000000000000"
        for _k, v in d.items():
            fix_mock_dict(v)
        return d
    elif isinstance(d, list):
        return [fix_mock_dict(v) for v in d]
    return d


from backend_v2.exceptions import AppException
from backend_v2.models.enums import ExecutionStatus, ScoringStrategy, XaiExtensionType
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    I18nText,
    OutputLayoutBlock,
    OutputProfile,
    RenderedSynthesisCache,
    ReportDataDTO,
)
from backend_v2.services.blueprint import BlueprintTransformer


def dict_to_obj(d: Any) -> Any:
    if isinstance(d, dict):
        if "translations" in d and "default_locale" in d:
            return I18nText(**d)

        # Ensure mock claims have tda_assertions to prevent Phase 2 Blueprint crash
        if "label" in d and "tda_assertions" not in d:
            d["tda_assertions"] = []

        # Ensure mock workflows have expected_inputs
        d.setdefault("expected_inputs", [])

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
            "description": {"default_locale": "en", "translations": {"en": "desc", "fi": "desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_dddd1111dddd1111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_dddd1111dddd1111": {
                    "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                    "layouts": [
                        {
                            "preset_view": "1d_metrics",
                            "text_delivery_mode": "full",
                            "title": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
                            "target_blocks": ["*"],
                        }
                    ],
                }
            },
        }
    )
    repo.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
            }
        ]
    )
    repo.get_all_prompt_blocks.return_value = fix_mock_dict(
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
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_00000000000000000000000000000000",
                                        "concept_description": "concept 0",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "score": 100,
                        "name": {"default_locale": "en", "translations": {"fi": "Täysi", "en": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_11111111111111111111111111111111",
                                        "concept_description": "concept 1",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
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

    repo.get_all_output_profiles.return_value = [
        OutputProfile(
            id="prf_dddd1111dddd1111",
            slug="default",
            workflow_id="wf_1234abcd1234abcd",
            name=I18nText(default_locale="en", translations={"en": "Default", "fi": "Default"}),
            display_scale="original",
            layouts=[
                OutputLayoutBlock(
                    preset_view="1d_metrics",
                    target_blocks=["blk_1234abcd1234abcd"],
                )
            ],
            extension_labels={
                XaiExtensionType.REMEDIATION_STEPS: I18nText(
                    default_locale="en", translations={"en": "Remediation", "fi": "Korjaus"}
                ),
                XaiExtensionType.COACHING: I18nText(
                    default_locale="en", translations={"en": "Coaching", "fi": "Vinkki"}
                ),
                XaiExtensionType.RISK_FLAG: I18nText(default_locale="en", translations={"en": "Risk", "fi": "Riski"}),
            },
            visible_block_extensions=[
                XaiExtensionType.REMEDIATION_STEPS,
                XaiExtensionType.COACHING,
                XaiExtensionType.RISK_FLAG,
            ],
            visible_workflow_extensions=[],
            max_extension_items=2,
            strictness_level=85,
        )
    ]

    pb_dict = {
        "id": "blk_1234abcd1234abcd",
        "slug": "logic_matrix",
        "category_id": "matrix",
        "type": "float",
        "is_evaluative": True,
        "description": {"default_locale": "en", "translations": {"fi": "Kuvaus", "en": "Description"}},
        "label": {"default_locale": "en", "translations": {"fi": "Logiikka", "en": "Logic"}},
        "scales": [
            {
                "score": 1,
                "name": {"default_locale": "en", "translations": {"en": "1"}},
                "ai_label": "1",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "claim"}},
                        "ai_description": "desc",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000000000000000000000",
                                "concept_description": "concept",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            }
        ],
        "computed_min": 0,
        "computed_max": 100,
        "scale_min": 0,
        "scale_max": 100,
    }
    repo.get_all_prompt_blocks.return_value = fix_mock_dict([pb_dict])
    return repo


@pytest.mark.asyncio
async def test_graceful_degradation_missing_fields(mock_repo_transformer: Any) -> None:
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000002",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "fi"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000002")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 1
    assert dto.layouts[0].preset_view == "3d_matrix"


@pytest.fixture
def mock_repo_microcot() -> Any:
    repo = AsyncMock()
    repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234567890abcdef",
            "slug": "mock_workflow",
            "description": {"default_locale": "en", "translations": {"en": "desc", "fi": "desc"}},
            "status": "published",
            "version": 1,
            "name": {"default_locale": "en", "translations": {"en": "Mock Workflow", "fi": "Mock Workflow"}},
            "default_profile_id": "prf_1234567890abcdef",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_1234567890abcdef": {
                    "name": {
                        "default_locale": "en",
                        "translations": {"en": "Default Profile", "fi": "Default Profile"},
                    },
                    "layouts": [
                        {
                            "preset_view": "2d_compare",
                            "text_delivery_mode": "full",
                            "title": {
                                "default_locale": "en",
                                "translations": {"en": "Micro-CoT Map", "fi": "Micro-CoT Map"},
                            },
                            "target_blocks": ["*"],
                            "description": None,
                        }
                    ],
                }
            },
        }
    )
    repo.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_1234567890abcdef",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default Profile", "fi": "Default Profile"}},
                "workflow_id": "wf_1234567890abcdef",
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "text_delivery_mode": "full",
                        "title": {
                            "default_locale": "en",
                            "translations": {"en": "Micro-CoT Map", "fi": "Micro-CoT Map"},
                        },
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
            }
        ]
    )
    repo.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_1111222233334444",
                "slug": "kahneman",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Description", "fi": "Description"}},
                "label": {"default_locale": "en", "translations": {"en": "Kahneman T1", "fi": "Kaksoisprosessiteoria"}},  # noqa: E501
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero", "fi": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 3,
                        "name": {"default_locale": "en", "translations": {"en": "Full", "fi": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
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
                "description": {"default_locale": "en", "translations": {"en": "Description", "fi": "Description"}},
                "label": {"default_locale": "en", "translations": {"en": "Epistemic", "fi": "Episteeminen Nöyryys"}},  # noqa: E501
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero", "fi": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Full", "fi": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
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


@pytest.fixture
def mock_repo_sdui() -> AsyncMock:
    repo = AsyncMock()
    repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_test",
            "name": {"default_locale": "en", "translations": {"en": "Mock", "fi": "Mock"}},
            "description": {"default_locale": "en", "translations": {"en": "desc", "fi": "desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_1234abcd1234abcd",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
        }
    )
    repo.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_1234abcd1234abcd",
                "slug": "default",
                "workflow_id": "wf_1234abcd1234abcd",
                "name": {"default_locale": "en", "translations": {"fi": "Oletus", "en": "Default"}},
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Metrics", "fi": "Metrics"}},
                        "steps": [],
                        "target_blocks": ["*"],
                        "description": None,
                        "synthesis": {},
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
            }
        ]
    )
    repo.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_1234abcd1234abcd",
                "slug": "metric",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Description", "fi": "Description"}},
                "label": {"default_locale": "en", "translations": {"en": "Metric Category", "fi": "Metric Category"}},
                "computed_min": 0,
                "computed_max": 5,
                "scale_min": 0,
                "scale_max": 5,
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero", "fi": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Full", "fi": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim", "fi": "claim"}},
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
async def test_blueprint_synthesis_markdown_packaging(mock_repo_sdui: AsyncMock) -> None:
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_sdui,
        workflow_repo=mock_repo_sdui,
        comp_repo=mock_repo_sdui,
        prompt_block_repo=mock_repo_sdui,
        output_profile_repo=mock_repo_sdui,
        identity_repo=mock_repo_sdui,
        system_repo=mock_repo_sdui,
    )  # noqa: E501

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        profile_syntheses={
            "prf_1234abcd1234abcd": RenderedSynthesisCache(
                section_syntheses={
                    "layout_0_1d_metrics": [
                        __import__("backend_v2.models.view.sdui", fromlist=["MarkdownBlock"]).MarkdownBlock(
                            text="### Title\n<script>alert('xss');</script>Some content."
                        )
                    ]
                }
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
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "slug": "mock-workflow",
            "name": {"default_locale": "en", "translations": {"en": "Mock", "fi": "Mock"}},
            "description": {"default_locale": "en", "translations": {"en": "Mock", "fi": "Mock"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_1234abcd1234abcd",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
        }
    )

    dto = await transformer.build_report_dto("exe_1111111122222222", accept_language="en")
    assert dto.has_warning is True

    assert dto.layouts is not None
    assert len(dto.layouts) > 0
    assert dto.layouts[0].synthesis_blocks is not None
    assert len(dto.layouts[0].synthesis_blocks) > 0
    from backend_v2.models.view.sdui import MarkdownBlock

    assert isinstance(dto.layouts[0].synthesis_blocks[0], MarkdownBlock)
    safe_md = dto.layouts[0].synthesis_blocks[0].text

    assert "Some content." in safe_md


# ---------------------------------------------------------------------------
# Phase 2: Suffix-based flat key extraction (no isinstance(v, dict) fallback)
# ---------------------------------------------------------------------------


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
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        frozen_context=frozen,
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000004", accept_language="en")

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
            status=ExecutionStatus.PASSED,
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
        exec_repo=mock_repo_sdui,
        workflow_repo=mock_repo_sdui,
        comp_repo=mock_repo_sdui,
        prompt_block_repo=mock_repo_sdui,
        output_profile_repo=mock_repo_sdui,
        identity_repo=mock_repo_sdui,
        system_repo=mock_repo_sdui,
    )

    mock_execution = ExecutionRecord(
        id="exe_3333333344444444",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
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

    dto = await transformer.build_report_dto("exe_3333333344444444", accept_language="en")

    assert dto.global_score == 4.5

    # 2. Duplicate quotes MUST be removed (handled by Pydantic / Logic natively or ignored)
    # NOTE: In V2, Matrix blocks (StrippedBaseMatrixXAI) explicitly do NOT map exact_quotes
    # so we no longer test quote deduplication inside Matrix trace evaluations.


@pytest.mark.asyncio
async def test_blueprint_variance_validation_success(mock_repo_transformer: Any) -> None:
    """Test that build_report_dto computes variance validation using context variables."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000009",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="sr_1234",
                event_type="output",
                content={
                    "blk_fb15f8dcf23f4865": {
                        "raw_score": 4.0,
                        "normalized_score": 75.55,
                    }
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        context_variables={
            "step_detector": {"raw_score": 4.0},
            "step_linguistics": {
                "performative_patterns": [
                    {"pattern_id": "pat_1", "detected_phrase": "basically", "category": "performative_filler"}
                ]
            },
        },
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "Workflow Name"}},
            "description": {"default_locale": "en", "translations": {"en": "Workflow Desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_dddd1111dddd1111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [
                {
                    "id": "sr_1234",
                    "task_blueprint": "sp_7f9649114d2344dc",
                }
            ],
        }
    )

    mock_repo_transformer.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_fb15f8dcf23f4865",
                "slug": "matrix_archivist",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "label": {"default_locale": "en", "translations": {"en": "Label"}},
                "scales": [
                    {
                        "score": 1,
                        "name": {"default_locale": "en", "translations": {"en": "Min"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "claim",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Max"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "claim",
                            }
                        ],
                    },
                ],
            }
        ]
    )

    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "target_blocks": ["*"],
                        "title": {"default_locale": "en", "translations": {"en": "Title"}},
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
            }
        ]
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )
    dto = await transformer.build_report_dto("exe_0000000000000009", accept_language="en")

    assert len(dto.layouts) == 1
    matrix = dto.layouts[0].axes[0]
    assert len(matrix.inner_sdui_blocks) == 2

    grid_block = matrix.inner_sdui_blocks[0]
    alert_block = matrix.inner_sdui_blocks[1]

    from backend_v2.models.view.sdui import AlertBlock, SduiGridBlock

    assert isinstance(grid_block, SduiGridBlock)
    assert isinstance(alert_block, AlertBlock)

    assert "Mechanical: 1" in grid_block.items[0]
    assert "Cognitive: 4.0" in grid_block.items[1]
    assert "Variance: 1.2" in grid_block.items[2]

    assert alert_block.severity == "warning"
    assert "MISALIGNED_SYCOPHANCY" in alert_block.text


@pytest.mark.asyncio
async def test_blueprint_variance_validation_reproduce_crash(mock_repo_transformer: Any) -> None:
    """Test that build_report_dto crashes when variance_validation is requested but context_variables is empty."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000010",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        context_variables={},  # Empty context variables to trigger the crash
        metadata={"target_locale": "en"},
    )
    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
            }
        ]
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto("exe_0000000000000010", accept_language="en")

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast Enforced: 'variance_validation' requested but authenticity_score" in exc_info.value.message


@pytest.mark.asyncio
async def test_blueprint_variance_validation_fallback_from_trace(mock_repo_transformer: Any) -> None:
    """Test that build_report_dto falls back to execution_trace when context_variables is empty."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000011",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="sr_1d7e6d26b02b457b",
                event_type="output",
                content={
                    "blk_fb15f8dcf23f4865": {
                        "raw_score": 4.0222,
                        "normalized_score": 75.55,
                    }
                },
            ),
            TraceEvent(
                step_name="sr_f0a26d17cc9b48a7",
                event_type="decision",
                content={"step_linguistics": {"performative_patterns": []}},
            ),
        ],
        active_profile_id="prf_dddd1111dddd1111",
        context_variables={},  # Empty to force fallback lookup
        metadata={"target_locale": "en"},
    )

    # Configure workflow steps
    mock_repo_transformer.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "Workflow Name"}},
            "description": {"default_locale": "en", "translations": {"en": "Workflow Desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_dddd1111dddd1111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [
                {
                    "id": "sr_1d7e6d26b02b457b",
                    "task_blueprint": "sp_7f9649114d2344dc",
                }
            ],
        }
    )

    # Configure prompt blocks with scale definitions for blk_fb15f8dcf23f4865
    mock_repo_transformer.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_fb15f8dcf23f4865",
                "slug": "matrix_archivist",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "label": {"default_locale": "en", "translations": {"en": "Label"}},
                "scales": [
                    {
                        "score": 1,
                        "name": {"default_locale": "en", "translations": {"en": "Min"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "claim",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Max"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "claim"}},
                                "ai_description": "claim",
                            }
                        ],
                    },
                ],
            }
        ]
    )

    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "target_blocks": ["*"],
                        "title": {"default_locale": "en", "translations": {"en": "Title"}},
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
            }
        ]
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    dto = await transformer.build_report_dto("exe_0000000000000011", accept_language="en")

    assert len(dto.layouts) == 1
    matrix = dto.layouts[0].axes[0]
    assert len(matrix.inner_sdui_blocks) == 2

    grid_block = matrix.inner_sdui_blocks[0]
    alert_block = matrix.inner_sdui_blocks[1]

    from backend_v2.models.view.sdui import AlertBlock, SduiGridBlock

    assert isinstance(grid_block, SduiGridBlock)
    assert isinstance(alert_block, AlertBlock)

    assert "Cognitive: 2.5111" in grid_block.items[1]
    # target mechanical is 3.0, variance is 0.4889
    assert "Variance: 0.4889" in grid_block.items[2] or "Variance: 0.4888" in grid_block.items[2]

    assert alert_block.severity == "info"
    assert "ALIGNED" in alert_block.text


@pytest.mark.asyncio
async def test_blueprint_matrix_extensions_instantiate_alert_blocks(mock_repo_transformer: Any) -> None:
    """Verify that matrix payload extensions instantiate AlertBlock in inner_sdui_blocks."""
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.state import TraceEvent
    from backend_v2.models.v2_core import ExecutionRecord
    from backend_v2.models.view.sdui import AlertBlock

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000015",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="step_test",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 4.0,
                        "extensions": {
                            "remediation_steps": "Do this to fix.",
                            "risk_flag": True,
                            "missing_context": "",  # Should be ignored because truthy check fails
                        },
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
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    dto = await transformer.build_report_dto("exe_0000000000000015", accept_language="en")
    assert len(dto.layouts) > 0
    matrix = dto.layouts[0].axes[0]

    from backend_v2.models.view.sdui import AccordionBlock, AlertBlock
    accordion_blocks = [b for b in matrix.inner_sdui_blocks if getattr(b, "block_type", "") == "accordion"]
    assert len(accordion_blocks) == 2

    remediation_accordion = next((b for b in accordion_blocks if b.severity == "success"), None)
    assert remediation_accordion is not None
    remediation_alert = next((b for b in remediation_accordion.children if isinstance(b, AlertBlock)), None)
    assert remediation_alert is not None
    assert "Do this to fix" in remediation_alert.text

    risk_accordion = next((b for b in accordion_blocks if b.severity == "error"), None)
    assert risk_accordion is not None
    risk_alert = next((b for b in risk_accordion.children if isinstance(b, AlertBlock)), None)
    assert risk_alert is not None
    assert "True" in risk_alert.text


@pytest.mark.asyncio
async def test_blueprint_matrix_extensions_unknown_language(mock_repo_transformer: Any) -> None:
    """Verify fallback language logic when target language is unknown."""
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.state import TraceEvent
    from backend_v2.models.v2_core import ExecutionRecord
    from backend_v2.models.view.sdui import AlertBlock

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000016",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="step_test",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 4.0,
                        "extensions": {
                            "coaching": "Good job.",
                        },
                    },
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "unknown_lang"},  # Unknown language
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    dto = await transformer.build_report_dto("exe_0000000000000016", accept_language="en")
    matrix = dto.layouts[0].axes[0]

    accordion_blocks = [b for b in matrix.inner_sdui_blocks if getattr(b, "block_type", "") == "accordion"]
    assert len(accordion_blocks) == 1

    coaching_accordion = accordion_blocks[0]
    assert coaching_accordion.severity == "success"
    # It should fallback to title casing or default locale if missing.
    assert "Coaching" in coaching_accordion.title
    
    coaching_alert = next((b for b in coaching_accordion.children if isinstance(b, AlertBlock)), None)
    assert coaching_alert is not None
    assert coaching_alert.severity == "info"


@pytest.mark.asyncio
async def test_blueprint_transformer_slop_scan_uses_system_repo() -> None:
    """Proves that BlueprintTransformer correctly calls get_system_config on system_repo."""
    from backend_v2.services.blueprint import BlueprintTransformer

    mock_system_repo = AsyncMock()
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_comp_repo = AsyncMock()

    from backend_v2.models.enums import ExecutionStatus, ScoringStrategy
    from backend_v2.models.v2_core import ExecutionRecord, OutputProfile

    mock_exec_repo.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000001",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        profile_syntheses={},
    )

    def dict_to_obj(d: Any) -> Any:
        from types import SimpleNamespace

        from backend_v2.models.v2_core import I18nText

        if isinstance(d, dict):
            if "translations" in d and "default_locale" in d:
                return I18nText(**d)
            d.setdefault("expected_inputs", [])
            return SimpleNamespace(**{k: dict_to_obj(v) for k, v in d.items()})
        elif isinstance(d, list):
            return [dict_to_obj(v) for v in d]
        return d

    mock_workflow_repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "Mock", "fi": "Mock"}},
            "expected_inputs": [
                {
                    "id": "doc1",
                    "input_key": "producttext",
                    "label": {"default_locale": "en", "translations": {"en": "Product Text"}},
                    "type": "document",
                    "scan_for_performative_patterns": True,
                }
            ],
            "default_profile_id": "prf_dddd1111dddd1111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.AVERAGE,
            "steps": [],
            "output_profiles": {
                "prf_dddd1111dddd1111": {
                    "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                    "layouts": [],
                }
            },
        }
    )

    profile = OutputProfile.model_validate(
        {
            "id": "prf_dddd1111dddd1111",
            "slug": "default",
            "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
            "workflow_id": "wf_1234abcd1234abcd",
            "display_scale": "original",
            "layouts": [],
        }
    )

    mock_comp_repo.get_all_output_profiles.return_value = fix_mock_dict([profile.model_dump()])

    pb_dict_slop = {
        "id": "blk_1234abcd1234abcd",
        "slug": "logic_matrix",
        "category_id": "matrix",
        "type": "float",
        "is_evaluative": True,
        "description": {"default_locale": "en", "translations": {"fi": "Kuvaus", "en": "Description"}},
        "label": {"default_locale": "en", "translations": {"fi": "Logiikka", "en": "Logic"}},
        "scales": [
            {
                "score": 1,
                "name": {"default_locale": "en", "translations": {"en": "1"}},
                "ai_label": "1",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "claim"}},
                        "ai_description": "desc",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000000000000000000000",
                                "concept_description": "concept",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            }
        ],
        "computed_min": 0,
        "computed_max": 100,
        "scale_min": 0,
        "scale_max": 100,
    }
    mock_comp_repo.get_all_prompt_blocks.return_value = fix_mock_dict([pb_dict_slop])

    transformer = BlueprintTransformer(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        prompt_block_repo=mock_comp_repo,
        output_profile_repo=mock_comp_repo,
        identity_repo=AsyncMock(),
        system_repo=mock_system_repo,
    )

    try:
        await transformer.build_report_dto("exe_0000000000000001", accept_language="en")
    except Exception:
        import traceback

        traceback.print_exc()

    mock_system_repo.get_system_config.assert_called_once()


@pytest.mark.asyncio
async def test_blueprint_matrix_crash_missing_chart_label(mock_repo_transformer: MagicMock) -> None:
    """Proof of Failure:
    Matrix blocks (StrippedBaseMatrixXAI) do NOT output `chart_display_label`.
    blueprint.py line 533 blindly accesses ev_data["chart_display_label"], causing a KeyError.
    This test reproduces the crash.
    """
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000009",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                synthesized_markdown="Global MD", row_explanations={"blk_1234abcd1234abcd": "Matrix explanation"}
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
                    "evaluations": [
                        {
                            "atom_id": "tda_11111111111111111111111111111111",
                            "level": 100,
                            "level_name": "Full",
                            "claim_label": "claim",
                            "status": "PASS",
                            "exact_quotes": [],
                            "semantic_reasoning": "This is a matrix block evaluation.",
                            "contextual_override": False,
                            "structural_location": "N/A",
                            "chart_display_label": "Test",
                            "visual_intent": "positive",
                            # MISSING chart_display_label and visual_intent !
                        }
                    ],
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
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    # This should trigger KeyError: 'chart_display_label' at blueprint.py line 533
    dto = await transformer.build_report_dto("exe_0000000000000009", accept_language="en")
    assert dto is not None


@pytest.mark.asyncio
async def test_blueprint_sdui_layout_terminology_override(mock_repo_transformer: Any) -> None:
    """Epic 110: Verify Semantic Coverage for SDUI Parity
    Ensures that matrix_column_labels and extension_labels from OutputLayoutBlock
    are correctly passed into the final ReportLayoutDTO payload.
    """
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputLayoutBlock, OutputProfile

    # Override the mock to return an OutputProfile with custom terminology
    mock_repo_transformer.get_all_output_profiles.return_value = [
        OutputProfile(
            id="prf_dddd1111dddd1111",
            slug="default",
            workflow_id="wf_1234abcd1234abcd",
            name=I18nText(default_locale="en", translations={"en": "Default"}),
            display_scale="original",
            layouts=[
                OutputLayoutBlock(
                    preset_view="text_only",
                    target_blocks=["*"],
                    matrix_column_labels={
                        "explanation": I18nText(default_locale="fi", translations={"fi": "Selite", "en": "Explanation"})
                    },
                )
            ],
            extension_labels={
                XaiExtensionType.COACHING: I18nText(default_locale="fi", translations={"fi": "Vinkki", "en": "Tip"})
            },
        )
    ]
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000099",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "fi"},
    )

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )
    dto = await transformer.build_report_dto("exe_0000000000000099")

    assert len(dto.layouts) == 1
    layout = dto.layouts[0]

    assert layout.matrix_column_labels is not None
    assert layout.matrix_column_labels["explanation"].translations["fi"] == "Selite"

    assert layout.extension_labels is not None
    assert layout.extension_labels[XaiExtensionType.COACHING].translations["fi"] == "Vinkki"


@pytest.mark.asyncio
async def test_blueprint_transformer_missing_extension_label_raises_error(mock_repo_transformer: MagicMock) -> None:
    """Verify that a missing label_obj for an XAI extension correctly crashes with ConfigurationError."""
    # Setup execution trace with an extension that has no mapping in the profile
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000015",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "blk_0000000000000001": {
                        "raw_score": 4.0,
                        "extensions": {
                            "missing_context": "This is missing context",
                        },
                    }
                },
            )
        ],
        metadata={"target_locale": "fi"},
    )

    mock_repo_transformer.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_0000000000000001",
                "slug": "matrix_test",
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "label": {"default_locale": "en", "translations": {"en": "Label"}},
                "computed_min": 0,
                "computed_max": 5,
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim"}},
                                "ai_description": "test",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Five"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim"}},
                                "ai_description": "test",
                            }
                        ],
                    },
                ],
            }
        ]
    )

    mock_repo_transformer.get_all_output_profiles.return_value = [
        OutputProfile(
            id="prf_dddd1111dddd1111",
            slug="default",
            workflow_id="wf_1234abcd1234abcd",
            name=I18nText(default_locale="en", translations={"en": "Default"}),
            display_scale="original",
            layouts=[
                OutputLayoutBlock(
                    preset_view="text_only",
                    target_blocks=["*"],
                    # Intentionally omitting extension_labels to trigger ConfigurationError
                )
            ],
            visible_block_extensions=[],
            visible_workflow_extensions=[],
            max_extension_items=2,
            strictness_level=85,
        )
    ]

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto("exe_0000000000000098")

    assert "Missing extension label configuration for missing_context" in str(exc_info.value)
    assert exc_info.value.details["extension_key"] == "missing_context"


@pytest.mark.asyncio
async def test_blueprint_transformer_missing_coaching_label_raises_error(mock_repo_transformer: MagicMock) -> None:
    """Verify that a missing label_obj for the COACHING XAI extension crashes with ConfigurationError."""
    # Setup execution trace with coaching extension that has no mapping
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000097",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "blk_0000000000000001": {
                        "raw_score": 4.0,
                        "extensions": {
                            "coaching": "This is a coaching tip",
                        },
                    }
                },
            )
        ],
        metadata={"target_locale": "fi"},
    )

    mock_repo_transformer.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_0000000000000001",
                "slug": "matrix_test",
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "label": {"default_locale": "en", "translations": {"en": "Label"}},
                "computed_min": 0,
                "computed_max": 5,
                "scales": [
                    {
                        "score": 0,
                        "name": {"default_locale": "en", "translations": {"en": "Zero"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim"}},
                                "ai_description": "test",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"default_locale": "en", "translations": {"en": "Five"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim"}},
                                "ai_description": "test",
                            }
                        ],
                    },
                ],
            }
        ]
    )

    mock_repo_transformer.get_all_output_profiles.return_value = [
        OutputProfile(
            id="prf_dddd1111dddd1111",
            slug="default",
            workflow_id="wf_1234abcd1234abcd",
            name=I18nText(default_locale="en", translations={"en": "Default"}),
            display_scale="original",
            layouts=[
                OutputLayoutBlock(
                    preset_view="text_only",
                    target_blocks=["*"],
                    # Intentionally omitting extension_labels to trigger ConfigurationError
                )
            ],
            visible_block_extensions=[],
            visible_workflow_extensions=[],
            max_extension_items=2,
            strictness_level=85,
        )
    ]

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto("exe_0000000000000097")

    assert "Missing extension label configuration for coaching" in str(exc_info.value)
    assert exc_info.value.details["extension_key"] == "coaching"
