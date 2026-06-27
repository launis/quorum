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
                                "concept_description": "Standard rule",
                                "anchor_target": "The summary",
                                "bounding_box_scope": "paragraph",
                                "extraction_rule": "Must be nice",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            },
                            {
                                "tda_id": "tda_22222222222222222222222222222222",
                                "concept_description": "Inverse rule",
                                "anchor_target": "The conclusion",
                                "bounding_box_scope": "document",
                                "extraction_rule": "Must not be mean",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS",
                                "contrastive_example": "This is a contrastive example text.",
                            },
                        ],
                    }
                ],
            }
        ],
    }

    block = PromptBlock.model_validate(mock_matrix_block)
    rubrics = compiler.compile_xml_rubrics([block], target_locale="en")

    # Assert standard rule fields are present in the new XML format
    assert "<anchor_target>The summary</anchor_target>" in rubrics
    assert "<validation_rule>Must be nice</validation_rule>" in rubrics

    # Assert inverse logic rule ID is present in XML rubrics
    assert '<rule id="tda_22222222222222222222222222222222">' in rubrics

    # Phase 4: Component: Prompt Compiler Integration Tests
    # Assert rule calibration and contrastive example tags are compiled correctly
    assert "<RULE_CALIBRATION_EXAMPLES>" in rubrics
    assert "<EXAMPLE>This is a contrastive example text.</EXAMPLE>" in rubrics
