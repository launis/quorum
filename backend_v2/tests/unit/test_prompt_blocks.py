"""Unit tests for polymorphic PromptBlock domain models."""

import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixRow, MatrixScale, TDAAssertion


@pytest.fixture
def sample_i18n_text() -> I18nText:
    return I18nText(
        default_locale="en",
        translations={"en": "Sample Label", "fi": "Esimerkki"},
    )


@pytest.fixture
def sample_matrix_scale(sample_i18n_text: I18nText) -> MatrixScale:
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


def test_system_rule_prompt_block_instantiation(sample_i18n_text: I18nText) -> None:
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
    adapter = TypeAdapter(AnyPromptBlock)

    matrix_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "matrix-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "matrix",
        "scales": [sample_matrix_scale.model_dump()],
    }
    parsed_matrix = adapter.validate_python(matrix_data)
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
    parsed_rule = adapter.validate_python(rule_data)
    assert isinstance(parsed_rule, SystemRulePromptBlock)

    persona_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "persona-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "execution_persona",
        "role_enforcement": "Role X",
    }
    parsed_persona = adapter.validate_python(persona_data)
    assert isinstance(parsed_persona, PersonaPromptBlock)

    protocol_data = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "protocol-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "protocol",
        "protocol_instructions": "Protocol Y",
    }
    parsed_protocol = adapter.validate_python(protocol_data)
    assert isinstance(parsed_protocol, ProtocolPromptBlock)


def test_matrix_prompt_block_requires_scales(sample_i18n_text: I18nText) -> None:
    with pytest.raises(ValidationError):
        MatrixPromptBlock(
            id="blk_0123456789abcdef0123456789abcdef",
            slug="test-matrix",
            label=sample_i18n_text,
            description=sample_i18n_text,
            scales=[],  # min_length=1 required
        )


def test_prompt_block_extra_forbid(sample_i18n_text: I18nText) -> None:
    adapter = TypeAdapter(AnyPromptBlock)
    with pytest.raises(ValidationError):
        adapter.validate_python(
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
    block = SystemRulePromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test-rule",
        label=sample_i18n_text,
        description=sample_i18n_text,
    )
    with pytest.raises(ValidationError):
        block.slug = "mutated-slug"  # type: ignore[misc]


def test_prompt_block_polymorphic_factory(
    sample_i18n_text: I18nText,
    sample_matrix_scale: MatrixScale,
) -> None:
    """Verify that PromptBlock(...) polymorphic constructor creates the exact subclass."""
    # 1. Matrix block
    mb = PromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="matrix-block",
        label=sample_i18n_text,
        description=sample_i18n_text,
        category_id=PromptBlockCategory.MATRIX,
        scales=[sample_matrix_scale],
    )
    assert isinstance(mb, MatrixPromptBlock)

    # 2. System rule block
    srb = PromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="rule-block",
        label=sample_i18n_text,
        description=sample_i18n_text,
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    assert isinstance(srb, SystemRulePromptBlock)

    # 3. Persona block
    pb = PromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="persona-block",
        label=sample_i18n_text,
        description=sample_i18n_text,
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
    )
    assert isinstance(pb, PersonaPromptBlock)

    # 4. Protocol block
    prb = PromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="protocol-block",
        label=sample_i18n_text,
        description=sample_i18n_text,
        category_id=PromptBlockCategory.PROTOCOL,
    )
    assert isinstance(prb, ProtocolPromptBlock)


def test_prompt_block_model_validate_and_json(sample_i18n_text: I18nText) -> None:
    """Verify PromptBlock.model_validate and PromptBlock.model_validate_json."""
    import json

    raw_dict = {
        "id": "blk_0123456789abcdef0123456789abcdef",
        "slug": "mv-test",
        "label": sample_i18n_text.model_dump(),
        "description": sample_i18n_text.model_dump(),
        "category_id": "system_rule",
        "type": "string",
    }
    validated_dict = PromptBlock.model_validate(raw_dict)
    assert isinstance(validated_dict, SystemRulePromptBlock)

    raw_json = json.dumps(raw_dict)
    validated_json = PromptBlock.model_validate_json(raw_json)
    assert isinstance(validated_json, SystemRulePromptBlock)


def test_prompt_block_model_construct() -> None:
    """Verify PromptBlock.model_construct for all categories."""
    m = PromptBlock.model_construct(category_id=PromptBlockCategory.MATRIX)
    assert isinstance(m, MatrixPromptBlock)

    sr = PromptBlock.model_construct(category_id=PromptBlockCategory.SYSTEM_RULE)
    assert isinstance(sr, SystemRulePromptBlock)

    p = PromptBlock.model_construct(category_id=PromptBlockCategory.EXECUTION_PERSONA)
    assert isinstance(p, PersonaPromptBlock)

    pr = PromptBlock.model_construct(category_id=PromptBlockCategory.PROTOCOL)
    assert isinstance(pr, ProtocolPromptBlock)

    d = PromptBlock.model_construct()
    assert isinstance(d, SystemRulePromptBlock)

    # Empty __new__ fallback
    empty_block = PromptBlock.__new__(PromptBlock)
    assert isinstance(empty_block, PromptBlock)


