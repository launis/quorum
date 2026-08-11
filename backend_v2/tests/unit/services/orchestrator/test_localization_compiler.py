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
