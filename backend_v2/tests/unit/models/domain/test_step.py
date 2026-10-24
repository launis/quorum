"""Unit tests for Step domain models.

Validates that Step, StepRule, Role, QuestionnaireItem, and ExpectedInput enforce
strict validation, boundary limits, and Fail-Fast validation behavior.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import (
    ALLOWED_INPUT_MODES,
    ExpectedInput,
    QuestionnaireItem,
    Role,
    Step,
    StepRule,
)
from backend_v2.models.enums import CognitiveTier, StepType, StepZone


def test_step_valid_llm() -> None:
    """Test valid instantiation of an LLM Step."""
    step = Step(
        id="stp_0123456789abcdef",
        slug="step_analyst",
        name=I18nText(translations={"en": "Analyst Step"}),
        type=StepType.LLM,
        role_block_id="blk_0123456789abcdef",
        extraction_protocol_block_id="blk_abcdef0123456789",
        criteria_block_ids=["blk_1111222233334444"],
        cognitive_tier=CognitiveTier.FAST,
    )
    assert step.id == "stp_0123456789abcdef"
    assert step.type == StepType.LLM
    assert step.cognitive_tier == CognitiveTier.FAST
    assert step.is_system_core is False
    assert step.zone == StepZone.ZONE_B


def test_step_valid_logic() -> None:
    """Test valid instantiation of a logic hook Step."""
    step = Step(
        id="stp_0123456789abcdef",
        slug="step_transform",
        name=I18nText(translations={"en": "Transform Step"}),
        type=StepType.LOGIC,
        hook="backend_v2.hooks.transform_hook",
    )
    assert step.id == "stp_0123456789abcdef"
    assert step.type == StepType.LOGIC
    assert step.hook == "backend_v2.hooks.transform_hook"


def test_step_llm_missing_criteria_block_ids_fails() -> None:
    """Test that LLM step without criteria_block_ids fails validation."""
    with pytest.raises(AppException) as exc_info:
        Step(
            id="stp_0123456789abcdef",
            slug="step_broken",
            name=I18nText(translations={"en": "Broken Step"}),
            type=StepType.LLM,
            role_block_id="blk_0123456789abcdef",
            extraction_protocol_block_id="blk_abcdef0123456789",
            criteria_block_ids=[],
            cognitive_tier=CognitiveTier.FAST,
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "must define at least one criteria_block_id" in exc_info.value.message


def test_step_llm_missing_extraction_protocol_fails() -> None:
    """Test that LLM step without extraction_protocol_block_id fails validation."""
    with pytest.raises(AppException) as exc_info:
        Step(
            id="stp_0123456789abcdef",
            slug="step_broken",
            name=I18nText(translations={"en": "Broken Step"}),
            type=StepType.LLM,
            role_block_id="blk_0123456789abcdef",
            extraction_protocol_block_id=None,
            criteria_block_ids=["blk_1111222233334444"],
            cognitive_tier=CognitiveTier.FAST,
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "must define a valid extraction_protocol_block_id" in exc_info.value.message


def test_step_consistency_missing_cognitive_tier_raises_app_exception() -> None:
    """Test that LLM step without cognitive_tier fails validation."""
    with pytest.raises(AppException) as exc_info:
        Step(
            id="stp_0123456789abcdef",
            slug="step_broken",
            name=I18nText(translations={"en": "Broken Step"}),
            type=StepType.LLM,
            role_block_id="blk_0123456789abcdef",
            extraction_protocol_block_id="blk_abcdef0123456789",
            criteria_block_ids=["blk_1111222233334444"],
            cognitive_tier=None,
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "must declare an explicit cognitive_tier" in exc_info.value.message


def test_step_logic_missing_hook_fails() -> None:
    """Test that Logic step without hook target fails validation."""
    with pytest.raises(AppException) as exc_info:
        Step(
            id="stp_0123456789abcdef",
            slug="step_logic_broken",
            name=I18nText(translations={"en": "Logic Broken"}),
            type=StepType.LOGIC,
            hook=None,
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "must define a native 'hook' execution target" in exc_info.value.message


def test_step_extra_fields_forbidden() -> None:
    """Test that Step rejects unrecognized extra fields."""
    with pytest.raises(ValidationError):
        Step.model_validate(
            {
                "id": "stp_0123456789abcdef",
                "slug": "step_extra",
                "name": {"translations": {"en": "Extra Step"}},
                "type": "logic",
                "hook": "some_hook",
                "unrecognized_field": 123,
            }
        )


def test_step_rule_valid_and_variable_extraction() -> None:
    """Test StepRule instantiation and dynamic variable reference extraction."""
    rule = StepRule(
        id="sr_0123456789abcdef",
        task_blueprint="stp_0123456789abcdef",
        depends_on=["sr_upstream01234567"],
        input_mappings={
            "doc": "$inputs.document",
            "context": "$steps.sr_upstream01234567.output",
            "static_val": "plain_string",
        },
    )
    assert rule.id == "sr_0123456789abcdef"
    assert rule.task_blueprint == "stp_0123456789abcdef"
    refs = rule.extract_variable_references()
    assert set(refs) == {"$inputs.document", "$steps.sr_upstream01234567.output"}


def test_step_rule_extra_fields_forbidden() -> None:
    """Test that StepRule rejects extra fields."""
    with pytest.raises(ValidationError):
        StepRule.model_validate(
            {
                "id": "sr_0123456789abcdef",
                "task_blueprint": "stp_0123456789abcdef",
                "extra_key": "forbidden",
            }
        )


def test_role_valid_and_extra_fields_forbidden() -> None:
    """Test Role model instantiation and rejection of extra fields."""
    role = Role(
        id="rol_0123456789abcdef",
        name=I18nText(translations={"en": "Lead Auditor"}),
        model_role="analyst_model",
        pre_hooks=["hook_a"],
        post_hooks=["hook_b"],
    )
    assert role.id == "rol_0123456789abcdef"
    assert role.model_role == "analyst_model"

    with pytest.raises(ValidationError):
        Role.model_validate(
            {
                "id": "rol_0123456789abcdef",
                "name": {"translations": {"en": "Lead Auditor"}},
                "model_role": "analyst_model",
                "invalid_field": True,
            }
        )


def test_questionnaire_item_valid() -> None:
    """Test QuestionnaireItem valid instantiation."""
    item = QuestionnaireItem(
        question_id="q1",
        question=I18nText(translations={"en": "What is the scope?"}),
        type="text",
    )
    assert item.question_id == "q1"
    assert item.type == "text"


def test_expected_input_valid() -> None:
    """Test ExpectedInput instantiation for text modality."""
    inp = ExpectedInput(
        input_key="candidate_doc",
        label=I18nText(translations={"en": "Candidate Document"}),
        required=True,
        input_modes=["file", "text"],
        description=I18nText(translations={"en": "Upload the document"}),
        ai_description="Primary evaluation document",
    )
    assert inp.input_key == "candidate_doc"
    assert inp.is_assignment is False
    assert inp.is_endorsed_deliverable is False


def test_expected_input_assignment_modality() -> None:
    """Test ExpectedInput with assignment modality."""
    inp = ExpectedInput(
        input_key="case_assignment",
        label=I18nText(translations={"en": "Case Assignment"}),
        required=True,
        input_modes=["assignment"],
        description=I18nText(translations={"en": "The assignment brief"}),
    )
    assert inp.is_assignment is True


def test_expected_input_empty_input_modes_fails() -> None:
    """Test ExpectedInput fails on empty input_modes list."""
    with pytest.raises(ValidationError, match="must have at least one input_mode"):
        ExpectedInput(
            input_key="test_input",
            label=I18nText(translations={"en": "Test"}),
            required=True,
            input_modes=[],
            description=I18nText(translations={"en": "Test desc"}),
        )


def test_expected_input_invalid_input_mode_fails() -> None:
    """Test ExpectedInput fails when invalid input_mode is supplied."""
    with pytest.raises(ValidationError, match="contains invalid input_modes"):
        ExpectedInput(
            input_key="test_input",
            label=I18nText(translations={"en": "Test"}),
            required=True,
            input_modes=["unsupported_mode"],
            description=I18nText(translations={"en": "Test desc"}),
        )


def test_expected_input_assignment_conflicts() -> None:
    """Test ExpectedInput fails when assignment mode conflicts with chat_history or questionnaire."""
    with pytest.raises(ValidationError, match="cannot mix 'questionnaire' with other input modes"):
        ExpectedInput(
            input_key="test_input",
            label=I18nText(translations={"en": "Test"}),
            required=True,
            input_modes=["assignment", "questionnaire"],
            description=I18nText(translations={"en": "Test desc"}),
            questionnaire_definition=[
                QuestionnaireItem(
                    question_id="q1",
                    question=I18nText(translations={"en": "Q1"}),
                    type="text",
                )
            ],
        )

    with pytest.raises(ValidationError, match="cannot use 'assignment' mode when flagged as chat history"):
        ExpectedInput(
            input_key="test_input",
            label=I18nText(translations={"en": "Test"}),
            required=True,
            is_chat_history=True,
            input_modes=["assignment"],
            description=I18nText(translations={"en": "Test desc"}),
        )


def test_expected_input_questionnaire_modes_validation() -> None:
    """Test ExpectedInput questionnaire modality constraints."""
    with pytest.raises(ValidationError, match="cannot use 'questionnaire' mode when flagged as chat history"):
        ExpectedInput(
            input_key="test_q",
            label=I18nText(translations={"en": "Q"}),
            required=True,
            is_chat_history=True,
            input_modes=["questionnaire"],
            description=I18nText(translations={"en": "Q desc"}),
            questionnaire_definition=[
                QuestionnaireItem(
                    question_id="q1",
                    question=I18nText(translations={"en": "Q1"}),
                    type="text",
                )
            ],
        )

    with pytest.raises(ValidationError, match="cannot mix 'questionnaire' with other input modes"):
        ExpectedInput(
            input_key="test_q",
            label=I18nText(translations={"en": "Q"}),
            required=True,
            input_modes=["questionnaire", "file"],
            description=I18nText(translations={"en": "Q desc"}),
            questionnaire_definition=[
                QuestionnaireItem(
                    question_id="q1",
                    question=I18nText(translations={"en": "Q1"}),
                    type="text",
                )
            ],
        )

    with pytest.raises(ValidationError, match="uses 'questionnaire' mode but lacks definitions"):
        ExpectedInput(
            input_key="test_q",
            label=I18nText(translations={"en": "Q"}),
            required=True,
            input_modes=["questionnaire"],
            description=I18nText(translations={"en": "Q desc"}),
            questionnaire_definition=[],
        )

    with pytest.raises(
        ValidationError, match="cannot have questionnaire_definition when 'questionnaire' mode is not active"
    ):
        ExpectedInput(
            input_key="test_q",
            label=I18nText(translations={"en": "Q"}),
            required=True,
            input_modes=["text"],
            description=I18nText(translations={"en": "Q desc"}),
            questionnaire_definition=[
                QuestionnaireItem(
                    question_id="q1",
                    question=I18nText(translations={"en": "Q1"}),
                    type="text",
                )
            ],
        )


def test_expected_input_endorsed_deliverable_mutual_exclusion() -> None:
    """Test ExpectedInput is_endorsed_deliverable mutual exclusion invariants."""
    with pytest.raises(
        ValidationError, match="cannot be simultaneously marked as both is_chat_history and is_endorsed_deliverable"
    ):
        ExpectedInput(
            input_key="test_endorsed",
            label=I18nText(translations={"en": "Deliverable"}),
            required=True,
            is_chat_history=True,
            is_endorsed_deliverable=True,
            input_modes=["file"],
            description=I18nText(translations={"en": "Desc"}),
        )

    with pytest.raises(
        ValidationError, match="cannot be simultaneously marked as both an assignment and is_endorsed_deliverable"
    ):
        ExpectedInput(
            input_key="test_endorsed",
            label=I18nText(translations={"en": "Deliverable"}),
            required=True,
            is_endorsed_deliverable=True,
            input_modes=["assignment"],
            description=I18nText(translations={"en": "Desc"}),
        )

    with pytest.raises(
        ValidationError, match="cannot be simultaneously marked as both a questionnaire and is_endorsed_deliverable"
    ):
        ExpectedInput(
            input_key="test_endorsed",
            label=I18nText(translations={"en": "Deliverable"}),
            required=True,
            is_endorsed_deliverable=True,
            input_modes=["questionnaire"],
            description=I18nText(translations={"en": "Desc"}),
            questionnaire_definition=[
                QuestionnaireItem(
                    question_id="q1",
                    question=I18nText(translations={"en": "Q1"}),
                    type="text",
                )
            ],
        )


def test_allowed_input_modes_ssot() -> None:
    """Verify ALLOWED_INPUT_MODES SSOT members."""
    expected = frozenset({"file", "paste", "text", "questionnaire", "assignment"})
    assert ALLOWED_INPUT_MODES == expected


def test_step_causal_discovery_valid_without_criteria() -> None:
    """Test valid instantiation of a CAUSAL_DISCOVERY Step with empty criteria."""
    step = Step(
        id="stp_0123456789abcdef",
        slug="step_causal",
        name=I18nText(translations={"en": "Causal Discovery Step"}),
        type=StepType.CAUSAL_DISCOVERY,
        role_block_id="blk_0123456789abcdef",
        extraction_protocol_block_id="blk_abcdef0123456789",
        criteria_block_ids=[],
        cognitive_tier=CognitiveTier.FAST,
    )
    assert step.id == "stp_0123456789abcdef"
    assert step.type == StepType.CAUSAL_DISCOVERY
    assert step.criteria_block_ids == []
    assert step.cognitive_tier == CognitiveTier.FAST


def test_step_causal_discovery_missing_extraction_protocol_raises_app_exception() -> None:
    """Test that CAUSAL_DISCOVERY step without extraction_protocol_block_id fails validation."""
    with pytest.raises(AppException) as exc_info:
        Step(
            id="stp_0123456789abcdef",
            slug="step_causal_broken",
            name=I18nText(translations={"en": "Broken Step"}),
            type=StepType.CAUSAL_DISCOVERY,
            role_block_id="blk_0123456789abcdef",
            extraction_protocol_block_id=None,
            criteria_block_ids=[],
            cognitive_tier=CognitiveTier.FAST,
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "must define a valid extraction_protocol_block_id" in exc_info.value.message


def test_step_causal_discovery_missing_cognitive_tier_raises_app_exception() -> None:
    """Test that CAUSAL_DISCOVERY step without cognitive_tier fails validation."""
    with pytest.raises(AppException) as exc_info:
        Step(
            id="stp_0123456789abcdef",
            slug="step_causal_broken",
            name=I18nText(translations={"en": "Broken Step"}),
            type=StepType.CAUSAL_DISCOVERY,
            role_block_id="blk_0123456789abcdef",
            extraction_protocol_block_id="blk_abcdef0123456789",
            criteria_block_ids=[],
            cognitive_tier=None,
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "must declare an explicit cognitive_tier" in exc_info.value.message


def test_step_rule_causal_source_step_id_in_depends_on_valid() -> None:
    """Test StepRule with causal_source_step_id present in depends_on validates successfully."""
    step_rule = StepRule(
        id="sr_0123456789abcdef",
        task_blueprint="stp_0123456789abcdef",
        depends_on=["sr_1111111111111111", "sr_2222222222222222"],
        causal_source_step_id="sr_1111111111111111",
    )
    assert step_rule.causal_source_step_id == "sr_1111111111111111"
    assert "sr_1111111111111111" in step_rule.depends_on


def test_step_rule_causal_source_step_id_not_in_depends_on_raises_app_exception() -> None:
    """Test StepRule with causal_source_step_id not in depends_on raises AppException."""
    with pytest.raises(AppException) as exc_info:
        StepRule(
            id="sr_0123456789abcdef",
            task_blueprint="stp_0123456789abcdef",
            depends_on=["sr_2222222222222222"],
            causal_source_step_id="sr_1111111111111111",
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "references causal_source_step_id" in exc_info.value.message


def test_step_rule_invalid_opaque_id_raises_validation_error() -> None:
    """Boundary test: StepRule with causal_source_step_id violating OPAQUE_STRIPE_ID_REGEX raises ValidationError."""
    with pytest.raises(ValidationError):
        StepRule(
            id="sr_0123456789abcdef",
            task_blueprint="stp_0123456789abcdef",
            depends_on=["invalid_id!"],
            causal_source_step_id="invalid_id!",
        )


def test_step_zone_assignment_and_default() -> None:
    """Test Step zone default value, explicit assignment, and validation."""
    # 1. Default zone should be ZONE_B
    step_default = Step(
        id="stp_0123456789abcdef",
        slug="step_default_zone",
        name=I18nText(translations={"en": "Default Zone"}),
        type=StepType.LOGIC,
        hook="backend_v2.hooks.transform_hook",
    )
    assert step_default.zone == StepZone.ZONE_B

    # 2. Explicit ZONE_A
    step_zone_a = Step(
        id="stp_0123456789abcdef",
        slug="step_zone_a",
        name=I18nText(translations={"en": "Zone A Step"}),
        type=StepType.LOGIC,
        hook="backend_v2.hooks.transform_hook",
        zone=StepZone.ZONE_A,
    )
    assert step_zone_a.zone == StepZone.ZONE_A

    # 3. Explicit ZONE_C via string
    step_zone_c = Step(
        id="stp_0123456789abcdef",
        slug="step_zone_c",
        name=I18nText(translations={"en": "Zone C Step"}),
        type=StepType.LOGIC,
        hook="backend_v2.hooks.transform_hook",
        zone="zone_c",
    )
    assert step_zone_c.zone == StepZone.ZONE_C

    # 4. Invalid zone raises ValidationError
    with pytest.raises(ValidationError):
        Step.model_validate(
            {
                "id": "stp_0123456789abcdef",
                "slug": "step_invalid_zone",
                "name": {"translations": {"en": "Invalid Zone"}},
                "type": "logic",
                "hook": "backend_v2.hooks.transform_hook",
                "zone": "invalid_zone",
            }
        )

