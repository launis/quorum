import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import ReportDataDTO

# Import existing tests so they are included in the coverage run for v2_core.py
from backend_v2.tests.unit.models.dtos.test_output_profile import *  # noqa: F403, F401
from backend_v2.tests.unit.models.test_output_profile_regression import *  # noqa: F403, F401
from backend_v2.tests.unit.test_core_base import *  # noqa: F403, F401
from backend_v2.tests.unit.test_report_data_dto import *  # noqa: F403, F401
from backend_v2.tests.unit.test_v2_core_models import *  # noqa: F403, F401
from backend_v2.tests.unit.test_v2_core_strictness import *  # noqa: F403, F401


def test_report_data_dto_strictness_level_validation() -> None:
    dto = ReportDataDTO.model_validate(
        {
            "workflow_id": "wf_1",
            "execution_id": "exe_1",
            "profile_id": "prof_1",
        }
    )
    assert dto.strictness_level is None


def test_scorecard_atom_dto_firewall() -> None:
    from backend_v2.models.enums import ExecutionStatus, VisualIntent
    from backend_v2.models.v2_core import ScorecardAtomDTO

    larger_payload = {
        "atom_id": "atom_1",
        "level": 1,
        "level_name": "Level 1",
        "claim_label": "Claim 1",
        "extracted_facts": {},
        "exact_quotes": [{"quote": "Quote 1", "source_id": "DOC-1"}],
        "internal_logic_en": {
            "step_1_identify_premise": "1",
            "step_2_scan_source": "2",
            "step_3_evaluate_anti_patterns": "3",
            "step_4_final_conclusion": "4",
        },
        "status": ExecutionStatus.PASSED,
        "semantic_reasoning": "Reason",
        "contextual_override": False,
        "structural_location": None,
        "chart_display_label": "N/A",
        "visual_intent": VisualIntent.NEUTRAL,
        "db_secret_key": "should_be_stripped",
        "internal_ai_score": 0.99,
    }

    with pytest.raises(ValidationError):
        ScorecardAtomDTO.model_validate(larger_payload, context={"alias_registry": {"DOC-1": "opaque_1"}})


def test_mcp_audit_trace_new_fields() -> None:
    from backend_v2.models.v2_core import MCPAuditTrace

    trace = MCPAuditTrace(
        tool_id="test_tool",
        step_name="test_step",
        query="test query",
        knowledge_gap="What is the test about?",
        search_rationale="To verify the test.",
        reasoning="Because it is a test.",
    )
    assert trace.knowledge_gap == "What is the test about?"
    assert trace.search_rationale == "To verify the test."


def test_citation_extraction_item_dto_new_fields() -> None:
    from backend_v2.models.domain.mcp import CitationExtractionItemDTO

    item = CitationExtractionItemDTO(
        claim_text="This is a claim",
        search_query="Search query",
        knowledge_gap="Need more info",
        search_rationale="To be certain",
        reasoning="Just in case",
    )
    assert item.knowledge_gap == "Need more info"
    assert item.search_rationale == "To be certain"


def test_report_data_dto_rejects_legacy_fields() -> None:
    from backend_v2.models.v2_core import ReportDataDTO

    # Test 1: evaluative_matrices is forbidden
    with pytest.raises(ValidationError) as exc_info:
        ReportDataDTO.model_validate(
            {"workflow_id": "wf_1", "execution_id": "exe_1", "profile_id": "prof_1", "evaluative_matrices": []}
        )
    assert "evaluative_matrices" in str(exc_info.value)

    # Test 2: content_blocks is forbidden
    with pytest.raises(ValidationError) as exc_info2:
        ReportDataDTO.model_validate(
            {"workflow_id": "wf_1", "execution_id": "exe_1", "profile_id": "prof_1", "content_blocks": []}
        )
    assert "content_blocks" in str(exc_info2.value)

    # Test 3: penalties_applied is forbidden
    with pytest.raises(ValidationError) as exc_info3:
        ReportDataDTO.model_validate(
            {"workflow_id": "wf_1", "execution_id": "exe_1", "profile_id": "prof_1", "penalties_applied": []}
        )
    assert "penalties_applied" in str(exc_info3.value)


