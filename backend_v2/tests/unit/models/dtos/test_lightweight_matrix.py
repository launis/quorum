import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import (
    AtomEvaluationItemDTO,
    LightweightMatrixOutput,
    OutputProfileConfig,
    ReasoningStepDTO,
)
from backend_v2.models.enums import XaiExtensionType


@pytest.mark.skip("Legacy architecture obsolete")
def test_output_profile_config_strictness() -> None:
    """Test OutputProfileConfig enforces Fail-Fast constraints."""
    config = OutputProfileConfig(visible_block_extensions=[XaiExtensionType.CITATION], visible_workflow_extensions=[])
    assert XaiExtensionType.CITATION in config.visible_block_extensions

    # Test strictness / forbid extra
    with pytest.raises(ValidationError):
        OutputProfileConfig(
            visible_block_extensions=[XaiExtensionType.CITATION],
            visible_workflow_extensions=[],
            extra_field="should_fail",  # type: ignore
        )

    # Test mutability (frozen=True)
    with pytest.raises(ValidationError):
        config.visible_block_extensions = []  # type: ignore


@pytest.mark.skip("Legacy architecture obsolete")
def test_lightweight_matrix_output_strictness() -> None:
    """Test LightweightMatrixOutput enforces Fail-Fast logic."""
    output = LightweightMatrixOutput(
        raw_score=45.5,
        normalized_score=90.0,
        level_breakdown={"level1": {"A": 1}},
        justification="Perfect score",
        evaluated_atoms={"atom1": True},
        extensions={XaiExtensionType.CITATION: "Some quote"},
    )
    assert output.normalized_score == 90.0
    assert output.extensions[XaiExtensionType.CITATION] == "Some quote"

    # Test normalized_score bounds (ge=0.0, le=100.0)
    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput(
            raw_score=150.0,
            normalized_score=150.0,  # Fails le=100.0
            level_breakdown={},
            justification="Too high",
            evaluated_atoms={},
            extensions={},
        )
    assert "Input should be less than or equal to 100" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput(
            raw_score=-10.0,
            normalized_score=-10.0,  # Fails ge=0.0
            level_breakdown={},
            justification="Too low",
            evaluated_atoms={},
            extensions={},
        )
    assert "Input should be greater than or equal to 0" in str(exc.value)

    # Test forbid extra
    with pytest.raises(ValidationError):
        LightweightMatrixOutput(
            raw_score=50.0,
            normalized_score=50.0,
            justification="Valid",
            evaluated_atoms={},
            extensions={},
            invalid_duck="quack",  # type: ignore
        )


