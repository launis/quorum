import json
from pathlib import Path
from typing import Any

SEED_FILE = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")


def test_prompt_blocks_do_not_contain_ui_logic() -> None:
    """Architectural Guardrail: PromptBlocks MUST NOT contain UI formatting instructions."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    for block in data.get("prompt_blocks", []):
        block_id = block.get("id", "unknown")
        assert block.get("slug") != "row_explanation_generator", (
            f"Block {block_id} violates architecture by being a row_explanation_generator"
        )

        # Rule 2: ai_description must not enforce 0-100 scales
        ai_desc = block.get("ai_description", "").upper()
        assert "0-100" not in ai_desc, f"Block {block_id} contains 0-100 UI scale logic in ai_description"

        # Rule 3: No UI keywords
        assert "PUNCHY SENTENCE" not in ai_desc, f"Block {block_id} contains UI formatting in ai_description"


def test_output_profiles_do_not_contain_execution_logic() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain execution terminology."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    execution_terms = ["NULL HYPOTHESIS", "ZERO-TRUST AUDITOR", "BOOLEAN", "FALSE", "TRUE"]

    def assert_no_execution_logic(synthesis: dict[str, Any] | None, context: str) -> None:
        if not synthesis or "system_prompt" not in synthesis:
            return
        prompt = synthesis.get("system_prompt", "").upper()
        for term in execution_terms:
            # Exception for actual instructions like "Do not evaluate as true/false"
            # But the requirement strictly says "No OutputProfile contains execution terminology".
            # We will just check if the term exists and is not part of a negated instruction.
            # Actually, the requirement says "No OutputProfile contains execution terminology."
            assert term not in prompt, f"Execution terminology '{term}' found in {context}"

    if "output_profiles" in data:
        for profile in data["output_profiles"]:
            profile_id = profile.get("id", "unknown")
            assert_no_execution_logic(profile.get("synthesis"), f"Root Profile {profile_id}")
            for i, layout in enumerate(profile.get("layouts", [])):
                assert_no_execution_logic(layout.get("synthesis"), f"Root Profile {profile_id} layout {i}")

    if "workflows" in data:
        for wf in data["workflows"]:
            wf_id = wf.get("id", "unknown")
            profiles = wf.get("output_profiles", {})
            if isinstance(profiles, dict):
                for p_id, profile in profiles.items():
                    assert_no_execution_logic(profile.get("synthesis"), f"Workflow {wf_id} Profile {p_id}")
                    for i, layout in enumerate(profile.get("layouts", [])):
                        assert_no_execution_logic(
                            layout.get("synthesis"), f"Workflow {wf_id} Profile {p_id} layout {i}"
                        )
            elif isinstance(profiles, list):
                for profile in profiles:
                    profile_id = profile.get("id", "unknown")
                    assert_no_execution_logic(profile.get("synthesis"), f"Workflow {wf_id} Profile {profile_id}")
                    for i, layout in enumerate(profile.get("layouts", [])):
                        assert_no_execution_logic(
                            layout.get("synthesis"), f"Workflow {wf_id} Profile {profile_id} layout {i}"
                        )
