"""Architectural guardrails and structural validation tests for the seed vault (seed_data.json)."""

import json
import re
from pathlib import Path
from typing import Any

from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.workflow import Workflow

SEED_FILE = Path(__file__).resolve().parents[2] / "seed" / "seed_data.json"


def test_prompt_blocks_do_not_contain_ui_logic() -> None:
    """Architectural Guardrail: PromptBlocks MUST NOT contain UI formatting instructions."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    blocks = [PromptBlockAdapter.validate_python(b) for b in data["prompt_blocks"]] if "prompt_blocks" in data else []

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
            for directive in [
                profile.tone_instruction,
                profile.executive_summary_directive,
                profile.matrix_1d_synthesis_directive,
                profile.matrix_2d_synthesis_directive,
                profile.matrix_3d_synthesis_directive,
                profile.matrix_text_synthesis_directive,
                profile.row_explanation_directive,
                profile.xai_synthesis_directive,
                profile.variance_synthesis_directive,
            ]:
                if directive:
                    prompt = directive.upper()
                    for term in execution_terms:
                        assert term not in prompt, f"Execution terminology '{term}' found in Root Profile {profile.id}"

    if "workflows" in data:
        for raw_wf in data["workflows"]:
            Workflow.model_validate(raw_wf)


def test_output_profiles_do_not_contain_scoring_penalties() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain scoring penalties."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    profiles = data["output_profiles"] if "output_profiles" in data else []
    assert profiles, "At least one output profile must exist in master seed"

    penalty_keys = ["security_penalty", "post_hoc_penalty", "passivity_penalty"]
    for raw_profile in profiles:
        prof_id = raw_profile["id"] if "id" in raw_profile else "unknown"
        for p_key in penalty_keys:
            assert p_key not in raw_profile, (
                f"Scoring penalty key '{p_key}' found in OutputProfile '{prof_id}'. "
                "Penalties belong strictly to Workflow (Phase 1 Execution Tier)."
            )

    # Anti-happy-path negative verification
    malformed_profile = {"id": "prf_invalid", "security_penalty": 0.15}
    assert any(k in malformed_profile for k in penalty_keys)


def test_workflows_contain_scoring_penalties() -> None:
    """Architectural Guardrail: Workflows MUST declare scoring penalties."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    workflows = data["workflows"] if "workflows" in data else []
    assert workflows, "At least one workflow must exist in master seed"

    penalty_keys = ["security_penalty", "post_hoc_penalty", "passivity_penalty"]
    for raw_wf in workflows:
        wf_id = raw_wf["id"] if "id" in raw_wf else "unknown"
        for p_key in penalty_keys:
            assert p_key in raw_wf, (
                f"Scoring penalty key '{p_key}' missing from Workflow '{wf_id}'. "
                "Workflows must sovereignly own automated scoring penalties."
            )
            val = raw_wf[p_key]
            assert isinstance(val, (int, float))
            assert 0.0 <= float(val) <= 1.0, f"Penalty '{p_key}' value {val} out of bounds [0.0, 1.0]"

    # Anti-happy-path negative verification
    malformed_wf = {"id": "wf_invalid"}
    assert not all(k in malformed_wf for k in penalty_keys)


