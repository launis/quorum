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
            if hasattr(profile, "layouts"):
                for i, layout in enumerate(profile.layouts):
                    assert_no_execution_logic(layout.synthesis, f"Root Profile {profile.id} layout {i}")

    if "workflows" in data:
        for raw_wf in data["workflows"]:
            Workflow.model_validate(raw_wf)


def test_model_strategies_are_bound_to_registry() -> None:
    """Architectural Guardrail: All model_strategy references must exist in the SystemConfigModelRegistry."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # 1. Collect valid strategies from registry
    valid_strategies = set()
    for sys_cfg in data.get("system_config", []):
        if sys_cfg.get("type") == "model_registry" and "models" in sys_cfg:
            valid_strategies.update(sys_cfg["models"].keys())

    assert valid_strategies, "Model registry must contain at least one strategy"

    # 2. Check steps
    for raw_step in data.get("steps", []):
        strategy = raw_step.get("model_strategy")
        if strategy:
            assert strategy in valid_strategies, (
                f"Step '{raw_step.get('slug')}' references unknown model_strategy '{strategy}'"
            )

    # 3. Check output profiles
    if "output_profiles" in data:
        for raw_profile in data["output_profiles"]:
            synthesis = raw_profile.get("synthesis", {})
            strategy = synthesis.get("model_strategy")
            if strategy:
                assert strategy in valid_strategies, (
                    f"Profile '{raw_profile.get('id')}' references unknown model_strategy '{strategy}'"
                )

    # 4. Check embedded profiles in workflows
    if "workflows" in data:
        for raw_wf in data["workflows"]:
            profiles = raw_wf.get("output_profiles", {})
            for p_id, profile in profiles.items():
                synthesis = profile.get("synthesis", {})
                strategy = synthesis.get("model_strategy")
                if strategy:
                    assert strategy in valid_strategies, (
                        f"Workflow '{raw_wf.get('slug')}' profile '{p_id}' references unknown model_strategy '{strategy}'"
                    )
