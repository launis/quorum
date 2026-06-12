from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_inverse_logic_injected() -> None:
    compiler = PromptCompiler()

    mock_matrix_block = {
        "id": "blk_1234567890abcdef",
        "slug": "test_matrix",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": "float",
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
        "computed_min": 1,
        "computed_max": 5,
        "label": {"default_locale": "en", "translations": {"en": "Inverse Test Matrix", "fi": "Inverse Test Matrix"}},
        "ai_description": "Test description",
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                        "ai_description": "Legacy desc",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": {
                                    "default_locale": "en",
                                    "translations": {"en": "Standard rule", "fi": "Standard rule"},
                                },
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            },
                            {
                                "tda_id": "tda_22222222222222222222222222222222",
                                "concept_description": {
                                    "default_locale": "en",
                                    "translations": {"en": "Inverse rule", "fi": "Inverse rule"},
                                },
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS",
                            },
                        ],
                    }
                ],
            }
        ],
    }

    block = PromptBlock.model_validate(mock_matrix_block)
    rubrics = compiler.compile_xml_rubrics([block], target_locale="en")

    # Assert standard rule is present without inverse text
    assert "Standard rule" in rubrics
    assert "Standard rule This is an inverse rule" not in rubrics

    # Assert inverse logic string is properly injected
    expected_inverse_text = (
        "Inverse rule This is an inverse rule (Vice). "
        "If rule_satisfied = True (no issues found), evidence_found MUST be False "
        'and you must return an empty string "" for exact_quote. '
        "If rule_satisfied = False (violation found), evidence_found MUST be True "
        "and you MUST quote the exact violation."
    )

    assert expected_inverse_text in rubrics, "Inverse logic text was not injected properly."