def test_scorecard_atom_contested_warning_mapping() -> None:
    from backend_v2.models.enums import ExecutionStatus, VisualIntent
    from backend_v2.models.v2_core import ScorecardAtomDTO

    payload = {
        "atom_id": "atom_1",
        "level": 1,
        "level_name": "Level 1",
        "claim_label": "Claim 1",
        "extracted_facts": {},
        "exact_quotes": [],
        "internal_logic_en": {
            "step_1_identify_premise": "1",
            "step_2_scan_source": "2",
            "step_3_evaluate_anti_patterns": "3",
            "step_4_final_conclusion": "4",
        },
        "status": ExecutionStatus.PASSED,
        "semantic_reasoning": "Reason",
        "contextual_override": True,
        "structural_location": None,
        "chart_display_label": "N/A",
        "visual_intent": VisualIntent.NEUTRAL,
    }

    dto = ScorecardAtomDTO.model_validate(payload)
    assert dto.visual_intent == VisualIntent.WARNING


def test_i18n_text_validation_and_resolve() -> None:
    from backend_v2.exceptions import AppException
    from backend_v2.models.v2_core import I18nText

    # 1. Missing or whitespace English translation raises AppException
    with pytest.raises(AppException):
        I18nText.model_validate({"default_locale": "fi", "translations": {"fi": "Moi", "en": "   "}})

    # 2. Resolve logic
    i18n = I18nText(default_locale="fi", translations={"fi": "Moi", "en": "Hello", "sv": "Hej"})
    assert i18n.resolve("sv-SE") == "Hej"
    assert i18n.resolve("de") == "Moi"  # fallback to default_locale
    assert i18n.get("sv") == "Hej"
    assert i18n.get("de") == "Moi"  # fallback to default_locale

    i18n_en = I18nText(default_locale="de", translations={"en": "Hello"})
    assert i18n_en.resolve("fr") == "Hello"
    assert i18n_en.get("fr") == "Hello"


def test_tda_assertion_validation_branches() -> None:
    from backend_v2.models.v2_core import TDAAssertion

    # Inverse evidence requires EXISTS aggregation mode
    with pytest.raises(ValueError, match="Inverse evidence"):
        TDAAssertion.model_validate(
            {
                "tda_id": "tda_11111111111111111111111111111111",
                "concept_description": "Concept description",
                "inverse_evidence": True,
                "aggregation_mode": "ALL_MUST_COMPLY",
            }
        )

    # EXTRACTIVE_SENSOR requires facts_to_find and logical_expression
    with pytest.raises(ValueError, match="facts_to_find"):
        TDAAssertion.model_validate(
            {
                "tda_id": "tda_11111111111111111111111111111111",
                "concept_description": "Concept description",
                "inverse_evidence": False,
                "aggregation_mode": "EXISTS",
                "evaluation_track": "EXTRACTIVE_SENSOR",
                "facts_to_find": [],
                "logical_expression": "A and B",
            }
        )

    with pytest.raises(ValueError, match="logical_expression"):
        TDAAssertion.model_validate(
            {
                "tda_id": "tda_11111111111111111111111111111111",
                "concept_description": "Concept description",
                "inverse_evidence": False,
                "aggregation_mode": "EXISTS",
                "evaluation_track": "EXTRACTIVE_SENSOR",
                "facts_to_find": ["fact1"],
                "logical_expression": "",
            }
        )


