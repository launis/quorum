"""Tests for SDUI View Models."""

from backend_v2.models.view.sdui import HeroInsightBlock
from pydantic import ValidationError
import pytest


def test_hero_insight_block_initialization() -> None:
    """Ensure strict Pydantic V2 instantiation works correctly."""
    block = HeroInsightBlock(block_type="hero_insight")
    assert block.block_type == "hero_insight"


def test_hero_insight_block_forbids_extra() -> None:
    """Ensure extra='forbid' strictly rejects unknown fields."""
    with pytest.raises(ValidationError) as exc:
        HeroInsightBlock(block_type="hero_insight", unknown_field="hax")
    
    assert "Extra inputs are not permitted" in str(exc.value)


def test_hero_insight_block_invalid_type() -> None:
    """Ensure Discriminator Literal requires exact match."""
    with pytest.raises(ValidationError) as exc:
        HeroInsightBlock(block_type="wrong_type")  # type: ignore
    
    assert "Input should be 'hero_insight'" in str(exc.value)
