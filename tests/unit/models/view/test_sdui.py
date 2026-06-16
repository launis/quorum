"""Unit tests for Server-Driven UI (SDUI) view models."""

import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
    BulletListBlock,
    ParagraphBlock,
)


def test_paragraph_block_success() -> None:
    """Test successful parsing of ParagraphBlock."""
    data = {
        "block_type": "paragraph",
        "text": "This is a paragraph.",
        "citations": [1, 2],
    }
    block = ParagraphBlock.model_validate(data)
    assert block.block_type == "paragraph"
    assert block.text == "This is a paragraph."
    assert block.citations == [1, 2]


def test_paragraph_block_failure() -> None:
    """Test failure when required fields are missing."""
    data = {
        "block_type": "paragraph",
        # missing text
    }
    with pytest.raises(ValidationError):
        ParagraphBlock.model_validate(data)


def test_bullet_list_block_success() -> None:
    """Test successful parsing of BulletListBlock."""
    data = {
        "block_type": "bullet_list",
        "items": [
            {"text": "Item 1", "citations": [1]},
            {"text": "Item 2", "citations": []},
        ],
    }
    block = BulletListBlock.model_validate(data)
    assert block.block_type == "bullet_list"
    assert len(block.items) == 2
    assert block.items[0].text == "Item 1"
    assert block.items[0].citations == [1]


def test_alert_block_success() -> None:
    """Test successful parsing of AlertBlock."""
    data = {
        "block_type": "alert_box",
        "severity": "info",
        "text": "This is an alert.",
        "citations": [3],
    }
    block = AlertBlock.model_validate(data)
    assert block.block_type == "alert_box"
    assert block.severity == "info"
    assert block.text == "This is an alert."


def test_alert_block_invalid_severity() -> None:
    """Test failure when severity is invalid."""
    data = {
        "block_type": "alert_box",
        "severity": "critical",  # invalid
        "text": "This is an alert.",
    }
    with pytest.raises(ValidationError):
        AlertBlock.model_validate(data)


def test_any_sdui_block_discriminator() -> None:
    """Test that AnySduiBlock parses correctly into the underlying types."""
    any_sdui_adapter = TypeAdapter(AnySduiBlock)

    data_para = {
        "block_type": "paragraph",
        "text": "Hello",
    }
    block_para = any_sdui_adapter.validate_python(data_para)
    assert isinstance(block_para, ParagraphBlock)

    data_alert = {
        "block_type": "alert_box",
        "severity": "warning",
        "text": "Warning!",
    }
    block_alert = any_sdui_adapter.validate_python(data_alert)
    assert isinstance(block_alert, AlertBlock)
