"""Unit tests for polymorphic PromptBlock domain models."""

import json

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.prompt_blocks import (
    PROMPT_BLOCK_REGISTRY,
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import BlockDataType, ExecutionStatus, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixRow, MatrixScale, TDAAssertion


@pytest.fixture
def sample_i18n_text() -> I18nText:
    """Provides a sample I18nText fixture for testing."""
    return I18nText(
        translations={"en": "Sample Label", "fi": "Esimerkki"},
    )


@pytest.fixture
def sample_matrix_scale(sample_i18n_text: I18nText) -> MatrixScale:
    """Provides a sample MatrixScale fixture with valid TDA assertions."""
    assertion = TDAAssertion(
        tda_id="tda_0123456789abcdef0123456789abcdef",
        concept_description="Critical directive requiring adherence to empirical evidence.",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
    )
    claim = MatrixClaim(
        label=sample_i18n_text,
        tda_assertions=[assertion],
    )
    return MatrixScale(
        score=4,
        ai_label="ROBUST EVIDENCE",
        claims=[claim],
    )


def test_matrix_prompt_block_computed_min_max(
    sample_i18n_text: I18nText,
    sample_matrix_scale: MatrixScale,
) -> None:
    """Tests automatic min/max score calculation on MatrixPromptBlock."""
    scale_1 = MatrixScale(
        score=1,
        ai_label="POOR",
        claims=sample_matrix_scale.claims,
    )
    scale_5 = MatrixScale(
        score=5,
        ai_label="EXCELLENT",
        claims=sample_matrix_scale.claims,
    )

    block = MatrixPromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-matrix",
        label=sample_i18n_text,
        description=sample_i18n_text,
        scales=[scale_1, sample_matrix_scale, scale_5],
        rows=[MatrixRow(label=sample_i18n_text, ai_description="Row instruction text")],
    )

    assert block.category_id == PromptBlockCategory.MATRIX
    assert block.computed_min == 1
    assert block.computed_max == 5
    assert block.is_evaluative is True


def test_matrix_prompt_block_compute_min_max_immutable(
    sample_i18n_text: I18nText,
    sample_matrix_scale: MatrixScale,
) -> None:
    """Contract: MatrixPromptBlock dynamically computes min and max scores from scales."""
    scale_1 = MatrixScale(
        score=1,
        ai_label="POOR",
        claims=sample_matrix_scale.claims,
    )
    scale_5 = MatrixScale(
        score=5,
        ai_label="EXCELLENT",
        claims=sample_matrix_scale.claims,
    )

    block = MatrixPromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-matrix-contract",
        label=sample_i18n_text,
        description=sample_i18n_text,
        scales=[scale_1, sample_matrix_scale, scale_5],
        rows=[MatrixRow(label=sample_i18n_text, ai_description="Row instruction text")],
    )

    assert block.computed_min == 1
    assert block.computed_max == 5


def test_system_rule_prompt_block_instantiation(sample_i18n_text: I18nText) -> None:
    """Tests direct instantiation and default fields of SystemRulePromptBlock."""
    block = SystemRulePromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-rule",
        label=sample_i18n_text,
        description=sample_i18n_text,
        instruction_text="You must strictly follow formatting rules.",
    )

    assert block.category_id == PromptBlockCategory.SYSTEM_RULE
    assert block.type == BlockDataType.INSTRUCTION
    assert block.is_evaluative is False
    assert block.instruction_text == "You must strictly follow formatting rules."


def test_persona_prompt_block_instantiation(sample_i18n_text: I18nText) -> None:
    """Tests direct instantiation and fields of PersonaPromptBlock."""
    block = PersonaPromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-persona",
        label=sample_i18n_text,
        description=sample_i18n_text,
        role_enforcement="ACT AS SENIOR REVIEWER",
        tone_directives=["Objective", "Rigorous"],
    )

    assert block.category_id == PromptBlockCategory.EXECUTION_PERSONA
    assert block.role_enforcement == "ACT AS SENIOR REVIEWER"
    assert block.tone_directives == ["Objective", "Rigorous"]


def test_protocol_prompt_block_instantiation(sample_i18n_text: I18nText) -> None:
    """Tests direct instantiation and fields of ProtocolPromptBlock."""
    block = ProtocolPromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-protocol",
        label=sample_i18n_text,
        description=sample_i18n_text,
        protocol_instructions="Extract fact atoms sequentially.",
    )

    assert block.category_id == PromptBlockCategory.PROTOCOL
    assert block.protocol_instructions == "Extract fact atoms sequentially."


def test_discriminated_union_parsing(sample_i18n_text: I18nText, sample_matrix_scale: MatrixScale) -> None:
    """Tests polymorphic parsing via PromptBlockAdapter."""
    matrix_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "matrix-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "matrix",
        "scales": [sample_matrix_scale.model_dump()],
    }
    parsed_matrix = PromptBlockAdapter.validate_python(matrix_data)
    assert isinstance(parsed_matrix, MatrixPromptBlock)
    assert parsed_matrix.computed_min == 4
    assert parsed_matrix.computed_max == 4

    rule_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "rule-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "system_rule",
        "instruction_text": "Strict rule",
    }
    parsed_rule = PromptBlockAdapter.validate_python(rule_data)
    assert isinstance(parsed_rule, SystemRulePromptBlock)

    persona_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "persona-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "execution_persona",
        "role_enforcement": "Role X",
    }
    parsed_persona = PromptBlockAdapter.validate_python(persona_data)
    assert isinstance(parsed_persona, PersonaPromptBlock)

    protocol_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "protocol-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "protocol",
        "protocol_instructions": "Protocol Y",
    }
    parsed_protocol = PromptBlockAdapter.validate_python(protocol_data)
    assert isinstance(parsed_protocol, ProtocolPromptBlock)


