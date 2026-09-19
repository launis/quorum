"""Unit tests for Workflow domain model.

Covers target block separation and layout targets calculation.
"""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import LaxHistoricalContextMode, StepType, TargetBlockType


def _build_test_step(
    step_id: str,
    role_block_id: str | None = None,
    extraction_protocol_block_id: str | None = None,
    criteria_block_ids: list[str] | None = None,
) -> Step:
    """Helper to build a valid Step instance."""
    return Step(
        id=step_id,
        slug=f"slug_{step_id}",
        name=I18nText(translations={"fi": "Askel", "en": "Step"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        type=StepType.LOGIC,
        hook="some_hook",
        role_block_id=role_block_id,
        extraction_protocol_block_id=extraction_protocol_block_id,
        criteria_block_ids=criteria_block_ids or [],
    )


def test_workflow_get_allowed_prompt_block_targets_positive() -> None:
    """Positive: assert concrete PromptBlock IDs are extracted from matching task blueprints."""
    step_rule_1 = StepRule(
        id="sr_11111111111111111111111111111111",
        task_blueprint="stp_11111111111111111111111111111111",
    )
    step_rule_2 = StepRule(
        id="sr_22222222222222222222222222222222",
        task_blueprint="stp_22222222222222222222222222222222",
    )

    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"fi": "Työnkulku", "en": "Workflow"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        status="active",
        version=1,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=LaxHistoricalContextMode.DISABLED,
        steps=[step_rule_1, step_rule_2],
    )

    hydrated_steps = [
        _build_test_step(
            step_id="stp_11111111111111111111111111111111",
            role_block_id="blk_11111111111111111111111111111111",
            extraction_protocol_block_id="blk_22222222222222222222222222222222",
            criteria_block_ids=["blk_33333333333333333333333333333333", "blk_44444444444444444444444444444444"],
        ),
        _build_test_step(
            step_id="stp_22222222222222222222222222222222",
            role_block_id="blk_55555555555555555555555555555555",
        ),
        # Unrelated step not in this workflow's rules
        _build_test_step(
            step_id="stp_99999999999999999999999999999999",
            role_block_id="blk_99999999999999999999999999999999",
        ),
    ]

    prompt_targets = workflow.get_allowed_prompt_block_targets(hydrated_steps)
    assert prompt_targets == {
        "blk_11111111111111111111111111111111",
        "blk_22222222222222222222222222222222",
        "blk_33333333333333333333333333333333",
        "blk_44444444444444444444444444444444",
        "blk_55555555555555555555555555555555",
    }
    assert "blk_99999999999999999999999999999999" not in prompt_targets


def test_workflow_get_allowed_layout_targets_composes_blocks_and_system_types() -> None:
    """Assert layout targets compose concrete prompt blocks with all TargetBlockType system enums."""
    step_rule = StepRule(
        id="sr_11111111111111111111111111111111",
        task_blueprint="stp_11111111111111111111111111111111",
    )

    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"fi": "Työnkulku", "en": "Workflow"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        status="active",
        version=1,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=LaxHistoricalContextMode.DISABLED,
        steps=[step_rule],
    )

    hydrated_steps = [
        _build_test_step(
            step_id="stp_11111111111111111111111111111111",
            role_block_id="blk_11111111111111111111111111111111",
        )
    ]

    layout_targets = workflow.get_allowed_layout_targets(hydrated_steps)

    # Contains concrete block
    assert "blk_11111111111111111111111111111111" in layout_targets

    # Contains all TargetBlockType values
    for e in TargetBlockType:
        assert e.value in layout_targets


def test_workflow_get_allowed_prompt_block_targets_empty_steps() -> None:
    """ISTQB Boundary: Workflow with no matching steps returns empty set."""
    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"fi": "Työnkulku", "en": "Workflow"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        status="active",
        version=1,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=LaxHistoricalContextMode.DISABLED,
        steps=[],
    )

    prompt_targets = workflow.get_allowed_prompt_block_targets([])
    assert prompt_targets == set()

    # Layout targets still include system blocks even if prompt targets are empty
    layout_targets = workflow.get_allowed_layout_targets([])
    assert layout_targets == {e.value for e in TargetBlockType}


def test_workflow_validation_dag_orphan_reference_fails() -> None:
    """ISTQB Negative: Step with unknown dependency fails DAG validation."""
    with pytest.raises(ValidationError) as exc_info:
        Workflow(
            id="wor_1234567890abcdef1234567890abcdef",
            slug="test_wf_orphan",
            name=I18nText(translations={"fi": "Työnkulku", "en": "Workflow"}),
            description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
            status="active",
            version=1,
            model_registry_id="sys_e26807f3bfa3454d",
            historical_context_mode=LaxHistoricalContextMode.DISABLED,
            steps=[
                StepRule(
                    id="sr_11111111111111111111111111111111",
                    task_blueprint="stp_11111111111111111111111111111111",
                    depends_on=["sr_non_existent"],
                ),
            ],
        )
    assert "depends on 'sr_non_existent', which does not exist" in str(exc_info.value)


def test_workflow_validation_dag_circular_dependency_fails() -> None:
    """ISTQB Negative: Circular dependency in workflow steps fails DAG validation."""
    with pytest.raises(ValidationError) as exc_info:
        Workflow(
            id="wor_1234567890abcdef1234567890abcdef",
            slug="test_wf_circular",
            name=I18nText(translations={"fi": "Työnkulku", "en": "Workflow"}),
            description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
            status="active",
            version=1,
            model_registry_id="sys_e26807f3bfa3454d",
            historical_context_mode=LaxHistoricalContextMode.DISABLED,
            steps=[
                StepRule(
                    id="sr_11111111111111111111111111111111",
                    task_blueprint="stp_11111111111111111111111111111111",
                    depends_on=["sr_22222222222222222222222222222222"],
                ),
                StepRule(
                    id="sr_22222222222222222222222222222222",
                    task_blueprint="stp_22222222222222222222222222222222",
                    depends_on=["sr_11111111111111111111111111111111"],
                ),
            ],
        )
    assert "Circular dependency detected" in str(exc_info.value)
