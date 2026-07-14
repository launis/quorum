from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


def fix_mock_dict(d):
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
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_dddd1111dddd1111": {
                    "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                    "synthesis": None,
                    "layouts": [
                        {
                            "preset_view": "1d_metrics",
                            "text_delivery_mode": "full",
                            "title": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
                            "target_blocks": ["*"],
                            "synthesis": None,
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
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
                        "target_blocks": ["*"],
                        "synthesis": None,
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
            layouts=[OutputLayoutBlock(preset_view="1d_metrics", target_blocks=["blk_1234abcd1234abcd"])],
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
async def test_build_report_dto_maps_correctly(mock_repo_transformer: Any) -> None:
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000001",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
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
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000001", accept_language="en")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 1
    assert len(dto.layouts[0].axes) == 1

    axis = dto.layouts[0].axes[0]
    assert axis.name in ["Mock Workflow", "step_analyst", "matrix_logic1234", "test_k", "Logic", "Logic *"]  # noqa: E501
    assert axis.score == 75.0
    assert axis.row_explanation == ""


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
    assert len(dto.layouts) == 0


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
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_1234567890abcdef": {
                    "name": {
                        "default_locale": "en",
                        "translations": {"en": "Default Profile", "fi": "Default Profile"},
                    },
                    "synthesis": None,
                    "layouts": [
                        {
                            "preset_view": "2d_compare",
                            "text_delivery_mode": "full",
                            "title": {
                                "default_locale": "en",
                                "translations": {"en": "Micro-CoT Map", "fi": "Micro-CoT Map"},
                            },
                            "target_blocks": ["*"],
                            "synthesis": None,
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
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "text_delivery_mode": "full",
                        "title": {
                            "default_locale": "en",
                            "translations": {"en": "Micro-CoT Map", "fi": "Micro-CoT Map"},
                        },
                        "target_blocks": ["*"],
                        "synthesis": None,
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


@pytest.mark.asyncio
async def test_blueprint_crashes_on_naked_microcot_dict(mock_repo_microcot: Any, mock_repo_transformer: Any) -> None:
    mock_repo_microcot.get_execution.return_value = ExecutionRecord(
        id="exe_abcdef1234567890",
        workflow_id="wf_1234567890abcdef",
        status=ExecutionStatus.PASSED,
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
        prompt_block_repo=mock_repo_microcot,
        output_profile_repo=mock_repo_microcot,
        identity_repo=mock_repo_microcot,
        system_repo=mock_repo_transformer,
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
            "name": {"default_locale": "en", "translations": {"en": "Mock", "fi": "Mock"}},
            "description": {"default_locale": "en", "translations": {"en": "desc", "fi": "desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_1234abcd1234abcd",
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
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Metrics", "fi": "Metrics"}},
                        "steps": [],
                        "target_blocks": ["*"],
                        "synthesis": None,
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
async def test_blueprint_zero_math_rounding(mock_repo_sdui: AsyncMock) -> None:
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

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.global_score == 4.6

    assert len(dto.layouts) > 0
    axis = next(a for a in dto.layouts[0].axes if a.name in ["Metric Category", "Metric Category *"])
    assert axis.score == 3.1


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
                content_blocks=[
                    {"type": "markdown", "content": "### Title\\n<script>alert('xss');</script>Some content."}
                ]
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

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.has_warning is True

    assert dto.content_blocks is not None
    assert len(dto.content_blocks) > 0
    safe_md = dto.content_blocks[0]["content"]

    assert "Some content." in safe_md


# ---------------------------------------------------------------------------
# Phase 2: Suffix-based flat key extraction (no isinstance(v, dict) fallback)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_xai_extraction_works_for_nested_dict(mock_repo_transformer: Any) -> None:
    """Phase 9: Verify XAI metadata is extracted from nested dicts."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000003",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
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
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )  # noqa: E501
    dto = await transformer.build_report_dto("exe_0000000000000003", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.score == 85.0
    assert axis.row_explanation == ""
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

    dto = await transformer.build_report_dto("exe_3333333344444444")

    assert dto.global_score == 4.5


@pytest.mark.asyncio
async def test_blueprint_virtual_matrix_allows_missing_justification(mock_repo_transformer: Any) -> None:
    """Tier 4 Bug Hunting: Reproduce bug where mathematically generated matrix blocks lack justification."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000006",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
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
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
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
        status=ExecutionStatus.PASSED,
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
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )
    # This should succeed without raising any Pydantic ValidationError.
    dto = await transformer.build_report_dto("exe_0000000000000007", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.score == 90.0
    assert axis.confidence is None
    assert axis.risk_flag is True
    assert axis.remediation_steps == "Step 1\nStep 2"


@pytest.mark.asyncio
async def test_blueprint_2d_compare_graceful_degradation(mock_repo_sdui: AsyncMock) -> None:
    """Tier 4 Bug Hunting: 2d_compare must gracefully degrade to 'bar' if only 1 axis is found, instead of crashing."""
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_sdui,
        workflow_repo=mock_repo_sdui,
        comp_repo=mock_repo_sdui,
        prompt_block_repo=mock_repo_sdui,
        output_profile_repo=mock_repo_sdui,
        identity_repo=mock_repo_sdui,
        system_repo=mock_repo_sdui,
    )
    mock_repo_sdui.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_1234abcd1234abcd",
                "slug": "default",
                "workflow_id": "wf_1234abcd1234abcd",
                "name": {"default_locale": "en", "translations": {"fi": "Oletus", "en": "Default"}},
                "synthesis": None,
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Metrics", "fi": "Metrics"}},
                        "steps": [],
                        "target_blocks": ["*"],
                        "synthesis": None,
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
    mock_execution = ExecutionRecord(
        id="exe_5555555555555555",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_1234abcd1234abcd",
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 3.0,
                        "justification": "Valid matrix 1",
                    }
                    # Missing second matrix, so axes count will be 1
                },
            )
        ],
    )
    mock_repo_sdui.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_5555555555555555")
    assert len(dto.layouts) > 0
    assert dto.layouts[0].preset_view == "1d_metrics", "Should have gracefully degraded to '1d_metrics'"


@pytest.mark.asyncio
async def test_blueprint_quotes_and_row_explanation_visibility(mock_repo_transformer: Any) -> None:
    """Tier 4 Bug Hunting: Reproduce bug where row_explanation is suppressed when quotes are shown,
    and quotes are not deduplicated.
    """
    from backend_v2.models.v2_core import RenderedSynthesisCache

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000008",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
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
                    "evaluations": [
                        {
                            "atom_id": "tda_11111111111111111111111111111111",
                            "level": 100,
                            "level_name": "Full",
                            "claim_label": "claim",
                            "status": "PASS",
                            "exact_quotes": [
                                "This is a unique quote.",
                                "This is a duplicated quote.",
                                "This is a duplicated quote.",
                            ],
                            "semantic_reasoning": "Reason",
                            "contextual_override": False,
                            "structural_location": "N/A",
                            "chart_display_label": "Test",
                            "visual_intent": "positive",
                            "internal_logic_en": {"chain_of_thought": "cot", "confidence_score": 1.0},
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

    dto = await transformer.build_report_dto("exe_0000000000000008", accept_language="en")

    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]

    # 1. row_explanation MUST NOT be suppressed when quotes are visible
    assert axis.row_explanation == "This should not be empty!"

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
        execution_trace=[],
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
    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "synthesis": None,
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
    dto = await transformer.build_report_dto("exe_0000000000000009", accept_language="en")

    assert dto.grouped_extensions is not None
    assert "variance_validation" in dto.grouped_extensions
    ext = dto.grouped_extensions["variance_validation"][0]
    assert ext["extension_type"] == "variance_validation"
    assert ext["mechanical_metric_ref"] == "performative_phrases_count"
    assert ext["cognitive_metric_ref"] == "llm_authenticity_score"
    # authenticity_score = 4.0, performative_phrases_count = 1 -> target mechanical = 3.0 - 0.2 = 2.8.
    # Variance: abs(4.0 - 2.8) = 1.2
    assert ext["variance_score"] == 1.2
    assert ext["alignment_verdict"] == "MISALIGNED_SYCOPHANCY"


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
                "synthesis": None,
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
                "synthesis": None,
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

    dto = await transformer.build_report_dto("exe_0000000000000011", accept_language="en")

    assert dto.grouped_extensions is not None
    assert "variance_validation" in dto.grouped_extensions
    ext = dto.grouped_extensions["variance_validation"][0]
    assert ext["extension_type"] == "variance_validation"
    assert ext["mechanical_metric_ref"] == "performative_phrases_count"
    assert ext["cognitive_metric_ref"] == "llm_authenticity_score"

    # authenticity_score scaled from raw 4.0222 (on 1-5 scale) to (1-3 scale):
    # ((4.0222 - 1.0) / 4.0) * 2.0 + 1.0 = 2.5111
    # performative_phrases_count = 0
    # Target mechanical score = 3.0 - 0.0 * 0.2 = 3.0
    # Variance = abs(2.5111 - 3.0) = 0.4889
    assert round(ext["variance_score"], 4) == 0.4889
    assert ext["alignment_verdict"] == "ALIGNED"


@pytest.mark.asyncio
async def test_blueprint_skips_raw_extensions_when_curated_exists(mock_repo_transformer: Any) -> None:
    """Verify that blueprint.py skips appending raw matrix extensions when curated/synthesized ones exist,
    and falls back to "" for row explanation when explanations cache is empty.
    """
    from backend_v2.models.dtos.synthesis import XaiHighlightItem
    from backend_v2.models.v2_core import RenderedSynthesisCache

    # Set up mock repos to return custom execution record
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000012",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                synthesized_markdown="Global MD",
                row_explanations={},  # Empty explanations cache to trigger fallback to ""
            )
        },
        execution_trace=[
            TraceEvent(
                step_name="step_test",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 4.0,
                        "justification": "This raw justification should NOT be in row_explanation",
                        "extensions": {
                            "coaching": "This is raw coaching tip",
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

    # Let's populate grouped_extensions with a curated item for 'coaching'
    # Normally this happens when global curation runs

    # We will invoke build_report_dto and verify behavior
    dto = await transformer.build_report_dto("exe_0000000000000012", accept_language="en")

    # Verify row_explanation falls back to "" instead of the raw justification
    assert len(dto.layouts) == 1
    axis = dto.layouts[0].axes[0]
    assert axis.row_explanation == ""

    # Now let's inject a curated coaching tip into the transformer execution cache path:
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000013",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                synthesized_markdown="Global MD",
                xai_highlights=[XaiHighlightItem(extension_type="coaching", content="This is curated coaching tip")],
            )
        },
        execution_trace=[
            TraceEvent(
                step_name="step_test",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 4.0,
                        "extensions": {
                            "coaching": "This is raw coaching tip",
                        },
                    },
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )

    dto_curated = await transformer.build_report_dto("exe_0000000000000013", accept_language="en")

    # Check that coaching list contains ONLY the curated item, and the raw item was skipped
    assert dto_curated.grouped_extensions is not None
    assert "coaching" in dto_curated.grouped_extensions
    coaching_items = dto_curated.grouped_extensions["coaching"]
    assert len(coaching_items) == 1
    assert coaching_items[0]["content"] == "This is curated coaching tip"
    assert coaching_items[0].get("_is_synthesized") is True


async def test_blueprint_synthesis_cache_skips_raw_extensions_entirely(mock_repo_transformer: Any) -> None:
    """Verify that if a synthesis cache is active, raw extensions are skipped entirely
    even if the cache has NO curated highlights for a specific category (leaving it empty).
    """
    from backend_v2.models.dtos.synthesis import XaiHighlightItem
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.state import TraceEvent
    from backend_v2.models.v2_core import ExecutionRecord, RenderedSynthesisCache

    # Active cache exists, but ONLY contains remediation_steps, NO coaching or justification
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000014",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                synthesized_markdown="Global MD",
                xai_highlights=[
                    XaiHighlightItem(extension_type="remediation_steps", content="This is curated remediation")
                ],
            )
        },
        execution_trace=[
            TraceEvent(
                step_name="step_test",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 4.0,
                        "extensions": {
                            "coaching": "This is raw coaching tip",
                            "justification": "This is raw justification",
                            "remediation_steps": "This is raw remediation",
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

    # Mock visible extensions for this test and restore after
    profiles = mock_repo_transformer.get_all_output_profiles.return_value
    orig_exts = profiles[0].visible_block_extensions
    profiles[0] = profiles[0].model_copy(
        update={
            "visible_block_extensions": [
                XaiExtensionType.JUSTIFICATION,
                XaiExtensionType.COACHING,
                XaiExtensionType.REMEDIATION_STEPS,
            ]
        }
    )
    try:
        dto = await transformer.build_report_dto("exe_0000000000000014", accept_language="en")
    finally:
        profiles[0] = profiles[0].model_copy(update={"visible_block_extensions": orig_exts})

    # Check that remediation_steps has only the curated item
    assert dto.grouped_extensions is not None
    assert "remediation_steps" in dto.grouped_extensions
    remediation_items = dto.grouped_extensions["remediation_steps"]
    assert len(remediation_items) == 1
    assert remediation_items[0]["content"] == "This is curated remediation"

    # Check that coaching and justification have NO items (raw tips are skipped entirely)
    assert dto.grouped_extensions is not None
    assert "coaching" in dto.grouped_extensions
    assert len(dto.grouped_extensions["coaching"]) == 0
    assert "justification" in dto.grouped_extensions
    assert len(dto.grouped_extensions["justification"]) == 0


@pytest.mark.asyncio
async def test_blueprint_slop_scanning_applied_successfully(mock_repo_transformer: Any) -> None:
    """Verify that build_report_dto runs slop scanning, detects jargon, reduces score and sets warnings."""
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.state import TraceEvent
    from backend_v2.models.v2_core import ExecutionRecord

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000005",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 100.0,
                        "normalized_score": 100.0,
                        "justification": "Very logical.",
                    }
                },
            ),
            TraceEvent(
                step_name="step_scoring",
                event_type="output",
                content={
                    "scoring_result": {
                        "total_score": 100.0,
                        "final_score": 100.0,
                        "penalties_applied": ["PENALTY_SECURITY:10"],
                        "aggregation_status": "V2 Commensurate Average of 1 matrices",
                    }
                },
            ),
            TraceEvent(
                step_name="step_synthesis",
                event_type="output",
                content={
                    "_evaluative_matrices": {"matrix_1": 100.0},
                    "synthesized_markdown": "We need to leverage our robust synergy and drive disruption.",
                },
            ),
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
    )

    mock_workflow = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}},
            "description": {"default_locale": "en", "translations": {"en": "desc", "fi": "desc"}},
            "status": "published",
            "version": 1,
            "default_profile_id": "prf_dddd1111dddd1111",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "expected_inputs": [
                {
                    "input_key": "history_text",
                    "label": {"default_locale": "en", "translations": {"en": "History", "fi": "Historia"}},
                    "required": True,
                    "scan_for_performative_patterns": True,
                    "description": {"default_locale": "en", "translations": {"en": "desc", "fi": "desc"}},
                }
            ],
            "output_profiles": {
                "prf_dddd1111dddd1111": {
                    "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                    "synthesis": None,
                    "layouts": [
                        {
                            "preset_view": "1d_metrics",
                            "text_delivery_mode": "full",
                            "title": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
                            "target_blocks": ["*"],
                            "synthesis": None,
                        }
                    ],
                }
            },
        }
    )
    mock_repo_transformer.get_workflow.return_value = mock_workflow

    mock_profiles = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "synthesis": {"synthesis_block_id": "blk_synthesis_999"},
                "content_blocks": [{"id": "blk_synthesis_999", "block_type": "markdown", "text": ""}],
                "layouts": [
                    {
                        "preset_view": "1d_metrics",
                        "text_delivery_mode": "full",
                        "title": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
                        "target_blocks": ["*"],
                    }
                ],
                "display_scale": "original",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "max_extension_items": 2,
                "strictness_level": 85,
            }
        ]
    )
    mock_repo_transformer.get_all_output_profiles.return_value = mock_profiles

    mock_repo_transformer.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "words": ["synergy", "disruption", "leverage", "robust"],
                "fuzz_threshold": 90.0,
            }
        },
    }

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    dto = await transformer.build_report_dto("exe_0000000000000005", accept_language="en")

    assert dto.has_warning is True
    # Base average is 100. Security penalty is 10%, Slop penalty is 5%.
    # Capped or combined penalty: 15%. Total score = 100 * 0.85 = 85.0
    assert dto.global_score == 85.0
    assert any(p.startswith("PENALTY_SLOP:") for p in dto.penalties_applied)
    slop_penalty = next(p for p in dto.penalties_applied if p.startswith("PENALTY_SLOP:"))
    phrases = slop_penalty.split(":", 1)[1].split(",")
    assert len(phrases) >= 3
    assert set(phrases).issubset({"synergy", "disruption", "leverage", "robust"})


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
async def test_blueprint_causal_mapping_reverse_lookup(mock_repo_transformer: Any) -> None:
    """Epic 87: Verifies that used_evidence_ids from Matrix output blocks are
    correctly mapped backwards into MCPAuditTrace.impacted_axis_names.
    """
    from backend_v2.models.v2_core import FrozenContext, MCPAuditTrace

    # 1) Setup a frozen context with a Tavily search trace
    frozen = FrozenContext(
        mcp_tool_audit=[
            MCPAuditTrace(
                id="tavily_1234",
                tool_id="mcp_tavily_search",
                step_name="step_1",
                query="AI ethics",
            ),
            MCPAuditTrace(
                id="tavily_5678",
                tool_id="mcp_tavily_search",
                step_name="step_2",
                query="Bias detection",
            ),
        ]
    )
    # 2) Setup Execution record where a block extraction references 'tavily_1234'
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000011112222",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    "blk_1234abcd1234abcd": {
                        "raw_score": 80.0,
                        "justification": "Checked with sources.",
                        "used_evidence_ids": ["tavily_1234"],
                    }
                },
            )
        ],
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
    )

    dto = await transformer.build_report_dto("exe_0000000011112222", accept_language="en")

    # 3) Verification:
    # There are 2 mcp traces. tavily_1234 should have "Logic" in impacted_axis_names (since blk_1234abcd1234abcd is "Logic").
    # tavily_5678 should have empty impacted_axis_names.

    assert len(dto.mcp_tool_audit) == 2

    trace_1234 = next(t for t in dto.mcp_tool_audit if t.id == "tavily_1234")
    trace_5678 = next(t for t in dto.mcp_tool_audit if t.id == "tavily_5678")

    assert "Logic *" in trace_1234.impacted_axis_names
    assert len(trace_5678.impacted_axis_names) == 0


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
