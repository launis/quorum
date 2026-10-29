import pytest

from backend_v2.llm.mock_data import MOCK_PERFORMATIVITY_OUTPUT
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    PromptBlockCategory,
    TargetBlockType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_blueprint_variance_validation_success() -> None:
    repo = InMemoryUnifiedWorkflowRepository()

    variance_target_id = "blk_0195f3a00000700f8b15f8dcf23f4865"
    step_rule_id = "sr_0195f3a0000070018234567812345678"

    pb = MatrixPromptBlock(
        id=variance_target_id,
        slug="cognitive-depth",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        label=I18nText(translations={"en": "Cognitive Depth"}),
        description=I18nText(translations={"en": "Cognitive Depth"}),
        is_evaluative=True,
        scales=[
            MatrixScale(score=1, name=I18nText(translations={"en": "Low"}), ai_label="LOW"),
            MatrixScale(score=3, name=I18nText(translations={"en": "High"}), ai_label="HIGH"),
        ],
    )
    repo.set_prompt_blocks([pb])

    profile = OutputProfile(
        id="prf_0195f3a0000070018234567812345678",
        slug="test",
        workflow_id="wf_0195f3a0000070018234567812345678",
        name=I18nText(translations={"en": "test"}),
        display_scale=DisplayScale.ORIGINAL,
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK],
        visible_workflow_extensions=["variance_validation"],
        variance_target_block=variance_target_id,
    )
    await repo._output_profiles.create_output_profile(profile)

    workflow = Workflow(
        id="wf_0195f3a0000070018234567812345678",
        slug="test",
        name=I18nText(translations={"en": "test"}),
        description=I18nText(translations={"en": "test"}),
        status="draft",
        version=1,
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_strictness_level=85,
        default_profile_id="prf_0195f3a0000070018234567812345678",
        steps=[StepRule(id=step_rule_id, task_blueprint="step_1234567812345678")],
    )
    await repo.save_workflow(workflow)

    record = ExecutionRecord(
        id="exec_0195f3a0000070018234567812345678",
        workflow_id="wf_0195f3a0000070018234567812345678",
        output_profile_id="prf_0195f3a0000070018234567812345678",
        status=ExecutionStatus.PASSED,
        context_variables={"step_detector": MOCK_PERFORMATIVITY_OUTPUT.model_dump(mode="json")},
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name=step_rule_id,
                content={
                    variance_target_id: {
                        "raw_score": 2.5,
                        "justification": "Crash test success.",
                    }
                },
            )
        ],
        profile_syntheses={
            "prf_0195f3a0000070018234567812345678": RenderedSynthesisCache(
                row_explanations={variance_target_id: "Cognitive depth explanation."},
                extension_metrics=ExtensionMetricsDTO(
                    authenticity_score=2.5,
                    performative_phrases_count=0.0,
                    variance_score=0.1,
                    alignment_verdict="ALIGNED",
                ),
            )
        },
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    await repo.save_execution(record)

    transformer = BlueprintTransformer(
        exec_repo=repo,
        output_profile_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        comp_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    report = await transformer.build_report_dto(
        "exec_0195f3a0000070018234567812345678", "prf_0195f3a0000070018234567812345678", "en"
    )
    assert report is not None
    assert len(report.inner_sdui_blocks) >= 1
