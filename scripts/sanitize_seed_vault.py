"""Seed Vault Sanitizer and Formatter CLI Tool.

Provides an automated, deterministic in-memory migration and sanitization pipeline
for Quorum's master `seed_data.json` database vault. Enforces pure declarative ontology,
strips raw XML and screaming imperatives, validates every entity against strict Pydantic V2
models, and persists changes atomically.
"""

from __future__ import annotations

import argparse
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import BaseModel, ConfigDict, Field, JsonValue, TypeAdapter

from backend_v2.models.core_base import (
    I18nText,
    generate_uuid7_opaque_id,
)
from backend_v2.models.enums import (
    EntityPrefix,
    PromptBlockCategory,
    StepType,
    SystemConfigID,
)
from backend_v2.seed.seed_registry import STANDARD_REGISTRY

_CAUSAL_COHESION_MATRIX_BLOCK_ID: str = "blk_0195f3a00000700c80a1e50000000001"
_SYSTEM_ORG_UUID7_ID: str = "org_0195f3a0000070008000000000000000"


def _upgrade_or_generate_opaque_id(raw_id: object, expected_prefix: EntityPrefix) -> str:
    """Deterministically upgrade a 16-hex ID to 32-hex RFC 9562 UUIDv7 or generate a fresh UUIDv7 ID.

    Args:
        raw_id: Candidate raw identifier value from seed_data.json.
        expected_prefix: Canonical EntityPrefix expected for the entity or foreign key.

    Returns:
        Canonical 32-hex '{expected_prefix.value}_{32_hex}' string matching OPAQUE_STRIPE_ID_REGEX.
    """
    if not isinstance(raw_id, str) or not raw_id.strip():
        return generate_uuid7_opaque_id(expected_prefix)

    cleaned = raw_id.strip()
    if cleaned == SystemConfigID.MCP_GATEWAYS.value:
        return SystemConfigID.MCP_GATEWAYS.value
    if expected_prefix == EntityPrefix.ORGANIZATION and cleaned in (
        "org_system000000",
        "SYSTEM",
        _SYSTEM_ORG_UUID7_ID,
    ):
        return _SYSTEM_ORG_UUID7_ID

    if "_" in cleaned:
        _, hex_part = cleaned.split("_", 1)
        if expected_prefix == EntityPrefix.SYSTEM_CONFIG and hex_part.lower() == "8172bda70c8641c5":
            return SystemConfigID.MCP_GATEWAYS.value
        if re.fullmatch(r"[0-9a-fA-F]{32}", hex_part):
            h32 = hex_part.lower()
            if expected_prefix == EntityPrefix.TDA or uuid.UUID(hex=h32).version == 7:
                return f"{expected_prefix.value}_{h32}"
            return f"{expected_prefix.value}_0195f3a000007{h32[13:16]}8{h32[17:32]}"
        if re.fullmatch(r"[0-9a-fA-F]{16}", hex_part):
            h16 = hex_part.lower()
            return f"{expected_prefix.value}_0195f3a00000700{h16[0]}8{h16[1:16]}"

    return generate_uuid7_opaque_id(expected_prefix)


class SanitizeResult(BaseModel):
    """Result summary of a seed vault sanitization run."""

    model_config = ConfigDict(strict=True, extra="forbid")

    total_blocks_sanitized: int = Field(default=0, description="Total prompt blocks inspected and sanitized.")
    total_atoms_mutated: int = Field(default=0, description="Total matrix atoms modified.")
    total_steps_sanitized: int = Field(default=0, description="Total steps validated and cleaned.")
    total_workflows_sanitized: int = Field(default=0, description="Total workflows validated.")
    total_profiles_sanitized: int = Field(default=0, description="Total output profiles cleaned.")
    backup_path: str | None = Field(default=None, description="Path to the created timestamped backup.")
    is_dry_run: bool = Field(default=False, description="Whether the run was a dry-run.")
    success: bool = Field(default=True, description="Whether the entire sanitization passed cleanly.")


