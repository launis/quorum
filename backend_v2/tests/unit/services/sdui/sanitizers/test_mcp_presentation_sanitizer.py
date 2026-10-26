"""Unit tests for McpPresentationSanitizer (ISTQB Test Matrix).

Covers real Tavily CDATA JSON payloads, plain text extracts, markdown code fences,
sentence-boundary character budgeting, empty/whitespace inputs, and malformed pseudo-JSON.
"""

from __future__ import annotations

from backend_v2.services.sdui.sanitizers.mcp_presentation_sanitizer import McpPresentationSanitizer


def test_tavily_real_cdata_json_sanitized() -> None:
    """TC-SAN-01: Verify CDATA-wrapped Tavily search JSON is sanitized to clean finding."""
    raw_payload = (
        '<![CDATA[\n{"query":"Työterveyslaitos Stanford etätyö","results":['
        '{"url":"https://www.ttl.fi/tutkimus","title":"Etätyö tutkimus",'
        '"content":"Työterveyslaitoksen ja Stanfordin yliopiston tutkimus osoittaa, '
        'että säännöllinen etätyö parantaa asiantuntijoiden työhyvinvointia ja palautumista."}]}\n]]>'
    )
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert "<![CDATA[" not in result
    assert "]]>" not in result
    assert '{"query"' not in result
    assert "url" not in result
    assert "Työterveyslaitoksen ja Stanfordin yliopiston tutkimus osoittaa" in result
    assert result.endswith(".")


def test_plain_text_cdata_sanitized() -> None:
    """TC-SAN-02: Verify plain text wrapped in CDATA envelope is cleanly preserved."""
    raw_payload = "<![CDATA[Faktalähde: Työterveyslaitos on suomalainen työelämän asiantuntijaorganisaatio.]]>"
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert result == "Faktalähde: Työterveyslaitos on suomalainen työelämän asiantuntijaorganisaatio."
    assert "<![CDATA[" not in result
    assert "]]>" not in result


def test_sentence_boundary_budgeting_long_content() -> None:
    """TC-SAN-03: Verify length budgeting cuts at sentence terminal punctuation within window."""
    s1 = "Ensimmäinen tutkimushavainto vahvistaa etätyön tuottavuuden kasvun 13 prosentilla."
    s2 = "Toinen tutkimus osoittaa hiljaisen työn mahdollistavan syvemmän keskittymisen ja vähentävän keskeytyksiä."
    s3 = "Kolmas laajamittainen analyysi korostaa säännöllisten lepotaukojen merkitystä kognitiiviselle jaksamiselle."
    long_content = f"{s1} {s2} {s3}"
    assert len(long_content) > 280

    result = McpPresentationSanitizer.sanitize_finding(long_content, max_chars=200)

    assert result is not None
    assert len(result) <= 200
    assert result.endswith((".", "!", "?"))
    assert s1 in result


def test_empty_or_whitespace_cdata_returns_none() -> None:
    """TC-SAN-04: Negative equivalence: empty, whitespace-only, or empty CDATA return None."""
    assert McpPresentationSanitizer.sanitize_finding(None) is None
    assert McpPresentationSanitizer.sanitize_finding("") is None
    assert McpPresentationSanitizer.sanitize_finding("   \n\t  ") is None
    assert McpPresentationSanitizer.sanitize_finding("<![CDATA[   ]]>") is None
    assert McpPresentationSanitizer.sanitize_finding("<![CDATA[]]>") is None
    assert McpPresentationSanitizer.sanitize_finding("```\n```") is None
    assert McpPresentationSanitizer.sanitize_finding("```json\n```") is None


def test_malformed_pseudo_json_recovery() -> None:
    """TC-SAN-05: Negative resilient: unclosed or corrupted pseudo-JSON recovers gracefully as text."""
    raw_payload = '<![CDATA[{"corrupted: json string without closing quote or closing brace]]>'
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert "<![CDATA[" not in result
    assert "]]>" not in result
    assert "corrupted: json string without closing quote or closing brace" in result
    assert result.endswith(".")


def test_structured_json_without_results_summary_extraction() -> None:
    """Positive: verify top-level summary is extracted when results list is empty or absent."""
    raw_payload = '<![CDATA[\n{"summary": "Tutkimus osoittaa etätyön tukevan autonomiaa ja joustavuutta."}\n]]>'
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert result == "Tutkimus osoittaa etätyön tukevan autonomiaa ja joustavuutta."


def test_markdown_code_fenced_json_extraction() -> None:
    """Positive: verify markdown code-fenced JSON is stripped and parsed correctly."""
    raw_payload = (
        '```json\n{"results":[{"content":"WHO suosittelee vähintään 150 minuuttia kestävyysliikuntaa viikossa."}]}\n```'
    )
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert result == "WHO suosittelee vähintään 150 minuuttia kestävyysliikuntaa viikossa."


def test_top_level_answer_extraction() -> None:
    """Positive: verify top-level answer field is extracted if results list is empty."""
    raw_payload = '{"answer": "Harvardin tutkimuksen mukaan riittävä uni parantaa kognitiivista suorituskykyä."}'
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert result == "Harvardin tutkimuksen mukaan riittävä uni parantaa kognitiivista suorituskykyä."


def test_plain_text_without_cdata_gets_terminal_punctuation() -> None:
    """Positive: verify plain text without terminal punctuation has period appended."""
    raw_payload = "Tämä on vahvistettu ulkoinen havainto"
    result = McpPresentationSanitizer.sanitize_finding(raw_payload)

    assert result is not None
    assert result == "Tämä on vahvistettu ulkoinen havainto."
