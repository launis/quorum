"""Unit tests for PromptCompilerAdapter and static-first cryptographic determinism verification."""

from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


def test_prompt_compiler_adapter_delegation() -> None:
    """Verifies that PromptCompilerAdapter correctly delegates unknown methods to PromptCompiler."""
    adapter = PromptCompilerAdapter()

    # Verify delegation of build_dynamic_schema
    DynamicSchema = adapter.build_dynamic_schema("DynamicTest", [], False, "en", strictness_level=50)
    assert DynamicSchema is not None
    assert hasattr(DynamicSchema, "model_fields")

    # Verify delegation of calibrate_strictness
    assert "SCORING_STRICTNESS: 0/100" in adapter.calibrate_strictness(0)
    assert "SCORING_STRICTNESS: 100/100" in adapter.calibrate_strictness(100)


def test_prompt_compiler_adapter_compile_prompt_fallback() -> None:
    """Verifies compile_prompt fallback correctly splits pre-compiled message list via regex tags."""
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
        {"role": "system", "content": "Static system prompt"},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": "Previous response"},
        {"role": "user", "content": "Follow-up question"},
    ]

    prompt = adapter.compile_prompt(messages)

    # 1. System is static
    assert prompt.static_messages[0]["role"] == "system"
    assert prompt.static_messages[0]["content"] == "Static system prompt"

    # 2. Static user contents are isolated in static
    static_user = prompt.static_messages[1]
    assert static_user["role"] == "user"
    assert "<source_data>Verbatim content</source_data>" in static_user["content"]
    assert "<task>Execute task.</task>" in static_user["content"]
    assert "<execution_parameters>" not in static_user["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" not in static_user["content"]

    # 3. Dynamic blocks are isolated in dynamic
    dynamic_user = prompt.dynamic_messages[0]
    assert dynamic_user["role"] == "user"
    assert "<execution_parameters>" in dynamic_user["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" in dynamic_user["content"]
    assert "<source_data>" not in dynamic_user["content"]
    assert "<task>" not in dynamic_user["content"]

    # 4. Assistant and subsequent users are kept in dynamic
    assert prompt.dynamic_messages[1]["role"] == "assistant"
    assert prompt.dynamic_messages[2]["role"] == "user"


def test_prompt_compiler_adapter_compile_prompt_empty_dynamic_fallback() -> None:
    """Verifies that if no dynamic tags are present, the last message is moved to dynamic_msgs to prevent Vertex AI 400 errors."""
    adapter = PromptCompilerAdapter()

    messages = [
        {"role": "system", "content": "Static system"},
        {"role": "user", "content": "Just a plain user message without any execution parameters or error tags."},
    ]

    prompt = adapter.compile_prompt(messages)

    # 1. System is static
    assert len(prompt.static_messages) == 1
    assert prompt.static_messages[0]["role"] == "system"

    # 2. User message moved to dynamic as fallback
    assert len(prompt.dynamic_messages) == 1
    assert prompt.dynamic_messages[0]["role"] == "user"
    assert "plain user message" in prompt.dynamic_messages[0]["content"]