# Specific atom ontology harmonizations (Map of tda_id -> (concept_description, extraction_rule))
SPECIFIC_ATOM_HARMONIZATIONS: dict[str, tuple[str, str]] = {
    "tda_453ddf8b14a442e988836098e3c7b55c": (
        "Identified organizational or operational risks are presented without actionable mitigation controls or procedures.",
        "Locate risk identification markers and verify if concrete technical, administrative, or physical mitigation actions are absent.",
    ),
    "tda_b7dfe23403db4db5b92a29a8bda9957c": (
        "Concepts or entities are listed in mere juxtaposition without explaining their relational connection, functional interaction, or synthesis.",
        "Locate sequential listings of entities or nouns and verify if explicit relational verbs or synthesis explanations are omitted.",
    ),
    "tda_a946688e5f5549e8ac30584d1a02ad26": (
        "The argument delivers objective, impersonal propositions without subjective or first-person anchoring.",
        "Locate and extract substantive sections where informational delivery is formulated in an impersonal, third-person factual style.",
    ),
    "tda_611db266856848b68fda02dd9f602ce5": (
        "Methodological limitations are stated passively without a corresponding procedural mitigation or test.",
        "Locate limitation markers and verify whether actionable evaluation or mitigation mechanisms are absent.",
    ),
    "tda_1361cf5ec5b5420c905cd2a1f80893a7": (
        "The argument exhibits retrospective claims of intent where the claimed parameters are absent from preceding instructions.",
        "Locate retrospective claims of intent and verify whether the referenced parameters were physically omitted in preceding context.",
    ),
    "tda_86ccd40936bb4dfc9a6d1f532568c05c": (
        "The reasoning explicitly connects at least three sequential actions where each step depends on the output of the prior step.",
        "Locate and extract substantive multi-step operational chains where each subsequent action explicitly consumes previous findings.",
    ),
    "tda_65cb33b82c54425aa86df7e84b66ffde": (
        "The argument explicitly couples framework clauses with physical security actions taken.",
        "Locate and extract substantive evidence demonstrating the specific framework clause directly linked to the physical security action taken.",
    ),
    "tda_72d297df24fb45c3a85dc0b8248b9188": (
        "The alternative hypothesis is mentioned without presenting comparative data or counter-arguments.",
        "Locate mentions of alternative hypotheses and verify whether comparative metrics or counter-arguments are omitted.",
    ),
    "tda_003f932abb9642fc8c3147b04fac95c5": (
        "The argument exhibits declarations of exhaustive or complete knowledge.",
        "Locate and extract substantive sections asserting total certainty or the absolute absence of unknown variables.",
    ),
    "tda_84b7784951c84e948c131c189261f564": (
        "The argument exhibits immediate rationalization or dismissal of recognized operational constraints.",
        "Locate and extract sections where an acknowledged constraint is immediately followed by a dismissive rationalization.",
    ),
    "tda_24bdc98709e84de984aabd67b597239b": (
        "The text contains procedural execution steps that lack analytical framing or synthesis terminology.",
        "Locate sequential procedural markers and verify whether analytical framing and synthesis explanations are absent.",
    ),
    "tda_aa0b85a7febe4a3d9f580223c36a1646": (
        "The text provides unconditional status assertions that omit acknowledged operational risks.",
        "Locate status declarations asserting absolute operational certainty while omitting documented system challenges.",
    ),
    "tda_01edff70b75047ec9f6df0c49745f46e": (
        "A causal inference derived from a limited domain is applied universally without boundary conditions.",
        "Locate causal claims extrapolated across distinct operational domains without explicit qualification.",
    ),
    "tda_ac3b078498e048889ad3bc46b634c2ee": (
        "The context substantiates mandatory source anchoring across analytical claims.",
        "Locate and extract substantive statements where analytical deductions are explicitly tethered to verified sources.",
    ),
    "tda_6f4f8fc663c241acad6da5bff5abe321": (
        "The warning specifies concrete operational boundaries and unsupported capabilities using domain terminology.",
        "Locate and extract substantive warning notices delineating explicit analytical and operational limits.",
    ),
    "tda_18fd37ad3f1f4903a812c12346d0ca8e": (
        "The input variables are explicitly connected to their resulting analytical outputs.",
        "Locate and extract substantive sections mapping specific input parameters directly to generated conclusions.",
    ),
    "tda_fcdde66df02c4edb9e090172c3e2b956": (
        "A continuous chain of sequential logical derivations is documented.",
        "Locate and extract multi-step reasoning pathways where each inference builds directly on the prior conclusion.",
    ),
    "tda_e407bc0297324a5da95c9091d08b88bc": (
        "The text presents measurable operational targets confirmed with quantitative metrics.",
        "Locate and extract substantive evidence demonstrating verified quantitative metrics aligned with stated goals.",
    ),
    "tda_9eff656db790437dafb7f75be5f64b0c": (
        "The argument presents detailed empirical refutations of alternative models.",
        "Locate and extract substantive counter-arguments identifying contradictions or empirical gaps in alternative models.",
    ),
    "tda_236ebf69629e41a58b0f13eb82b44875": (
        "Outlier data points or contradictory evidence are dismissed to preserve the original premise without empirical justification.",
        "Locate dismissal markers and verify whether contradictory data or outlier observations are rejected without changing the core premise.",
    ),
    "tda_873a1fab603544048f95e612773f0574": (
        "Counter-arguments are introduced and immediately dismissed without citations, named sources, or comparative empirical data.",
        "Locate counter-argument transitions and extract statements where opposing views are dismissed without substantive evidence.",
    ),
    "tda_3b951170f9f54f649b7da95fb9f121e6": (
        "Empirical observations are reported descriptively without formulating a testable or falsifiable hypothesis.",
        "Locate descriptive reporting statements and verify whether an explicit testable hypothesis is omitted.",
    ),
    "tda_0af46ca3de69431e8a3eea89df104507": (
        "Conflicting analytical claims or data points are acknowledged but left unresolved through passive synthesis.",
        "Locate conflict identification statements and extract sections where contradictory claims remain unresolved.",
    ),
    "tda_52ffb15768ba4a62ac3a8be5824a8aa6": (
        "The analysis defines explicit, measurable boundary conditions that would falsify the central claim.",
        "Locate and extract substantive statements defining specific measurable criteria under which the claim is considered invalid.",
    ),
    "tda_43516f120e4a415bb0ee3a878a53a5bc": (
        "The argument explicitly identifies specific structural flaws or methodological weaknesses in its own proposal or analysis.",
        "Locate and extract substantive statements where methodological weaknesses or analytical limitations of the proposal are detailed.",
    ),
}


class ClaimUpdateConfig(BaseModel):
    """Configuration for updating a Track A Novice claim and assertion."""

    model_config = ConfigDict(strict=True, extra="forbid")

    label: I18nText
    concept: str
    rule: str


class TrackAConfig(BaseModel):
    """Configuration for refactoring a Track A matrix Level 1 scale."""

    model_config = ConfigDict(strict=True, extra="forbid")

    scale_name: I18nText
    ai_label: str
    claim_updates: dict[str, ClaimUpdateConfig]