def test_prompt_block_validator_branches() -> None:
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory
    from backend_v2.models.v2_core import I18nText, PromptBlock

    label = I18nText(default_locale="en", translations={"en": "Scale Block"})
    desc = I18nText(default_locale="en", translations={"en": "Scale Desc"})

    # Empty scales list raises ValueError
    with pytest.raises(ValueError, match="vähintään yksi MatrixScale"):
        PromptBlock.model_validate(
            {
                "id": "blk_1111111111111111",
                "slug": "empty_scales",
                "label": label,
                "description": desc,
                "category_id": PromptBlockCategory.MATRIX,
                "type": BlockDataType.FLOAT,
                "scales": [],
            }
        )

    # Scale without claims raises ValueError
    with pytest.raises(ValueError, match="vähintään yksi claim"):
        PromptBlock.model_validate(
            {
                "id": "blk_1111111111111111",
                "slug": "scale_no_claims",
                "label": label,
                "description": desc,
                "category_id": PromptBlockCategory.MATRIX,
                "type": BlockDataType.FLOAT,
                "scales": [{"score": 1.0, "label": label, "description": desc, "claims": []}],
            }
        )

    # Matrix category without computable scales
    with pytest.raises(ValueError, match="computed_min ja computed_max on pakko pystyä laskemaan"):
        PromptBlock.model_validate(
            {
                "id": "blk_1111111111111111",
                "slug": "matrix_no_scales",
                "label": label,
                "description": desc,
                "category_id": PromptBlockCategory.MATRIX,
                "type": BlockDataType.FLOAT,
                "scales": None,
            }
        )


def test_step_and_step_rule_validation() -> None:
    from backend_v2.models.v2_core import I18nText, Step, StepRule

    name = I18nText(default_locale="en", translations={"en": "Step 1"})

    # Step LLM without extraction protocol
    with pytest.raises(ValueError, match="extraction_protocol_block_id"):
        Step.model_validate(
            {
                "id": "step_1111111111111111",
                "slug": "step_llm",
                "name": name,
                "type": "llm",
                "model_strategy": "fast",
                "criteria_block_ids": ["blk_1234567890123456"],
                "extraction_protocol_block_id": None,
            }
        )

    # Step Logic without hook
    with pytest.raises(ValueError, match="must define a native 'hook'"):
        Step.model_validate(
            {
                "id": "step_1111111111111111",
                "slug": "step_logic",
                "name": name,
                "type": "logic",
                "hook": None,
            }
        )

    # StepRule extract_variable_references
    rule = StepRule(
        id="blk_1111111111111111",
        task_blueprint="step_1111111111111111",
        input_mappings={"doc": "$inputs.document", "static": "plain_text"},
    )
    assert rule.extract_variable_references() == ["$inputs.document"]