def test_matrix_prompt_block_requires_scales(sample_i18n_text: I18nText) -> None:
    """Tests that MatrixPromptBlock enforces min_length=1 on scales."""
    with pytest.raises(ValidationError):
        MatrixPromptBlock(
            id="blk_0123456789abcdef0123456789abcdef",
            slug="test-matrix",
            label=sample_i18n_text,
            description=sample_i18n_text,
            scales=[],  # min_length=1 required
        )


def test_prompt_block_extra_forbid(sample_i18n_text: I18nText) -> None:
    """Tests that extra forbidden attributes are rejected in strict mode."""
    with pytest.raises(ValidationError):
        PromptBlockAdapter.validate_python(
            {
                "id": "blk_0123456789abcdef0123456789abcdef",
                "slug": "rule-test",
                "label": sample_i18n_text.model_dump(),
                "description": sample_i18n_text.model_dump(),
                "category_id": "system_rule",
                "forbidden_extra_field": "disallowed",
            }
        )


def test_prompt_block_frozen_immutability(sample_i18n_text: I18nText) -> None:
    """Tests that all prompt block models are strictly frozen."""
    block = SystemRulePromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-rule",
        label=sample_i18n_text,
        description=sample_i18n_text,
    )
    with pytest.raises(ValidationError):
        block.slug = "mutated-slug"  # type: ignore[misc]


def test_prompt_block_registry_coverage() -> None:
    """Tests that PROMPT_BLOCK_REGISTRY covers all categories and maps to valid subclasses."""
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.MATRIX] is MatrixPromptBlock
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.SYSTEM_RULE] is SystemRulePromptBlock
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.RUNTIME_VARIABLES] is SystemRulePromptBlock
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.TASK_DEFINITION] is SystemRulePromptBlock
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.EXECUTION_PERSONA] is PersonaPromptBlock
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.AGENT_ROLE] is PersonaPromptBlock
    assert PROMPT_BLOCK_REGISTRY[PromptBlockCategory.PROTOCOL] is ProtocolPromptBlock


def test_prompt_block_json_deserialization(sample_i18n_text: I18nText) -> None:
    """Tests JSON string deserialization via PromptBlockAdapter."""
    raw_dict = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "mv-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "system_rule",
        "type": "string",
    }
    raw_json = json.dumps(raw_dict)
    validated = PromptBlockAdapter.validate_json(raw_json)
    assert isinstance(validated, SystemRulePromptBlock)
    assert validated.id == "blk_0123456789abcdef0123456789abcdef"


def test_matrix_prompt_block_deserialization_with_list_depends_on(
    sample_i18n_text: I18nText,
) -> None:
    """Tests that a MatrixPromptBlock serialized with JSON list depends_on deserializes into tuple CausalEdge."""
    raw_matrix_dict = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "test-matrix-deps",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "matrix",
        "type": "float",
        "scales": [
            {
                "score": 1,
                "ai_label": "LEVEL_1",
                "claims": [
                    {
                        "label": sample_i18n_text.model_dump(),
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000010000000000000001",
                                "concept_description": "Valid test concept description for assertion 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                                "depends_on": [],
                            },
                            {
                                "tda_id": "tda_00000000000000010000000000000002",
                                "concept_description": "Valid test concept description for assertion 2",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                                "depends_on": [
                                    {
                                        "edge_reasoning": "Assertion 1 must pass first",
                                        "tda_id": "tda_00000000000000010000000000000001",
                                        "source_id": "chk_123",
                                        "expected_status": ExecutionStatus.PASSED,
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        ],
    }
    # Test dictionary validation (PromptBlockAdapter.validate_python)
    block = PromptBlockAdapter.validate_python(raw_matrix_dict)
    assert isinstance(block, MatrixPromptBlock)
    claim = block.scales[0].claims[0]
    assert isinstance(claim.tda_assertions[0].depends_on, tuple)
    assert len(claim.tda_assertions[0].depends_on) == 0
    assert isinstance(claim.tda_assertions[1].depends_on, tuple)
    assert len(claim.tda_assertions[1].depends_on) == 1
    assert claim.tda_assertions[1].depends_on[0].tda_id == "tda_00000000000000010000000000000001"

    # Negative test case 1: Non-collection primitive (e.g. integer or string) must fail tuple validation
    invalid_primitive_dict = {
        **raw_matrix_dict,
        "scales": [
            {
                "score": 1,
                "ai_label": "LEVEL_1",
                "claims": [
                    {
                        "label": sample_i18n_text.model_dump(),
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000010000000000000001",
                                "concept_description": "Valid test concept description for assertion 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                                "depends_on": 12345,  # Invalid type (integer instead of collection)
                            }
                        ],
                    }
                ],
            }
        ],
    }
    with pytest.raises(ValidationError) as exc_info:
        PromptBlockAdapter.validate_python(invalid_primitive_dict)
    assert "Input should be a valid tuple" in str(exc_info.value)

    # Negative test case 2: Invalid item inside list (e.g. string instead of CausalEdge dict) must fail CausalEdge validation
    invalid_element_dict = {
        **raw_matrix_dict,
        "scales": [
            {
                "score": 1,
                "ai_label": "LEVEL_1",
                "claims": [
                    {
                        "label": sample_i18n_text.model_dump(),
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000010000000000000001",
                                "concept_description": "Valid test concept description for assertion 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                                "depends_on": ["invalid_edge_string"],  # Invalid item type
                            }
                        ],
                    }
                ],
            }
        ],
    }
    with pytest.raises(ValidationError) as exc_info_2:
        PromptBlockAdapter.validate_python(invalid_element_dict)
    assert "Input should be a valid dictionary or instance of CausalEdge" in str(exc_info_2.value)
