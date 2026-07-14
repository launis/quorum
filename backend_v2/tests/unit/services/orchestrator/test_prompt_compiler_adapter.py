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
    DynamicSchema = adapter.build_dynamic_schema("DynamicTest", [], False, "en", strictness_level=50)
    assert DynamicSchema is not None
    assert hasattr(DynamicSchema, "model_fields")

    # Verify delegation of calibrate_strictness
    assert "SCORING_STRICTNESS: 0/100" in adapter.calibrate_strictness(0)
    assert "SCORING_STRICTNESS: 100/100" in adapter.calibrate_strictness(100)


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
        base_payload="<source_data>\nVerbatim source doc.\n</source_data>",
        strictness_level=85,
        target_locale="en",
        previous_errors=["Syntax Error 1"],
    )

    assert isinstance(prompt, CompiledPrompt)
    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[0]["role"] == "system"
    assert prompt.static_messages[0]["content"] == "Analyze this text."
    assert prompt.static_messages[1]["role"] == "user"
    assert "<source_data>" in prompt.static_messages[1]["content"]

    assert len(prompt.dynamic_messages) == 1
    assert prompt.dynamic_messages[0]["role"] == "user"
    # V3 Default: System prompt is NOT in dynamic tier
    assert "Analyze this text." not in prompt.dynamic_messages[0]["content"]
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


def test_prompt_compiler_adapter_compile_prompt_empty_dynamic_fallback() -> None:
    """Verifies that if no dynamic tags are present, the last message is moved to dynamic_msgs to prevent Vertex AI 400 errors."""
    adapter = PromptCompilerAdapter()

    messages = [
        {"role": "system", "content": "Static system"},
        {"role": "user", "content": "Just a plain user message without any execution parameters or error tags."}
    ]

    prompt = adapter.compile_prompt(messages)

    # 1. System is static
    assert len(prompt.static_messages) == 1
    assert prompt.static_messages[0]["role"] == "system"

    # 2. User message moved to dynamic as fallback
    assert len(prompt.dynamic_messages) == 1
    assert prompt.dynamic_messages[0]["role"] == "user"
    assert "plain user message" in prompt.dynamic_messages[0]["content"]


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


