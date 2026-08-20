"""End-to-End Golden Master Test for Epic 93 SDUI Output Rendering Unification."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, FrozenContext, ReportDataDTO, WorkflowInputs
from backend_v2.models.view.sdui import ReportView
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.sdui_mapper_service import SduiMapperService


def dict_to_obj(d: dict[str, Any]) -> Any:
    from types import SimpleNamespace

    return SimpleNamespace(**{k: dict_to_obj(v) if isinstance(v, dict) else v for k, v in d.items()})


@pytest.mark.asyncio
async def test_epic_93_e2e_golden_master() -> None:
    """Verify the E2E data flow from ExecutionRecord to SduiComponent tree.

    ExecutionRecord -> MatrixReducer -> ReportDataDTO -> SduiMapper -> SduiComponent tree.
    """
    # 1. Mock Repositories
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_prompt_block_repo = AsyncMock()
    mock_output_profile_repo = AsyncMock()
    mock_comp_repo = AsyncMock()

    # Create dummy ExecutionRecord
    execution_id = "exe_1234abcd1234abcd"
    wf_id = "wf_1234abcd1234abcd"
    profile_id = "prf_1234abcd1234abcd"
    block_id = "blk_1234abcd1234abcd"

    frozen = FrozenContext(ui_hints_snapshot={})

    mock_exec_repo.get_execution.return_value = ExecutionRecord(
        id=execution_id,
        workflow_id=wf_id,
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        frozen_context=frozen,
        metadata={"target_locale": "en"},
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    block_id: {
                        "raw_score": 85.0,
                        "normalized_score": 85.0,
                        "justification": "Checked with sources.",
                    }
                },
            ),
            TraceEvent(
                step_name="step_scoring",
                event_type="output",
                content={
                    "scoring_result": {
                        "total_score": 85.0,
                        "final_score": 85.0,
                        "penalties_applied": [],
                        "aggregation_status": "V2 Commensurate Average",
                    }
                },
            ),
            TraceEvent(
                step_name="step_synthesis",
                event_type="output",
                content={
                    "_evaluative_matrices": {block_id: 85.0},
                    "synthesized_markdown": "We need to leverage our robust synergy and drive disruption.",
                },
            ),
        ],
        active_profile_id=profile_id,
    )

    # Workflow Mock
    mock_workflow = {
        "id": wf_id,
        "slug": "wf_1",
        "name": {"default_locale": "en", "translations": {"en": "Mock Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "status": "published",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "version": 1,
        "organization_id": "root",
        "default_profile_id": profile_id,
        "default_scoring_strategy": {"value": "WATERFALL"},
        "default_strictness_level": 85,
        "expected_inputs": [],
        "steps": [],
        "output_profiles": [profile_id],
    }
    mock_workflow_repo.get_workflow.return_value = dict_to_obj(mock_workflow)

    # Profile Mock
    mock_profile = {
        "id": profile_id,
        "slug": "mock-profile-slug",
        "workflow_id": wf_id,
        "organization_id": "root",
        "name": {"default_locale": "en", "translations": {"en": "Mock Profile"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "metric_mappings": {
            "metadata_scoring_engine": {"default_locale": "en", "translations": {"en": "Scoring Engine"}},
            "metadata_strictness": {"default_locale": "en", "translations": {"en": "Strictness"}},
        },
        "layouts": [
            {
                "preset_view": "1d_metrics",
                "steps": ["step_analyst"],
                "target_blocks": [block_id],
                "title": {"default_locale": "en", "translations": {"en": "Axis Title"}},
            }
        ],
    }
    mock_output_profile_repo.get_all_output_profiles.return_value = [mock_profile]

    # Prompt Block Mock
    mock_pb = {
        "id": block_id,
        "slug": "block_1",
        "category_id": "matrix",
        "is_evaluative": True,
        "type": "float",
        "label": {"default_locale": "en", "translations": {"en": "Matrix 1"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "ai_description": "ai desc",
        "scales": [
            {
                "name": {"default_locale": "en", "translations": {"en": "FAIL"}},
                "score": 0,
                "ai_label": "FAIL",
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
            },
            {
                "name": {"default_locale": "en", "translations": {"en": "PASS"}},
                "score": 100,
                "ai_label": "PASS",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "claim 2"}},
                        "ai_description": "desc 2",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "concept 2",
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
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = [mock_pb]
    mock_comp_repo.get_all_components.return_value = [mock_pb]

    transformer = BlueprintTransformer(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=mock_output_profile_repo,
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    # 2. Map Execution to ReportDataDTO
    dto = await transformer.build_report_dto(execution_id, profile_id)

    # 3. Map ReportDataDTO to SDUI ReportView
    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id=execution_id)

    # 4. Deep Assertions
    assert isinstance(dto, ReportDataDTO)
    assert isinstance(view, ReportView)
    assert view.view_id == execution_id
    assert view.metrics is not None
    assert view.metrics["global_score"] == 85.0

    # Verify that ReportDataDTO.inner_sdui_blocks are populated
    assert len(view.inner_sdui_blocks) > 0

    scorecard_block = next(
        (
            b
            for b in view.inner_sdui_blocks
            if getattr(b, "block_type", getattr(b, "preset_view", "")) in ("1d_metrics", "text_only")
        ),
        None,
    )
    assert scorecard_block is not None


@pytest.mark.asyncio
async def test_epic_95_na_cascade_e2e() -> None:
    """Verify that N_A AtomResultDTO correctly cascades to an n_a_card SduiComponent."""
    from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
    from backend_v2.models.v2_core import AtomResultDTO, HydratedAtomDTO

    # Create dummy ExecutionRecord mapped as ReportDataDTO with an N_A result
    execution_id = "exe_na1234567890"
    tda_id = "tda_short_circuit1234567"

    dto = ReportDataDTO(
        workflow_id="wf_na",
        execution_id=execution_id,
        profile_id="prf_na",
        results=[
            AtomResultDTO(
                tda_id="tda_target123",
                status=ExecutionStatus.N_A,
                short_circuit_reason_tda_ids=[tda_id],
                depends_on_tda_ids=[],
                evaluation_reasoning="Skipped",
                contextual_override=False,
                source_quote=None,
            )
        ],
        hydrated_references={
            tda_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="This is the NA reason claim",
                source_quote=None,
            ),
            "tda_target123": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD, resolved_claim="Target claim", source_quote=None
            ),
        },
    )

    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id=execution_id)

    # Assertions
    na_section = next(
        (s for s in view.sections if getattr(s.type, "value", s.type) == "MARKDOWN_BLOCK" and s.id == "na_outcomes"),
        None,
    )
    assert na_section is not None, "N/A outcomes section missing"

    na_data = na_section.data
    assert len(na_data) == 1

    na_card = na_data[0]
    assert na_card["block_type"] == "n_a_card"
    assert tda_id in na_card["short_circuit_reason_tda_ids"]
    assert "Ohitettu säännön perusteella: This is the NA reason claim" in na_card["message"]
