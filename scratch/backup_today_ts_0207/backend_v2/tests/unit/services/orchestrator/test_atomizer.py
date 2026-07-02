import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, PromptBlock, TDAAssertion
from backend_v2.services.orchestrator.atomizer import PromptAtomizer


def test_tda_assertion_validation() -> None:
    """Strict test verifying the inverse_evidence mathematical logic constraint."""
    # Should pass
    valid = TDAAssertion(
        tda_id="tda_12345678123456781234567812345678",
        concept_description="Test rule",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
    )
    assert valid.tda_id == "tda_12345678123456781234567812345678"

    # Should pass
    valid_inverse = TDAAssertion(
        tda_id="tda_87654321876543218765432187654321",
        concept_description="Poison test",
        inverse_evidence=True,
        aggregation_mode="EXISTS",
    )
    assert valid_inverse.aggregation_mode == "EXISTS"

    # Should fail-fast
    with pytest.raises(ValidationError) as exc:
        TDAAssertion(
            tda_id="tda_abcdef1234567890abcdef1234567890",
            concept_description="Invalid poison test",
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
        )
    assert "EHDOTTOMASTI 'EXISTS' -aggregaation" in str(exc.value)


@pytest.mark.asyncio
async def test_atomizer_deterministic_mapping() -> None:
    """Test the O(1) deterministic mapping of TDA assertions in PromptAtomizer."""
    # Arrange
    tda1 = TDAAssertion(
        concept_description="Rule 1",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
    )

    tda2 = TDAAssertion(
        tda_id="tda_12341234123412341234123412341234",  # Intentionally preset to test persistence
        concept_description="Rule 2",
        inverse_evidence=True,
        aggregation_mode="EXISTS",
    )

    claim = MatrixClaim(
        label=I18nText(default_locale="en", translations={"en": "Test claim", "fi": "Test claim"}),
        ai_description="Test",
        tda_assertions=[tda1, tda2],
    )

    scale = MatrixScale(score=1, ai_label="TEST", claims=[claim])

    block = PromptBlock.model_validate(
        {
            "id": "blk_1234567890abcdef",
            "slug": "test_block",
            "label": {"default_locale": "en", "translations": {"en": "Test block", "fi": "Test block"}},
            "description": {"default_locale": "en", "translations": {"en": "Test desc", "fi": "Test desc"}},
            "category_id": "system_rule",
            "type": "int",
            "scale_min": 1,
            "scale_max": 5,
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
