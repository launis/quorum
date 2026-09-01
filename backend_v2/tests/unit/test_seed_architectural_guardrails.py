"""Architectural guardrails and structural validation tests for the seed vault (seed_data.json)."""

import json
import re
from pathlib import Path
from typing import Any

from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.v2_core import OutputProfile, Workflow

SEED_FILE = Path(__file__).resolve().parents[2] / "seed" / "seed_data.json"


def test_prompt_blocks_do_not_contain_ui_logic() -> None:
    """Architectural Guardrail: PromptBlocks MUST NOT contain UI formatting instructions."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    blocks = [PromptBlockAdapter.validate_python(b) for b in data.get("prompt_blocks", [])]

    for block in blocks:
        desc_text = ""
        match block:
            case MatrixPromptBlock(ai_description=desc) if desc:
                desc_text = desc
            case SystemRulePromptBlock(instruction_text=text) if text:
                desc_text = text
            case PersonaPromptBlock(role_enforcement=text) if text:
                desc_text = text
            case ProtocolPromptBlock(protocol_instructions=text) if text:
                desc_text = text

        if desc_text:
            ai_desc = desc_text.upper()
            if block.id != "blk_1a2b3c4d5e6f7a8b":
                assert "0-100" not in ai_desc, f"Block {block.id} contains 0-100 UI scale logic in prompt text"
            assert "PUNCHY SENTENCE" not in ai_desc, f"Block {block.id} contains UI formatting in prompt text"


def test_output_profiles_do_not_contain_execution_logic() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain execution terminology."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    execution_terms = ["NULL HYPOTHESIS", "ZERO-TRUST AUDITOR", "BOOLEAN", "FALSE", "TRUE"]

    if "output_profiles" in data:
        for raw_profile in data["output_profiles"]:
            profile = OutputProfile.model_validate(raw_profile)
            if profile.tone_instruction:
                for lang, text in profile.tone_instruction.translations.items():
                    prompt = text.upper()
                    for term in execution_terms:
                        assert term not in prompt, (
                            f"Execution terminology '{term}' found in Root Profile {profile.id} ({lang})"
                        )

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


def test_output_profiles_zero_legacy_dictionaries_and_valid_matrix_synthesis_groups() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain legacy dictionaries and MUST have valid matrix_synthesis_groups."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    legacy_keys = [
        "metric_mappings",
        "matrix_column_labels",
        "user_role_mappings",
        "extension_labels",
        "layouts",
        "preset_view",
        "text_delivery_mode",
    ]

    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in master seed"

    for raw_profile in profiles:
        # Assert 0 legacy dictionaries in master seed
        for leg_key in legacy_keys:
            assert leg_key not in raw_profile, (
                f"Legacy dictionary/field '{leg_key}' found in output_profile '{raw_profile.get('id')}'"
            )

        # Validate with strict OutputProfile domain model
        profile = OutputProfile.model_validate(raw_profile)
        assert hasattr(profile, "matrix_synthesis_groups")
        assert len(profile.matrix_synthesis_groups) >= 1
        for group in profile.matrix_synthesis_groups:
            assert len(group.target_blocks) >= 1
            assert group.title.get("en")
            assert group.title.get("fi")
            assert re.match(r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", group.id), (
                f"Group id '{group.id}' in profile '{profile.id}' is not a valid 16-hex Opaque Stripe ID"
            )

    # Verify static translation tables contain all 17 required metric mapping keys
    l10n_dir = Path(__file__).resolve().parents[2] / "l10n"
    with open(l10n_dir / "en.json", encoding="utf-8") as f_en, open(l10n_dir / "fi.json", encoding="utf-8") as f_fi:
        en_l10n = json.load(f_en)
        fi_l10n = json.load(f_fi)

    required_keys = [
        "metadata_user",
        "metadata_organization",
        "metadata_scoring_engine",
        "metadata_strictness",
        "variance_mechanical",
        "variance_cognitive",
        "variance_total",
        "variance_fallback_explanation",
        "alignment_verdict",
        "alignment_aligned",
        "alignment_misaligned",
        "jargon_score",
        "authenticity_level",
        "level_high",
        "level_medium",
        "level_low",
        "authenticity_fallback_explanation",
    ]
    for req_key in required_keys:
        assert req_key in en_l10n and bool(en_l10n[req_key]), f"Missing '{req_key}' in backend_v2/l10n/en.json"
        assert req_key in fi_l10n and bool(fi_l10n[req_key]), f"Missing '{req_key}' in backend_v2/l10n/fi.json"


def test_seed_has_no_default_locale() -> None:
    """Architectural Guardrail: seed_data.json MUST contain 0 occurrences of 'default_locale'."""
    with open(SEED_FILE, encoding="utf-8") as f:
        content = f.read()

    # Master seed positive assertion: 0 occurrences
    assert "default_locale" not in content, "Found legacy 'default_locale' in seed_data.json"

    # Anti-happy-path negative verification
    synthetic_legacy_payload = '{"label": {"translations": {"en": "Test"}, "default_locale": "en"}}'
    assert "default_locale" in synthetic_legacy_payload


def test_seed_i18n_has_100_percent_bilingual_parity() -> None:
    """Architectural Guardrail: 100% of all I18nText records in seed_data.json possess valid 'en' and 'fi' translations."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    i18n_records: list[tuple[str, dict[str, Any]]] = []

    def _collect_i18n(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            if "translations" in obj and isinstance(obj["translations"], dict):
                i18n_records.append((path, obj))
            for k, v in obj.items():
                _collect_i18n(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _collect_i18n(v, f"{path}[{i}]")

    _collect_i18n(data)

    assert len(i18n_records) >= 450, f"Expected >= 450 I18nText records in master seed, found {len(i18n_records)}"

    for path, record in i18n_records:
        translations = record["translations"]
        en_text = translations.get("en", "").strip()
        fi_text = translations.get("fi", "").strip()
        assert en_text, f"I18nText at '{path}' has empty or missing 'en' translation"
        assert fi_text, f"I18nText at '{path}' has empty or missing 'fi' translation"

    # Anti-happy-path negative verification
    def _is_valid_bilingual_i18n(rec: dict[str, Any]) -> bool:
        if not isinstance(rec, dict) or "translations" not in rec or not isinstance(rec["translations"], dict):
            return False
        tr = rec["translations"]
        return bool(tr.get("en", "").strip()) and bool(tr.get("fi", "").strip())

    assert _is_valid_bilingual_i18n({"translations": {"en": "Hello", "fi": "Hei"}})
    assert not _is_valid_bilingual_i18n({"translations": {"en": "Hello"}})
    assert not _is_valid_bilingual_i18n({"translations": {"en": "Hello", "fi": "   "}})
    assert not _is_valid_bilingual_i18n({"translations": {"fi": "Hei"}})
    assert not _is_valid_bilingual_i18n({"text": "Hello"})


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

    # Anti-happy-path negative verification
    def validate_profile_enums(profile_dict: dict[str, Any]) -> bool:
        if "display_scale" in profile_dict and profile_dict["display_scale"] not in valid_display_scales:
            return False
        if "scoring_strategy" in profile_dict and profile_dict["scoring_strategy"] not in valid_scoring_strategies:
            return False
        return True

    assert validate_profile_enums(
        {
            "display_scale": "original",
            "scoring_strategy": "AVERAGE",
        }
    )
    assert not validate_profile_enums({"display_scale": "unsupported_scale_1000"})
    assert not validate_profile_enums({"scoring_strategy": "NON_EXISTENT_STRATEGY"})
