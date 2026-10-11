"""Unit tests for PromptCompilerAdapter and static-first cryptographic determinism verification."""

from backend_v2.models.domain.system_config import ChatMessageDTO
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


def test_prompt_compiler_adapter_delegation() -> None:
    """Verifies that PromptCompilerAdapter correctly delegates methods to PromptCompiler."""
    adapter = PromptCompilerAdapter()

    # Verify delegation of build_dynamic_schema
    DynamicSchema = adapter.build_dynamic_schema("DynamicTest", [], False, "en", strictness_level=50)
    assert DynamicSchema is not None
    assert "model_fields" in dir(DynamicSchema)

    # Verify delegation of calibrate_strictness
    assert "SCORING_STRICTNESS: 0/100" in adapter.calibrate_strictness(0)
    assert "SCORING_STRICTNESS: 100/100" in adapter.calibrate_strictness(100)

    # Verify delegation of get_schema_healing_prompt
    healing = adapter.get_schema_healing_prompt("Test error", is_logical_error=False, is_eof=False)
    assert "STRICT JSON SCHEMA VALIDATION FAILED" in healing

    # Verify delegation of compile_chunk_payload_instruction
    chunk_inst = adapter.compile_chunk_payload_instruction("chunk_1", "Sample text")
    assert "<user_payload>" in chunk_inst


def test_prompt_compiler_adapter_compile_prompt_segregation() -> None:
    """Verifies compile_prompt cleanly segregates static system messages and dynamic tail without regex scraping."""
    adapter = PromptCompilerAdapter()

    user_content = (
        "<source_data>Verbatim content</source_data>\n\n"
        "<execution_parameters>\n"
        "<STRICTNESS_CALIBRATION>\nBalanced.\n</STRICTNESS_CALIBRATION>\n"
        "</execution_parameters>\n\n"
        "<PREVIOUS_SCHEMA_ERROR>\nValidation failed.\n</PREVIOUS_SCHEMA_ERROR>\n\n"
        "<task>Execute task.</task>"
    )

    messages = [
        ChatMessageDTO(role="system", content="Static system prompt"),
        ChatMessageDTO(role="user", content=user_content),
        ChatMessageDTO(role="assistant", content="Previous response"),
        ChatMessageDTO(role="user", content="Follow-up question"),
    ]

    prompt = adapter.compile_prompt(messages)

    # 1. System is static
    assert len(prompt.static_messages) == 1
    assert prompt.static_messages[0].role == "system"
    assert prompt.static_messages[0].content == "Static system prompt"

    # 2. Dynamic messages receive all non-system turns intact without regex scraping
    assert len(prompt.dynamic_messages) == 3
    assert prompt.dynamic_messages[0].role == "user"
    assert prompt.dynamic_messages[0].content == user_content
    assert prompt.dynamic_messages[1].role == "assistant"
    assert prompt.dynamic_messages[1].content == "Previous response"
    assert prompt.dynamic_messages[2].role == "user"
    assert prompt.dynamic_messages[2].content == "Follow-up question"


def test_prompt_compiler_adapter_compile_prompt_missing_dynamic_tail_raises_neg10() -> None:
    """Verifies Scenario NEG-10: compile_prompt fails fast when message list lacks dynamic tail."""
    import pytest

    from backend_v2.exceptions import AppException, ErrorCodes

    adapter = PromptCompilerAdapter()

    messages = [
        {"role": "system", "content": "Static system instruction 1"},
        {"role": "system", "content": "Static system instruction 2"},
    ]

    with pytest.raises(AppException) as exc_info:
        adapter.compile_prompt(messages)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Compiled prompt requires at least one dynamic message in the dynamic tail." in exc_info.value.message


def test_prompt_compiler_adapter_extended_delegation() -> None:
    """Verifies delegation for i18n, static/dynamic instructions, chunk schema, and xml context."""
    from pydantic import BaseModel

    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
    from backend_v2.models.dtos.prompt import PromptMappingDTO
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory

    adapter = PromptCompilerAdapter()

    # 1. resolve_i18n
    i18n_obj = I18nText(translations={"en": "English Hello", "fi": "Hei"})
    assert adapter.resolve_i18n(i18n_obj, "en") == "English Hello"
    assert adapter.resolve_i18n(i18n_obj, "fi") == "Hei"

    # 2. compile_static_instructions & compile_dynamic_instructions
    static_block = SystemRulePromptBlock(
        id="blk_1111222233334444",
        slug="static_inst",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        label=I18nText(translations={"en": "Label"}),
        description=I18nText(translations={"en": "Desc"}),
        instruction_text="Static directive instruction",
    )
    static_out = adapter.compile_static_instructions([static_block], "en")
    assert "Static directive instruction" in static_out

    dynamic_block = SystemRulePromptBlock(
        id="blk_2222333344445555",
        slug="dyn_inst",
        category_id=PromptBlockCategory.RUNTIME_VARIABLES,
        type=BlockDataType.STRING,
        label=I18nText(translations={"en": "Dyn Label"}),
        description=I18nText(translations={"en": "Dyn Desc"}),
        instruction_text="Dynamic directive instruction",
    )
    dyn_out = adapter.compile_dynamic_instructions([dynamic_block], "en")
    assert "Dynamic directive instruction" in dyn_out

    # 3. build_chunk_response_schema
    class ItemModel(BaseModel):
        summary: str

    chunk_schema = adapter.build_chunk_response_schema("ChunkContainer", ItemModel)
    assert issubclass(chunk_schema, BaseModel)

    # 4. generate_mcp_instruction
    mcp_inst = adapter.generate_mcp_instruction(["web_search", "fetch_url"])
    assert "web_search" in mcp_inst

    # 5. build_xml_context
    from backend_v2.models.domain.step import ExpectedInput

    expected_inputs = [
        ExpectedInput(
            input_key="input_doc",
            label=I18nText(translations={"en": "Input Document"}),
            description=I18nText(translations={"en": "Desc"}),
            required=True,
            input_modes=["file"],
        )
    ]
    mapping = PromptMappingDTO(mappings={"doc_text": "$inputs.input_doc"})
    state = ExecutionInputsDTO(raw_inputs={"input_doc": "Document text content"})
    xml_context = adapter.build_xml_context(mapping, state, "en", expected_inputs=expected_inputs)
    assert '<matrix_input source_id="doc_text">' in xml_context
    assert "Document text content" in xml_context


def test_prompt_compiler_adapter_build_xml_context_missing_mapping_negative() -> None:
    """Verifies that build_xml_context raises AppException when mapped input is absent."""
    import pytest

    from backend_v2.exceptions import AppException
    from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
    from backend_v2.models.dtos.prompt import PromptMappingDTO

    adapter = PromptCompilerAdapter()
    mapping = PromptMappingDTO(mappings={"doc_text": "$inputs.missing_key"})
    state = ExecutionInputsDTO(raw_inputs={"different_key": "Some text"})

    with pytest.raises(AppException):
        adapter.build_xml_context(mapping, state, "en")


def test_prompt_compiler_adapter_compile_prompt_invalid_message_negative() -> None:
    """Verifies that compile_prompt fails-fast with ValidationError on malformed input."""
    import pytest
    from pydantic import ValidationError

    adapter = PromptCompilerAdapter()
    invalid_messages = [{"invalid_key": "no role or content"}]

    with pytest.raises(ValidationError):
        adapter.compile_prompt(invalid_messages)