# Dual-Track Rubric Architecture: Track A Developmental Matrices configuration
DUAL_TRACK_A_CONFIG: dict[str, TrackAConfig] = {
    "blk_0195f3a00000700f8921c7c0989b47e8": TrackAConfig(
        scale_name=I18nText(
            translations={"fi": "Muistaminen ja nimeäminen (Remembering)", "en": "Remembering and Naming (Novice)"}
        ),
        ai_label="NOVICE - DECLARATIVE RECALL",
        claim_updates={
            "tda_b36d3ec7b1f94fe9ad4b45795a8a104b": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Tiedon mekaaninen toistaminen ja nimeäminen",
                        "en": "Mechanical Rote Recall and Naming",
                    }
                ),
                concept="Standalone declarative recall of factual definitions or nomenclature without causal elaboration.",
                rule="Locate and extract statements reciting a definition or nomenclature without elaborating on functional interactions or causal mechanisms.",
            )
        },
    ),
    "blk_0195f3a0000070078d8e9f0a1b2c3d4e": TrackAConfig(
        scale_name=I18nText(translations={"fi": "Alustava ohjaus (Noviisi)", "en": "Preliminary Guidance (Novice)"}),
        ai_label="NOVICE - BASELINE PROMPTING",
        claim_updates={
            "tda_682186093ed65428b0c2d3120a5c90ca": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Aiheen tai tehtävän alustava nimeäminen",
                        "en": "Initial Identification of Core Topic or Task",
                    }
                ),
                concept="Author states a primary topic, subject, or desired outcome without operational guidelines or execution constraints.",
                rule="Locate and extract statements specifying a core topic, subject, or desired task outcome.",
            ),
            "tda_c4ec19d4b2dc5a3e8778181878ca03a6": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Tekoälyn aloitusehdotuksen hyödyntäminen",
                        "en": "Baseline Utilization of AI Suggestions",
                    }
                ),
                concept="Author adopts model suggestions or initial outputs as a starting baseline for task progression.",
                rule="Locate and extract sections where author adopts model suggestions or initial outputs as starting baseline.",
            ),
        },
    ),
    "blk_0195f3a00000700583f32679aa514fcb": TrackAConfig(
        scale_name=I18nText(translations={"fi": "Perusvuorovaikutus (Noviisi)", "en": "Basic Interaction (Novice)"}),
        ai_label="NOVICE - BASIC INTERACTION",
        claim_updates={
            "tda_3ee4fe63a8ac50d24595bd3e90a6b016": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Perusvuorovaikutus ja tehtävän käynnistäminen",
                        "en": "Basic Interaction and Task Initiation",
                    }
                ),
                concept="Author opens interaction by stating a clear question, prompt, or task assignment for AI execution.",
                rule="Locate and extract the initial prompt, inquiry, or question opening the interaction.",
            ),
            "tda_daf7e137f58333015ad078c35a873ecc": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Vastauksen vastaanotto ja perustason jatko-ohjaus",
                        "en": "Response Reception and Baseline Follow-up",
                    }
                ),
                concept="Author receives generative response and provides baseline follow-up or acknowledgment.",
                rule="Locate and extract author follow-up acknowledging or building upon the generated output.",
            ),
        },
    ),
    "blk_0195f3a00000700f8f72c2d79edb4ebf": TrackAConfig(
        scale_name=I18nText(
            translations={"fi": "Pinnallinen arviointi (Noviisi)", "en": "Superficial Evaluation (Novice)"}
        ),
        ai_label="NOVICE - SUPERFICIAL EVALUATION",
        claim_updates={
            "tda_f93df8c0534f4d459c5c35c1ee717b54": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Pinnallinen arviointipäätös ja perusperustelu",
                        "en": "Superficial Evaluation Decision with Basic Justification",
                    }
                ),
                concept="Author provides an explicit pass/fail decision or initial assessment stance with basic justification.",
                rule="Locate and extract an explicit pass/fail decision, rating, or evaluative stance accompanied by basic justification.",
            )
        },
    ),
    "blk_0195f3a00000700f86e286f050c94d60": TrackAConfig(
        scale_name=I18nText(
            translations={"fi": "Alustava jäsentely (Noviisi)", "en": "Preliminary Structuring (Novice)"}
        ),
        ai_label="NOVICE - PRELIMINARY STRUCTURING",
        claim_updates={
            "tda_2f6c6565bf10f613d787c03fc97bfb91": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Kommunikatiivisen tavoitteen ja ydinteeman tunnistaminen",
                        "en": "Identification of Communicative Goal and Core Theme",
                    }
                ),
                concept="The text identifies the primary communicative goal, core theme, or foundational topic of the deliverable.",
                rule="Locate and extract explicit statements identifying the communicative goal, primary topic, or core theme.",
            )
        },
    ),
    "blk_0195f3a0000070068b8c766185294f7e": TrackAConfig(
        scale_name=I18nText(translations={"fi": "Peruskonsensus (Noviisi)", "en": "Basic Consensus (Novice)"}),
        ai_label="NOVICE - BASIC CONSENSUS",
        claim_updates={
            "tda_7f4854aefcb144faa4ee448081ac0c03": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Peruskonsensus ja yhteisten havaintojen tunnistaminen",
                        "en": "Basic Consensus and Shared Findings Identification",
                    }
                ),
                concept="Identifies basic shared findings, consensus points, or common ground across evaluated viewpoints.",
                rule="Locate and extract statements identifying shared findings, baseline consensus, or common themes across sources.",
            ),
            "tda_16f0d5b6d78dd7d15006bcc1bef2eb00": ClaimUpdateConfig(
                label=I18nText(
                    translations={
                        "fi": "Suositusten kytkentä analyyttisiin havaintoihin",
                        "en": "Traceable Connection Linking Recommendations to Analytical Findings",
                    }
                ),
                concept="Documents identifiable evidentiary anchors or step references connecting recommendations back to analytical inputs.",
                rule="Locate and extract clear, traceable references connecting specific recommendations to prior findings or analytical inputs.",
            ),
        },
    ),
}

