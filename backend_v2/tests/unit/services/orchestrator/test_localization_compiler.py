import pytest

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.domain.prompt_blocks import (
    PromptBlockAdapter,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import PromptBlockCategory
from backend_v2.services.orchestrator.localization_compiler import LocalizationCompiler


def test_resolve_i18n() -> None:
    compiler = LocalizationCompiler()

    text_obj = {"translations": {"en": "Hello", "fi": "Hei"}}
    assert compiler.resolve_i18n(text_obj, "en") == "Hello"
    assert compiler.resolve_i18n(text_obj, "fi") == "Hei"

    assert compiler.resolve_i18n(None, "en") == ""

    with pytest.raises(ConfigurationError):
        compiler.resolve_i18n(text_obj, "sv")


def test_compile_static_instructions_supported_locales() -> None:
    """Test all supported locales resolve successfully in compile_static_instructions."""
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_5234567890abcdef",
            "slug": "test_static",
            "category_id": "system_rule",
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "type": "instruction",
            "label": {"translations": {"en": "Test", "fi": "Test"}},
            "instruction_text": "Target language is {TARGET_LANGUAGE}",
        }
    ]
    blocks = [PromptBlockAdapter.validate_python(c) for c in mock_criteria]

    expected = {
        "en": "English",
        "fi": "Finnish",
        "sv": "Swedish",
        "de": "German",
        "fr": "French",
        "es": "Spanish",
    }
    for loc, lang_name in expected.items():
        result = compiler.compile_static_instructions(blocks, target_locale=loc)
        assert f"Target language is {lang_name}" in result


def test_compile_static_instructions_unsupported_locale_raises_app_exception() -> None:
    """Negative test 1: Unsupported locale raises AppException with VALIDATION_FAILED (400)."""
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_5234567890abcdef",
            "slug": "test_static",
            "category_id": "system_rule",
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "type": "instruction",
            "label": {"translations": {"en": "Test", "fi": "Test"}},
            "instruction_text": "Test static instruction",
        }
    ]
    blocks = [PromptBlockAdapter.validate_python(c) for c in mock_criteria]

    with pytest.raises(AppException) as exc_info:
        compiler.compile_static_instructions(blocks, target_locale="zh")

    assert exc_info.value.status_code == 400
    assert "Unsupported target locale 'zh'" in str(exc_info.value.message)
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


def test_compile_dynamic_instructions_supported_locales() -> None:
    """Test all supported locales resolve successfully in compile_dynamic_instructions."""
    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_6234567890abcdef",
            "slug": "test_dynamic",
            "category_id": "runtime_variables",
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "type": "instruction",
            "label": {"translations": {"en": "Test", "fi": "Test"}},
            "instruction_text": "Today is {CURRENT_DATE} in {TARGET_LANGUAGE}",
        }
    ]
    blocks = [PromptBlockAdapter.validate_python(c) for c in mock_criteria]
    result = compiler.compile_dynamic_instructions(blocks, target_locale="fi")
    assert "<DYNAMIC_INSTRUCTION" in result
    assert "{CURRENT_DATE}" not in result
    assert "in Finnish" in result


def test_resolve_i18n_invalid_inputs() -> None:
    """Test error handling in resolve_i18n for invalid dictionary or types."""
    compiler = LocalizationCompiler()

    # Invalid dict
    with pytest.raises(ConfigurationError):
        compiler.resolve_i18n({"invalid": "format"}, "en")

    # Non-dict
    with pytest.raises(ConfigurationError):
        compiler.resolve_i18n(12345, "en")


def test_compile_static_instructions_missing_instruction_text() -> None:
    """Test ConfigurationError when block is missing mandatory instruction_text."""
    compiler = LocalizationCompiler()
    mock_block = SystemRulePromptBlock.model_construct(
        id="blk_nodesc",
        slug="no_desc",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        label={"translations": {"en": "Label"}},
        instruction_text=None,
    )
    with pytest.raises(ConfigurationError):
        compiler.compile_static_instructions([mock_block], target_locale="en")


def test_compile_dynamic_instructions_missing_instruction_text() -> None:
    """Test ConfigurationError when runtime_variables block is missing instruction_text."""
    compiler = LocalizationCompiler()
    mock_block = SystemRulePromptBlock.model_construct(
        id="blk_nodyn",
        slug="no_dyn",
        category_id=PromptBlockCategory.RUNTIME_VARIABLES,
        label={"translations": {"en": "Label"}},
        instruction_text=None,
    )
    with pytest.raises(ConfigurationError):
        compiler.compile_dynamic_instructions([mock_block], target_locale="en")


