from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.blackboard import LLMDraftAtom, LLMDraftAtomList
from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap, OntologyEntity
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.atomizer import PromptAtomizer
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


def test_tda_assertion_validation() -> None:
    """Strict test verifying the inverse_evidence mathematical logic constraint."""
    # Should pass
    valid = TDAAssertion(
        tda_id="tda_12345678123456781234567812345678",
        concept_description="Test rule validation",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
    )
    assert valid.tda_id == "tda_12345678123456781234567812345678"

    # Should pass
    valid_inverse = TDAAssertion(
        tda_id="tda_87654321876543218765432187654321",
        concept_description="Poison test valid description",
        inverse_evidence=True,
        aggregation_mode="EXISTS",
    )
    assert valid_inverse.aggregation_mode == "EXISTS"

    # Should fail-fast
    with pytest.raises(ValidationError) as exc:
        TDAAssertion(
            tda_id="tda_abcdef1234567890abcdef1234567890",
            concept_description="Invalid poison test description",
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
        )
    assert "Inverse evidence (poison detection) strictly requires 'EXISTS' aggregation mode." in str(exc.value)


@pytest.mark.asyncio
async def test_atomizer_deterministic_mapping() -> None:
    """Test the O(1) deterministic mapping of TDA assertions in PromptAtomizer."""
    # Arrange
    tda1 = TDAAssertion(
        concept_description="Rule 1 concept description",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
    )

    tda2 = TDAAssertion(
        tda_id="tda_12341234123412341234123412341234",  # Intentionally preset to test persistence
        concept_description="Rule 2 concept description",
        inverse_evidence=True,
        aggregation_mode="EXISTS",
    )

    claim = MatrixClaim(
        label=I18nText(default_locale="en", translations={"en": "Test claim", "fi": "Test claim"}),
        tda_assertions=[tda1, tda2],
    )

    scale = MatrixScale(score=1, ai_label="TEST", claims=[claim])

    block = PromptBlockAdapter.validate_python(
        {
            "id": "blk_1234567890abcdef",
            "slug": "test_block",
            "label": {"default_locale": "en", "translations": {"en": "Test block", "fi": "Test block"}},
            "description": {"default_locale": "en", "translations": {"en": "Test desc", "fi": "Test desc"}},
            "category_id": "matrix",
            "type": "int",
            "scales": [scale.model_dump()],
        }
    )

    atomizer = PromptAtomizer()

    # Act
    updated_block = await atomizer.atomize_prompt_block(block)

    # Assert
    assert updated_block.scales is not None
    assert len(updated_block.scales[0].claims) == 1

    updated_claim = updated_block.scales[0].claims[0]
    assert len(updated_claim.tda_assertions) == 2

    # tda1 should have a generated tda_ ID
    assert updated_claim.tda_assertions[0].tda_id.startswith("tda_")
    assert len(updated_claim.tda_assertions[0].tda_id) >= 12

    # tda2 should retain its preset ID
    assert updated_claim.tda_assertions[1].tda_id == "tda_12341234123412341234123412341234"


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
