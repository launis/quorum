"""Unit tests for design-time PromptAtomizer and TwoPassAtomizer services."""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText
from backend_v2.models.domain.blackboard import LLMDraftAtom, LLMDraftAtomList
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, SystemRulePromptBlock
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap, OntologyEntity
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.atomizer import PromptAtomizer
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


def _build_matrix_block_with_scale(scale: MatrixScale) -> MatrixPromptBlock:
    """Build a valid MatrixPromptBlock and inject the target MatrixScale via model_copy.

    Args:
        scale: Target MatrixScale to inject into the MatrixPromptBlock.

    Returns:
        MatrixPromptBlock containing the injected scale.
    """
    seed_tda = TDAAssertion(
        tda_id="tda_12341234123412341234123412341234",
        concept_description="Baseline seed assertion description",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        depends_on=(),
    )
    seed_claim = MatrixClaim(
        label=I18nText(translations={"en": "Seed claim", "fi": "Siemenväite"}),
        tda_assertions=[seed_tda],
    )
    seed_scale = MatrixScale(score=1, ai_label="SEED", claims=[seed_claim])
    base_block = MatrixPromptBlock(
        id="blk_1234567890abcdef",
        slug="test_block",
        label=I18nText(translations={"en": "Test block", "fi": "Testilohko"}),
        description=I18nText(translations={"en": "Test desc", "fi": "Testikuvaus"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.INT,
        scales=[seed_scale],
    )
    return base_block.model_copy(update={"scales": [scale]})


def test_tda_assertion_validation() -> None:
    """Strict test verifying the inverse_evidence mathematical logic constraint."""
    # Should pass
    valid = TDAAssertion(
        tda_id="tda_12345678123456781234567812345678",
        concept_description="Test rule validation",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        depends_on=(),
    )
    assert valid.tda_id == "tda_12345678123456781234567812345678"

    # Should pass
    valid_inverse = TDAAssertion(
        tda_id="tda_87654321876543218765432187654321",
        concept_description="Poison test valid description",
        inverse_evidence=True,
        aggregation_mode="EXISTS",
        depends_on=(),
    )
    assert valid_inverse.aggregation_mode == "EXISTS"

    # Should fail-fast
    with pytest.raises(ValidationError) as exc:
        TDAAssertion(
            tda_id="tda_abcdef1234567890abcdef1234567890",
            concept_description="Invalid poison test description",
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
            depends_on=(),
        )
    assert "Inverse evidence (poison detection) strictly requires 'EXISTS' aggregation mode." in str(exc.value)


@pytest.mark.asyncio
async def test_atomizer_deterministic_mapping() -> None:
    """Test deterministic assignment and preservation of canonical Opaque Stripe IDs in PromptAtomizer."""
    # Arrange: tda1 has a missing/empty tda_id via model_copy to exercise ID generation
    tda1 = TDAAssertion(
        concept_description="Rule 1 concept description",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        depends_on=(),
    ).model_copy(update={"tda_id": ""})

    tda2 = TDAAssertion(
        tda_id="tda_12341234123412341234123412341234",
        concept_description="Rule 2 concept description",
        inverse_evidence=True,
        aggregation_mode="EXISTS",
        depends_on=(),
    )

    claim_with_assertions = MatrixClaim(
        label=I18nText(translations={"en": "Test claim", "fi": "Test claim"}),
        tda_assertions=[tda1, tda2],
    )
    empty_claim = claim_with_assertions.model_copy(update={"tda_assertions": []})

    scale = MatrixScale(score=1, ai_label="TEST", claims=[claim_with_assertions, empty_claim])
    block_to_atomize = _build_matrix_block_with_scale(scale)

    # Act
    updated_block = await PromptAtomizer.atomize_prompt_block(block_to_atomize)

    # Assert
    assert isinstance(updated_block, MatrixPromptBlock)
    assert len(updated_block.scales[0].claims) == 2

    updated_claim = updated_block.scales[0].claims[0]
    assert len(updated_claim.tda_assertions) == 2

    # tda1 must be assigned a valid 32-hex Opaque Stripe ID matching OPAQUE_STRIPE_ID_REGEX
    generated_id = updated_claim.tda_assertions[0].tda_id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, generated_id) is not None
    assert len(generated_id) == 36

    # tda2 must retain its preset ID
    assert updated_claim.tda_assertions[1].tda_id == "tda_12341234123412341234123412341234"
    assert updated_block.scales[0].claims[1].tda_assertions == []


@pytest.mark.asyncio
async def test_atomizer_passthrough_for_non_matrix_block() -> None:
    """Verify non-matrix PromptBlocks pass through PromptAtomizer untouched."""
    rule_block = SystemRulePromptBlock(
        id="blk_1234567890abcdef",
        slug="sys_rule_test",
        label=I18nText(translations={"en": "System Rule", "fi": "Sääntö"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        instruction_text="Follow the protocol.",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
    )

    result = await PromptAtomizer.atomize_prompt_block(rule_block)
    assert result == rule_block


@pytest.mark.asyncio
async def test_atomizer_raises_app_exception_on_generation_failure() -> None:
    """Negative test: Verify failure during ID generation raises AppException with VALIDATION_FAILED."""
    tda = TDAAssertion(
        concept_description="Rule 1 concept description",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        depends_on=(),
    ).model_copy(update={"tda_id": ""})
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Test claim", "fi": "Test claim"}),
        tda_assertions=[tda],
    )
    scale = MatrixScale(score=1, ai_label="TEST", claims=[claim])
    block = _build_matrix_block_with_scale(scale)

    with (
        patch(
            "backend_v2.services.orchestrator.atomizer.generate_opaque_id",
            side_effect=RuntimeError("Entropy source unavailable"),
        ),
        pytest.raises(AppException) as exc_info,
    ):
        await PromptAtomizer.atomize_prompt_block(block)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
async def test_atomizer_raises_app_exception_on_corrupted_assertion_copy() -> None:
    """Negative test: Verify failure during assertion model_copy raises AppException with VALIDATION_FAILED."""
    tda = TDAAssertion(
        concept_description="Rule 1 concept description",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        depends_on=(),
    ).model_copy(update={"tda_id": "usr_1234567890abcdef1234567890abcdef"})
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Test claim", "fi": "Test claim"}),
        tda_assertions=[tda],
    )
    scale = MatrixScale(score=1, ai_label="TEST", claims=[claim])
    block = _build_matrix_block_with_scale(scale)

    with (
        patch.object(
            TDAAssertion,
            "model_copy",
            side_effect=ValueError("Corrupted assertion state"),
        ),
        pytest.raises(AppException) as exc_info,
    ):
        await PromptAtomizer.atomize_prompt_block(block)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
async def test_two_pass_atomizer_phase_0() -> None:
    """Test Phase 0 global entity map extraction."""
    mock_executor = AsyncMock(spec=LLMTaskExecutor)

    # Mock return value for Phase 0
    mock_map = GlobalOntologyMap(
        entities=[OntologyEntity(name="System", description="The main system.")], macro_rules=["Rule 1"]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_map,
        TokenUsage(prompt_tokens=40, completion_tokens=10, total_tokens=50),
    )

    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_client = AsyncMock(spec=LLMClient)
    mock_client.provider_name = "mock_llm_99"
    mock_client.model_name = "mock"

    result, usage = await atomizer.execute_phase_0(client=mock_client, hydrated_text="[B0] Chunk 1\n\n[B1] Chunk 2")

    assert len(result.entities) == 1
    assert result.entities[0].name == "System"
    assert len(result.macro_rules) == 1
    assert usage.total_tokens == 50
    assert mock_executor.execute_structured_task.call_count == 1


@pytest.mark.asyncio
async def test_two_pass_atomizer_phase_1() -> None:
    """Test Phase 1 local extraction receiving the ontology map."""
    mock_executor = AsyncMock(spec=LLMTaskExecutor)

    # Mock return value for Phase 1
    mock_draft_list = LLMDraftAtomList(
        atoms=[LLMDraftAtom(reasoning="Test logic", resolved_claim="Test claim", source_block_id="B1", draft_id="a1")]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=60, completion_tokens=15, total_tokens=75),
    )

    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_client = AsyncMock(spec=LLMClient)
    mock_client.provider_name = "mock_llm_99"
    mock_client.model_name = "mock"
    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    result, usage = await atomizer.execute_phase_1(
        client=mock_client, hydrated_text="[B0] Chunk 1\n\n[B1] Chunk 2", ontology=mock_ontology
    )

    assert len(result) == 1
    assert isinstance(result[0], ExtractedAtom)
    assert result[0].resolved_claim == "Test claim"
    assert result[0].tda_id.startswith("tda_")
    assert result[0].source_id == "chunk_0"
    assert usage.total_tokens == 75
    assert mock_executor.execute_structured_task.call_count == 1
