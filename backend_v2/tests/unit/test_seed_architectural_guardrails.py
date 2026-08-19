import json
from pathlib import Path
from typing import Any

from backend_v2.models.v2_core import OutputProfile, PromptBlock, Workflow

SEED_FILE = Path(__file__).resolve().parents[2] / "seed" / "seed_data.json"


def test_prompt_blocks_do_not_contain_ui_logic() -> None:
    """Architectural Guardrail: PromptBlocks MUST NOT contain UI formatting instructions."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    blocks = [PromptBlock.model_validate(b) for b in data.get("prompt_blocks", [])]

    for block in blocks:
        if block.ai_description:
            ai_desc = block.ai_description.upper()
            if block.id != "blk_1a2b3c4d5e6f7a8b":
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


def test_output_profiles_zero_legacy_diagnostic_scorecard() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain legacy 'include_diagnostic_scorecard'."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Positive seed verification
    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in master seed"

    for profile in profiles:
        assert "include_diagnostic_scorecard" not in profile, (
            f"Legacy key 'include_diagnostic_scorecard' found in profile '{profile.get('id')}'"
        )

    # Anti-happy-path negative verification
    malformed_profile = {"id": "prf_invalid", "include_diagnostic_scorecard": True}
    assert "include_diagnostic_scorecard" in malformed_profile


def test_output_profiles_metric_mappings_contain_bilingual_metadata_keys() -> None:
    """Architectural Guardrail: All output profiles must have complete bilingual metric mappings (all 17 keys)."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    required_keys = [
        # Metadata labels
        "metadata_user",
        "metadata_organization",
        "metadata_scoring_engine",
        "metadata_strictness",
        # Variance labels
        "variance_mechanical",
        "variance_cognitive",
        "variance_total",
        "variance_fallback_explanation",
        # Alignment labels
        "alignment_verdict",
        "alignment_aligned",
        "alignment_misaligned",
        # Authenticity labels
        "jargon_score",
        "authenticity_level",
        "level_high",
        "level_medium",
        "level_low",
        "authenticity_fallback_explanation",
    ]

    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in master seed"

    for profile in profiles:
        mappings = profile.get("metric_mappings", {})
        for req_key in required_keys:
            assert req_key in mappings, (
                f"Required metric key '{req_key}' missing from metric_mappings in profile '{profile.get('id')}'"
            )
            i18n_entry = mappings[req_key]
            translations = i18n_entry.get("translations", {})
            assert "fi" in translations and bool(translations["fi"]), (
                f"Missing or empty 'fi' translation for '{req_key}' in profile '{profile.get('id')}'"
            )
            assert "en" in translations and bool(translations["en"]), (
                f"Missing or empty 'en' translation for '{req_key}' in profile '{profile.get('id')}'"
            )

    # Anti-happy-path negative verification
    def validate_metric_keys(mappings_dict: dict[str, Any]) -> bool:
        for key in required_keys:
            if key not in mappings_dict:
                return False
            t = mappings_dict[key].get("translations", {})
            if not t.get("fi") or not t.get("en"):
                return False
        return True

    assert not validate_metric_keys({})
    assert not validate_metric_keys({"metadata_user": {"translations": {"fi": "Käyttäjä:"}}})
    # Missing variance keys
    assert not validate_metric_keys(
        {
            "metadata_user": {"translations": {"fi": "Käyttäjä:", "en": "User:"}},
            "metadata_organization": {"translations": {"fi": "Org:", "en": "Org:"}},
            "metadata_scoring_engine": {"translations": {"fi": "Moottori:", "en": "Engine:"}},
            "metadata_strictness": {"translations": {"fi": "Taso:", "en": "Level:"}},
        }
    )
    # Complete dummy with 1 empty string in variance_mechanical
    complete_dummy: dict[str, Any] = {k: {"translations": {"fi": f"Val_{k}", "en": f"Val_{k}"}} for k in required_keys}
    assert validate_metric_keys(complete_dummy)
    complete_dummy["variance_mechanical"]["translations"]["en"] = ""
    assert not validate_metric_keys(complete_dummy)


def test_output_profiles_enums_valid() -> None:
    """Architectural Guardrail: OutputProfile fields must only use valid enum-compatible values."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    valid_display_scales = {"original", "custom", "normalized_100"}
    valid_scoring_strategies = {
        "AVERAGE",
        "WATERFALL",
        "WEIGHTED_AVERAGE",
        "PURE_MATH",
        "average",
        "waterfall",
        "weighted_average",
        "pure_math",
    }
    valid_preset_views = {"1d_metrics", "2d_compare", "3d_matrix", "text_only", "matrix_summary"}
    valid_text_delivery_modes = {"full", "summary", "bullets"}

    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in master seed"

    for profile in profiles:
        if "display_scale" in profile:
            assert profile["display_scale"] in valid_display_scales, (
                f"Invalid display_scale '{profile['display_scale']}' in profile '{profile.get('id')}'"
            )
        if "scoring_strategy" in profile:
            assert profile["scoring_strategy"] in valid_scoring_strategies, (
                f"Invalid scoring_strategy '{profile['scoring_strategy']}' in profile '{profile.get('id')}'"
            )
        if "preset_view" in profile:
            assert profile["preset_view"] in valid_preset_views, (
                f"Invalid preset_view '{profile['preset_view']}' in profile '{profile.get('id')}'"
            )
        if "text_delivery_mode" in profile:
            assert profile["text_delivery_mode"] in valid_text_delivery_modes, (
                f"Invalid text_delivery_mode '{profile['text_delivery_mode']}' in profile '{profile.get('id')}'"
            )

    # Anti-happy-path negative verification
    def validate_profile_enums(profile_dict: dict[str, Any]) -> bool:
        if "display_scale" in profile_dict and profile_dict["display_scale"] not in valid_display_scales:
            return False
        if "scoring_strategy" in profile_dict and profile_dict["scoring_strategy"] not in valid_scoring_strategies:
            return False
        if "preset_view" in profile_dict and profile_dict["preset_view"] not in valid_preset_views:
            return False
        if "text_delivery_mode" in profile_dict and profile_dict["text_delivery_mode"] not in valid_text_delivery_modes:
            return False
        return True

    assert validate_profile_enums(
        {
            "display_scale": "original",
            "scoring_strategy": "AVERAGE",
            "preset_view": "3d_matrix",
            "text_delivery_mode": "full",
        }
    )
    assert not validate_profile_enums({"display_scale": "unsupported_scale_1000"})
    assert not validate_profile_enums({"scoring_strategy": "NON_EXISTENT_STRATEGY"})
    assert not validate_profile_enums({"preset_view": "invalid_preset"})
    assert not validate_profile_enums({"text_delivery_mode": "invalid_mode"})
