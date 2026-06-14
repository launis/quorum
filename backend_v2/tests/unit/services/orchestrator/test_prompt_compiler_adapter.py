"""Unit tests for PromptCompilerAdapter and static-first cryptographic determinism verification."""

import hashlib
import json

from backend_v2.models.enums import BlockDataType
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


def test_prompt_compiler_adapter_delegation() -> None:
    """Verifies that PromptCompilerAdapter correctly delegates unknown methods to PromptCompiler."""
    adapter = PromptCompilerAdapter()

    # Verify delegation of build_dynamic_schema
    DynamicSchema = adapter.build_dynamic_schema("DynamicTest", [], False, False, "en")
    assert DynamicSchema is not None
    assert hasattr(DynamicSchema, "model_fields")

    # Verify delegation of calibrate_strictness
    assert "Absolute Leniency" in adapter.calibrate_strictness(0)
    assert "Absolute Strictness" in adapter.calibrate_strictness(100)


def test_prompt_compiler_adapter_compile_chunk_prompt() -> None:
    """Verifies that compile_chunk_prompt natively constructs CompiledPrompt segments."""
    adapter = PromptCompilerAdapter()

    mock_block_dict = {
        "id": "blk_1234567890abcdef",
        "slug": "test",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "label": {"default_locale": "en", "translations": {"en": "Score", "fi": "Score"}},
        "ai_description": "Audit criteria",
        "scales": [
            {
                "score": 1,
                "ai_label": "UNCRITICAL ACCEPTANCE",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                        "ai_description": "Directive 1",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "Directive 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    mock_block = PromptBlock.model_validate(mock_block_dict)

    prompt = adapter.compile_chunk_prompt(
        base_system_prompt="Analyze this text.",
        chunk_criteria=[mock_block],
        base_payload="Verbatim source doc.",
        strictness_level=85,
        target_locale="en",
        previous_errors=["Syntax Error 1"],
    )

    assert isinstance(prompt, CompiledPrompt)
    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[0]["role"] == "system"
    assert "Analyze this text." in prompt.static_messages[0]["content"]
    # V3: Rubrics are in dynamic tier, NOT in static system message
    assert "EVALUATION_RUBRICS" not in prompt.static_messages[0]["content"]

    assert prompt.static_messages[1]["role"] == "user"
    assert "<source_data>\nVerbatim source doc.\n</source_data>" in prompt.static_messages[1]["content"]

    assert len(prompt.dynamic_messages) == 1
    assert prompt.dynamic_messages[0]["role"] == "user"
    # V3: Rubrics, strictness, and errors are all in dynamic tier
    assert "<evaluation_criteria>" in prompt.dynamic_messages[0]["content"]
    assert "<STRICTNESS_CALIBRATION>" in prompt.dynamic_messages[0]["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" in prompt.dynamic_messages[0]["content"]


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


def test_prompt_caching_cryptographic_determinism_proof() -> None:
    """Cryptographic Determinism Proof: Modifying dynamic parameters across 10 distinct runs
    MUST result in a 100% identical SHA-256 hash for the static_messages segment.
    """
    adapter = PromptCompilerAdapter()

    mock_block_dict = {
        "id": "blk_a1b2c3d4e5f6a7b8",
        "slug": "proof",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "label": {"default_locale": "en", "translations": {"en": "Parity", "fi": "Parity"}},
        "ai_description": "Proof criteria",
        "scales": [
            {
                "score": 1,
                "ai_label": "PARITY",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                        "ai_description": "Directive 1",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_22222222222222222222222222222222",
                                "concept_description": "Directive 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    mock_block = PromptBlock.model_validate(mock_block_dict)

    static_system = "Role: ADVERSARIAL AUDITOR."
    static_criteria = [mock_block]
    static_source_text = "Verbatim contract text for testing context cache hits."

    hashes = []

    # Compile 10 prompts, varying strictness, languages, retries, and errors in each run
    for i in range(10):
        strictness = i * 10
        lang = "fi" if i % 2 == 0 else "en"
        errors = [f"Healing Attempt {i}"] if i > 0 else None

        prompt = adapter.compile_chunk_prompt(
            base_system_prompt=static_system,
            chunk_criteria=static_criteria,
            base_payload=static_source_text,
            strictness_level=strictness,
            target_locale=lang,
            previous_errors=errors,
        )

        # Calculate cryptographic SHA-256 of the static_messages segment
        static_str = json.dumps(prompt.static_messages, sort_keys=True)
        sha256_hash = hashlib.sha256(static_str.encode("utf-8")).hexdigest()
        hashes.append(sha256_hash)

        # V3: Dynamic tier contains rubrics, strictness, and errors
        assert len(prompt.dynamic_messages) == 1
        assert "<evaluation_criteria>" in prompt.dynamic_messages[0]["content"]

    # Mathematically prove that all 10 runs produced the exact same static hash!
    first_hash = hashes[0]
    for idx, h in enumerate(hashes):
        assert h == first_hash, f"Hash mismatch at index {idx}! Caching efficiency degraded."
