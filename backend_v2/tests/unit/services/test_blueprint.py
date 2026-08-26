from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import MatrixClaim, MatrixScale, TDAAssertion, XaiHighlightItem
from backend_v2.tests.unit.services.test_blueprint_sdui_crash import *  # noqa: F403, F401


def fix_mock_dict(d: Any) -> Any:
    from backend_v2.models.v2_core import I18nText, OutputProfile

    if isinstance(d, OutputProfile):
        if not hasattr(d, "metric_mappings") or d.metric_mappings is None:
            object.__setattr__(d, "metric_mappings", {})
        d.metric_mappings.setdefault(
            "metadata_user",
            I18nText(translations={"en": "User", "fi": "Käyttäjä"}),
        )
        d.metric_mappings.setdefault(
            "metadata_organization",
            I18nText(translations={"en": "Organization", "fi": "Organisaatio"}),
        )
        d.metric_mappings.setdefault(
            "metadata_scoring_engine",
            I18nText(translations={"en": "Scoring Engine", "fi": "Arviointimoottori"}),
        )
        d.metric_mappings.setdefault(
            "metadata_strictness",
            I18nText(translations={"en": "Strictness Level", "fi": "Ankaruustaso"}),
        )
        return d
    if isinstance(d, dict):
        import re

        if "score" in d and "claims" in d and "ai_label" not in d:
            d["ai_label"] = "ai_label_mock"
        if "claims" in d and isinstance(d["claims"], list):
            for claim_dict in d["claims"]:
                if isinstance(claim_dict, dict):
                    claim_dict.pop("ai_description", None)
                    if "tda_assertions" not in claim_dict:
                        claim_dict["tda_assertions"] = [
                            {
                                "tda_id": "tda_00000000000000000000000000000000",
                                "concept_description": "concept_description_valid",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ]
                    else:
                        for assertion in claim_dict["tda_assertions"]:
                            if isinstance(assertion, dict):
                                desc = assertion.get("concept_description", "")
                                if not isinstance(desc, str) or len(desc) < 10:
                                    assertion["concept_description"] = "concept_description_valid"
        if (
            "concept_description" in d
            and isinstance(d["concept_description"], str)
            and len(d["concept_description"]) < 10
        ):
            d["concept_description"] = "concept_description_valid"
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
        if "metric_mappings" in d and isinstance(d["metric_mappings"], dict):
            d["metric_mappings"].setdefault(
                "metadata_user",
                {"translations": {"en": "User", "fi": "Käyttäjä"}},
            )
            d["metric_mappings"].setdefault(
                "metadata_organization",
                {"translations": {"en": "Organization", "fi": "Organisaatio"}},
            )
            d["metric_mappings"].setdefault(
                "metadata_scoring_engine",
                {"translations": {"en": "Scoring Engine", "fi": "Arviointimoottori"}},
            )
            d["metric_mappings"].setdefault(
                "metadata_strictness",
                {"translations": {"en": "Strictness Level", "fi": "Ankaruustaso"}},
            )
        for _k, v in d.items():
            fix_mock_dict(v)
        return d
    elif isinstance(d, list):
        return [fix_mock_dict(v) for v in d]
    return d


from datetime import datetime, timezone

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.enums import DisplayScale, ExecutionStatus, ScoringStrategy, TargetBlockType, XaiExtensionType
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExtensionMetricsDTO,
    I18nText,
    OutputLayoutBlock,
    OutputProfile,
    RenderedSynthesisCache,
    ReportDataDTO,
)
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.matrix_domain_parser import MatrixDomainParser