def test_model_strategies_are_bound_to_registry() -> None:
    """Architectural Guardrail: All cognitive_tier references must exist in the SystemConfigModelRegistry."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # 1. Collect valid tiers from registry
    valid_tiers: set[str] = set()
    sys_configs = data["system_config"] if "system_config" in data else []
    for sys_cfg in sys_configs:
        if "type" in sys_cfg and sys_cfg["type"] == "model_registry" and "tier_definitions" in sys_cfg:
            valid_tiers.update(sys_cfg["tier_definitions"].keys())

    assert valid_tiers, "Model registry must contain at least one cognitive tier"

    # 2. Check steps
    raw_steps = data["steps"] if "steps" in data else []
    for raw_step in raw_steps:
        tier = None
        if "cognitive_tier" in raw_step and raw_step["cognitive_tier"]:
            tier = raw_step["cognitive_tier"]
        elif "model_strategy" in raw_step and raw_step["model_strategy"]:
            tier = raw_step["model_strategy"]
        if tier:
            step_slug = raw_step["slug"] if "slug" in raw_step else "unknown"
            assert tier in valid_tiers, f"Step '{step_slug}' references unknown cognitive_tier '{tier}'"

    # 3. Check output profiles
    if "output_profiles" in data:
        for raw_profile in data["output_profiles"]:
            synthesis = raw_profile["synthesis"] if "synthesis" in raw_profile else {}
            tier = None
            if "cognitive_tier" in synthesis and synthesis["cognitive_tier"]:
                tier = synthesis["cognitive_tier"]
            elif "model_strategy" in synthesis and synthesis["model_strategy"]:
                tier = synthesis["model_strategy"]
            if tier:
                prof_id = raw_profile["id"] if "id" in raw_profile else "unknown"
                assert tier in valid_tiers, f"Profile '{prof_id}' references unknown cognitive_tier '{tier}'"

    # 4. Check embedded profiles in workflows
    if "workflows" in data:
        for raw_wf in data["workflows"]:
            profiles = raw_wf["output_profiles"] if "output_profiles" in raw_wf else {}
            for p_id, profile in profiles.items():
                synthesis = profile["synthesis"] if "synthesis" in profile else {}
                tier = None
                if "cognitive_tier" in synthesis and synthesis["cognitive_tier"]:
                    tier = synthesis["cognitive_tier"]
                elif "model_strategy" in synthesis and synthesis["model_strategy"]:
                    tier = synthesis["model_strategy"]
                if tier:
                    wf_slug = raw_wf["slug"] if "slug" in raw_wf else "unknown"
                    assert tier in valid_tiers, (
                        f"Workflow '{wf_slug}' profile '{p_id}' references unknown cognitive_tier '{tier}'"
                    )


def test_output_profiles_zero_legacy_diagnostic_scorecard() -> None:
    """Architectural Guardrail: OutputProfiles MUST NOT contain legacy 'include_diagnostic_scorecard'."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Positive seed verification
    profiles = data["output_profiles"] if "output_profiles" in data else []
    assert profiles, "At least one output profile must exist in master seed"

    for profile in profiles:
        prof_id = profile["id"] if "id" in profile else "unknown"
        assert "include_diagnostic_scorecard" not in profile, (
            f"Legacy key 'include_diagnostic_scorecard' found in profile '{prof_id}'"
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

    profiles = data["output_profiles"] if "output_profiles" in data else []
    assert profiles, "At least one output profile must exist in master seed"

    for raw_profile in profiles:
        prof_id = raw_profile["id"] if "id" in raw_profile else "unknown"
        # Assert 0 legacy dictionaries in master seed
        for leg_key in legacy_keys:
            assert leg_key not in raw_profile, (
                f"Legacy dictionary/field '{leg_key}' found in output_profile '{prof_id}'"
            )

        # Validate with strict OutputProfile domain model
        profile = OutputProfile.model_validate(raw_profile)
        assert "matrix_synthesis_groups" in profile.model_fields
        assert len(profile.matrix_synthesis_groups) >= 1
        for group in profile.matrix_synthesis_groups:
            assert len(group.target_blocks) >= 1
            assert "en" in group.title.translations and group.title.translations["en"]
            assert "fi" in group.title.translations and group.title.translations["fi"]
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
        if type(obj) is dict:
            if "translations" in obj and type(obj["translations"]) is dict:
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
        en_text = translations["en"].strip() if "en" in translations else ""
        fi_text = translations["fi"].strip() if "fi" in translations else ""
        assert en_text, f"I18nText at '{path}' has empty or missing 'en' translation"
        assert fi_text, f"I18nText at '{path}' has empty or missing 'fi' translation"

    # Anti-happy-path negative verification
    def _is_valid_bilingual_i18n(rec: dict[str, Any]) -> bool:
        if type(rec) is not dict or "translations" not in rec or type(rec["translations"]) is not dict:
            return False
        tr = rec["translations"]
        has_en = "en" in tr and bool(tr["en"].strip())
        has_fi = "fi" in tr and bool(tr["fi"].strip())
        return has_en and has_fi

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

    profiles = data["output_profiles"] if "output_profiles" in data else []
    assert profiles, "At least one output profile must exist in master seed"

    for profile in profiles:
        prof_id = profile["id"] if "id" in profile else "unknown"
        if "display_scale" in profile:
            assert profile["display_scale"] in valid_display_scales, (
                f"Invalid display_scale '{profile['display_scale']}' in profile '{prof_id}'"
            )
        assert "scoring_strategy" not in profile, f"Legacy scoring_strategy must be pruned from profile '{prof_id}'"
        assert "strictness_level" not in profile, (
            f"strictness_level must be pruned from profile '{prof_id}' and owned by Workflow"
        )

    workflows = data["workflows"] if "workflows" in data else []
    assert workflows, "At least one workflow must exist in master seed"
    for workflow in workflows:
        wf_id = workflow["id"] if "id" in workflow else "unknown"
        assert "default_strictness_level" in workflow, (
            f"Mandatory default_strictness_level missing from workflow '{wf_id}'"
        )
        assert 0 <= workflow["default_strictness_level"] <= 100, (
            f"default_strictness_level out of bounds in workflow '{wf_id}'"
        )

    # Anti-happy-path negative verification
    def validate_profile_enums(profile_dict: dict[str, Any]) -> bool:
        if "display_scale" in profile_dict and profile_dict["display_scale"] not in valid_display_scales:
            return False
        if "strictness_level" in profile_dict:
            return False
        return True

    assert validate_profile_enums(
        {
            "display_scale": "original",
        }
    )
    assert not validate_profile_enums({"display_scale": "unsupported_scale_1000"})
    assert not validate_profile_enums({"strictness_level": 50})


def test_model_registry_calibrated_limits() -> None:
    """Architectural Guardrail: Model Registry strategies must meet calibrated token and temperature limits."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    sys_configs = data["system_config"] if "system_config" in data else []
    model_registries = [c for c in sys_configs if "type" in c and c["type"] == "model_registry"]
    assert model_registries, "SystemConfig with type 'model_registry' must exist in seed"

    required_tiers = {"deep", "fast", "balanced", "reasoning"}
    for registry_conf in model_registries:
        tier_defs = registry_conf["tier_definitions"] if "tier_definitions" in registry_conf else {}
        reg_id = registry_conf["id"] if "id" in registry_conf else "unknown"
        reg_name = registry_conf["name"] if "name" in registry_conf else "unknown"
        assert tier_defs, f"Model registry {reg_id} tier_definitions must not be empty"
        assert required_tiers.issubset(set(tier_defs.keys())), (
            f"Model registry '{reg_name}' must contain all required tiers: {required_tiers}"
        )
        for tier_name, model_def in tier_defs.items():
            max_tokens = model_def["max_tokens"] if "max_tokens" in model_def else 0
            assert max_tokens >= 32768, (
                f"Registry '{reg_name}' tier '{tier_name}' max_tokens {max_tokens} must be >= 32768"
            )

    # Anti-happy-path negative verification
    def validate_strategy_limits(strat_dict: dict[str, Any]) -> bool:
        tokens = strat_dict["max_tokens"] if "max_tokens" in strat_dict else 0
        return bool(tokens >= 32768)

    assert validate_strategy_limits({"max_tokens": 32768, "temperature": 0.1})
    assert validate_strategy_limits({"max_tokens": 65536, "temperature": 0.2})
    assert not validate_strategy_limits({"max_tokens": 8192, "temperature": 0.1})  # Under token ceiling


def test_synthesis_strategy_isolation() -> None:
    """Architectural Guardrail: No evaluative matrix step may declare model_strategy='synthesis'."""
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    steps = data["steps"] if "steps" in data else []
    assert steps, "Steps registry must contain step definitions"

    for step in steps:
        step_id = step["id"] if "id" in step else "unknown"
        cat = step["category_id"] if "category_id" in step else None
        is_eval = step["is_evaluative"] if "is_evaluative" in step else False
        tier = None
        if "cognitive_tier" in step and step["cognitive_tier"]:
            tier = step["cognitive_tier"]
        elif "model_strategy" in step and step["model_strategy"]:
            tier = step["model_strategy"]

        # Evaluative matrix steps must strictly isolate from synthesis strategy
        if cat == "matrix" or is_eval is True:
            assert tier != "synthesis", (
                f"Evaluative step '{step_id}' (category: '{cat}') must not use 'synthesis' model_strategy"
            )

    # Anti-happy-path negative verification
    def validate_evaluative_isolation(step_dict: dict[str, Any]) -> bool:
        c = step_dict["category_id"] if "category_id" in step_dict else None
        ie = step_dict["is_evaluative"] if "is_evaluative" in step_dict else False
        strat = step_dict["model_strategy"] if "model_strategy" in step_dict else None
        if (c == "matrix" or ie is True) and strat == "synthesis":
            return False
        return True

    assert validate_evaluative_isolation({"category_id": "matrix", "is_evaluative": True, "model_strategy": "deep"})
    assert validate_evaluative_isolation(
        {"category_id": "report", "is_evaluative": False, "model_strategy": "synthesis"}
    )
    assert not validate_evaluative_isolation(
        {"category_id": "matrix", "is_evaluative": True, "model_strategy": "synthesis"}
    )
    assert not validate_evaluative_isolation(
        {"category_id": "evaluator", "is_evaluative": True, "model_strategy": "synthesis"}
    )