def test_compile_dynamic_instructions_execution_time_types() -> None:
    """Test compilation with valid ISO string, valid datetime, invalid string, and invalid type."""
    import datetime

    compiler = LocalizationCompiler()
    mock_criteria = [
        {
            "id": "blk_7234567890abcdef",
            "slug": "test_dyn_time",
            "category_id": "runtime_variables",
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "type": "instruction",
            "label": {"translations": {"en": "Test", "fi": "Test"}},
            "instruction_text": "Date: {CURRENT_DATE} Time: {DYNAMIC_TIME}",
        }
    ]
    blocks = [PromptBlockAdapter.validate_python(c) for c in mock_criteria]

    # ISO string
    res1 = compiler.compile_dynamic_instructions(blocks, target_locale="en", execution_time="2026-05-01T12:00:00Z")
    assert "Date: 2026-05-01" in res1

    # Datetime object
    dt = datetime.datetime(2026, 7, 7, 8, 30, tzinfo=datetime.timezone.utc)
    res2 = compiler.compile_dynamic_instructions(blocks, target_locale="en", execution_time=dt)
    assert "Date: 2026-07-07" in res2

    # Invalid string raises AppException
    with pytest.raises(AppException) as exc1:
        compiler.compile_dynamic_instructions(blocks, target_locale="en", execution_time="not-a-datetime")
    assert exc1.value.status_code == 400

    # Invalid type raises AppException
    with pytest.raises(AppException) as exc2:
        compiler.compile_dynamic_instructions(blocks, target_locale="en", execution_time=12345)  # type: ignore[arg-type]
    assert exc2.value.status_code == 400


def test_compile_static_instructions_polymorphic_subtypes() -> None:
    """Test compile_static_instructions extracts text correctly across Persona, Protocol, and SystemRule blocks."""
    from backend_v2.models.domain.prompt_blocks import (
        PersonaPromptBlock,
        ProtocolPromptBlock,
        SystemRulePromptBlock,
    )
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory
    from backend_v2.models.v2_core import I18nText

    compiler = LocalizationCompiler()

    persona = PersonaPromptBlock(
        id="blk_1111111111111111",
        slug="persona_block",
        label=I18nText(translations={"en": "Persona"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Act as senior analyst in {TARGET_LANGUAGE}",
    )
    protocol = ProtocolPromptBlock(
        id="blk_2222222222222222",
        slug="protocol_block",
        label=I18nText(translations={"en": "Protocol"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        protocol_instructions="Extract exact quotes for {TARGET_LANGUAGE}",
    )
    system_rule = SystemRulePromptBlock(
        id="blk_3333333333333333",
        slug="system_rule_block",
        label=I18nText(translations={"en": "SystemRule"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Enforce strict logic in {TARGET_LANGUAGE}",
    )

    compiled = compiler.compile_static_instructions([persona, protocol, system_rule], target_locale="fi")
    assert "Act as senior analyst in Finnish" in compiled
    assert "Extract exact quotes for Finnish" in compiled
    assert "Enforce strict logic in Finnish" in compiled


def test_compile_static_instructions_missing_instruction_text_raises_configuration_error() -> None:
    """Anti-happy path: PromptBlock with missing instruction_text raises ConfigurationError."""
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.enums import PromptBlockCategory

    compiler = LocalizationCompiler()
    mock_block = SystemRulePromptBlock.model_construct(
        id="blk_nodesc_empty",
        slug="no_desc_empty",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        label={"translations": {"en": "Label"}},
        instruction_text=None,
    )
    with pytest.raises(ConfigurationError):
        compiler.compile_static_instructions([mock_block], target_locale="en")


def test_compile_dynamic_instructions_unsupported_locale_raises_app_exception() -> None:
    """Anti-happy path: compile_dynamic_instructions raises AppException for unsupported locale."""
    compiler = LocalizationCompiler()
    with pytest.raises(AppException) as exc_info:
        compiler.compile_dynamic_instructions([], target_locale="zh")
    assert exc_info.value.status_code == 400
    assert "Unsupported target locale 'zh'" in str(exc_info.value.message)


def test_compile_dynamic_instructions_polymorphic_system_rule() -> None:
    """Test compile_dynamic_instructions extracts instruction_text on SystemRulePromptBlock."""
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory
    from backend_v2.models.v2_core import I18nText

    compiler = LocalizationCompiler()
    block = SystemRulePromptBlock(
        id="blk_1111222233334444",
        slug="dyn_sys",
        label=I18nText(translations={"en": "DynSys"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.RUNTIME_VARIABLES,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Dynamic run on {CURRENT_DATE} in {TARGET_LANGUAGE}",
    )
    res = compiler.compile_dynamic_instructions([block], target_locale="fi")
    assert "<DYNAMIC_INSTRUCTION" in res
    assert "in Finnish" in res
