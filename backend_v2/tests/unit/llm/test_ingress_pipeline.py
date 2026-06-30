import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.ingress_pipeline import UniversalIngress


def test_parse_llm_output_success():
    """Test successful parsing of raw JSON."""
    raw_text = """
    {
      "test_key": "test_value"
    }
    """
    result = UniversalIngress.parse_llm_output(raw_text)
    assert result["test_key"] == "test_value"


def test_parse_llm_output_markdown_stripping():
    """Test parsing strips markdown fences correctly."""
    raw_text = """```json
{
  "test_key": "test_value"
}
```"""
    result = UniversalIngress.parse_llm_output(raw_text)
    assert result["test_key"] == "test_value"


def test_parse_llm_output_invalid_json():
    """Test parsing fails when json content is malformed."""
    raw_text = """
    {
      "invalid_key": "value",
    }
    """
    with pytest.raises(AppException) as exc:
        UniversalIngress.parse_llm_output(raw_text)

    assert exc.value.details["error_code"] == ErrorCodes.PARSING_FAILED.value
    assert "Malformed JSON" in exc.value.message


def test_parse_llm_output_list_wrapper():
    """Test parsing of a top-level list wraps it in a dict."""
    raw_text = """
    [
      {"item": 1},
      {"item": 2}
    ]
    """
    result = UniversalIngress.parse_llm_output(raw_text)
    assert "data" in result
    assert len(result["data"]) == 2
    assert result["data"][0]["item"] == 1