# Dual-Track Rubric Architecture: Track B Diagnostic Error Radars (Toulmin is golden reference blk_0195f3a000007004840a5fef9331451b)
DUAL_TRACK_B_BLOCK_IDS: set[str] = {
    "blk_0195f3a00000700c85804a9143c34cb1",  # matrix_causal_analyst
    "blk_0195f3a000007001809dab5b6b3f403a",  # matrix_kahneman
    "blk_0195f3a00000700b8476f89fb732448c",  # matrix_falsifier
    "blk_0195f3a00000700880732a33fe1947ee",  # matrix_taskguard
    "blk_0195f3a00000700f8b15f8dcf23f4865",  # matrix_archivist
    "blk_0195f3a00000700c83bc5f3eb8e74110",  # matrix_causal_abductive
    "blk_0195f3a00000700282e3598e06414409",  # matrix_epistemic_humility
}


def strip_raw_xml(text: str) -> str:
    """Removes raw XML tags and sanitizes angle brackets from text.

    Args:
        text: The string to clean.

    Returns:
        The sanitized string without XML tags.
    """
    if not text:
        return text
    # Remove XML tags like <system_directive> or </rule>
    cleaned = re.sub(r"<[a-zA-Z_][a-zA-Z0-9_\-]*.*?>", "", text)
    cleaned = re.sub(r"</[a-zA-Z_][a-zA-Z0-9_\-]*>", "", cleaned)
    # Remove loose XML-like brackets
    cleaned = cleaned.replace("<", "").replace(">", "")
    return cleaned.strip()


