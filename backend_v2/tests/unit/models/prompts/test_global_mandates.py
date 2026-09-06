from backend_v2.models.prompts.common.global_mandates import (
    ANTI_ID_MANDATE,
    ANTI_SCORE_MANDATE,
    CONTEXT_SEGREGATION_MANDATE,
    EPISTEMIC_GLOSSARY_MANDATE,
    EXTENSION_ANCHORING_MANDATE,
    GLOBAL_MANDATES_XML,
    NULL_HYPOTHESIS_MANDATE,
    SCHEMA_PURITY_MANDATE,
    SEMANTIC_BLEED_MANDATE,
    VERBATIM_EXTRACTION_MANDATE,
)


def test_global_mandates_constants() -> None:
    """Test that all global mandates are non-empty strings and formatted correctly."""
    assert isinstance(ANTI_SCORE_MANDATE, str)
    assert "<anti_score_mandate>" in ANTI_SCORE_MANDATE

    assert isinstance(ANTI_ID_MANDATE, str)
    assert "<anti_id_mandate>" in ANTI_ID_MANDATE

    assert isinstance(EPISTEMIC_GLOSSARY_MANDATE, str)
    assert "<epistemic_glossary>" in EPISTEMIC_GLOSSARY_MANDATE

    assert isinstance(SEMANTIC_BLEED_MANDATE, str)
    assert "<semantic_bleed_mandate>" in SEMANTIC_BLEED_MANDATE

    assert isinstance(NULL_HYPOTHESIS_MANDATE, str)
    assert "<null_hypothesis_mandate>" in NULL_HYPOTHESIS_MANDATE

    assert isinstance(VERBATIM_EXTRACTION_MANDATE, str)
    assert "<verbatim_extraction_mandate>" in VERBATIM_EXTRACTION_MANDATE

    assert isinstance(SCHEMA_PURITY_MANDATE, str)
    assert "<schema_purity_mandate>" in SCHEMA_PURITY_MANDATE

    assert isinstance(EXTENSION_ANCHORING_MANDATE, str)
    assert "<extension_anchoring_mandate>" in EXTENSION_ANCHORING_MANDATE

    assert isinstance(CONTEXT_SEGREGATION_MANDATE, str)
    assert "<context_segregation_mandate>" in CONTEXT_SEGREGATION_MANDATE

    assert isinstance(GLOBAL_MANDATES_XML, str)
    assert "<global_system_mandates>" in GLOBAL_MANDATES_XML
    assert "<context_segregation_mandate>" in GLOBAL_MANDATES_XML
    assert "<anti_score_mandate>" in GLOBAL_MANDATES_XML
