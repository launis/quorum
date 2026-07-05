from backend_v2.models.domain.mcp import CitationExtractionItemDTO
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.v2_core import BaseMatrixXAI, BaseTDAExtraction


def test_mcp_reasoning_graceful_truncation():
    """Varmistetaan, että MCP:n (CitationExtractionItemDTO) tiukka 400 merkin
    raja EI kaada ajoa, vaan tekee siistin 'graceful truncation' leikkauksen.
    """
    massive_reasoning = "This is a very long reasoning string. " * 50  # Paljon yli 400 merkkiä
    assert len(massive_reasoning) > 1000

    item = CitationExtractionItemDTO(
        claim_text="Test claim",
        search_query="Test query",
        knowledge_gap="Test gap",
        search_rationale="Test rationale",
        reasoning=massive_reasoning,
    )

    # Varmistetaan, että teksti katkaistiin oikein alle 400 merkkiin.
    assert len(item.reasoning) <= 400
    assert item.reasoning.endswith("...") or item.reasoning.endswith(".")


def test_chunk_worker_reasoning_integrity():
    """Varmistetaan, että TDA Extraction (Chunk Workerin ydin) EI typistä
    valtavaa semantic_reasoning -kenttää, vaan säilyttää tekoälyn koko ajatusketjun.
    """
    massive_reasoning = "Tämä on massiivinen ja syvällinen päättelyketju. " * 500  # Yli 25 000 merkkiä!
    assert len(massive_reasoning) > 20000

    quote = LLMExtractedQuote(
        text="Lainaus",
        exact_quote="Lainaus",
        page_number=1,
        source_document_id="doc1",
        reasoning_trace="Reasoning trace",
    )

    tda = BaseTDAExtraction(
        exact_quotes=[quote],
        localized_anchors_found=["sana"],
        contextual_override=False,
        semantic_reasoning=massive_reasoning,
    )

    # Varmistetaan, että yhtäkään merkkiä ei leikattu tai kadotettu!
    assert len(tda.semantic_reasoning) == len(massive_reasoning)
    assert tda.semantic_reasoning == massive_reasoning


def test_matrix_xai_reasoning_integrity():
    """Varmistetaan, että myös Matrix-tason XAI-analyysit säilyttävät massiivisen päättelyn."""
    huge_reasoning = "A " * 50000  # 100 000 merkkiä

    xai = BaseMatrixXAI(semantic_reasoning=huge_reasoning)

    assert len(xai.semantic_reasoning) == 100000
    assert xai.semantic_reasoning == huge_reasoning