def _make_test_block() -> PromptBlock:
    """Shared helper to create a minimal valid PromptBlock for feature flag tests."""
    return PromptBlock.model_validate(
        {
            "id": "blk_e80f1a9b00000001",
            "slug": "flag_test",
            "category_id": "matrix",
            "description": {"default_locale": "en", "translations": {"en": "Flag", "fi": "Flag"}},
            "type": BlockDataType.FLOAT,
            "label": {"default_locale": "en", "translations": {"en": "FlagTest", "fi": "FlagTest"}},
            "ai_description": "Epic 80 feature flag test criteria",
            "scales": [
                {
                    "score": 1,
                    "ai_label": "LEVEL_ONE",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "C1", "fi": "C1"}},
                            "ai_description": "Directive flag test",
                            "tda_assertions": [
                                {
                                    "tda_id": "tda_e80f1a9b0000000000000000000000f1",
                                    "concept_description": "Flag test assertion",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )


def test_content_cache_enabled_demotes_system_to_user() -> None:
    """Epic 80 Feature Flag: When CONTENT_CACHE_ENABLED=1, the system prompt MUST be
    demoted from native 'system' role to '<system_instructions>' within a 'user' message.
    This is a deliberate architectural trade-off for Vertex AI cache compatibility.
    """
    from unittest.mock import patch

    adapter = PromptCompilerAdapter()
    block = _make_test_block()
    system_prompt = "You are an adversarial auditor. Never compromise."

    with patch("backend_v2.services.orchestrator.prompt_compiler_adapter.get_settings") as mock_settings:
        # Simulate CONTENT_CACHE_ENABLED = 1
        mock_settings.return_value.content_cache_enabled = 1

        prompt = adapter.compile_chunk_prompt(
            base_system_prompt=system_prompt,
            chunk_criteria=[block],
            base_payload="<source_data>\nSource document for cache testing.\n</source_data>",
            strictness_level=50,
            target_locale="fi",
        )

    assert isinstance(prompt, CompiledPrompt)

    # Static tier: ONLY the PDF, no system role at all
    assert len(prompt.static_messages) == 1
    assert prompt.static_messages[0]["role"] == "user"
    assert "<source_data>" in prompt.static_messages[0]["content"]
    # System prompt MUST NOT appear in static tier
    assert system_prompt not in prompt.static_messages[0]["content"]

    # Dynamic tier: System prompt demoted inside <system_instructions> tags
    dynamic_content = prompt.dynamic_messages[0]["content"]
    assert "<system_instructions>" in dynamic_content
    assert system_prompt in dynamic_content
    assert prompt.dynamic_messages[0]["role"] == "user"

    # Prove no message in the entire prompt has role="system"
    all_messages = prompt.static_messages + prompt.dynamic_messages
    system_roles = [m for m in all_messages if m["role"] == "system"]
    assert len(system_roles) == 0, "Epic 80 mode MUST NOT produce any system-role messages (Vertex AI API constraint)"


def test_content_cache_modes_are_structurally_incompatible() -> None:
    """Proves that CONTENT_CACHE_ENABLED=0 and CONTENT_CACHE_ENABLED=1 produce
    structurally different outputs. This validates the feature flag actually
    changes behavior and guards against accidental no-ops.

    The V3 default (disabled) MUST have system role; Epic 80 (enabled) MUST NOT.
    Their static SHA-256 hashes MUST differ (different message counts and roles).
    """
    from unittest.mock import patch

    adapter = PromptCompilerAdapter()
    block = _make_test_block()
    system_prompt = "Strict evaluation rules."
    payload = "Identical source document."

    compile_kwargs = {
        "base_system_prompt": system_prompt,
        "chunk_criteria": [block],
        "base_payload": payload,
        "strictness_level": 70,
        "target_locale": "en",
    }

    # --- Mode 0: V3 Default (system role preserved) ---
    with patch("backend_v2.services.orchestrator.prompt_compiler_adapter.get_settings") as mock_settings:
        mock_settings.return_value.content_cache_enabled = 0
        prompt_v3 = adapter.compile_chunk_prompt(**compile_kwargs)

    # --- Mode 1: Epic 80 Content Cache (system role demoted) ---
    with patch("backend_v2.services.orchestrator.prompt_compiler_adapter.get_settings") as mock_settings:
        mock_settings.return_value.content_cache_enabled = 1
        prompt_epic80 = adapter.compile_chunk_prompt(**compile_kwargs)

    # Structural divergence: V3 has 2 static messages, Epic 80 has 1
    assert len(prompt_v3.static_messages) == 2, "V3 default must have system + user in static"
    assert len(prompt_epic80.static_messages) == 1, "Epic 80 must have only user in static"

    # Role divergence: V3 has system role, Epic 80 does not
    v3_roles = {m["role"] for m in prompt_v3.static_messages}
    epic80_roles = {m["role"] for m in prompt_epic80.static_messages}
    assert "system" in v3_roles, "V3 default MUST preserve native system role"
    assert "system" not in epic80_roles, "Epic 80 MUST NOT have system role"

    # Content divergence: Epic 80 dynamic tier contains system_instructions tag
    epic80_dynamic = prompt_epic80.dynamic_messages[0]["content"]
    v3_dynamic = prompt_v3.dynamic_messages[0]["content"]
    assert "<system_instructions>" in epic80_dynamic
    assert "<system_instructions>" not in v3_dynamic

    # Cryptographic proof: Static hashes MUST differ between modes
    hash_v3 = hashlib.sha256(json.dumps(prompt_v3.static_messages, sort_keys=True).encode()).hexdigest()
    hash_epic80 = hashlib.sha256(json.dumps(prompt_epic80.static_messages, sort_keys=True).encode()).hexdigest()
    assert hash_v3 != hash_epic80, "Feature flag is a no-op! V3 and Epic 80 static hashes must differ."