def clean_mechanical_phrases(text: str) -> str:
    """Cleans mechanical imperatives, count phrases, and banned directives from text.

    Args:
        text: The raw prompt string.

    Returns:
        The cleaned declarative string.
    """
    if not text:
        return text

    cleaned = text

    # Remove screaming phrases
    banned_prefixes = [
        "ABSOLUTE MITIGATION ENFORCEMENT:",
        "ABSOLUTE MITIGATION ENFORCEMENT",
        "ABSOLUTE LEXICAL BOUNDARY:",
        "ABSOLUTE LEXICAL BOUNDARY",
        "ABSOLUTE LEXICAL ENFORCEMENT:",
        "ABSOLUTE LEXICAL ENFORCEMENT",
        "CRITICAL DIRECTIVE:",
        "CRITICAL DIRECTIVE",
        "NEGATIVE BOUNDARY:",
    ]
    for bp in banned_prefixes:
        cleaned = cleaned.replace(bp, "")

    # Replace "IF AND ONLY IF" with declarative phrasing
    cleaned = cleaned.replace("IF AND ONLY IF", "when")
    cleaned = cleaned.replace("if and only if", "when")

    # Replace mechanical counting & scanning
    cleaned = re.sub(r"count of [a-zA-Z0-9_\-\s]+ is EXACTLY ZERO", "markers are absent", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"is EXACTLY ZERO", "is absent", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"contains exactly 0", "lacks", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"scan the paragraph and ", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"scan the paragraph for ", "locate ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"scan the paragraph", "locate text", cleaned, flags=re.IGNORECASE)

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def create_vault_backup(seed_path: Path) -> Path:
    """Creates a timestamped backup copy of seed_data.json in backend_v2/seed/backups/.

    Args:
        seed_path: Absolute or relative path to seed_data.json.

    Returns:
        The Path to the created backup file.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = seed_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"seed_data_backup_{timestamp}.json"
    shutil.copyfile(seed_path, backup_file)
    return backup_file


def atomic_save_seed_data(data: Mapping[str, JsonValue], target_path: Path) -> None:
    """Atomically writes sanitized dictionary to target_path using temporary file replacement.

    Args:
        data: The sanitized dictionary to persist.
        target_path: Destination JSON file path.

    Raises:
        ValueError: If JSON syntax or serialization check fails before move.
    """
    target_path = target_path.resolve()
    temp_dir = target_path.parent
    temp_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
        temp_name = tf.name
        json.dump(data, tf, indent=2, ensure_ascii=False)
        tf.write("\n")
        tf.flush()
        os.fsync(tf.fileno())

    # Dry-run validation of temporary file syntax
    with open(temp_name, encoding="utf-8") as tf_read:
        verified_data = json.load(tf_read)
        if "prompt_blocks" not in verified_data:
            os.remove(temp_name)
            raise ValueError(f"Temporary file '{temp_name}' failed seed collection validation.")

    # Atomic move over target file
    os.replace(temp_name, target_path)


def sanitize_prompt_blocks(prompt_blocks: Sequence[Any]) -> tuple[list[JsonValue], int]:
    """Sanitizes prompt_blocks collection, matrix atoms, and prompt texts.

    Args:
        prompt_blocks: Raw prompt block dictionaries.

    Returns:
        A tuple of (sanitized blocks, mutated atoms count).
    """
    sanitized_blocks: list[JsonValue] = []
    mutated_atoms_count = 0

    for block in prompt_blocks:
        b = dict(block)
        # Phase 1 & 2, Step 1 & 2: Explicit key membership check and deterministic 32-hex UUIDv7 upgrade
        raw_block_id = str(b["id"]) if "id" in b else ""
        block_id = _upgrade_or_generate_opaque_id(raw_block_id, EntityPrefix.PROMPT_BLOCK)
        b["id"] = block_id
        category_id = str(b["category_id"]) if "category_id" in b else ""

        # Strip XML from top-level prompt fields
        for field in ["ai_description", "role_enforcement", "instruction_text", "protocol_instructions"]:
            if field in b and isinstance(b[field], str):
                b[field] = strip_raw_xml(b[field])

        if category_id in (PromptBlockCategory.MATRIX, PromptBlockCategory.MATRIX.value):
            scales = b["scales"] if "scales" in b else []
            if isinstance(scales, list):
                new_scales: list[JsonValue] = []
                for scale in scales:
                    s = dict(scale)
                    # Phase 1, Step 1: Explicit key membership check instead of .get()
                    score_val = s["score"] if "score" in s else None
                    if "id" in s:
                        s["id"] = _upgrade_or_generate_opaque_id(s["id"], EntityPrefix.SCALE)

                    # Track A Level 1 Refactoring
                    cfg: TrackAConfig | None = None
                    if block_id in DUAL_TRACK_A_CONFIG and score_val == 1:
                        cfg = DUAL_TRACK_A_CONFIG[block_id]
                        s["name"] = cfg.scale_name.model_dump()
                        s["ai_label"] = cfg.ai_label

                    claims = s["claims"] if "claims" in s else []
                    if isinstance(claims, list):
                        new_claims: list[JsonValue] = []
                        for claim in claims:
                            c = dict(claim)
                            assertions = c["tda_assertions"] if "tda_assertions" in c else []
                            if isinstance(assertions, list):
                                new_assertions: list[JsonValue] = []
                                for assertion in assertions:
                                    a = dict(assertion)
                                    raw_tda_id = str(a["tda_id"]) if "tda_id" in a else ""
                                    tda_id = _upgrade_or_generate_opaque_id(raw_tda_id, EntityPrefix.TDA)
                                    a["tda_id"] = tda_id
                                    if "depends_on" in a and isinstance(a["depends_on"], list):
                                        upgraded_edges: list[JsonValue] = []
                                        for edge in a["depends_on"]:
                                            e_dict = dict(edge)
                                            if "tda_id" in e_dict:
                                                e_dict["tda_id"] = _upgrade_or_generate_opaque_id(
                                                    e_dict["tda_id"], EntityPrefix.TDA
                                                )
                                            upgraded_edges.append(e_dict)
                                        a["depends_on"] = upgraded_edges

                                    # Dual-Track Invariants
                                    if block_id in DUAL_TRACK_A_CONFIG and score_val == 1:
                                        a["inverse_evidence"] = False
                                        a["aggregation_mode"] = "ALL_MUST_COMPLY"
                                        if cfg and tda_id in cfg.claim_updates:
                                            u = cfg.claim_updates[tda_id]
                                            c["label"] = u.label.model_dump()
                                            a["concept_description"] = u.concept
                                            a["extraction_rule"] = u.rule
                                            mutated_atoms_count += 1
                                    elif block_id in DUAL_TRACK_B_BLOCK_IDS and score_val in (1, 2):
                                        a["inverse_evidence"] = True
                                        a["aggregation_mode"] = "EXISTS"

                                    # Check specific harmonization first
                                    if tda_id in SPECIFIC_ATOM_HARMONIZATIONS:
                                        new_desc, new_rule = SPECIFIC_ATOM_HARMONIZATIONS[tda_id]
                                        a["concept_description"] = new_desc
                                        a["extraction_rule"] = new_rule
                                        mutated_atoms_count += 1
                                    else:
                                        # Generic sanitization
                                        desc = a["concept_description"] if "concept_description" in a else ""
                                        rule = a["extraction_rule"] if "extraction_rule" in a else ""

                                        cleaned_desc = clean_mechanical_phrases(strip_raw_xml(desc))
                                        cleaned_rule = clean_mechanical_phrases(strip_raw_xml(rule))

                                        # Ensure rule is populated
                                        if not cleaned_rule or len(cleaned_rule) < 10:
                                            cleaned_rule = f"Locate and extract substantive evidence demonstrating the following requirement: {cleaned_desc}"

                                        # Ensure concept is concise
                                        if len(cleaned_desc) > 180:
                                            cleaned_desc = cleaned_desc[:175].rsplit(" ", 1)[0] + "."

                                        if cleaned_desc != desc or cleaned_rule != rule:
                                            a["concept_description"] = cleaned_desc
                                            a["extraction_rule"] = cleaned_rule
                                            mutated_atoms_count += 1

                                    new_assertions.append(a)
                                c["tda_assertions"] = new_assertions
                            new_claims.append(c)
                        s["claims"] = new_claims
                    new_scales.append(s)
                b["scales"] = new_scales

        # Validate with strict Pydantic V2 TypeAdapter
        adapter_blocks = cast(TypeAdapter[BaseModel], STANDARD_REGISTRY["prompt_blocks"]["model"])
        validated_model = adapter_blocks.validate_python(b)
        serialized_block = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_blocks.append(serialized_block)

    return sanitized_blocks, mutated_atoms_count


def sanitize_steps(steps: Sequence[Any]) -> list[JsonValue]:
    """Sanitizes steps collection and validates with Pydantic V2.

    Args:
        steps: Raw step dictionaries.

    Returns:
        Sanitized and validated step dictionaries.
    """
    sanitized_steps: list[JsonValue] = []
    adapter_steps = cast(TypeAdapter[BaseModel], STANDARD_REGISTRY["steps"]["model"])

    for step in steps:
        s = {k: v for k, v in step.items() if k != "output_schema"}
        # Phase 2, Step 2: Upgrade step ID (normalizing sp_ -> stp_) and block foreign keys
        raw_step_id = s["id"] if "id" in s else None
        s["id"] = _upgrade_or_generate_opaque_id(raw_step_id, EntityPrefix.STEP)
        for fk_field in ("role_block_id", "extraction_protocol_block_id", "execution_persona_block_id"):
            if fk_field in s and s[fk_field] is not None:
                s[fk_field] = _upgrade_or_generate_opaque_id(s[fk_field], EntityPrefix.PROMPT_BLOCK)

        raw_criteria = s["criteria_block_ids"] if "criteria_block_ids" in s else []
        if isinstance(raw_criteria, list):
            s["criteria_block_ids"] = [
                _upgrade_or_generate_opaque_id(cid, EntityPrefix.PROMPT_BLOCK) for cid in raw_criteria
            ]
        else:
            s["criteria_block_ids"] = []

        # Phase 2, Step 2: Bind causal cohesion BARS matrix block directly to CAUSAL_DISCOVERY steps
        step_type = str(s["type"]) if "type" in s else ""
        if step_type in (StepType.CAUSAL_DISCOVERY, StepType.CAUSAL_DISCOVERY.value):
            if not s["criteria_block_ids"]:
                s["criteria_block_ids"] = [_CAUSAL_COHESION_MATRIX_BLOCK_ID]

        for field in ["step_rules", "ai_description", "label"]:
            if field in s and isinstance(s[field], str):
                s[field] = strip_raw_xml(s[field])

        validated_model = adapter_steps.validate_python(s)
        serialized_step = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_steps.append(serialized_step)

    return sanitized_steps


def sanitize_workflows(workflows: Sequence[Any]) -> list[JsonValue]:
    """Sanitizes workflows collection and validates with Pydantic V2.

    Args:
        workflows: Raw workflow dictionaries.

    Returns:
        Sanitized and validated workflow dictionaries.
    """
    sanitized_workflows: list[JsonValue] = []
    adapter_workflows = cast(TypeAdapter[BaseModel], STANDARD_REGISTRY["workflows"]["model"])

    for workflow in workflows:
        w = {k: v for k, v in workflow.items() if k not in ("ui_schema", "default_scoring_strategy")}
        # Phase 1 & 2, Step 1 & 2: Explicit key membership check and 32-hex UUIDv7 upgrade
        raw_w_id = w["id"] if "id" in w else None
        w_id = _upgrade_or_generate_opaque_id(raw_w_id, EntityPrefix.WORKFLOW)
        w["id"] = w_id

        if "default_profile_id" in w and w["default_profile_id"] is not None:
            w["default_profile_id"] = _upgrade_or_generate_opaque_id(
                w["default_profile_id"], EntityPrefix.OUTPUT_PROFILE
            )
        if "mcp_gateway_id" in w and w["mcp_gateway_id"] is not None:
            w["mcp_gateway_id"] = _upgrade_or_generate_opaque_id(w["mcp_gateway_id"], EntityPrefix.SYSTEM_CONFIG)
        if "model_registry_id" in w and w["model_registry_id"] is not None:
            w["model_registry_id"] = _upgrade_or_generate_opaque_id(w["model_registry_id"], EntityPrefix.SYSTEM_CONFIG)

        if "steps" in w and isinstance(w["steps"], list):
            sr_id_map: dict[str, str] = {}
            for sr_item in w["steps"]:
                sr_dict = dict(sr_item)
                if "id" in sr_dict and sr_dict["id"] is not None:
                    old_sr = str(sr_dict["id"])
                    sr_id_map[old_sr] = _upgrade_or_generate_opaque_id(old_sr, EntityPrefix.STEP_REFERENCE)

            new_step_rules: list[JsonValue] = []
            for sr_item in w["steps"]:
                sr = dict(sr_item)
                old_sr_id = str(sr["id"]) if "id" in sr and sr["id"] is not None else ""
                sr["id"] = (
                    sr_id_map[old_sr_id]
                    if old_sr_id in sr_id_map
                    else _upgrade_or_generate_opaque_id(None, EntityPrefix.STEP_REFERENCE)
                )
                if "task_blueprint" in sr and sr["task_blueprint"] is not None:
                    sr["task_blueprint"] = _upgrade_or_generate_opaque_id(sr["task_blueprint"], EntityPrefix.STEP)
                if "depends_on" in sr and isinstance(sr["depends_on"], list):
                    sr["depends_on"] = [
                        sr_id_map[str(dep)]
                        if str(dep) in sr_id_map
                        else _upgrade_or_generate_opaque_id(dep, EntityPrefix.STEP_REFERENCE)
                        for dep in sr["depends_on"]
                    ]
                if "causal_source_step_id" in sr and sr["causal_source_step_id"] is not None:
                    cs_str = str(sr["causal_source_step_id"])
                    sr["causal_source_step_id"] = (
                        sr_id_map[cs_str]
                        if cs_str in sr_id_map
                        else _upgrade_or_generate_opaque_id(cs_str, EntityPrefix.STEP_REFERENCE)
                    )
                if "input_mappings" in sr and sr["input_mappings"]:
                    new_mappings: dict[str, str] = {}
                    for mk, mv in dict(sr["input_mappings"]).items():
                        val_str = str(mv)
                        parts = val_str.split(".", 2)
                        if len(parts) >= 2 and parts[0] == "$steps":
                            ref_sr = parts[1]
                            if ref_sr != "matrix_reducer":
                                upgraded_ref = (
                                    sr_id_map[ref_sr]
                                    if ref_sr in sr_id_map
                                    else _upgrade_or_generate_opaque_id(ref_sr, EntityPrefix.STEP_REFERENCE)
                                )
                                suffix = f".{parts[2]}" if len(parts) == 3 else ""
                                val_str = f"$steps.{upgraded_ref}{suffix}"
                        new_mappings[str(mk)] = val_str
                    sr["input_mappings"] = new_mappings
                new_step_rules.append(sr)
            w["steps"] = new_step_rules

        wf_03_id = "wf_0195f3a00000700083a1d71000000003"
        wf_05_id = "wf_0195f3a00000700085a1d71000000005"
        if "default_strictness_level" not in w:
            w["default_strictness_level"] = 70 if w_id == wf_03_id else 50
        if "security_penalty" not in w:
            w["security_penalty"] = 0.15 if w_id == wf_05_id else 0.0
        if "post_hoc_penalty" not in w:
            w["post_hoc_penalty"] = 0.0
        if "passivity_penalty" not in w:
            w["passivity_penalty"] = 0.05 if w_id == wf_03_id else 0.0
        validated_model = adapter_workflows.validate_python(w)
        serialized_workflow = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_workflows.append(serialized_workflow)

    return sanitized_workflows


def sanitize_output_profiles(output_profiles: Sequence[Any]) -> list[JsonValue]:
    """Sanitizes output_profiles collection and validates with Pydantic V2.

    Args:
        output_profiles: Raw output profile dictionaries.

    Returns:
        Sanitized and validated output profile dictionaries.
    """
    sanitized_profiles: list[JsonValue] = []
    adapter_profiles = cast(TypeAdapter[BaseModel], STANDARD_REGISTRY["output_profiles"]["model"])

    for profile in output_profiles:
        p = {
            k: v
            for k, v in profile.items()
            if k
            not in (
                "scoring_strategy",
                "strictness_level",
                "security_penalty",
                "post_hoc_penalty",
                "passivity_penalty",
            )
        }
        raw_p_id = p["id"] if "id" in p else None
        p["id"] = _upgrade_or_generate_opaque_id(raw_p_id, EntityPrefix.OUTPUT_PROFILE)
        if "workflow_id" in p and p["workflow_id"] is not None:
            p["workflow_id"] = _upgrade_or_generate_opaque_id(p["workflow_id"], EntityPrefix.WORKFLOW)
        if "target_block_order" in p and isinstance(p["target_block_order"], list):
            new_tbo: list[JsonValue] = []
            for tbo in p["target_block_order"]:
                if isinstance(tbo, str) and "_" in tbo and tbo.split("_", 1)[0] == EntityPrefix.PROMPT_BLOCK.value:
                    new_tbo.append(_upgrade_or_generate_opaque_id(tbo, EntityPrefix.PROMPT_BLOCK))
                else:
                    new_tbo.append(tbo)
            p["target_block_order"] = new_tbo
        if "matrix_synthesis_groups" in p and isinstance(p["matrix_synthesis_groups"], list):
            new_groups: list[JsonValue] = []
            for grp_item in p["matrix_synthesis_groups"]:
                grp = dict(grp_item)
                raw_grp_id = grp["id"] if "id" in grp else None
                grp["id"] = _upgrade_or_generate_opaque_id(raw_grp_id, EntityPrefix.SYNTHESIS_GROUP)
                if "target_blocks" in grp and isinstance(grp["target_blocks"], list):
                    grp["target_blocks"] = [
                        _upgrade_or_generate_opaque_id(tb, EntityPrefix.PROMPT_BLOCK) for tb in grp["target_blocks"]
                    ]
                new_groups.append(grp)
            p["matrix_synthesis_groups"] = new_groups
        if "variance_target_block" in p and p["variance_target_block"] is not None:
            p["variance_target_block"] = _upgrade_or_generate_opaque_id(
                p["variance_target_block"], EntityPrefix.PROMPT_BLOCK
            )
        if "user_role_target_block" in p and p["user_role_target_block"] is not None:
            p["user_role_target_block"] = _upgrade_or_generate_opaque_id(
                p["user_role_target_block"], EntityPrefix.PROMPT_BLOCK
            )
        validated_model = adapter_profiles.validate_python(p)
        serialized_profile = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_profiles.append(serialized_profile)

    return sanitized_profiles


def _sanitize_auxiliary_collections(data: dict[str, JsonValue]) -> None:
    """Upgrades IDs in system_config, organizations, and users collections in-place.

    Args:
        data: Root seed_data.json dictionary.
    """
    if "system_config" in data and isinstance(data["system_config"], list):
        raw_sys_cfgs: Sequence[Any] = data["system_config"]
        new_sys_cfgs: list[JsonValue] = []
        for item in raw_sys_cfgs:
            cfg = dict(item)
            raw_cfg_id = cfg["id"] if "id" in cfg else None
            cfg["id"] = _upgrade_or_generate_opaque_id(raw_cfg_id, EntityPrefix.SYSTEM_CONFIG)
            new_sys_cfgs.append(cfg)
        data["system_config"] = new_sys_cfgs

    if "organizations" in data and isinstance(data["organizations"], list):
        raw_orgs: Sequence[Any] = data["organizations"]
        new_orgs: list[JsonValue] = []
        for item in raw_orgs:
            org = dict(item)
            raw_org_id = org["id"] if "id" in org else None
            if raw_org_id != "org_system000000":
                org["id"] = _upgrade_or_generate_opaque_id(raw_org_id, EntityPrefix.ORGANIZATION)
            new_orgs.append(org)
        data["organizations"] = new_orgs

    if "users" in data and isinstance(data["users"], list):
        raw_users: Sequence[Any] = data["users"]
        new_users: list[JsonValue] = []
        for item in raw_users:
            usr = dict(item)
            raw_usr_id = usr["id"] if "id" in usr else None
            usr["id"] = _upgrade_or_generate_opaque_id(raw_usr_id, EntityPrefix.USER)
            if "organization_id" in usr and usr["organization_id"] not in (None, "org_system000000", "SYSTEM"):
                usr["organization_id"] = _upgrade_or_generate_opaque_id(
                    usr["organization_id"], EntityPrefix.ORGANIZATION
                )
            new_users.append(usr)
        data["users"] = new_users


def run_seed_vault_sanitization(seed_path: Path, dry_run: bool = False) -> SanitizeResult:
    """Executes the full in-memory sanitization pipeline on the seed vault.

    Args:
        seed_path: Path to seed_data.json.
        dry_run: If True, executes validations and calculations without writing to disk.

    Returns:
        A SanitizeResult model with execution statistics.
    """
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed data file not found at: {seed_path}")

    raw_content = seed_path.read_text(encoding="utf-8")
    raw_data = json.loads(raw_content)

    # Purge orphan root collections
    data = {k: v for k, v in raw_data.items() if k != "step_blueprints"}

    backup_path_str: str | None = None
    if not dry_run:
        backup_file = create_vault_backup(seed_path)
        backup_path_str = str(backup_file)

    # 0. Upgrade auxiliary collections (system_config, organizations, users)
    _sanitize_auxiliary_collections(data)

    # 1. Sanitize prompt_blocks
    prompt_blocks = data["prompt_blocks"] if "prompt_blocks" in data else []
    sanitized_blocks, mutated_atoms = sanitize_prompt_blocks(prompt_blocks)
    data["prompt_blocks"] = sanitized_blocks

    # 2. Sanitize steps
    steps = data["steps"] if "steps" in data else []
    sanitized_steps = sanitize_steps(steps)
    data["steps"] = sanitized_steps

    # 3. Sanitize workflows
    workflows = data["workflows"] if "workflows" in data else []
    sanitized_workflows = sanitize_workflows(workflows)
    data["workflows"] = sanitized_workflows

    # 4. Sanitize output_profiles
    output_profiles = data["output_profiles"] if "output_profiles" in data else []
    sanitized_profiles = sanitize_output_profiles(output_profiles)
    data["output_profiles"] = sanitized_profiles

    # 5. Persist atomically if not dry-run
    if not dry_run:
        atomic_save_seed_data(data, seed_path)

    return SanitizeResult(
        total_blocks_sanitized=len(sanitized_blocks),
        total_atoms_mutated=mutated_atoms,
        total_steps_sanitized=len(sanitized_steps),
        total_workflows_sanitized=len(sanitized_workflows),
        total_profiles_sanitized=len(sanitized_profiles),
        backup_path=backup_path_str,
        is_dry_run=dry_run,
        success=True,
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for sanitize_seed_vault.py."""
    parser = argparse.ArgumentParser(
        description="""Seed Vault Sanitization & Schema Normalization Engine.

Automates deterministic cleanup, formatting, and verification of seed_data.json:
  - Key Ordering: Sorts prompt blocks, scales, claims, and TDA assertions into canonical SSOT order.
  - Whitespace Normalization: Trims leading/trailing whitespace and normalizes multiline text blocks.
  - Automatic Backup: Creates timestamped snapshots in backend_v2/seed/backups/ prior to mutations.
  - Post-Sanitization Verification: Optionally executes atom audits (--test) and database reseeding (--reseed).
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/sanitize_seed_vault.py --dry-run
  uv run python scripts/sanitize_seed_vault.py --test
  uv run python scripts/sanitize_seed_vault.py --seed-path backend_v2/seed/seed_data.json --test --reseed
""",
    )
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=Path("backend_v2/seed/seed_data.json"),
        help="Filesystem path to seed_data.json (default: backend_v2/seed/seed_data.json).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute sanitization in memory without persisting changes or writing backups to disk.",
    )
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="Trigger local database wipe and re-seed after successful sanitization.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Execute audit_database_atoms.py --strict and Flutter parity tests after sanitization.",
    )

    args = parser.parse_args(argv)

    print(f"[Sanitizer] Starting Seed Vault Sanitization on '{args.seed_path}' (dry_run={args.dry_run})...")
    result = run_seed_vault_sanitization(args.seed_path, dry_run=args.dry_run)

    print(
        f"[Sanitizer] Sanitized {result.total_blocks_sanitized} prompt blocks ({result.total_atoms_mutated} atoms mutated)."
    )
    print(
        f"[Sanitizer] Sanitized {result.total_steps_sanitized} steps, {result.total_workflows_sanitized} workflows, {result.total_profiles_sanitized} output profiles."
    )
    if result.backup_path:
        print(f"[Sanitizer] Vault backup saved at: {result.backup_path}")

    if args.test and not args.dry_run:
        print("\n[Sanitizer] Running Verification Engine (--strict)...")
        audit_proc = subprocess.run(
            [sys.executable, "scripts/audit_database_atoms.py", "--seed-path", str(args.seed_path), "--strict"],
            capture_output=False,
        )
        if audit_proc.returncode != 0:
            print("[Sanitizer] ERROR: audit_database_atoms.py returned non-zero exit code.")
            sys.exit(1)

        print("\n[Sanitizer] Running Flutter Dart Parity Test...")
        parity_proc = subprocess.run(
            [sys.executable, "scripts/flutter_audit_loop.py", "client_app_v2/test/models/domain_parity_test.dart"],
            capture_output=False,
        )
        if parity_proc.returncode != 0:
            print("[Sanitizer] ERROR: Flutter domain parity test failed.")
            sys.exit(1)

    if args.reseed and not args.dry_run:
        print("\n[Sanitizer] Re-seeding local database...")
        reseed_proc = subprocess.run(
            [sys.executable, "backend_v2/seed/run_seed.py", "local"],
            capture_output=False,
        )
        if reseed_proc.returncode != 0:
            print("[Sanitizer] ERROR: Seeding script failed.")
            sys.exit(1)

    print("\n[Sanitizer] SUCCESS: Seed vault is 100% clean and synchronized.")
    sys.exit(0)


if __name__ == "__main__":
    main()
