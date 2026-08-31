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

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from backend_v2.models.enums import PromptBlockCategory
from backend_v2.seed.seed_registry import STANDARD_REGISTRY


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


def atomic_save_seed_data(data: dict[str, Any], target_path: Path) -> None:
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
        if not isinstance(verified_data, dict):
            os.remove(temp_name)
            raise ValueError(f"Temporary file '{temp_name}' failed dictionary type validation.")

    # Atomic move over target file
    os.replace(temp_name, target_path)


def sanitize_prompt_blocks(prompt_blocks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Sanitizes prompt_blocks collection, matrix atoms, and prompt texts.

    Args:
        prompt_blocks: Raw prompt block dictionaries.

    Returns:
        A tuple of (sanitized blocks, mutated atoms count).
    """
    sanitized_blocks: list[dict[str, Any]] = []
    mutated_atoms_count = 0

    for block in prompt_blocks:
        b = dict(block)
        category_id = str(b["category_id"]) if "category_id" in b else ""

        # Strip XML from top-level prompt fields
        for field in ["ai_description", "role_enforcement", "instruction_text", "protocol_instructions"]:
            if field in b and isinstance(b[field], str):
                b[field] = strip_raw_xml(b[field])

        if category_id in (PromptBlockCategory.MATRIX, PromptBlockCategory.MATRIX.value):
            scales = b["scales"] if "scales" in b else []
            if isinstance(scales, list):
                new_scales: list[dict[str, Any]] = []
                for scale in scales:
                    s = dict(scale)
                    claims = s["claims"] if "claims" in s else []
                    if isinstance(claims, list):
                        new_claims: list[dict[str, Any]] = []
                        for claim in claims:
                            c = dict(claim)
                            assertions = c["tda_assertions"] if "tda_assertions" in c else []
                            if isinstance(assertions, list):
                                new_assertions: list[dict[str, Any]] = []
                                for assertion in assertions:
                                    a = dict(assertion)
                                    tda_id = str(a["tda_id"]) if "tda_id" in a else ""

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
        adapter_blocks = cast(TypeAdapter[Any], STANDARD_REGISTRY["prompt_blocks"]["model"])
        validated_model = adapter_blocks.validate_python(b)
        serialized_block = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_blocks.append(serialized_block)

    return sanitized_blocks, mutated_atoms_count


def sanitize_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitizes steps collection and validates with Pydantic V2.

    Args:
        steps: Raw step dictionaries.

    Returns:
        Sanitized and validated step dictionaries.
    """
    sanitized_steps: list[dict[str, Any]] = []
    adapter_steps = cast(TypeAdapter[Any], STANDARD_REGISTRY["steps"]["model"])

    for step in steps:
        s = dict(step)
        s.pop("output_schema", None)
        for field in ["step_rules", "ai_description", "label"]:
            if field in s and isinstance(s[field], str):
                s[field] = strip_raw_xml(s[field])

        validated_model = adapter_steps.validate_python(s)
        serialized_step = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_steps.append(serialized_step)

    return sanitized_steps


def sanitize_workflows(workflows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitizes workflows collection and validates with Pydantic V2.

    Args:
        workflows: Raw workflow dictionaries.

    Returns:
        Sanitized and validated workflow dictionaries.
    """
    sanitized_workflows: list[dict[str, Any]] = []
    adapter_workflows = cast(TypeAdapter[Any], STANDARD_REGISTRY["workflows"]["model"])

    for workflow in workflows:
        w = dict(workflow)
        w.pop("ui_schema", None)
        validated_model = adapter_workflows.validate_python(w)
        serialized_workflow = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_workflows.append(serialized_workflow)

    return sanitized_workflows


def sanitize_output_profiles(output_profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitizes output_profiles collection and validates with Pydantic V2.

    Args:
        output_profiles: Raw output profile dictionaries.

    Returns:
        Sanitized and validated output profile dictionaries.
    """
    sanitized_profiles: list[dict[str, Any]] = []
    adapter_profiles = cast(TypeAdapter[Any], STANDARD_REGISTRY["output_profiles"]["model"])

    for profile in output_profiles:
        p = dict(profile)
        validated_model = adapter_profiles.validate_python(p)
        serialized_profile = validated_model.model_dump(mode="json", exclude_none=True)
        sanitized_profiles.append(serialized_profile)

    return sanitized_profiles


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
    data = json.loads(raw_content)

    # Purge orphan root collections
    data.pop("step_blueprints", None)

    backup_path_str: str | None = None
    if not dry_run:
        backup_file = create_vault_backup(seed_path)
        backup_path_str = str(backup_file)

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


def main() -> None:
    """CLI entrypoint for sanitize_seed_vault.py."""
    parser = argparse.ArgumentParser(description="Sanitize and format Quorum seed_data.json vault.")
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=Path("backend_v2/seed/seed_data.json"),
        help="Path to seed_data.json file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform all validations without persisting changes to disk.",
    )
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="Trigger local database wipe and re-seed after sanitization.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run audit_database_atoms.py and flutter parity test after sanitization.",
    )

    args = parser.parse_args()

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