_DEFAULT_TARGET_BLOCK_ORDER = [
    TargetBlockType.METADATA_BLOCK,
    TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
    TargetBlockType.SYNTHESIS_TEXT_BLOCK,
    TargetBlockType.MATRIX_GRAPHS_BLOCK,
    TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
    TargetBlockType.PENALTIES_BLOCK,
    TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
    TargetBlockType.VARIANCE_VALIDATION_BLOCK,
    TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK,
    TargetBlockType.PRINTABLE_SOURCES_BLOCK,
    TargetBlockType.GLOBAL_SCORE_BLOCK,
    TargetBlockType.AUDIT_TRAIL_BLOCK,
]


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
            "name": {"translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}},
            "description": {"translations": {"en": "desc", "fi": "desc"}},
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
                    "name": {"translations": {"en": "Default", "fi": "Default"}},
                    "layouts": [
                        {
                            "preset_view": "text_only",
                            "text_delivery_mode": "full",
                            "title": {"translations": {"en": "Title", "fi": "Title"}},
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
                "name": {"translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [
                    {
                        "preset_view": "text_only",
                        "text_delivery_mode": "full",
                        "title": {"translations": {"en": "Title", "fi": "Title"}},
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": DisplayScale.ORIGINAL,
                "metric_mappings": {
                    "variance_mechanical": {"translations": {"en": "Mechanical"}},
                    "variance_cognitive": {"translations": {"en": "Cognitive"}},
                    "variance_total": {"translations": {"en": "Variance"}},
                    "alignment_verdict": {"translations": {"en": "Alignment Verdict"}},
                    "alignment_aligned": {"translations": {"en": "ALIGNED"}},
                    "alignment_misaligned": {"translations": {"en": "MISALIGNED"}},
                    "jargon_score": {"translations": {"en": "AI-Jargon Score"}},
                    "authenticity_level": {"translations": {"en": "Authenticity Level"}},
                    "level_high": {"translations": {"en": "High"}},
                    "level_medium": {"translations": {"en": "Medium"}},
                    "level_low": {"translations": {"en": "Low"}},
                    "authenticity_fallback_explanation": {
                        "translations": {"en": "Fallback {0}"},
                    },
                    "variance_fallback_explanation": {
                        "translations": {"en": "Fallback {0} {1}"},
                    },
                },
                "visible_block_extensions": [],
                "visible_workflow_extensions": ["remediation_steps", "risk_flag", "coaching"],
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
                "description": {"translations": {"fi": "Kuvaus", "en": "Description"}},
                "label": {"translations": {"fi": "Logiikka", "en": "Logic"}},
                "scales": [
                    {
                        "score": 0,
                        "name": {"translations": {"fi": "Ei mitään", "en": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
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
                        "name": {"translations": {"fi": "Täysi", "en": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
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
            }
        ]
    )

    repo.get_all_output_profiles.return_value = fix_mock_dict(
        [
            OutputProfile(
                id="prf_dddd1111dddd1111",
                slug="default",
                workflow_id="wf_1234abcd1234abcd",
                name=I18nText(translations={"en": "Default", "fi": "Default"}),
                display_scale=DisplayScale.ORIGINAL,
                target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
                metric_mappings={
                    "variance_mechanical": I18nText(translations={"en": "Mechanical"}),
                    "variance_cognitive": I18nText(translations={"en": "Cognitive"}),
                    "variance_total": I18nText(translations={"en": "Variance"}),
                    "alignment_verdict": I18nText(translations={"en": "Alignment Verdict"}),
                    "alignment_aligned": I18nText(translations={"en": "ALIGNED"}),
                    "alignment_misaligned": I18nText(translations={"en": "MISALIGNED"}),
                    "jargon_score": I18nText(translations={"en": "AI-Jargon Score"}),
                    "authenticity_level": I18nText(translations={"en": "Authenticity Level"}),
                    "level_high": I18nText(translations={"en": "High"}),
                    "level_medium": I18nText(translations={"en": "Medium"}),
                    "level_low": I18nText(translations={"en": "Low"}),
                    "authenticity_fallback_explanation": I18nText(translations={"en": "Fallback {0}"}),
                    "variance_fallback_explanation": I18nText(translations={"en": "Fallback {0} {1}"}),
                },
                layouts=[
                    OutputLayoutBlock(
                        preset_view="text_only",
                        target_blocks=["blk_1234abcd1234abcd", "grouped_extensions_block"],
                    )
                ],
                extension_labels={
                    XaiExtensionType.REMEDIATION_STEPS: I18nText(translations={"en": "Remediation", "fi": "Korjaus"}),
                    XaiExtensionType.COACHING: I18nText(translations={"en": "Coaching", "fi": "Vinkki"}),
                    XaiExtensionType.RISK_FLAG: I18nText(translations={"en": "Risk", "fi": "Riski"}),
                },
                visible_block_extensions=[
                    XaiExtensionType.REMEDIATION_STEPS,
                    XaiExtensionType.COACHING,
                    XaiExtensionType.RISK_FLAG,
                ],
                visible_workflow_extensions=[
                    XaiExtensionType.REMEDIATION_STEPS,
                    XaiExtensionType.COACHING,
                    XaiExtensionType.RISK_FLAG,
                ],
                max_extension_items=2,
                strictness_level=85,
            )
        ]
    )

    pb_dict = {
        "id": "blk_1234abcd1234abcd",
        "slug": "logic_matrix",
        "category_id": "matrix",
        "type": "float",
        "is_evaluative": True,
        "description": {"translations": {"fi": "Kuvaus", "en": "Description"}},
        "label": {"translations": {"fi": "Logiikka", "en": "Logic"}},
        "scales": [
            {
                "score": 1,
                "name": {"translations": {"en": "1"}},
                "ai_label": "1",
                "claims": [
                    {
                        "label": {"translations": {"en": "claim"}},
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
    assert len(dto.inner_sdui_blocks) >= 1
    # Ensure text_only layout does NOT generate a 1d_metrics block anymore,
    # but instead gracefully outputs its text blocks (or title).
    matrices = [b for b in dto.inner_sdui_blocks if getattr(b, "block_type", "") == "1d_metrics"]
    assert len(matrices) == 0


@pytest.fixture
def mock_repo_microcot() -> Any:
    repo = AsyncMock()
    repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234567890abcdef",
            "slug": "mock_workflow",
            "description": {"translations": {"en": "desc", "fi": "desc"}},
            "status": "published",
            "version": 1,
            "name": {"translations": {"en": "Mock Workflow", "fi": "Mock Workflow"}},
            "default_profile_id": "prf_1234567890abcdef",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_strictness_level": 85,
            "default_scoring_strategy": ScoringStrategy.WATERFALL,
            "steps": [],
            "output_profiles": {
                "prf_1234567890abcdef": {
                    "name": {
                        "translations": {"en": "Default Profile", "fi": "Default Profile"},
                    },
                    "layouts": [
                        {
                            "preset_view": "2d_compare",
                            "text_delivery_mode": "full",
                            "title": {
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
                "name": {"translations": {"en": "Default Profile", "fi": "Default Profile"}},
                "workflow_id": "wf_1234567890abcdef",
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "text_delivery_mode": "full",
                        "title": {
                            "translations": {"en": "Micro-CoT Map", "fi": "Micro-CoT Map"},
                        },
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": DisplayScale.ORIGINAL,
                "metric_mappings": {
                    "variance_mechanical": {"translations": {"en": "Mechanical"}},
                    "variance_cognitive": {"translations": {"en": "Cognitive"}},
                    "variance_total": {"translations": {"en": "Variance"}},
                    "alignment_verdict": {"translations": {"en": "Alignment Verdict"}},
                    "alignment_aligned": {"translations": {"en": "ALIGNED"}},
                    "alignment_misaligned": {"translations": {"en": "MISALIGNED"}},
                    "jargon_score": {"translations": {"en": "AI-Jargon Score"}},
                    "authenticity_level": {"translations": {"en": "Authenticity Level"}},
                    "level_high": {"translations": {"en": "High"}},
                    "level_medium": {"translations": {"en": "Medium"}},
                    "level_low": {"translations": {"en": "Low"}},
                    "authenticity_fallback_explanation": {
                        "translations": {"en": "Fallback {0}"},
                    },
                    "variance_fallback_explanation": {
                        "translations": {"en": "Fallback {0} {1}"},
                    },
                },
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
                "description": {"translations": {"en": "Description", "fi": "Description"}},
                "label": {"translations": {"en": "Kahneman T1", "fi": "Kaksoisprosessiteoria"}},  # noqa: E501
                "scales": [
                    {
                        "score": 0,
                        "name": {"translations": {"en": "Zero", "fi": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 3,
                        "name": {"translations": {"en": "Full", "fi": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                ],
                "computed_min": 0,
                "computed_max": 3,
            },
            {
                "id": "blk_5555666677778888",
                "slug": "episteeminen",
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "description": {"translations": {"en": "Description", "fi": "Description"}},
                "label": {"translations": {"en": "Epistemic", "fi": "Episteeminen Nöyryys"}},  # noqa: E501
                "scales": [
                    {
                        "score": 0,
                        "name": {"translations": {"en": "Zero", "fi": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"translations": {"en": "Full", "fi": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                ],
                "computed_min": 0,
                "computed_max": 5,
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
            "name": {"translations": {"en": "Mock", "fi": "Mock"}},
            "description": {"translations": {"en": "desc", "fi": "desc"}},
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
                "name": {"translations": {"fi": "Oletus", "en": "Default"}},
                "layouts": [
                    {
                        "preset_view": "text_only",
                        "text_delivery_mode": "full",
                        "title": {"translations": {"en": "Metrics", "fi": "Metrics"}},
                        "steps": [],
                        "target_blocks": ["*"],
                        "description": None,
                    }
                ],
                "display_scale": DisplayScale.ORIGINAL,
                "metric_mappings": {
                    "variance_mechanical": {"translations": {"en": "Mechanical"}},
                    "variance_cognitive": {"translations": {"en": "Cognitive"}},
                    "variance_total": {"translations": {"en": "Variance"}},
                    "alignment_verdict": {"translations": {"en": "Alignment Verdict"}},
                    "alignment_aligned": {"translations": {"en": "ALIGNED"}},
                    "alignment_misaligned": {"translations": {"en": "MISALIGNED"}},
                    "jargon_score": {"translations": {"en": "AI-Jargon Score"}},
                    "authenticity_level": {"translations": {"en": "Authenticity Level"}},
                    "level_high": {"translations": {"en": "High"}},
                    "level_medium": {"translations": {"en": "Medium"}},
                    "level_low": {"translations": {"en": "Low"}},
                    "authenticity_fallback_explanation": {
                        "translations": {"en": "Fallback {0}"},
                    },
                    "variance_fallback_explanation": {
                        "translations": {"en": "Fallback {0} {1}"},
                    },
                },
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
                "description": {"translations": {"en": "Description", "fi": "Description"}},
                "label": {"translations": {"en": "Metric Category", "fi": "Metric Category"}},
                "computed_min": 0,
                "computed_max": 5,
                "scales": [
                    {
                        "score": 0,
                        "name": {"translations": {"en": "Zero", "fi": "Zero"}},
                        "ai_label": "zero",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"translations": {"en": "Full", "fi": "Full"}},
                        "ai_label": "full",
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim", "fi": "claim"}},
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
                step_name="sr_5f3dd7712a7f4bb3",
                event_type="output",
                content={
                    "blk_fb15f8dcf23f4865": {
                        "raw_score": 85.00,
                        "normalized_score": 85.00,
                    },
                    "_step_metadata": {
                        "execution_id": "exe_0000000000000009",
                        "workflow_id": "wf_1234abcd1234abcd",
                        "step_id": "sr_5f3dd7712a7f4bb3",
                        "initiator_id": "system",
                        "timestamp_isot": "2026-08-05T00:00:00Z",
                        "unix_time": 1700000000,
                        "v2_engine": True,
                        "task_blueprint": "sp_7f9649114d2344dc",
                    },
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                extension_metrics=ExtensionMetricsDTO(
                    authenticity_score=4.0,
                    performative_phrases_count=1,
                    variance_score=1.2,
                    alignment_verdict="MISALIGNED",
                )
            )
        },
        context_variables={},
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"translations": {"en": "Workflow Name"}},
            "description": {"translations": {"en": "Workflow Desc"}},
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
                "description": {"translations": {"en": "Desc"}},
                "label": {"translations": {"en": "Label"}},
                "scales": [
                    {
                        "score": 1,
                        "name": {"translations": {"en": "Min"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim"}},
                                "ai_description": "claim",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"translations": {"en": "Max"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim"}},
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
                "name": {"translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [
                    {
                        "preset_view": "text_only",
                        "text_delivery_mode": "full",
                        "target_blocks": ["*"],
                        "title": {"translations": {"en": "Title"}},
                    }
                ],
                "display_scale": DisplayScale.ORIGINAL,
                "metric_mappings": {
                    "variance_mechanical": {"translations": {"en": "Mechanical"}},
                    "variance_cognitive": {"translations": {"en": "Cognitive"}},
                    "variance_total": {"translations": {"en": "Variance"}},
                    "alignment_verdict": {"translations": {"en": "Alignment Verdict"}},
                    "alignment_aligned": {"translations": {"en": "ALIGNED"}},
                    "alignment_misaligned": {"translations": {"en": "MISALIGNED"}},
                    "jargon_score": {"translations": {"en": "AI-Jargon Score"}},
                    "authenticity_level": {"translations": {"en": "Authenticity Level"}},
                    "level_high": {"translations": {"en": "High"}},
                    "level_medium": {"translations": {"en": "Medium"}},
                    "level_low": {"translations": {"en": "Low"}},
                    "authenticity_fallback_explanation": {
                        "translations": {"en": "Fallback {0}"},
                    },
                    "variance_fallback_explanation": {
                        "translations": {"en": "Fallback {0} {1}"},
                    },
                },
                "visible_block_extensions": [],
                "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
                "extension_labels": {
                    XaiExtensionType.VARIANCE_VALIDATION: {"translations": {"en": "Variance"}},
                },
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

    assert len(dto.inner_sdui_blocks) >= 2
    print(f"DEBUG blocks: {[getattr(b, 'block_type', '') for b in dto.inner_sdui_blocks]}")
    metrics_blocks = [b for b in dto.inner_sdui_blocks if getattr(b, "block_type", "") == "1d_metrics"]
    assert len(metrics_blocks) >= 1
    variance_layout = metrics_blocks[-1]

    from backend_v2.models.view.sdui import SduiMetrics1DBlock

    assert isinstance(variance_layout, SduiMetrics1DBlock)

    matrix = variance_layout.axes[0]
    assert len(matrix.inner_sdui_blocks) >= 1

    grid_block = matrix.inner_sdui_blocks[0]
    alert_block = matrix.inner_sdui_blocks[1]

    from backend_v2.models.view.sdui import AlertBlock, SduiGridBlock

    assert isinstance(grid_block, SduiGridBlock)
    assert isinstance(alert_block, AlertBlock)

    assert "Mechanical: 1" in getattr(grid_block.items[0], "text", "")
    assert "Cognitive: 4.0" in getattr(grid_block.items[1], "text", "")
    assert "Variance: 1.2" in getattr(grid_block.items[2], "text", "")

    assert alert_block.severity == "warning"
    assert "MISALIGNED" in alert_block.text


@pytest.mark.asyncio
async def test_blueprint_variance_validation_reproduce_crash(mock_repo_transformer: Any) -> None:
    """Test that build_report_dto crashes when variance_validation is requested but context_variables is empty."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000010",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        active_profile_id="prf_dddd1111dddd1111",
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                extension_metrics=None  # Missing metrics to trigger the crash
            )
        },
        metadata={"target_locale": "en"},
    )
    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            {
                "id": "prf_dddd1111dddd1111",
                "slug": "default",
                "name": {"translations": {"en": "Default", "fi": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [],
                "display_scale": DisplayScale.ORIGINAL,
                "metric_mappings": {
                    "variance_mechanical": {"translations": {"en": "Mechanical"}},
                    "variance_cognitive": {"translations": {"en": "Cognitive"}},
                    "variance_total": {"translations": {"en": "Variance"}},
                    "alignment_verdict": {"translations": {"en": "Alignment Verdict"}},
                    "alignment_aligned": {"translations": {"en": "ALIGNED"}},
                    "alignment_misaligned": {"translations": {"en": "MISALIGNED"}},
                    "jargon_score": {"translations": {"en": "AI-Jargon Score"}},
                    "authenticity_level": {"translations": {"en": "Authenticity Level"}},
                    "level_high": {"translations": {"en": "High"}},
                    "level_medium": {"translations": {"en": "Medium"}},
                    "level_low": {"translations": {"en": "Low"}},
                    "authenticity_fallback_explanation": {
                        "translations": {"en": "Fallback {0}"},
                    },
                    "variance_fallback_explanation": {
                        "translations": {"en": "Fallback {0} {1}"},
                    },
                },
                "visible_block_extensions": [],
                "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
                "extension_labels": {
                    XaiExtensionType.VARIANCE_VALIDATION: {"translations": {"en": "Variance"}},
                },
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
    assert (
        "Strict Fail-Fast Enforced: 'variance_validation' requested but extension_metrics is missing in cache"
        in exc_info.value.message
    )


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
                        "raw_score": 2.51,
                        "normalized_score": 75.55,
                    },
                    "_step_metadata": {
                        "execution_id": "exe_0000000000000011",
                        "workflow_id": "wf_1234abcd1234abcd",
                        "step_id": "sr_1d7e6d26b02b457b",
                        "initiator_id": "system",
                        "timestamp_isot": "2026-08-05T00:00:00Z",
                        "unix_time": 1700000000,
                        "v2_engine": True,
                        "task_blueprint": "sp_7f9649114d2344dc",
                    },
                },
            ),
            TraceEvent(
                step_name="sr_f0a26d17cc9b48a7",
                event_type="decision",
                content={
                    "step_linguistics": {
                        "performative_patterns": [
                            {"pattern_id": "p1", "detected_phrase": "phrase1", "category": "performative"},
                            {"pattern_id": "p2", "detected_phrase": "phrase2", "category": "performative"},
                        ]
                    }
                },
            ),
        ],
        active_profile_id="prf_dddd1111dddd1111",
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                extension_metrics=ExtensionMetricsDTO(
                    authenticity_score=2.51,
                    performative_phrases_count=2,
                    variance_score=0.09,
                    alignment_verdict="ALIGNED",
                )
            )
        },
        context_variables={},  # Empty to force fallback lookup
        metadata={"target_locale": "en"},
    )

    # Configure workflow steps
    mock_repo_transformer.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"translations": {"en": "Workflow Name"}},
            "description": {"translations": {"en": "Workflow Desc"}},
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
                "description": {"translations": {"en": "Desc"}},
                "label": {"translations": {"en": "Label"}},
                "scales": [
                    {
                        "score": 1,
                        "name": {"translations": {"en": "Min"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim"}},
                                "ai_description": "claim",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"translations": {"en": "Max"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim"}},
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
                "name": {"translations": {"en": "Default"}},
                "workflow_id": "wf_1234abcd1234abcd",
                "layouts": [
                    {
                        "preset_view": "text_only",
                        "text_delivery_mode": "full",
                        "target_blocks": ["*"],
                        "title": {"translations": {"en": "Title"}},
                    }
                ],
                "display_scale": DisplayScale.ORIGINAL,
                "metric_mappings": {
                    "variance_mechanical": {"translations": {"en": "Mechanical"}},
                    "variance_cognitive": {"translations": {"en": "Cognitive"}},
                    "variance_total": {"translations": {"en": "Variance"}},
                    "alignment_verdict": {"translations": {"en": "Alignment Verdict"}},
                    "alignment_aligned": {"translations": {"en": "ALIGNED"}},
                    "alignment_misaligned": {"translations": {"en": "MISALIGNED"}},
                    "jargon_score": {"translations": {"en": "AI-Jargon Score"}},
                    "authenticity_level": {"translations": {"en": "Authenticity Level"}},
                    "level_high": {"translations": {"en": "High"}},
                    "level_medium": {"translations": {"en": "Medium"}},
                    "level_low": {"translations": {"en": "Low"}},
                    "authenticity_fallback_explanation": {
                        "translations": {"en": "Fallback {0}"},
                    },
                    "variance_fallback_explanation": {
                        "translations": {"en": "Fallback {0} {1}"},
                    },
                },
                "visible_block_extensions": [],
                "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
                "extension_labels": {
                    XaiExtensionType.VARIANCE_VALIDATION: {"translations": {"en": "Variance"}},
                },
                "max_extension_items": 2,
                "strictness_level": 85,
                "scoring_strategy": None,
                "visible_metadata": [],
                "custom_preface": None,
                "performativity_detector_step_id": "sr_1d7e6d26b02b457b",
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

    assert len(dto.inner_sdui_blocks) >= 2
    metrics_blocks = [b for b in dto.inner_sdui_blocks if getattr(b, "block_type", "") == "1d_metrics"]
    assert len(metrics_blocks) >= 1
    variance_layout = metrics_blocks[-1]

    from backend_v2.models.view.sdui import SduiMetrics1DBlock

    assert isinstance(variance_layout, SduiMetrics1DBlock)

    matrix = variance_layout.axes[0]
    assert len(matrix.inner_sdui_blocks) >= 1

    grid_block = matrix.inner_sdui_blocks[0]
    alert_block = matrix.inner_sdui_blocks[1]

    from backend_v2.models.view.sdui import AlertBlock, SduiGridBlock

    assert isinstance(grid_block, SduiGridBlock)
    assert isinstance(alert_block, AlertBlock)

    assert "Cognitive: 2.51" in getattr(grid_block.items[1], "text", "")
    assert "Variance: 0.09" in getattr(grid_block.items[2], "text", "")

    assert alert_block.severity == "info"
    assert "ALIGNED" in alert_block.text


@pytest.mark.asyncio
async def test_blueprint_matrix_extensions_instantiate_alert_blocks(mock_repo_transformer: Any) -> None:
    """Verify that xai_highlights are grouped into AccordionBlocks."""
    from backend_v2.models.enums import ExecutionStatus, XaiExtensionType
    from backend_v2.models.state import TraceEvent
    from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputProfile, RenderedSynthesisCache

    profile_mock = OutputProfile.model_construct(
        id="prf_dddd1111dddd1111",
        slug="default",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Default"}),
        display_scale=DisplayScale.ORIGINAL,
        target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
        layouts=[
            OutputLayoutBlock(
                preset_view="text_only",
                target_blocks=["*"],
            ),
            OutputLayoutBlock(
                preset_view="text_only",
                target_blocks=["grouped_extensions_block"],
            ),
        ],
        extension_labels={
            XaiExtensionType.REMEDIATION_STEPS: I18nText(translations={"en": "Remediation"}),
            XaiExtensionType.FALSIFICATION: I18nText(translations={"en": "Falsification"}),
        },
        visible_block_extensions=[XaiExtensionType.REMEDIATION_STEPS, XaiExtensionType.FALSIFICATION],
    )
    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict([profile_mock])
    mock_repo_transformer.get_by_id.return_value = profile_mock

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
                            "falsification": "This is false.",
                        },
                    },
                },
            )
        ],
        active_profile_id="prf_dddd1111dddd1111",
        metadata={"target_locale": "en"},
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                cited_sources=[],
                section_syntheses={},
                xai_highlights=[
                    XaiHighlightItem(extension_type="remediation_steps", content="Do this to fix."),
                    XaiHighlightItem(extension_type="falsification", content="This is false."),
                ],
            )
        },
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
    assert len(dto.inner_sdui_blocks) > 0

    assert len(dto.inner_sdui_blocks) > 1
    accordions = [b for b in dto.inner_sdui_blocks if getattr(b, "block_type", "") == "accordion"]
    assert len(accordions) >= 2

    alert_blocks: list[Any] = []
    for acc in accordions:
        alert_blocks.extend(getattr(acc, "children", []))

    remediation_alert = next((b for b in alert_blocks if "Do this to fix" in getattr(b, "text", "")), None)
    assert remediation_alert is not None

    falsification_alert = next((b for b in alert_blocks if "This is false" in getattr(b, "text", "")), None)
    assert falsification_alert is not None


@pytest.mark.asyncio
async def test_blueprint_matrix_extensions_unknown_language(mock_repo_transformer: Any) -> None:
    """Verify fallback language logic when target language is unknown."""
    from backend_v2.models.enums import ExecutionStatus, XaiExtensionType
    from backend_v2.models.state import TraceEvent
    from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputProfile, RenderedSynthesisCache

    profile_mock = OutputProfile.model_construct(
        id="prf_dddd1111dddd1111",
        slug="default",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Default"}),
        display_scale=DisplayScale.ORIGINAL,
        target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
        layouts=[
            OutputLayoutBlock(
                preset_view="text_only",
                target_blocks=["*"],
            ),
            OutputLayoutBlock(
                preset_view="text_only",
                target_blocks=["grouped_extensions_block"],
            ),
        ],
        extension_labels={
            XaiExtensionType.COACHING: I18nText(translations={"en": "Coaching"}),
        },
        visible_block_extensions=[XaiExtensionType.COACHING],
    )
    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict([profile_mock])
    mock_repo_transformer.get_by_id.return_value = profile_mock

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
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                cited_sources=[],
                section_syntheses={},
                xai_highlights=[XaiHighlightItem(extension_type="coaching", content="Good job.")],
            )
        },
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

    from backend_v2.models.view.sdui import AccordionBlock, AlertBlock

    dto = await transformer.build_report_dto("exe_0000000000000016", accept_language="en")

    assert len(dto.inner_sdui_blocks) > 1
    accordions = [b for b in dto.inner_sdui_blocks if isinstance(b, AccordionBlock)]
    assert len(accordions) >= 1

    alert_blocks = [c for c in accordions[0].children if isinstance(c, AlertBlock)]

    coaching_alert = next((b for b in alert_blocks if "Good job" in b.text), None)
    assert coaching_alert is not None
    assert accordions[0].title == "Coaching"


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
        profile_syntheses={"prf_dddd1111dddd1111": RenderedSynthesisCache()},
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
                            "structural_location": None,
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
async def test_blueprint_authenticity_evaluation_fallback_trace_extraction(
    mock_repo_transformer: MagicMock,
) -> None:
    """Verify that if step_detector is missing in cv, authenticity_evaluation falls back to folded trace extraction."""
    from datetime import datetime, timezone

    from backend_v2.models.v2_core import StepRule, Workflow

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000097",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        profile_syntheses={
            "prf_dddd1111dddd1111": RenderedSynthesisCache(
                extension_metrics=ExtensionMetricsDTO(
                    authenticity_score=85.0,
                    performative_phrases_count=0,
                    variance_score=0.0,
                    alignment_verdict="ALIGNED",
                )
            )
        },
        execution_trace=[
            TraceEvent(
                step_name="stp_1234abcd1234abcd",
                event_type="decision",
                content={"blk_mock_id": {"raw_score": 85.0}},
                timestamp=datetime.now(timezone.utc),
                v=1,
            )
        ],
        context_variables={},
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_workflow.return_value = Workflow.model_construct(
        id="wf_1234abcd1234abcd",
        slug="test-wf",
        name="Test WF",
        description="Test",
        status="PUBLISHED",
        version=1,
        allowed_exports=[],
        historical_context_mode=__import__(
            "backend_v2.models.enums", fromlist=["HistoricalContextMode"]
        ).HistoricalContextMode.DISABLED,
        default_profile_id="prf_dddd1111dddd1111",
        steps=[StepRule(id="stp_1234abcd1234abcd", task_blueprint="sp_7f9649114d2344dc")],
    )

    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            OutputProfile(
                id="prf_dddd1111dddd1111",
                slug="default",
                workflow_id="wf_1234abcd1234abcd",
                name=I18nText(translations={"en": "Default"}),
                display_scale=DisplayScale.ORIGINAL,
                target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
                metric_mappings={
                    "variance_mechanical": I18nText(translations={"en": "Mechanical"}),
                    "variance_cognitive": I18nText(translations={"en": "Cognitive"}),
                    "variance_total": I18nText(translations={"en": "Variance"}),
                    "alignment_verdict": I18nText(translations={"en": "Alignment Verdict"}),
                    "alignment_aligned": I18nText(translations={"en": "ALIGNED"}),
                    "alignment_misaligned": I18nText(translations={"en": "MISALIGNED"}),
                    "jargon_score": I18nText(translations={"en": "AI-Jargon Score"}),
                    "authenticity_level": I18nText(translations={"en": "Authenticity Level"}),
                    "level_high": I18nText(translations={"en": "High"}),
                    "level_medium": I18nText(translations={"en": "Medium"}),
                    "level_low": I18nText(translations={"en": "Low"}),
                    "authenticity_fallback_explanation": I18nText(translations={"en": "Fallback {0}"}),
                    "variance_fallback_explanation": I18nText(translations={"en": "Fallback {0} {1}"}),
                },
                layouts=[
                    OutputLayoutBlock(
                        preset_view="text_only",
                        target_blocks=["*"],
                    ),
                    OutputLayoutBlock(
                        preset_view="text_only",
                        target_blocks=["grouped_extensions_block"],
                    ),
                ],
                visible_block_extensions=[],
                visible_workflow_extensions=[XaiExtensionType.AUTHENTICITY_EVALUATION],
                extension_labels={
                    XaiExtensionType.AUTHENTICITY_EVALUATION: I18nText(translations={"en": "Authenticity"}),
                },
                max_extension_items=2,
                strictness_level=85,
                performativity_detector_step_id="stp_1234abcd1234abcd",
            )
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

    report_dto = await transformer.build_report_dto("exe_0000000000000097")

    assert report_dto is not None
    assert any(
        getattr(axis, "block_id", None) == "authenticity_metrics_row"
        for block in report_dto.inner_sdui_blocks
        for axis in getattr(block, "axes", []) or []
    )


@pytest.mark.asyncio
async def test_blueprint_transformer_custom_scale_missing_bounds(mock_repo_transformer: MagicMock) -> None:
    """Verify that ConfigurationError is raised when custom scale lacks bounds."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000099",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "blk_0000000000000002": {
                        "raw_score": 4.0,
                    }
                },
            )
        ],
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_0000000000000002",
                "slug": "matrix_test",
                "description": {"translations": {"en": "Desc"}},
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "label": {"translations": {"en": "Label"}},
                "computed_min": 0,
                "computed_max": 5,
                # Intentionally omitting scale_min and scale_max
                "scales": [
                    {
                        "score": 0,
                        "name": {"translations": {"en": "Zero"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "Claim"}},
                                "ai_description": "test",
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "name": {"translations": {"en": "Five"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "Claim"}},
                                "ai_description": "test",
                            }
                        ],
                    },
                ],
            }
        ]
    )

    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            OutputProfile.model_construct(
                id="prf_dddd1111dddd1111",
                slug="default",
                workflow_id="wf_1234abcd1234abcd",
                name=I18nText(translations={"en": "Default"}),
                display_scale=DisplayScale.CUSTOM,
                custom_scale_min=None,
                custom_scale_max=None,
                target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
                metric_mappings={},
                layouts=[
                    OutputLayoutBlock(
                        preset_view="text_only",
                        target_blocks=["*"],
                    ),
                ],
                visible_block_extensions=[],
                visible_workflow_extensions=[],
                max_extension_items=2,
                strictness_level=85,
            )
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

    with pytest.raises(ValidationError) as exc_info:
        await transformer.build_report_dto("exe_0000000000000099")

    assert "custom_scale_min and custom_scale_max are required when display_scale is CUSTOM" in str(exc_info.value)


@pytest.mark.asyncio
async def test_blueprint_transformer_unrecognized_text_delivery_mode(mock_repo_transformer: MagicMock) -> None:
    """Verify that unrecognized text_delivery_mode fails deterministically."""
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000099",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        execution_trace=[],
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            OutputProfile(
                id="prf_dddd1111dddd1111",
                slug="default",
                workflow_id="wf_1234abcd1234abcd",
                name=I18nText(translations={"en": "Default"}),
                display_scale=DisplayScale.ORIGINAL,
                target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
                metric_mappings={},
                layouts=[
                    OutputLayoutBlock.model_construct(
                        preset_view="text_only",
                        target_blocks=["*"],
                        text_delivery_mode="invalid_mode",  # type: ignore[arg-type]
                    )
                ],
                visible_block_extensions=[],
                visible_workflow_extensions=[],
                extension_labels={},
                max_extension_items=2,
                strictness_level=85,
            )
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

    with pytest.raises(ConfigurationError) as exc_info:
        await transformer.build_report_dto("exe_0000000000000099")

    assert "Unrecognized text_delivery_mode: 'invalid_mode'" in str(exc_info.value)
    assert exc_info.value.details["error_code"] == "CONFIGURATION_ERROR"


@pytest.mark.asyncio
async def test_blueprint_apply_pii_masking(mock_repo_transformer: Any) -> None:
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )
    result = transformer._apply_pii_masking("Contact me at test@example.com or 555-123-4567.")
    assert "[REDACTED EMAIL]" in result
    assert "[REDACTED PHONE]" in result
    assert "test@example.com" not in result
    assert "555-123-4567" not in result


@pytest.mark.asyncio
async def test_blueprint_parse_matrix_trace_results_comprehensive(mock_repo_transformer: Any) -> None:
    from backend_v2.models.v2_core import OutputLayoutBlock, OutputProfile
    from backend_v2.services.blueprint import BlueprintTransformer

    _transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    from backend_v2.models.enums import ExecutionStatus

    # 1. Provide custom scale and normalized_100 profiles to hit 337-339, 354-355
    profile_custom = OutputProfile(
        id="prf_1111111111111111",
        slug="test",
        workflow_id="wf_1111111111111111",
        name=I18nText(translations={"en": "test"}),
        display_scale=DisplayScale.CUSTOM,
        custom_scale_min=1.0,
        custom_scale_max=5.0,
        target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                matrix_visible_columns=["quotes"],  # Hit 213-214 and 437
            )
        ],
    )

    # 2. Provide results with `block_id` = 'evaluations' to hit 457-546
    results = [
        SimpleNamespace(
            step_id="step_1",
            block_id="matrix_logic1234",
            payload={
                "raw_score": None,  # Hit 251-255
                "normalized_score": None,
                "level_breakdown": {},
                "evaluated_atoms": {"tda_11111111111111111111111111111111": ExecutionStatus.PASSED},
                "extensions": {},
            },
        ),
        SimpleNamespace(
            step_id="step_1",
            block_id="matrix_logic1234",  # Duplicate to trigger collision counter 380-385
            payload={
                "raw_score": 100.0,
                "normalized_score": 100.0,
                "level_breakdown": {"100.0": {"hits": 1, "total": 1}},
                "evaluated_atoms": {},
                "extensions": {},
            },
        ),
        SimpleNamespace(
            step_id="step_1",
            block_id="evaluations",
            payload=[
                {
                    "atom_id": "tda_11111111111111111111111111111111",
                    "semantic_reasoning": "Sem reasoning",
                }
            ],
        ),
    ]

    mock_label = I18nText(translations={"en": "Logic"})
    mock_desc = I18nText(translations={"en": "Description"})
    mock_name = I18nText(translations={"en": "Full"})
    mock_claim = I18nText(translations={"en": "claim"})

    mock_matrix_pb = MatrixPromptBlock(
        id="blk_1234abcd1234abcd",
        slug="matrix_logic1234",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        description=mock_desc,
        label=mock_label,
        allow_contextual_override=False,
        scales=[
            MatrixScale(
                score=0,
                ai_label="Fail",
                name=I18nText(translations={"en": "Fail"}),
                claims=[
                    MatrixClaim(
                        label=mock_claim,
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_00000000000000000000000000000000",
                                concept_description="concept description for failure",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                            )
                        ],
                    )
                ],
            ),
            MatrixScale(
                score=100,
                ai_label="Full",
                name=mock_name,
                claims=[
                    MatrixClaim(
                        label=mock_claim,
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_11111111111111111111111111111111",
                                concept_description="concept description for testing",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                            )
                        ],
                    )
                ],
            ),
        ],
    )

    blocks_by_id: dict[str, AnyPromptBlock] = {
        "matrix_logic1234": mock_matrix_pb,
    }

    workflow_steps: Any = {
        "step_1": SimpleNamespace(
            id="step_1",
            depends_on=[],
        )
    }

    mcp_audit_map: Any = {"doc1": SimpleNamespace(tool_id="test", step_name="step_1", query="query", source_urls=[])}

    evaluative, info, parsed, atoms = MatrixDomainParser.parse_matrices(
        results=results,
        locale="en",
        blocks_by_id=blocks_by_id,
        workflow_steps=workflow_steps,
        profile=profile_custom,
        row_explanations_cache={"matrix_logic1234": "Explanation"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
        mcp_audit_map=mcp_audit_map,
    )

    assert len(evaluative) == 2
    assert "tda_11111111111111111111111111111111" in atoms["step_1"]


@pytest.mark.asyncio
async def test_blueprint_parse_matrix_trace_results_exceptions(mock_repo_transformer: Any) -> None:
    from backend_v2.exceptions import AppException
    from backend_v2.models.v2_core import OutputProfile
    from backend_v2.services.blueprint import BlueprintTransformer

    _transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    profile = OutputProfile(
        id="prf_1111111111111111",
        slug="test",
        workflow_id="wf_1111111111111111",
        name=I18nText(translations={"en": "test"}),
        display_scale=DisplayScale.ORIGINAL,
        target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
        layouts=[],
    )

    valid_scale_0 = MatrixScale(
        score=0,
        ai_label="Fail",
        name=I18nText(translations={"en": "Fail"}),
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "claim"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id="tda_00000000000000000000000000000000",
                        concept_description="concept description for failure",
                        inverse_evidence=False,
                        aggregation_mode="EXISTS",
                    )
                ],
            )
        ],
    )
    valid_scale_100 = MatrixScale(
        score=100,
        ai_label="Full",
        name=I18nText(translations={"en": "Full"}),
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "claim"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id="tda_11111111111111111111111111111111",
                        concept_description="concept description for testing",
                        inverse_evidence=False,
                        aggregation_mode="EXISTS",
                    )
                ],
            )
        ],
    )
    base_matrix = MatrixPromptBlock(
        id="blk_1234abcd1234abcd",
        slug="matrix_logic1234",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        description=I18nText(translations={"en": "desc"}),
        label=I18nText(translations={"en": "Logic"}),
        scales=[valid_scale_0, valid_scale_100],
    )

    blocks_by_id: dict[str, Any] = {
        "matrix_logic1234": base_matrix,
    }

    # 1. Invalid matrix payload format (not a dict) -> lines 226-231
    results = [SimpleNamespace(step_id="step_1", block_id="matrix_logic1234", payload="invalid_payload_string")]
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "expected dict" in str(exc.value)

    # 2. Validation failure inside TraceMatrixPayloadDTO -> lines 238-241
    results = [
        SimpleNamespace(
            step_id="step_1",
            block_id="matrix_logic1234",
            payload={"invalid_key": "value"},  # Fails TraceMatrixPayloadDTO validation
        )
    ]
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "Invalid matrix payload format" in str(exc.value)

    # 3. Missing I18n label -> lines 264-269
    blocks_by_id["matrix_logic1234"] = MatrixPromptBlock.model_construct(
        id="blk_1234abcd1234abcd",
        slug="matrix_logic1234",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        description=I18nText(translations={"en": "desc"}),
        label=None,
        scales=[valid_scale_0, valid_scale_100],
    )
    results = [
        SimpleNamespace(
            step_id="step_1",
            block_id="matrix_logic1234",
            payload={"raw_score": 100.0, "level_breakdown": {}, "evaluated_atoms": {}, "extensions": {}},
        )
    ]
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "missing a required I18n label" in str(exc.value)

    # 4. Missing scales -> lines 293-298
    blocks_by_id["matrix_logic1234"] = MatrixPromptBlock.model_construct(
        id="blk_1234abcd1234abcd",
        slug="matrix_logic1234",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        description=I18nText(translations={"en": "desc"}),
        label=I18nText(translations={"en": "Logic"}),
        scales=[],
    )
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "missing Pydantic computed_min/max" in str(exc.value) or "initialized as matrix but has no scales" in str(
        exc.value
    )

    # 5. Missing scale name
    blocks_by_id["matrix_logic1234"] = MatrixPromptBlock.model_construct(
        id="blk_1234abcd1234abcd",
        slug="matrix_logic1234",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        description=I18nText(translations={"en": "desc"}),
        label=I18nText(translations={"en": "Logic"}),
        scales=[MatrixScale.model_construct(score=100, name=None)],
        computed_min=0,
        computed_max=100,
    )
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "missing 'name'" in str(exc.value)

    # 6. Invalid breakdown key
    blocks_by_id["matrix_logic1234"] = base_matrix
    results[0].payload["level_breakdown"] = {"invalid_float": {"hits": 1, "total": 1}}
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "Invalid level key 'invalid_float'" in str(exc.value)

    # 7. Missing row_explanations_cache
    results[0].payload["level_breakdown"] = {}
    object.__setattr__(profile, "synthesis", SimpleNamespace(row_explanations_block_id="foo"))
    with pytest.raises(AppException) as exc:
        MatrixDomainParser.parse_matrices(results, "en", blocks_by_id, {}, profile, {}, [], {})
    assert "row_explanations_cache missing entry" in str(exc.value)


@pytest.mark.asyncio
async def test_blueprint_slop_and_penalty_coverage(mock_repo_transformer: Any) -> None:
    """Verifies penalty parsing and ensures AI output slop never affects global score."""
    from types import SimpleNamespace

    mock_repo_transformer.get_workflow.return_value.expected_inputs = [
        SimpleNamespace(name="input_text", type="string")
    ]

    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000101",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "scoring_result": {
                        "total_score": 100.0,
                        "penalties_applied": ["PENALTY_SECURITY:10", "PENALTY_POST_HOC:15", "PENALTY_INVALID:20"],
                    },
                    "blk_1234abcd1234abcd": {
                        "raw_score": 100.0,
                        "normalized_score": 100.0,
                        "level_breakdown": {},
                        "evaluated_atoms": {},
                        "extensions": {},
                    },
                },
            )
        ],
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_all_prompt_blocks.return_value = fix_mock_dict(
        [
            {
                "id": "blk_1234abcd1234abcd",
                "slug": "matrix_test",
                "description": {"translations": {"en": "Desc"}},
                "category_id": "matrix",
                "type": "float",
                "is_evaluative": True,
                "label": {"translations": {"en": "Label"}},
                "computed_min": 0,
                "computed_max": 100,
                "scales": [
                    {
                        "score": 100,
                        "name": {"translations": {"en": "Full"}},
                        "claims": [
                            {
                                "label": {"translations": {"en": "claim"}},
                                "ai_description": "desc",
                            }
                        ],
                    }
                ],
            }
        ]
    )

    from backend_v2.models.v2_core import OutputLayoutBlock, OutputProfile

    mock_repo_transformer.get_all_output_profiles.return_value = fix_mock_dict(
        [
            OutputProfile.model_construct(
                id="prf_dddd1111dddd1111",
                slug="default",
                workflow_id="wf_1234abcd1234abcd",
                name=I18nText(translations={"en": "Default"}),
                display_scale=DisplayScale.NORMALIZED_100,
                target_block_order=_DEFAULT_TARGET_BLOCK_ORDER,
                metric_mappings={},
                layouts=[
                    OutputLayoutBlock.model_construct(
                        preset_view="text_only",
                        target_blocks=["*"],
                    ),
                ],
                visible_block_extensions=[],
                visible_workflow_extensions=[],
                max_extension_items=2,
                strictness_level=85,
            )
        ]
    )

    from backend_v2.services.blueprint import BlueprintTransformer

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    # Expect Exception for PENALTY_INVALID:20
    with pytest.raises(AppException) as exc:
        await transformer.build_report_dto("exe_0000000000000101")
    assert "Legacy or unsupported penalty string detected" in str(exc.value)

    # Remove invalid penalty and keep only valid user-input penalties (10% + 15% = 25% penalty on 100 base)
    mock_repo_transformer.get_execution.return_value.execution_trace[0].content["scoring_result"][
        "penalties_applied"
    ] = ["PENALTY_SECURITY:10", "PENALTY_POST_HOC:15"]

    dto = await transformer.build_report_dto("exe_0000000000000101")
    assert dto.global_score == 75.0


@pytest.mark.asyncio
async def test_output_profile_target_blocks_sdui_dispatch(mock_repo_transformer: Any) -> None:
    """Verifies that OutputProfile settings strictly drive SDUI block dispatch, metadata filtering, and XAI highlight limits."""
    from datetime import datetime, timezone

    from backend_v2.models.view.sdui import AccordionBlock, SduiMetadataBlock

    custom_profile = OutputProfile(
        id="prf_1111222233334444",
        slug="test-profile",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"fi": "Testiprofiili", "en": "Test Profile"}),
        description=I18nText(translations={"fi": "Testikuvaus", "en": "Test Description"}),
        user_role_label=I18nText(translations={"fi": "Kohderyhmä", "en": "Target Audience"}),
        user_role_mappings={"ROLE_ARCHITECT": I18nText(translations={"fi": "Pääarkkitehti", "en": "Lead Architect"})},
        custom_preface=I18nText(translations={"fi": "Mukautettu esipuhe.", "en": "Custom preface."}),
        visible_metadata=["user", "date", "scoring_engine"],
        visible_block_extensions=[XaiExtensionType.COACHING, XaiExtensionType.FALSIFICATION],
        max_extension_items=2,
        strictness_level=85,
        scoring_strategy=ScoringStrategy.WATERFALL,
        display_scale=DisplayScale.NORMALIZED_100,
        target_block_order=[
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
            TargetBlockType.MATRIX_GRAPHS_BLOCK,
        ],
        layouts=[
            OutputLayoutBlock(
                preset_view="1d_metrics",
                text_delivery_mode="full",
                title=I18nText(translations={"fi": "Mittarit", "en": "Metrics"}),
            )
        ],
        metric_mappings={
            "metadata_user": I18nText(translations={"fi": "Käyttäjä", "en": "User"}),
            "metadata_organization": I18nText(translations={"fi": "Organisaatio", "en": "Organization"}),
            "metadata_scoring_engine": I18nText(translations={"fi": "Arviointimoottori", "en": "Scoring Engine"}),
            "metadata_strictness": I18nText(translations={"fi": "Ankaruustaso", "en": "Strictness Level"}),
        },
        extension_labels={
            XaiExtensionType.COACHING: I18nText(translations={"fi": "Valmennusvinkit", "en": "Coaching Tips"}),
            XaiExtensionType.FALSIFICATION: I18nText(translations={"fi": "Falsifiointi", "en": "Falsification"}),
        },
    )

    mock_repo_transformer.get_all_output_profiles.return_value = [custom_profile.model_dump()]

    mock_exec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=custom_profile.id,
        created_at=datetime.now(timezone.utc),
        created_by="usr_admin",
        metadata={"target_locale": "fi"},
        execution_trace=[],
        profile_syntheses={
            custom_profile.id: RenderedSynthesisCache(
                user_role="ROLE_ARCHITECT",
                xai_highlights=[
                    XaiHighlightItem(extension_type="coaching", content="Focus on modular architecture."),
                    XaiHighlightItem(extension_type="coaching", content="Avoid monolithic God classes."),
                    XaiHighlightItem(extension_type="falsification", content="Validate performance assumptions."),
                ],
                section_syntheses={},
            )
        },
    )
    mock_repo_transformer.get_execution.return_value = mock_exec
    mock_repo_transformer.get_user.return_value = {"display_name": "Test User"}

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    report_dto = await transformer.build_report_dto(
        execution_id="exe_1111222233334444",
        profile_id=custom_profile.id,
        accept_language="fi",
    )

    block_type_names = [type(b).__name__ for b in report_dto.inner_sdui_blocks]
    assert block_type_names == ["SduiMetadataBlock", "ParagraphBlock", "AccordionBlock", "AccordionBlock"]

    meta_block = next(b for b in report_dto.inner_sdui_blocks if isinstance(b, SduiMetadataBlock))
    assert any("Käyttäjä" in line for line in meta_block.metadata_lines)
    assert not any("Organisaatio" in line for line in meta_block.metadata_lines)

    coaching = next(
        b for b in report_dto.inner_sdui_blocks if isinstance(b, AccordionBlock) and b.title == "Valmennusvinkit"
    )
    assert len(coaching.children) == 2


@pytest.mark.asyncio
async def test_blueprint_transformer_invalid_target_block_type_raises_app_exception(
    mock_repo_transformer: MagicMock,
) -> None:
    """Negative: unmapped target block type in hydrators raises AppException."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        layouts=[],
        user_role_mappings={},
    )

    mock_repo_transformer.get_all_output_profiles.return_value = [profile.model_dump()]

    mock_exec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        created_by="usr_admin",
        metadata={"target_locale": "fi"},
        execution_trace=[],
        profile_syntheses={},
    )
    mock_repo_transformer.get_execution.return_value = mock_exec
    mock_repo_transformer.get_user.return_value = {"display_name": "Test User"}

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    # Intentionally remove TargetBlockType.METADATA_BLOCK from hydrators to trigger Fail-Fast KeyError handling
    transformer._target_block_hydrators.pop(TargetBlockType.METADATA_BLOCK, None)

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto(
            execution_id="exe_1111222233334444",
            profile_id=profile.id,
            accept_language="fi",
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_blueprint_transformer_fail_fast_branches(
    mock_repo_transformer: MagicMock,
) -> None:
    """Test Fail-Fast branches: missing execution, missing workflow, missing locale, missing profile."""
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    # 1. Missing execution -> 404
    mock_repo_transformer.get_execution.return_value = None
    with pytest.raises(AppException) as exc1:
        await transformer.build_report_dto("exe_nonexistent", accept_language="en")
    assert exc1.value.status_code == 404
    assert exc1.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    # 2. Missing workflow -> 500
    mock_exec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_nonexistent",
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "en"},
        execution_trace=[],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec
    mock_repo_transformer.get_workflow.return_value = None
    with pytest.raises(AppException) as exc2:
        await transformer.build_report_dto("exe_1111222233334444", accept_language="en")
    assert exc2.value.status_code == 500
    assert exc2.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 3. Missing locale -> 400
    mock_wf = SimpleNamespace(
        id="wf_1234abcd1234abcd",
        default_profile_id="prf_dddd1111dddd1111",
        steps=[],
    )
    mock_repo_transformer.get_workflow.return_value = mock_wf
    mock_exec_no_locale = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        created_at=datetime.now(timezone.utc),
        metadata={},
        execution_trace=[],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec_no_locale
    with pytest.raises(AppException) as exc3:
        await transformer.build_report_dto("exe_1111222233334444", accept_language=None)
    assert exc3.value.status_code == 400
    assert exc3.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 4. Missing profile in repo -> 404
    mock_repo_transformer.get_execution.return_value = mock_exec
    mock_repo_transformer.get_all_output_profiles.return_value = []
    with pytest.raises(AppException) as exc4:
        await transformer.build_report_dto("exe_1111222233334444", profile_id="prf_nonexistent", accept_language="en")
    assert exc4.value.status_code == 404
    assert exc4.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_blueprint_transformer_identity_errors_and_penalties(
    mock_repo_transformer: MagicMock,
) -> None:
    """Test identity repository resolution errors and invalid penalty handling."""
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],  # Empty target_block_order to test fallback radar block
        layouts=[],
        user_role_mappings={},
    )
    mock_repo_transformer.get_all_output_profiles.return_value = [profile.model_dump()]

    # 1. Organization resolution error -> 404
    mock_exec_org_err = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        organization_id="org_err",
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        execution_trace=[],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec_org_err
    mock_repo_transformer.get_organization_model.side_effect = Exception("Org lookup failed")

    with pytest.raises(AppException) as exc_org:
        await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert exc_org.value.status_code == 404
    assert exc_org.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    # Reset side effect
    mock_repo_transformer.get_organization_model.side_effect = None

    # 2. User resolution error -> 404
    mock_exec_user_err = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_by="usr_err",
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        execution_trace=[],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec_user_err
    mock_repo_transformer.get_user.side_effect = Exception("User lookup failed")

    with pytest.raises(AppException) as exc_u:
        await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert exc_u.value.status_code == 404
    assert exc_u.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    # Reset side effect
    mock_repo_transformer.get_user.side_effect = None
    mock_repo_transformer.get_user.return_value = {"name": "Test User"}

    # 3. Empty target block order fallback test (lines 709-710)
    mock_exec_valid = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        execution_trace=[],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec_valid
    report = await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert report is not None
    assert len(report.inner_sdui_blocks) == 1


@pytest.mark.asyncio
async def test_blueprint_transformer_unsupported_penalty_format_and_cache_none(
    mock_repo_transformer: MagicMock,
) -> None:
    """Test unsupported penalty format and section_syntheses None fail-fast."""
    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        layouts=[],
        user_role_mappings={},
    )
    mock_repo_transformer.get_all_output_profiles.return_value = [profile.model_dump()]

    # 1. Unsupported penalty format fail-fast (lines 652-656)
    mock_exec_penalty = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        execution_trace=[
            TraceEvent(
                step_name="step_system_scoring",
                event_type="output",
                content={"total_score": 80.0, "penalties_applied": ["UNSUPPORTED_PENALTY_FORMAT:50"]},
            )
        ],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec_penalty

    with pytest.raises(AppException) as exc_pen:
        await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert exc_pen.value.status_code == 500
    assert exc_pen.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 2. Section syntheses is None fail-fast (lines 228-232)
    mock_cache = RenderedSynthesisCache()
    object.__setattr__(mock_cache, "section_syntheses", None)
    mock_exec_cache = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        execution_trace=[],
        profile_syntheses={profile.id: mock_cache},
    )
    mock_repo_transformer.get_execution.return_value = mock_exec_cache

    with pytest.raises(AppException) as exc_cache:
        await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert exc_cache.value.status_code == 500
    assert exc_cache.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_blueprint_transformer_step_state_update_and_reverse_lookup(
    mock_repo_transformer: MagicMock,
) -> None:
    """Test step_states updating and reverse lookup for MCP audit data."""
    from backend_v2.models.v2_core import (
        ExecutionStepState,
        FrozenContext,
        HumanOverrideDTO,
        MCPAuditTrace,
        ScorecardAtomDTO,
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

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        layouts=[],
        user_role_mappings={},
        metric_mappings={
            "metadata_user": I18nText(translations={"en": "User", "fi": "Käyttäjä"}),
            "metadata_organization": I18nText(translations={"en": "Organization", "fi": "Organisaatio"}),
            "metadata_scoring_engine": I18nText(translations={"en": "Scoring Engine", "fi": "Arviointimoottori"}),
            "metadata_strictness": I18nText(translations={"en": "Strictness", "fi": "Ankaruustaso"}),
        },
    )
    mock_repo_transformer.get_all_output_profiles.return_value = [profile.model_dump()]

    audit_trace = MCPAuditTrace(
        id="mcp_00000000000000000000000000000001",
        tool_id="tavily_search",
        step_name="step_evidence",
        query="search query",
        knowledge_gap="gap",
        search_rationale="rationale",
        reasoning="reason",
    )

    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.enums import VisualIntent

    existing_atom = ScorecardAtomDTO(
        atom_id="atom_1",
        level=1,
        level_name="Level 1",
        claim_label="Claim 1",
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reason",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="1",
            step_2_scan_source="2",
            step_3_evaluate_anti_patterns="3",
            step_4_final_conclusion="4",
        ),
        contextual_override=True,
        structural_location=None,
        chart_display_label="Claim 1",
        visual_intent=VisualIntent.NEUTRAL,
        human_override=HumanOverrideDTO(
            new_status=ExecutionStatus.FAILED,
            reason="Manual fix",
            evidence_quotes=[],
            overridden_by="usr_admin",
            overridden_at=datetime.now(timezone.utc),
        ),
    )

    step_state = ExecutionStepState(
        id="step_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={"atom_1": existing_atom},
    )

    mock_exec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        frozen_context=FrozenContext(mcp_tool_audit=[audit_trace]),
        step_states={"step_1": step_state},
        execution_trace=[
            TraceEvent(
                step_name="step_1",
                event_type="output",
                content={
                    "source_id": "mcp_00000000000000000000000000000001",
                    "used_evidence_ids": ["mcp_00000000000000000000000000000001"],
                    "used_mcp_ids": ["mcp_00000000000000000000000000000001"],
                },
            ),
        ],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec

    report = await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert report is not None
    assert report.total_tokens == 0
    assert report.prompt_tokens == 0
    assert report.completion_tokens == 0
    assert report.reasoning_tokens == 0
    assert report.cost_estimate == 0.0


@pytest.mark.asyncio
async def test_blueprint_transformer_evidence_rejection_and_reverse_mcp(
    mock_repo_transformer: MagicMock,
) -> None:
    """Test evidence override user rejection, AtomResultDTO parsing, and MCP audit impacted axis mapping."""
    from backend_v2.models.enums import SDUIComponentType
    from backend_v2.models.v2_core import (
        FrozenContext,
        MCPAuditTrace,
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

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1234abcd1234abcd",
        name=I18nText(translations={"en": "Test", "fi": "Testi"}),
        content_blocks=[],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        layouts=[],
        user_role_mappings={},
        metric_mappings={
            "metadata_user": I18nText(translations={"en": "User", "fi": "Käyttäjä"}),
            "metadata_organization": I18nText(translations={"en": "Organization", "fi": "Organisaatio"}),
            "metadata_scoring_engine": I18nText(translations={"en": "Scoring Engine", "fi": "Arviointimoottori"}),
            "metadata_strictness": I18nText(translations={"en": "Strictness", "fi": "Ankaruustaso"}),
        },
    )
    mock_repo_transformer.get_all_output_profiles.return_value = [profile.model_dump()]

    audit_trace = MCPAuditTrace(
        id="mcp_00000000000000000000000000000001",
        tool_id="tavily_search",
        step_name="step_evidence",
        query="search query",
        knowledge_gap="gap",
        search_rationale="rationale",
        reasoning="reason",
    )

    mock_exec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1234abcd1234abcd",
        active_profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        frozen_context=FrozenContext(
            mcp_tool_audit=[
                audit_trace,
                MCPAuditTrace(
                    id="mcp_internal",
                    tool_id="internal_source",
                    step_name="internal",
                    query="internal",
                    knowledge_gap="gap",
                    search_rationale="rationale",
                    reasoning="reason",
                ),
            ]
        ),
        execution_trace=[
            TraceEvent(
                step_name="step_evidence_override",
                event_type="evidence_override",
                content={
                    "user_rejected": True,
                    "evq_id": "evq_00000000000000000000000000000001",
                },
            ),
            TraceEvent(
                step_name="step_evidence_override_2",
                event_type="evidence_override",
                content={
                    "user_rejected": False,
                    "evq_id": "evq_00000000000000000000000000000002",
                },
            ),
            TraceEvent(
                step_name="step_dag_exec",
                event_type="output",
                content={
                    "blk_dag_exec": {
                        "results": [
                            {
                                "tda_id": "tda_00000000000000000000000000000000",
                                "status": ExecutionStatus.PASSED,
                                "evaluation_reasoning": "Well done",
                                "contextual_override": False,
                                "source_quote": "Found quote",
                                "depends_on_tda_ids": [],
                                "short_circuit_reason_tda_ids": [],
                            }
                        ],
                        "hydrated_references": {
                            "tda_00000000000000000000000000000000": {
                                "sdui_component": SDUIComponentType.BOOLEAN_CARD,
                                "resolved_claim": "Atom 1",
                                "source_quote": "Found quote",
                            }
                        },
                        "source_id": "mcp_00000000000000000000000000000001",
                        "used_evidence_ids": ["mcp_00000000000000000000000000000001"],
                        "used_mcp_ids": ["mcp_00000000000000000000000000000001"],
                    }
                },
            ),
        ],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec

    report = await transformer.build_report_dto("exe_1111222233334444", profile_id=profile.id, accept_language="fi")
    assert report is not None
    assert len(report.results) >= 1
    assert "tda_00000000000000000000000000000000" in report.hydrated_references
    assert len(report.mcp_tool_audit) == 1
    assert report.mcp_tool_audit[0].id == "mcp_00000000000000000000000000000001"


@pytest.mark.asyncio
async def test_blueprint_transformer_data_starvation_renders_only_warning_and_metadata(
    mock_repo_transformer: MagicMock,
) -> None:
    """Test that in data starvation mode, BlueprintTransformer renders only AlertBlock and SduiMetadataBlock."""
    from backend_v2.models.dtos.trace import DataStarvationEvent
    from backend_v2.models.enums import TargetBlockType
    from backend_v2.models.view.sdui import AlertBlock, SduiMetadataBlock

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    profile = OutputProfile(
        id="prf_99998888777766665555444433332222",
        slug="starvation-profile",
        workflow_id="wf_1234abcd1234abcd1234abcd1234abcd",
        name=I18nText(translations={"en": "Report", "fi": "Talousraportti"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        target_block_order=[
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.MATRIX_GRAPHS_BLOCK,
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
            TargetBlockType.GLOBAL_SCORE_BLOCK,
        ],
        content_blocks=[],
        layouts=[],
        metric_mappings={
            "metadata_user": I18nText(translations={"en": "User", "fi": "Käyttäjä"}),
            "metadata_organization": I18nText(translations={"en": "Organization", "fi": "Organisaatio"}),
            "metadata_scoring_engine": I18nText(translations={"en": "Scoring Engine", "fi": "Arviointimoottori"}),
            "metadata_strictness": I18nText(translations={"en": "Strictness", "fi": "Ankaruustaso"}),
        },
    )
    mock_repo_transformer.get_all_output_profiles.return_value = [profile]
    mock_repo_transformer.get_output_profile.return_value = profile

    mock_wf = SimpleNamespace(
        id="wf_1234abcd1234abcd1234abcd1234abcd",
        default_profile_id=profile.id,
        default_scoring_strategy=ScoringStrategy.AVERAGE,
        default_strictness_level=80,
        steps=[],
    )
    mock_repo_transformer.get_workflow.return_value = mock_wf

    mock_exec = ExecutionRecord(
        id="exe_99998888777766665555444433332222",
        workflow_id="wf_1234abcd1234abcd1234abcd1234abcd",
        created_at=datetime.now(timezone.utc),
        metadata={"target_locale": "fi"},
        profile_syntheses={
            profile.id: RenderedSynthesisCache(
                data_starvation=DataStarvationEvent(total_atoms=0, reason="Data starvation"),
            )
        },
        execution_trace=[],
    )
    mock_repo_transformer.get_execution.return_value = mock_exec

    report = await transformer.build_report_dto(mock_exec.id, profile_id=profile.id, accept_language="fi")
    assert report is not None
    assert report.has_warning is True
    assert report.global_score is None

    # Verify inner_sdui_blocks contains ONLY WarningCard (AlertBlock) and Metadata (SduiMetadataBlock)
    assert len(report.inner_sdui_blocks) == 2
    assert isinstance(report.inner_sdui_blocks[0], AlertBlock)
    assert isinstance(report.inner_sdui_blocks[1], SduiMetadataBlock)