def test_expected_input_validation() -> None:
    from backend_v2.models.v2_core import ExpectedInput

    # Missing input_modes
    with pytest.raises(ValueError, match="at least one input_mode"):
        ExpectedInput.model_validate(
            {
                "input_key": "k1",
                "label": {"default_locale": "en", "translations": {"en": "K1"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "required": True,
                "input_modes": [],
            }
        )

    # Questionnaire mode with is_chat_history
    with pytest.raises(ValueError, match="cannot use 'questionnaire' mode when flagged as chat history"):
        ExpectedInput.model_validate(
            {
                "input_key": "k1",
                "label": {"default_locale": "en", "translations": {"en": "K1"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "required": True,
                "input_modes": ["questionnaire"],
                "is_chat_history": True,
                "questionnaire_definition": [
                    {
                        "question_id": "q1",
                        "question": {"default_locale": "en", "translations": {"en": "Q1"}},
                        "type": "text",
                    }
                ],
            }
        )

    # Questionnaire mixed with other modes
    with pytest.raises(ValueError, match="cannot mix 'questionnaire'"):
        ExpectedInput.model_validate(
            {
                "input_key": "k1",
                "label": {"default_locale": "en", "translations": {"en": "K1"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "required": True,
                "input_modes": ["questionnaire", "file"],
                "questionnaire_definition": [
                    {
                        "question_id": "q1",
                        "question": {"default_locale": "en", "translations": {"en": "Q1"}},
                        "type": "text",
                    }
                ],
            }
        )

    # Questionnaire mode without definition
    with pytest.raises(ValueError, match="uses 'questionnaire' mode but lacks definitions"):
        ExpectedInput.model_validate(
            {
                "input_key": "k1",
                "label": {"default_locale": "en", "translations": {"en": "K1"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "required": True,
                "input_modes": ["questionnaire"],
                "questionnaire_definition": [],
            }
        )

    # Non-questionnaire mode with questionnaire definition
    with pytest.raises(ValueError, match="cannot have questionnaire_definition"):
        ExpectedInput.model_validate(
            {
                "input_key": "k1",
                "label": {"default_locale": "en", "translations": {"en": "K1"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "required": True,
                "input_modes": ["file"],
                "questionnaire_definition": [
                    {
                        "question_id": "q1",
                        "question": {"default_locale": "en", "translations": {"en": "Q1"}},
                        "type": "text",
                    }
                ],
            }
        )


def test_workflow_validation_and_allowed_layout_targets() -> None:
    from backend_v2.models.enums import HistoricalContextMode, TargetBlockType
    from backend_v2.models.v2_core import I18nText, Step, StepRule, Workflow

    name = I18nText(default_locale="en", translations={"en": "Workflow Name"})
    desc = I18nText(default_locale="en", translations={"en": "Workflow Desc"})

    # Orphan dependency check
    with pytest.raises(ValueError, match="depends on 'blk_2222222222222222'"):
        Workflow.model_validate(
            {
                "id": "wf_1111111111111111",
                "slug": "wf_test",
                "name": name,
                "description": desc,
                "status": "active",
                "version": 1,
                "default_profile_id": "prf_1111111111111111",
                "allowed_exports": ["pdf"],
                "historical_context_mode": HistoricalContextMode.DISABLED,
                "steps": [
                    StepRule(
                        id="blk_1111111111111111",
                        task_blueprint="step_1111111111111111",
                        depends_on=["blk_2222222222222222"],
                    )
                ],
            }
        )

    # Circular dependency check
    with pytest.raises(ValueError, match="Circular dependency detected"):
        Workflow.model_validate(
            {
                "id": "wf_1111111111111111",
                "slug": "wf_test",
                "name": name,
                "description": desc,
                "status": "active",
                "version": 1,
                "default_profile_id": "prf_1111111111111111",
                "allowed_exports": ["pdf"],
                "historical_context_mode": HistoricalContextMode.DISABLED,
                "steps": [
                    StepRule(
                        id="blk_1111111111111111",
                        task_blueprint="step_1111111111111111",
                        depends_on=["blk_2222222222222222"],
                    ),
                    StepRule(
                        id="blk_2222222222222222",
                        task_blueprint="step_2222222222222222",
                        depends_on=["blk_1111111111111111"],
                    ),
                ],
            }
        )

    # get_allowed_layout_targets
    wf = Workflow(
        id="wf_1111111111111111",
        slug="wf_valid",
        name=name,
        description=desc,
        status="active",
        version=1,
        default_profile_id="prf_1111111111111111",
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[
            StepRule(
                id="blk_1111111111111111",
                task_blueprint="step_1111111111111111",
            )
        ],
    )
    step1 = Step(
        id="step_1111111111111111",
        slug="step1",
        name=name,
        type="llm",
        model_strategy="fast",
        role_block_id="blk_1111111111111111",
        extraction_protocol_block_id="blk_2222222222222222",
        criteria_block_ids=["blk_3333333333333333"],
    )
    targets = wf.get_allowed_layout_targets([step1])
    assert "blk_1111111111111111" in targets
    assert "blk_2222222222222222" in targets
    assert "blk_3333333333333333" in targets
    assert TargetBlockType.METADATA_BLOCK.value in targets


def test_evaluated_atom_validation_branches() -> None:
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.v2_core import AtomResultDTO

    # 1. FAILED atom with override resets override and quote
    atom_fail = AtomResultDTO.model_validate(
        {
            "tda_id": "tda_11111111111111111111111111111111",
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Reason for failure",
            "contextual_override": True,
            "source_quote": "Some quote",
        }
    )
    assert atom_fail.contextual_override is False
    assert atom_fail.source_quote is None

    # 2. SYSTEM_ERROR without error_details raises ValueError
    with pytest.raises(ValueError, match="Error details are mandatory"):
        AtomResultDTO.model_validate(
            {
                "tda_id": "tda_11111111111111111111111111111111",
                "status": ExecutionStatus.SYSTEM_ERROR,
            }
        )

    # 3. PASSED atom without quote or override raises ValueError
    with pytest.raises(ValueError, match="source_quote is mandatory"):
        AtomResultDTO.model_validate(
            {
                "tda_id": "tda_11111111111111111111111111111111",
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Passed reasoning",
                "contextual_override": False,
                "source_quote": None,
            }
        )
