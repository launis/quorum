import json
from pathlib import Path
from typing import Any

from backend_v2.models.v2_core import OutputProfile, PromptBlock, Workflow

SEED_FILE = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")


def test_prompt_blocks_do_not_contain_ui_logic() -> None:
    """Architectural Guardrail: PromptBlocks MUST NOT contain UI formatting instructions."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    blocks = [PromptBlock.model_validate(b) for b in data.get("prompt_blocks", [])]

    for block in blocks:
        if block.ai_description:
            ai_desc = block.ai_description.upper()
            assert "0-100" not in ai_desc, f"Block {block.id} contains 0-100 UI scale logic in ai_description"
            assert "PUNCHY SENTENCE" not in ai_desc, f"Block {block.id} contains UI formatting in ai_description"


def test_output_profiles_do_not_contain_execution_logic() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain execution terminology."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    execution_terms = ["NULL HYPOTHESIS", "ZERO-TRUST AUDITOR", "BOOLEAN", "FALSE", "TRUE"]

    def assert_no_execution_logic(synthesis: Any, context: str) -> None:
        if not synthesis or not getattr(synthesis, "system_prompt", None):
            return
        prompt = synthesis.system_prompt.upper()
        for term in execution_terms:
            assert term not in prompt, f"Execution terminology '{term}' found in {context}"

    if "output_profiles" in data:
        for raw_profile in data["output_profiles"]:
            profile = OutputProfile.model_validate(raw_profile)
            assert_no_execution_logic(profile.synthesis, f"Root Profile {profile.id}")
            if hasattr(profile, "layouts"):
                for i, layout in enumerate(profile.layouts):
                    assert_no_execution_logic(layout.synthesis, f"Root Profile {profile.id} layout {i}")

    if "workflows" in data:
        for raw_wf in data["workflows"]:
            wf = Workflow.model_validate(raw_wf)
            if wf.output_profiles:
                for p_id, embedded_profile in wf.output_profiles.items():
                    assert_no_execution_logic(embedded_profile.synthesis, f"Workflow {wf.id} Profile {p_id}")
