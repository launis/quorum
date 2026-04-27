import pytest
from pydantic import ValidationError

from backend_v2.models.view.sdui import (
    AnySduiBlock,
    EvidenceItem,
    HeroInsightBlock,
    HighlightBoxDisplay,
    ReferenceIntent,
    ReferenceItem,
    UiSection,
)


def test_strict_str_strips_whitespace_and_enforces_length() -> None:
    """Test that StrictStr automatically strips whitespace and enforces min_length=1 after stripping."""
    # Valid input with surrounding whitespace
    ref = ReferenceItem(id="  REF-123  ", intent=ReferenceIntent.SEARCH, snippet="  This is a snippet.  \n")

    # Verify whitespace was stripped
    assert ref.id == "REF-123"
    assert ref.snippet == "This is a snippet."

    # Invalid input: Only whitespace
    with pytest.raises(ValidationError) as exc_info:
        ReferenceItem(
            id="   ",  # Should strip to "" and fail min_length=1
            intent=ReferenceIntent.SEARCH,
            snippet="Valid snippet",
        )
    assert "String should have at least 1 character" in str(exc_info.value)
    assert "id" in str(exc_info.value)


def test_frozen_mutability_is_enforced() -> None:
    """Test that models cannot be mutated after instantiation (frozen=True)."""
    ev = EvidenceItem(id="EV-1", source="Source", content="Content", score=0.95, type="concept")

    with pytest.raises(ValidationError) as exc_info:
        ev.score = 0.5  # type: ignore[misc]

    assert "Instance is frozen" in str(exc_info.value)


def test_extra_fields_are_strictly_forbidden() -> None:
    """Test that extra="forbid" drops any unauthorized fields, preventing injection."""
    with pytest.raises(ValidationError) as exc_info:
        HighlightBoxDisplay(
            content="Important note",
            color_theme="danger",
            malicious_injection="DROP TABLE users;",  # type: ignore[call-arg]
        )

    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_enum_validation_is_strict() -> None:
    """Test that SectionType strictly enforces the Enum values."""
    with pytest.raises(ValidationError) as exc_info:
        UiSection(
            id="sec-1",
            type="INVALID_TYPE",  # type: ignore[arg-type]
            title="My Section",
        )

    assert "Input should be an instance of SectionType" in str(exc_info.value)


def test_polymorphic_sdui_block_validation() -> None:
    """Test that polymorphic AnySduiBlock requires exact discriminator match."""
    from pydantic import TypeAdapter

    adapter = TypeAdapter(AnySduiBlock)

    # Valid HeroInsightBlock
    valid_obj = adapter.validate_python({"block_type": "hero_insight"})
    assert isinstance(valid_obj, HeroInsightBlock)

    # Invalid block_type
    with pytest.raises(ValidationError) as exc_info:
        adapter.validate_python({"block_type": "hacker_insight"})

    assert "Input tag 'hacker_insight' found using 'block_type' does not match any of the expected tags" in str(
        exc_info.value
    )  # noqa: E501
