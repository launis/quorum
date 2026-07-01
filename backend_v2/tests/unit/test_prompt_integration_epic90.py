"""Integration test to verify Epic 90 prompt logic incorporates seed_data and legacy mandates."""

import json
from pathlib import Path

from backend_v2.models.prompts.global_mandates import (
    ANTI_SCORE_MANDATE,
    LANGUAGE_MANDATE,
    NULL_HYPOTHESIS_MANDATE,
    SEMANTIC_BLEED_MANDATE,
)
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


def load_seed_blocks() -> dict[str, PromptBlock]:
    """Helper to load all prompt blocks from seed_data.json."""
    seed_path = Path("backend_v2/seed/seed_data.json")
    with seed_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    blocks = {}
    for b in data.get("prompt_blocks", []):
        blocks[b["id"]] = PromptBlock.model_validate(b)
    return blocks


def test_epic90_prompt_integration_holistic() -> None:
    """Test that execution persona, workflow defaults, and old mandates are properly integrated."""
    # 1. Load seed data
    blocks = load_seed_blocks()

    # execution_persona from L198
    persona_id = "blk_e6b638d1307641da83ed192c65c0283f"
    assert persona_id in blocks, "Execution Persona block missing from seed_data.json"
    persona_block = blocks[persona_id]

    # workflow default from L7374 (we can just verify it exists, or test the profile)
    seed_path = Path("backend_v2/seed/seed_data.json")
    with seed_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    wf = next((w for w in data.get("workflows", []) if w["id"] == "wf_0000000000000000"), None)
    assert wf is not None, "Workflow wf_0000000000000000 missing"
    assert wf["default_profile_id"] == "prf_4050cb0e1f4245e2b44e42153d9cc962", "Workflow default_profile_id mismatch"

    # 2. Build XML Rubrics using LocalizationCompiler (inside PromptCompiler)
    compiler = PromptCompiler()

    # Note: Execution persona is passed to compile_xml_rubrics
    rubrics_xml = compiler.compile_xml_rubrics(criteria=[], target_locale="fi", execution_persona_block=persona_block)

    # Assert persona was injected correctly
    assert "<EXECUTION_PERSONA>" in rubrics_xml
    assert persona_block.ai_description in rubrics_xml, "Persona ai_description was not injected into rubrics"

    # 3. Compile the full chunk prompt
    adapter = PromptCompilerAdapter()
    compiled_prompt = adapter.compile_chunk_prompt(
        base_system_prompt="Base system prompt",
        chunk_criteria=[],
        base_payload="Test Payload",
        strictness_level=100,
        target_locale="fi",
    )

    dynamic_content = compiled_prompt.dynamic_messages[0]["content"]

    # 4. Analyze presence of legacy mandates from global_mandates.py

    print("\n--- TEST ANALYSIS ---")
    print("Checking if global_mandates.py is perfectly synced with the prompt builder:")

    # Assert Exact Matches from source of truth
    assert ANTI_SCORE_MANDATE.strip() in dynamic_content.strip(), (
        "ANTI_SCORE_MANDATE from global_mandates.py is missing or diverged from final prompt!"
    )
    assert LANGUAGE_MANDATE.strip() in dynamic_content.strip(), (
        "LANGUAGE_MANDATE from global_mandates.py is missing or diverged from final prompt!"
    )
    assert SEMANTIC_BLEED_MANDATE.strip() in dynamic_content.strip(), "SEMANTIC_BLEED_MANDATE missing or diverged!"
    assert NULL_HYPOTHESIS_MANDATE.strip() in dynamic_content.strip(), "NULL_HYPOTHESIS_MANDATE missing or diverged!"

    print("Test passed! The mandates from global_mandates.py are perfectly mirrored in the final prompt.")
