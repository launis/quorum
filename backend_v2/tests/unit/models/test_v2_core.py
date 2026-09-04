"""Unit tests for v2_core models and trace metadata DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataEnvelope
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.llm import TokenUsage
from backend_v2.models.v2_core import (
    AllowedMCPTool,
    ExecutionRecord,
    ExecutionStep,
    ExecutionSummarySnapshot,
    ExpectedInput,
    I18nText,
    MatrixClaim,
    MatrixScale,
    ModelProfile,
    ProviderExtraParamsDTO,
    QuestionnaireItem,
    Step,
    StepRule,
    TDAAssertion,
    Workflow,
)


def test_provider_extra_params_valid() -> None:
    """Test ProviderExtraParamsDTO initialization with valid data."""
    params = ProviderExtraParamsDTO(
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        max_output_tokens=2048,
    )
    assert params.temperature == 0.7
    assert params.top_p == 0.9
    assert params.top_k == 40
    assert params.max_output_tokens == 2048


def test_provider_extra_params_extra_forbidden() -> None:
    """Test Contract 2: ProviderExtraParamsDTO raises ValidationError on unknown extra field."""
    with pytest.raises(ValidationError) as exc_info:
        ProviderExtraParamsDTO(temperature=0.7, unknown_field="invalid")  # type: ignore[call-arg]
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_provider_extra_params_type_strictness() -> None:
    """Test Contract 3: ProviderExtraParamsDTO raises ValidationError on type mismatch."""
    with pytest.raises(ValidationError) as exc_info:
        ProviderExtraParamsDTO(max_output_tokens="two_thousand")  # type: ignore[arg-type]
    assert "Input should be a valid integer" in str(exc_info.value)


def test_model_profile_uses_provider_extra_params() -> None:
    """Test ModelProfile additional_params defaults to ProviderExtraParamsDTO."""
    profile = ModelProfile(
        model_name="gemini-1.5-pro",
        provider="vertex_ai",
    )
    assert isinstance(profile.additional_params, ProviderExtraParamsDTO)
    assert profile.additional_params.temperature is None


def test_step_trace_metadata_extra_forbidden() -> None:
    """Test Contract 4: StepTraceMetadataDTO raises ValidationError on forbidden extra field."""
    with pytest.raises(ValidationError) as exc_info:
        StepTraceMetadataDTO(task_blueprint="step_1", fake_key=123)  # type: ignore[call-arg]
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_step_trace_metadata_type_strictness() -> None:
    """Test StepTraceMetadataDTO raises ValidationError on invalid types."""
    with pytest.raises(ValidationError):
        StepTraceMetadataDTO(chunk_size="invalid_size")  # type: ignore[arg-type]


def test_trace_event_metadata_envelope_hydration() -> None:
    """Test TraceEventMetadataEnvelope hydrates StepTraceMetadataDTO from _step_metadata alias."""
    raw_event_content = {
        "_step_metadata": {
            "task_blueprint": "step_extract",
            "model_strategy": "fast",
            "chunk_size": 2,
            "token_usage": {
                "prompt_tokens": 150,
                "completion_tokens": 50,
                "total_tokens": 200,
            },
        }
    }
    envelope = TraceEventMetadataEnvelope.model_validate(raw_event_content)
    assert envelope.step_metadata is not None
    assert envelope.step_metadata.task_blueprint == "step_extract"
    assert envelope.step_metadata.model_strategy == "fast"
    assert envelope.step_metadata.chunk_size == 2
    assert isinstance(envelope.step_metadata.token_usage, TokenUsage)
    assert envelope.step_metadata.token_usage.prompt_tokens == 150
    assert envelope.step_metadata.token_usage.completion_tokens == 50
    assert envelope.step_metadata.token_usage.total_tokens == 200


def test_i18n_text_validation() -> None:
    """Test I18nText resolution and validation."""
    text = I18nText(translations={"en": "Hello", "fi": "Hei"})
    assert text.resolve("en") == "Hello"
    assert text.resolve("fi") == "Hei"
    assert text.resolve("de") == "Hello"  # Fallback to en

    with pytest.raises(AppException):
        I18nText(translations={})


def test_step_model_validation_rules() -> None:
    """Test Step validation rules for LLM and logic steps."""
    # Valid LLM step
    step_llm = Step(
        id="stp_11111111111111111111111111111111",
        slug="step_llm",
        name=I18nText(translations={"en": "LLM Step"}),
        description=I18nText(translations={"en": "Desc"}),
        type="llm",
        model_strategy="fast",
        role_block_id="blk_11111111111111111111111111111111",
        extraction_protocol_block_id="blk_11111111111111111111111111111111",
        criteria_block_ids=["blk_11111111111111111111111111111111"],
    )
    assert step_llm.type == "llm"

    # Missing criteria_block_ids in LLM step
    with pytest.raises(ValidationError):
        Step(
            id="stp_11111111111111111111111111111111",
            slug="step_llm_invalid",
            name=I18nText(translations={"en": "LLM Step"}),
            description=I18nText(translations={"en": "Desc"}),
            type="llm",
            model_strategy="fast",
            role_block_id="blk_11111111111111111111111111111111",
            extraction_protocol_block_id="blk_11111111111111111111111111111111",
            criteria_block_ids=[],
        )

    # Missing extraction_protocol_block_id in LLM step
    with pytest.raises(ValidationError):
        Step(
            id="stp_11111111111111111111111111111111",
            slug="step_llm_invalid",
            name=I18nText(translations={"en": "LLM Step"}),
            description=I18nText(translations={"en": "Desc"}),
            type="llm",
            model_strategy="fast",
            role_block_id="blk_11111111111111111111111111111111",
            criteria_block_ids=["blk_11111111111111111111111111111111"],
        )

    # Valid logic step
    step_logic = Step(
        id="stp_22222222222222222222222222222222",
        slug="step_logic",
        name=I18nText(translations={"en": "Logic Step"}),
        description=I18nText(translations={"en": "Desc"}),
        type="logic",
        hook="scoring_hook",
    )
    assert step_logic.type == "logic"

    # Logic step missing hook
    with pytest.raises(ValidationError):
        Step(
            id="stp_22222222222222222222222222222222",
            slug="step_logic_invalid",
            name=I18nText(translations={"en": "Logic Step"}),
            description=I18nText(translations={"en": "Desc"}),
            type="logic",
        )


def test_workflow_model_validation_rules() -> None:
    """Test Workflow DAG validations."""
    # Valid workflow
    wf = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        status="active",
        version=1,
        default_profile_id="pro_1234567890abcdef1234567890abcdef",
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[
            ExpectedInput(
                input_key="doc",
                label=I18nText(translations={"en": "Doc"}),
                required=True,
                description=I18nText(translations={"en": "Doc desc"}),
                input_modes=["paste"],
            )
        ],
        steps=[
            StepRule(
                id="stp_11111111111111111111111111111111",
                task_blueprint="step_extract",
                depends_on=[],
            ),
            StepRule(
                id="stp_22222222222222222222222222222222",
                task_blueprint="step_eval",
                depends_on=["stp_11111111111111111111111111111111"],
            ),
        ],
    )
    assert len(wf.steps) == 2

    # Self dependency cycle
    with pytest.raises(ValidationError):
        Workflow(
            id="wor_1234567890abcdef1234567890abcdef",
            slug="test_wf_cycle",
            name=I18nText(translations={"en": "Test WF"}),
            description=I18nText(translations={"en": "Desc"}),
            status="active",
            version=1,
            default_profile_id="pro_1234567890abcdef1234567890abcdef",
            allowed_exports=[],
            historical_context_mode=HistoricalContextMode.DISABLED,
            expected_inputs=[],
            steps=[
                StepRule(
                    id="stp_11111111111111111111111111111111",
                    task_blueprint="step_1",
                    depends_on=["stp_11111111111111111111111111111111"],
                ),
            ],
        )

    # Missing dependency reference in steps
    with pytest.raises(ValidationError):
        Workflow(
            id="wor_1234567890abcdef1234567890abcdef",
            slug="test_wf_bad_dep",
            name=I18nText(translations={"en": "Test WF"}),
            description=I18nText(translations={"en": "Desc"}),
            status="active",
            version=1,
            default_profile_id="pro_1234567890abcdef1234567890abcdef",
            allowed_exports=[],
            historical_context_mode=HistoricalContextMode.DISABLED,
            expected_inputs=[],
            steps=[
                StepRule(
                    id="stp_11111111111111111111111111111111",
                    task_blueprint="step_1",
                    depends_on=["stp_missing"],
                ),
            ],
        )


def test_allowed_mcp_tool_validation() -> None:
    """Test AllowedMCPTool validation."""
    tool = AllowedMCPTool(
        tool_id="tool_1",
        name=I18nText(translations={"en": "Web Search"}),
        description="Search the web",
    )
    assert tool.name.resolve("en") == "Web Search"


def test_matrix_models_validation() -> None:
    """Test MatrixScale, MatrixClaim, and TDAAssertion validation."""
    tda = TDAAssertion(concept_description="Verify evidence", inverse_evidence=False, aggregation_mode="EXISTS")
    assert tda.concept_description == "Verify evidence"

    claim = MatrixClaim(
        label=I18nText(translations={"en": "Claim"}),
        tda_assertions=[tda],
    )
    assert len(claim.tda_assertions) == 1

    scale = MatrixScale(score=1, ai_label="POOR", claims=[claim])
    assert scale.score == 1


def test_execution_step_model() -> None:
    """Test ExecutionStep with physical model provenance and FinOps metrics."""
    step = ExecutionStep(
        id="stp_11111111111111111111111111111111",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        model_strategy="fast",
        physical_model="vertex_ai/gemini-2.5-flash",
        system_fingerprint="fp_test_123",
        prompt_tokens=150,
        completion_tokens=50,
        cached_tokens=20,
        reasoning_tokens=10,
        cost_usd=0.0015,
        duration_ms=450,
        chunk_count=2,
    )
    assert step.id == "stp_11111111111111111111111111111111"
    assert step.status == ExecutionStatus.PASSED
    assert step.model_strategy == "fast"
    assert step.physical_model == "vertex_ai/gemini-2.5-flash"
    assert step.system_fingerprint == "fp_test_123"
    assert step.prompt_tokens == 150
    assert step.cost_usd == 0.0015


def test_execution_step_negative_tokens_fail_fast() -> None:
    """Verify negative token counts fail validation immediately."""
    with pytest.raises(ValidationError):
        ExecutionStep(
            id="stp_11111111111111111111111111111111",
            label="Step 1",
            prompt_tokens=-10,
        )


def test_execution_step_negative_cost_fails_fast() -> None:
    """Verify negative cost fails validation immediately."""
    with pytest.raises(ValidationError):
        ExecutionStep(
            id="stp_11111111111111111111111111111111",
            label="Step 1",
            cost_usd=-0.5,
        )


def test_execution_step_all_zeros_boundary() -> None:
    """Verify all-zero metrics validate at the minimum boundary."""
    step = ExecutionStep(
        id="stp_11111111111111111111111111111111",
        label="Step Non LLM",
        status=ExecutionStatus.PASSED,
        prompt_tokens=0,
        completion_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0,
        cost_usd=0.0,
        duration_ms=0,
    )
    assert step.prompt_tokens == 0
    assert step.cost_usd == 0.0
    assert step.physical_model is None


def test_execution_summary_snapshot_model() -> None:
    """Test ExecutionSummarySnapshot model creation and defaults."""
    snapshot = ExecutionSummarySnapshot(
        strictness_level=90,
        is_ensemble_run=True,
        is_degraded=False,
        system_concurrency_snapshot={"active_workers": 2},
    )
    assert snapshot.strictness_level == 90
    assert snapshot.is_ensemble_run is True
    assert snapshot.system_concurrency_snapshot["active_workers"] == 2


def test_execution_record_flat_finops_and_steps() -> None:
    """Test ExecutionRecord with flat FinOps metrics and steps collection."""
    step = ExecutionStep(
        id="stp_11111111111111111111111111111111",
        label="Ingest",
        status=ExecutionStatus.PASSED,
        prompt_tokens=100,
        completion_tokens=40,
        cost_usd=0.001,
    )
    record = ExecutionRecord(
        id="exe_1111111111111111",
        workflow_id="wor_1111111111111111",
        workflow_version=2,
        output_profile_id="prof_default",
        target_locale="fi",
        steps=[step],
        prompt_tokens=100,
        completion_tokens=40,
        dag_cost_usd=0.001,
        models_used={"fast": 140},
    )
    assert record.id == "exe_1111111111111111"
    assert record.workflow_version == 2
    assert len(record.steps) == 1
    assert record.steps[0].id == "stp_11111111111111111111111111111111"
    assert record.prompt_tokens == 100
    assert record.dag_cost_usd == 0.001
    assert record.target_locale == "fi"


def test_execution_record_extra_forbidden() -> None:
    """Verify ExecutionRecord rejects unknown extra fields."""
    with pytest.raises(ValidationError):
        ExecutionRecord(
            id="exe_1111111111111111",
            workflow_id="wor_1111111111111111",
            output_profile_id="prof_default",
            target_locale="fi",
            unknown_legacy_field="illegal",  # type: ignore[call-arg]
        )


def test_coerce_to_tuple_helper() -> None:
    """Verifies _coerce_to_tuple converts lists to tuples."""
    from backend_v2.models.v2_core import _coerce_to_tuple

    assert _coerce_to_tuple([1, 2, 3]) == (1, 2, 3)
    assert _coerce_to_tuple("not_a_list") == "not_a_list"


def test_tda_assertion_validation_rules() -> None:
    """Verifies TDAAssertion business rules fail-fast."""
    # 1. inverse_evidence requires EXISTS
    with pytest.raises(ValueError, match="strictly requires 'EXISTS'"):
        TDAAssertion(
            concept_description="Concept description valid length",
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
        )

    # 2. enforce_pre_flight requires syntactic_anchors
    with pytest.raises(ValueError, match="requires at least one syntactic anchor"):
        TDAAssertion(
            concept_description="Concept description valid length",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            enforce_pre_flight=True,
            syntactic_anchors=[],
        )

    # 3. EXTRACTIVE_SENSOR requires facts_to_find and logical_expression
    with pytest.raises(ValueError, match="requires at least one fact"):
        TDAAssertion(
            concept_description="Concept description valid length",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            evaluation_track="EXTRACTIVE_SENSOR",
            facts_to_find=[],
            logical_expression="F1",
        )

    with pytest.raises(ValueError, match="requires a defined logical_expression"):
        TDAAssertion(
            concept_description="Concept description valid length",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            evaluation_track="EXTRACTIVE_SENSOR",
            facts_to_find=["F1"],
            logical_expression="",
        )


def test_step_rule_extract_variable_references() -> None:
    """Verifies StepRule extracts dynamic variable references correctly."""
    rule = StepRule(
        task_blueprint="stp_bp1",
        input_mappings={"doc": "$inputs.document", "prev": "$steps.step_1.output", "static": "plain_text"},
    )
    refs = rule.extract_variable_references()
    assert "$inputs.document" in refs
    assert "$steps.step_1.output" in refs
    assert "plain_text" not in refs


def test_expected_input_questionnaire_validations() -> None:
    """Verifies ExpectedInput questionnaire mode consistency."""
    # Empty input modes
    with pytest.raises(ValueError, match="must have at least one input_mode"):
        ExpectedInput(
            input_key="k1",
            label=I18nText(translations={"en": "Label"}),
            description=I18nText(translations={"en": "Desc"}),
            required=True,
            input_modes=[],
        )

    valid_q_item = QuestionnaireItem(
        question_id="q1",
        question=I18nText(translations={"en": "Q1"}),
        type="text",
    )

    # Questionnaire mixed with is_chat_history
    with pytest.raises(ValueError, match="cannot use 'questionnaire' mode when flagged as chat history"):
        ExpectedInput(
            input_key="k2",
            label=I18nText(translations={"en": "Label"}),
            description=I18nText(translations={"en": "Desc"}),
            required=True,
            input_modes=["questionnaire"],
            is_chat_history=True,
            questionnaire_definition=[valid_q_item],
        )

    # Questionnaire mixed with other modes
    with pytest.raises(ValueError, match="cannot mix 'questionnaire' with other input modes"):
        ExpectedInput(
            input_key="k3",
            label=I18nText(translations={"en": "Label"}),
            description=I18nText(translations={"en": "Desc"}),
            required=True,
            input_modes=["questionnaire", "text"],
            questionnaire_definition=[valid_q_item],
        )

    # Questionnaire lacks definitions
    with pytest.raises(ValueError, match="uses 'questionnaire' mode but lacks definitions"):
        ExpectedInput(
            input_key="k4",
            label=I18nText(translations={"en": "Label"}),
            description=I18nText(translations={"en": "Desc"}),
            required=True,
            input_modes=["questionnaire"],
            questionnaire_definition=[],
        )

    # Non-questionnaire has definitions
    with pytest.raises(ValueError, match="cannot have questionnaire_definition when 'questionnaire' mode is not active"):
        ExpectedInput(
            input_key="k5",
            label=I18nText(translations={"en": "Label"}),
            description=I18nText(translations={"en": "Desc"}),
            required=True,
            input_modes=["text"],
            questionnaire_definition=[valid_q_item],
        )


def test_output_profile_synthesis_properties_and_custom_scale_validation() -> None:
    """Verifies OutputProfile synthesis properties and custom scale validations."""
    from backend_v2.models.enums import DisplayScale
    from backend_v2.models.v2_core import MatrixSynthesisGroup, OutputProfile

    role_blk_id = "blk_1234567890abcdef"

    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="slug",
        workflow_id="wf_1234567890123456",
        name=I18nText(translations={"en": "Prof"}),
        matrix_visible_columns=["row_explanation"],
        target_block_order=["executive_summary_block", "matrix_graphs_block"],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                title=I18nText(translations={"en": "Group"}),
                target_blocks=[role_blk_id],
            )
        ],
    )
    assert profile.requires_row_explanations is True
    assert profile.requires_executive_synthesis is True
    assert profile.requires_group_synthesis is True
    assert profile.is_synthesis_expected is True

    # Custom scale validation: missing min/max
    with pytest.raises(ValueError, match="custom_scale_min and custom_scale_max are required"):
        OutputProfile(
            id="prf_1234567890abcdef",
            slug="slug",
            workflow_id="wf_1234567890123456",
            name=I18nText(translations={"en": "Prof"}),
            target_block_order=["executive_summary_block"],
            display_scale=DisplayScale.CUSTOM,
        )

    # Custom scale validation: max <= min
    with pytest.raises(ValueError, match="must be strictly greater than custom_scale_min"):
        OutputProfile(
            id="prf_1234567890abcdef",
            slug="slug",
            workflow_id="wf_1234567890123456",
            name=I18nText(translations={"en": "Prof"}),
            target_block_order=["executive_summary_block"],
            display_scale=DisplayScale.CUSTOM,
            custom_scale_min=10.0,
            custom_scale_max=5.0,
        )


def test_base_tda_extraction_validation() -> None:
    """Verifies BaseTDAExtraction cross-validation between exact_quotes and contextual_override."""
    from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
    from backend_v2.models.v2_core import BaseTDAExtraction

    # contextual_override=True with exact_quotes raises ValueError
    with pytest.raises(ValueError, match="cannot be combined with exact_quotes"):
        BaseTDAExtraction(
            exact_quotes=[LLMExtractedQuote(text="quote")],
            localized_anchors_found=["anchor"],
            contextual_override=True,
            semantic_reasoning="reasoning",
        )

    # contextual_override=False with [CONTEXTUAL_OVERRIDE_APPLIED] raises ValueError
    with pytest.raises(ValueError, match="Cross-validation failed"):
        BaseTDAExtraction(
            exact_quotes=[LLMExtractedQuote(text="[CONTEXTUAL_OVERRIDE_APPLIED]")],
            localized_anchors_found=["anchor"],
            contextual_override=False,
            semantic_reasoning="reasoning",
        )


def test_execution_create_resolve_matrix_sampling_strategy() -> None:
    """Verifies ExecutionCreate resolves matrix_sampling_strategy when passed as None."""
    from backend_v2.models.v2_core import ExecutionCreate

    ec = ExecutionCreate.model_validate(
        {
            "workflow_id": "wf_1",
            "target_locale": "fi",
            "matrix_sampling_strategy": None,
        }
    )
    assert ec.matrix_sampling_strategy is not None

