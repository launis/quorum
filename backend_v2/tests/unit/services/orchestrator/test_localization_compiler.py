import pytest

from backend_v2.exceptions import ConfigurationError
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.localization_compiler import LocalizationCompiler


def test_resolve_i18n() -> None:
    compiler = LocalizationCompiler()

    text_obj = {"default_locale": "en", "translations": {"en": "Hello", "fi": "Hei"}}
    assert compiler.resolve_i18n(text_obj, "en") == "Hello"
    assert compiler.resolve_i18n(text_obj, "fi") == "Hei"

    assert compiler.resolve_i18n(None, "en") == ""

    with pytest.raises(ConfigurationError):
        compiler.resolve_i18n(text_obj, "sv")


def test_compile_xml_rubrics_basic() -> None:
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_3234567890abcdef",
            "slug": "test",
            "category_id": "matrix",
            "allow_contextual_override": True,
            "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
            "type": "float",
            "scale_min": 1,
            "scale_max": 5,
            "computed_min": 1,
            "computed_max": 5,
            "label": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "ai_description": "Test description",
            "scales": [
                {
                    "score": 1,
                    "ai_label": "ONE",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                            "ai_description": "Directive 1",
                            "tda_assertions": [
                                {
                                    "tda_id": "tda_44444444444444444444444444444444",
                                    "concept_description": "Directive 1",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY",
                                    "anchor_target": "Source",
                                    "bounding_box_scope": "document",
                                    "extraction_rule": "Rule",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ]

    result = compiler.compile_xml_rubrics([PromptBlock.model_validate(c) for c in mock_criteria], target_locale="en")

    assert "<EVALUATION_RUBRICS>" in result
    assert "[CONTEXTUAL OVERRIDE ALLOWED]" in result
    assert "This is an inverse rule (Vice)." not in result


def test_compile_static_instructions() -> None:
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_5234567890abcdef",
            "slug": "test_static",
            "category_id": "system_rule",
            "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "ai_description": "Test static instruction",
        }
    ]
    result = compiler.compile_static_instructions(
        [PromptBlock.model_validate(c) for c in mock_criteria], target_locale="en"
    )
    assert "<STATIC_INSTRUCTION" in result
    assert "Test static instruction" in result


def test_compile_dynamic_instructions() -> None:
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_6234567890abcdef",
            "slug": "test_dynamic",
            "category_id": "runtime_variables",
            "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "ai_description": "Today is {CURRENT_DATE}",
        }
    ]
    result = compiler.compile_dynamic_instructions(
        [PromptBlock.model_validate(c) for c in mock_criteria], target_locale="en"
    )
    assert "<DYNAMIC_INSTRUCTION" in result
    assert "{CURRENT_DATE}" not in result


def test_compile_xml_rubrics_atom_alias_map_filtering() -> None:
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_4234567890abcdef",
            "slug": "test_filtered",
            "category_id": "matrix",
            "allow_contextual_override": True,
            "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
            "type": "float",
            "scale_min": 1,
            "scale_max": 5,
            "computed_min": 1,
            "computed_max": 5,
            "label": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "ai_description": "Test description",
            "scales": [
                {
                    "score": 1,
                    "ai_label": "ONE",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                            "ai_description": "Directive 1",
                            "tda_assertions": [
                                {
                                    "tda_id": "tda_44444444444444444444444444444444",
                                    "concept_description": "Directive 1",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY",
                                    "anchor_target": "Source",
                                    "bounding_box_scope": "document",
                                    "extraction_rule": "Rule",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ]

    criteria = [PromptBlock.model_validate(c) for c in mock_criteria]

    # Scenario 1: atom_alias_map is provided and matches. Output should use alias.
    result_alias = compiler.compile_xml_rubrics(
        criteria, target_locale="en", atom_alias_map={"tda_44444444444444444444444444444444": "a0"}
    )
    assert '<rule id="a0">' in result_alias
    assert '<rule id="tda_44444444444444444444444444444444">' not in result_alias

    # Scenario 2: atom_alias_map is provided but does NOT match. Rule should be completely skipped.
    result_skipped = compiler.compile_xml_rubrics(criteria, target_locale="en", atom_alias_map={"tda_5555": "a1"})
    assert '<rule id="' not in result_skipped
    assert "CRITICAL_DIRECTIVES" not in result_skipped

    # Scenario 3: The error scenario. allowed_atom_ids is provided but it contains the alias ("a0"), not the UUID.
    # This proves the original bug behavior if atom_alias_map was missing.
    result_bug = compiler.compile_xml_rubrics(criteria, target_locale="en", allowed_atom_ids={"a0"})
    assert '<rule id="' not in result_bug
