from backend_v2.models.prompts.global_mandates import (
    ANTI_ID_MANDATE,
    ANTI_SCORE_MANDATE,
    EPISTEMIC_GLOSSARY_MANDATE,
    EXTENSION_ANCHORING_MANDATE,
    GLOBAL_MANDATES_MD,
    LANGUAGE_MANDATE,
    NULL_HYPOTHESIS_MANDATE,
    SEMANTIC_BLEED_MANDATE,
    VERBATIM_EXTRACTION_MANDATE,
)


def test_global_mandates_constants() -> None:
    """Test that all global mandates are non-empty strings and formatted correctly."""
    assert isinstance(LANGUAGE_MANDATE, str)
    assert "LANGUAGE MANDATE" in LANGUAGE_MANDATE

    assert isinstance(ANTI_SCORE_MANDATE, str)
    assert "ANTI-SCORE MANDATE" in ANTI_SCORE_MANDATE

    assert isinstance(ANTI_ID_MANDATE, str)
    assert "ANTI-ID MANDATE" in ANTI_ID_MANDATE

    assert isinstance(EPISTEMIC_GLOSSARY_MANDATE, str)
    assert "EPISTEMIC GLOSSARY" in EPISTEMIC_GLOSSARY_MANDATE

    assert isinstance(SEMANTIC_BLEED_MANDATE, str)
    assert "SEMANTIC BLEED MANDATE" in SEMANTIC_BLEED_MANDATE

    assert isinstance(NULL_HYPOTHESIS_MANDATE, str)
    assert "NULL HYPOTHESIS MANDATE" in NULL_HYPOTHESIS_MANDATE

    assert isinstance(VERBATIM_EXTRACTION_MANDATE, str)
    assert "VERBATIM EXTRACTION MANDATE" in VERBATIM_EXTRACTION_MANDATE

    assert isinstance(EXTENSION_ANCHORING_MANDATE, str)
    assert "EXTENSION ANCHORING MANDATE" in EXTENSION_ANCHORING_MANDATE

    assert isinstance(GLOBAL_MANDATES_MD, str)
    assert "LANGUAGE MANDATE" in GLOBAL_MANDATES_MD