@pytest.mark.skip("Legacy architecture obsolete")
def test_atom_evaluation_item_dto_strictness() -> None:
    """Test AtomEvaluationItemDTO enforces strict validation and V4.3 Blacklist."""
    item = AtomEvaluationItemDTO(
        atom_id="atom_123",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        extracted_facts={"fact_1": "Some valid quote"},
        status=None,
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert item.atom_id == "atom_123"
    assert item.evidence_found is True
    assert item.calculate_rule_satisfied(inverse_evidence=False) is True

    # Test forbid extra
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO(
            atom_id="atom_123",
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="stub",
                step_2_scan_source="stub",
                step_3_evaluate_anti_patterns="stub",
                step_4_final_conclusion="stub",
            ),
            extracted_facts={"fact_1": "Quote"},
            status=None,
            semantic_reasoning="Reasoning",
            contextual_override=False,
            structural_location="N/A",
            extra="not allowed",  # type: ignore
        )

    # Test V4.3 Phantom Boolean Sanity Check
    phantom = AtomEvaluationItemDTO(
        atom_id="atom_phantom",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        extracted_facts={"fact_1": "Not found"},
        status=None,
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert phantom.evidence_found is False

    # Test inverse evidence logic
    assert phantom.calculate_rule_satisfied(inverse_evidence=True) is True
    assert phantom.calculate_rule_satisfied(inverse_evidence=False) is False

    # Test status-based inverse evidence logic
    pass_item = AtomEvaluationItemDTO(
        atom_id="atom_pass",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        extracted_facts={"fact_1": "Found"},
        status="PASS",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert pass_item.calculate_rule_satisfied(inverse_evidence=True) is False
    assert pass_item.calculate_rule_satisfied(inverse_evidence=False) is True

    fail_item = AtomEvaluationItemDTO(
        atom_id="atom_fail",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        extracted_facts={"fact_1": "None"},
        status="FAIL",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert fail_item.calculate_rule_satisfied(inverse_evidence=True) is True
    assert fail_item.calculate_rule_satisfied(inverse_evidence=False) is False


@pytest.mark.skip("Legacy architecture obsolete")
def test_atom_evaluation_item_dto_accepts_exact_quote() -> None:
    """Test that AtomEvaluationItemDTO accepts exact_quote and correctly sanitises it against
    phantom boolean blacklist.
    """
    item = AtomEvaluationItemDTO(
        atom_id="atom_123",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        exact_quotes=["This is an exact quote"],
        status="PASS",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert item.atom_id == "atom_123"
    assert item.exact_quotes == ["This is an exact quote"]
    assert item.evidence_found is True

    # Test phantom blacklist for exact_quote
    phantom = AtomEvaluationItemDTO(
        atom_id="atom_123",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        exact_quotes=["None"],
        status="PASS",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert phantom.evidence_found is False


@pytest.mark.skip("Legacy architecture obsolete")
def test_atom_evaluation_item_dto_rejects_nulls() -> None:
    """Test that null values for strict non-nullable fields raise ValidationError."""
    raw_data = {
        "atom_id": None,
        "extracted_facts": None,
    }
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(raw_data)


@pytest.mark.skip("Legacy architecture obsolete")
def test_map_llm_extensions_with_base_tda_extraction_keys() -> None:
    """Test that Phase 4 BaseTDAExtraction fields map without raising extra_forbidden errors."""
    raw_data = {
        "raw_score": 50.0,
        "normalized_score": 50.0,
        "localized_anchors_found": ["avainsana1", "avainsana2"],
        "semantic_reasoning": "Käyttäjä ohjasi aktiivisesti...",
        "step_2_mitigating_context": "Prosessi alkoi...",
        "contextual_override": False,
        "exact_quote": "Megatrendien Kooste...",
    }

    mapped = LightweightMatrixOutput.map_llm_extensions_to_domain(raw_data)

    # This will fail with 'Extra inputs are not permitted' if the mapping doesn't strip the BaseTDA fields
    LightweightMatrixOutput.model_validate(mapped)


@pytest.mark.skip("Legacy architecture obsolete")
def test_atom_evaluation_item_dto_zero_variance_quote_verification() -> None:
    """Test quote verification under zero-variance protocol using context source text."""
    # 1. Matching quote
    item = AtomEvaluationItemDTO(
        atom_id="atom_1",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        contextual_override=False,
        exact_quotes=["Megatrendien kooste osoittaa kriisejä"],
        status="PASS",
        semantic_reasoning="Reasoning",
        structural_location="N/A",
    )
    context = {"source_text": "Tämä megatrendien kooste osoittaa kriisejä vuonna 2026."}
    validated = AtomEvaluationItemDTO.model_validate(item.model_dump(), context=context)
    assert validated.exact_quotes == ["Megatrendien kooste osoittaa kriisejä"]

    # 2. Fuzzy matching quote (similar enough >95%)
    item_fuzzy = AtomEvaluationItemDTO(
        atom_id="atom_2",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        contextual_override=False,
        exact_quotes=["Megatrendien  kooste-osoittaa\nkriisejä"],  # extra space, punctuation, newline
        status="PASS",
        semantic_reasoning="Reasoning",
        structural_location="N/A",
    )
    validated_fuzzy = AtomEvaluationItemDTO.model_validate(item_fuzzy.model_dump(), context=context)
    assert validated_fuzzy.atom_id == "atom_2"

    # 3. Completely hallucinated quote (fails similarity <95%)
    item_hallucinated = AtomEvaluationItemDTO(
        atom_id="atom_3",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        contextual_override=False,
        exact_quotes=["Tätä lausetta ei löydy tekstistä lainkaan"],
        status="PASS",
        semantic_reasoning="Reasoning",
        structural_location="N/A",
    )
    with pytest.raises(ValidationError) as exc:
        AtomEvaluationItemDTO.model_validate(item_hallucinated.model_dump(), context=context)
    assert "exact_quote not found in source text" in str(exc.value)


@pytest.mark.skip("Legacy architecture obsolete")
def test_atom_evaluation_item_dto_anti_laziness_override() -> None:
    """Test anti-laziness constraints on contextual overrides."""
    # 1. Valid override with long reasoning and structural location
    item_valid = AtomEvaluationItemDTO(
        atom_id="atom_override_1",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        contextual_override=True,
        semantic_reasoning=(
            "This is a very long reasoning text that explains the rationale "
            "to satisfy the anti-laziness length requirements."
        ),
        structural_location="page 42",
        status="PASS",
    )
    validated = AtomEvaluationItemDTO.model_validate(item_valid.model_dump())
    assert validated.contextual_override is True

    # 2. Fails anti-laziness due to short reasoning (<50 characters)
    with pytest.raises(ValidationError) as exc:
        AtomEvaluationItemDTO(
            atom_id="atom_override_2",
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="stub",
                step_2_scan_source="stub",
                step_3_evaluate_anti_patterns="stub",
                step_4_final_conclusion="stub",
            ),
            contextual_override=True,
            semantic_reasoning="Too short page 42.",
            structural_location="page 42",
            status="PASS",
        )
    assert "at least 50 characters" in str(exc.value)

    # 3. Fails anti-laziness due to missing structural location reference
    with pytest.raises(ValidationError) as exc:
        AtomEvaluationItemDTO(
            atom_id="atom_override_3",
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="stub",
                step_2_scan_source="stub",
                step_3_evaluate_anti_patterns="stub",
                step_4_final_conclusion="stub",
            ),
            contextual_override=True,
            semantic_reasoning=(
                "This is a very long reasoning text that completely lacks "
                "any structural location anchors at all, so it should fail."
            ),
            structural_location="N/A",
            status="PASS",
        )
    assert "explicit structural_location reference" in str(exc.value)


@pytest.mark.skip("Legacy architecture obsolete")
def test_calculate_rule_satisfied_truth_table() -> None:
    """Test calculate_rule_satisfied truth table for Double-Lock authorization and inverse evidence."""
    # 1. Double-Lock is Active (allow_contextual_override=True, contextual_override=True)
    # Regardless of status/evidence/inverse_evidence, should return True.
    item = AtomEvaluationItemDTO(
        atom_id="atom_1",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        contextual_override=True,
        semantic_reasoning="This reasoning is long enough to pass anti-laziness length checks.",
        structural_location="page 42",
        status=None,
    )
    assert item.calculate_rule_satisfied(inverse_evidence=False, allow_contextual_override=True) is True
    assert item.calculate_rule_satisfied(inverse_evidence=True, allow_contextual_override=True) is True

    # 2. Double-Lock is Inactive (allow_contextual_override=False, contextual_override=True)
    # Since status is not set, it should fall back to evidence_found.
    # exact_quote is not set or blacklisted, so evidence_found is False.
    # If inverse_evidence=False, should return False.
    # If inverse_evidence=True, should return True.
    assert item.calculate_rule_satisfied(inverse_evidence=False, allow_contextual_override=False) is False
    assert item.calculate_rule_satisfied(inverse_evidence=True, allow_contextual_override=False) is True

    # 3. status is DLQ
    dlq_item = AtomEvaluationItemDTO(
        atom_id="atom_2",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        status="DLQ",
        contextual_override=True,
        semantic_reasoning="This reasoning is long enough to pass anti-laziness length checks.",
        structural_location="page 42",
    )
    # If authorized: returns True
    assert dlq_item.calculate_rule_satisfied(inverse_evidence=False, allow_contextual_override=True) is True
    # If unauthorized: returns "DLQ"
    assert dlq_item.calculate_rule_satisfied(inverse_evidence=False, allow_contextual_override=False) == "DLQ"

    # 4. evidence_found is True (exact_quote is valid)
    valid_item = AtomEvaluationItemDTO(
        atom_id="atom_3",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        exact_quotes=["This is a valid quote"],
        status=None,
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    # If inverse_evidence=False: returns True
    assert valid_item.calculate_rule_satisfied(inverse_evidence=False, allow_contextual_override=False) is True
    # If inverse_evidence=True: returns False
    assert valid_item.calculate_rule_satisfied(inverse_evidence=True, allow_contextual_override=False) is False

    # 5. Sentinel quote is blacklisted and doesn't count as evidence
    sentinel_item = AtomEvaluationItemDTO(
        atom_id="atom_4",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        exact_quotes=["[CONTEXTUAL_OVERRIDE_APPLIED]"],
        status="PASS",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    assert sentinel_item.evidence_found is False


@pytest.mark.parametrize(
    "workflow_switch, assertion_switch, llm_override, evidence_found, inverse_evidence",
    [
        (w, a, o, e, i)
        for w in [True, False]
        for a in [True, False]
        for o in [True, False]
        for e in [True, False]
        for i in [True, False]
    ],
)
@pytest.mark.skip("Legacy architecture obsolete")
def test_calculate_rule_satisfied_truth_table_32(
    workflow_switch: bool,
    assertion_switch: bool,
    llm_override: bool,
    evidence_found: bool,
    inverse_evidence: bool,
) -> None:
    """Systematically test all 32 combinations of the double-lock and inverse evidence logic."""
    # 1. Map evidence_found parameter to physical exact_quote value
    exact_quote = "This is a valid quote" if evidence_found else "None"

    # 2. Bypassing Pydantic validation: if contextual_override is True,
    # semantic_reasoning must satisfy anti-laziness and spatial anchoring checks
    semantic_reasoning = (
        (
            "This is a very long reasoning text that explicitly mentions page 42 "
            "to satisfy the anti-laziness and spatial referencing rules."
        )
        if llm_override
        else ""
    )

    item = AtomEvaluationItemDTO(
        atom_id="test_atom",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        contextual_override=llm_override,
        exact_quotes=[exact_quote] if exact_quote != "None" else [],
        semantic_reasoning=semantic_reasoning,
        structural_location="page 42" if llm_override else "N/A",
        status=None,
    )

    # 3. Calculate the effective System 2 allow override
    effective_allow_override = workflow_switch and assertion_switch

    result = item.calculate_rule_satisfied(
        inverse_evidence=inverse_evidence,
        allow_contextual_override=effective_allow_override,
    )

    # 4. Calculate expected result using absolute System 2 rules
    if effective_allow_override and llm_override:
        expected = True
    else:
        if inverse_evidence:
            expected = not evidence_found
        else:
            expected = evidence_found

    assert result is expected


def test_atom_evaluation_item_dto_contested_state() -> None:
    """Test that CONTESTED status bypasses inverse_evidence logic."""
    item = AtomEvaluationItemDTO(
        atom_id="atom_contested",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        extracted_facts={"fact_1": "Found"},
        status="CONTESTED",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location="N/A",
    )
    # Phase 1: CONTESTED bypasses inversion logic
    assert item.calculate_rule_satisfied(inverse_evidence=False) is True
    assert item.calculate_rule_satisfied(inverse_evidence=True) is True
