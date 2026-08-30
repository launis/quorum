"""Unit tests for clean UTF-8 text extraction, control char sanitization, and Harvard citation prompt injection."""

from pydantic import BaseModel

from backend_v2.llm.ingress_pipeline import UniversalIngress
from backend_v2.models.prompts import SYNTHESIS_CITATION_RULES_HARVARD
from backend_v2.models.view.sdui import ParagraphBlock


class SampleModel(BaseModel):
    """Test model with text and list fields."""

    title: str
    description: str
    tags: list[str]


def test_sanitize_control_chars_strips_disallowed_and_preserves_allowed() -> None:
    r"""Test that disallowed control codes (0x04, 0x06, 0x00, etc.) are stripped while \n, \t, \r, and umlauts remain."""
    dirty_text = (
        "Suorituksesi osoittaa puutteita\x04 analyysiss\x04:\n\t- Kohta 1: teko\x06ly\r\n\t- Kohta 2: k\x04ytt\x06"
    )
    cleaned = UniversalIngress.sanitize_control_chars(dirty_text)

    assert "\x04" not in cleaned
    assert "\x06" not in cleaned
    assert "\n" in cleaned
    assert "\t" in cleaned
    assert "\r" in cleaned
    assert cleaned == "Suorituksesi osoittaa puutteita analyysiss:\n\t- Kohta 1: tekoly\r\n\t- Kohta 2: kytt"


def test_sanitize_control_chars_preserves_clean_finnish_umlauts() -> None:
    """Test that valid UTF-8 Finnish characters are 100% preserved."""
    clean_text = "Tämä on puhdas suomenkielinen teksti: käyttäjä, päätöksenteko, ympäristö, ÄÄKKÖSET."
    assert UniversalIngress.sanitize_control_chars(clean_text) == clean_text


def test_clean_dict_against_model_sanitizes_nested_strings() -> None:
    """Test that clean_dict_against_model strips control characters from primitive strings and string lists."""
    raw_data = {
        "title": "Raportti\x04 Otsikko",
        "description": "Sis\x06lt\x06 kuvaus\x00.",
        "tags": ["tag1\x04", "tag2\x06"],
    }

    cleaned = UniversalIngress.clean_dict_against_model(raw_data, SampleModel)
    assert cleaned["title"] == "Raportti Otsikko"
    assert cleaned["description"] == "Sislt kuvaus."
    assert cleaned["tags"] == ["tag1", "tag2"]


def test_clean_dict_against_paragraph_block_sanitizes_content() -> None:
    """Test that ParagraphBlock strings are sanitized during ACL ingress."""
    raw_data = {
        "block_type": "paragraph",
        "text": "Teko\x04lyn k\x04ytt\x06\x06nottosuunnitelma.",
        "exact_quotes": ["sitaatti\x04"],
        "citations": [1],
    }

    cleaned = UniversalIngress.clean_dict_against_model(raw_data, ParagraphBlock)
    block = ParagraphBlock.model_validate(cleaned)
    assert block.text == "Tekolyn kyttnottosuunnitelma."
    assert block.exact_quotes == ["sitaatti"]
    assert block.citations == [1]


def test_parse_llm_output_sanitizes_raw_json_with_control_chars() -> None:
    """Test that parse_llm_output strips control characters before json parsing."""
    raw_json = '{"title": "Otsikko\x04", "count": 5}'
    result = UniversalIngress.parse_llm_output(raw_json)
    assert result == {"title": "Otsikko", "count": 5}


def test_synthesis_citation_rules_harvard_is_defined() -> None:
    """Verify that SYNTHESIS_CITATION_RULES_HARVARD directive is non-empty and enforces cited_sources."""
    assert "<citation_rules>" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "cited_sources" in SYNTHESIS_CITATION_RULES_HARVARD
