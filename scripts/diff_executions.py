"""Execution Trace Comparison and Consistency Metric Suite.

Provides forensic cross-execution differential analysis, Fleiss/Cohen Kappa metrics,
Shannon entropy calculations, and Markdown report synthesis.

Usage Examples:
    # 1. Compare specific executions by ID:
    uv run python scripts/diff_executions.py exe_6c9e2f3b2ea14f9d exe_f16d8b0e40e44316

    # 2. Compare executions by directory path:
    uv run python scripts/diff_executions.py data/files/executions/exe_6c9e2f3b2ea14f9d data/files/executions/exe_f16d8b0e40e44316

    # 3. Compare latest 3 executions automatically:
    uv run python scripts/diff_executions.py
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

__all__ = [
    "BlockHeatmapDTO",
    "DisagreementRootCause",
    "IsolationAuditDTO",
    "KappaMetricsDTO",
    "MacroBlockScoreDTO",
    "RootCauseBreakdownDTO",
    "ScaleBreakdownDTO",
    "calculate_cohens_kappa",
    "calculate_entropy",
    "calculate_fleiss_kappa",
    "calculate_pairwise_consistency",
    "classify_disagreement",
    "extract_block_normalized_scores",
    "get_all_evals",
    "get_state",
    "get_trace",
    "has_quote",
    "main",
    "run_diff",
    "uses_contextual_override",
]

# Force UTF-8 encoding for stdout/stderr on Windows to support emojis and international characters
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")


class DisagreementRootCause(StrEnum):
    """Deterministic triage category for inter-run evaluation disagreements."""

    RETRIEVAL_GAP = "retrieval_gap"
    REASONING_GAP = "reasoning_gap"
    CONTEXTUAL_OVERRIDE = "contextual_override"
    TECHNICAL_ERROR = "technical_error"


class KappaMetricsDTO(BaseModel):
    """Immutable Cohen's and Fleiss' Kappa reliability metrics container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    kappa: float
    standard_error: float
    ci_lower: float
    ci_upper: float
    benchmark_category: str
    observed_agreement: float
    expected_agreement: float
    marginal_bias: float | None = None


class IsolationAuditDTO(BaseModel):
    """Immutable cross-run input document cache isolation audit container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    input_hashes_by_run: dict[str, dict[str, str]]
    shared_identical_files: list[str]
    is_fully_isolated: bool
    disable_vertex_cache_active: bool


class RootCauseBreakdownDTO(BaseModel):
    """Immutable 4-tier disagreement root cause categorization container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    retrieval_gap_count: int
    reasoning_gap_count: int
    contextual_override_count: int
    technical_error_count: int
    total_mismatches: int


class ScaleBreakdownDTO(BaseModel):
    """Immutable metric breakdown per normalized 0-100 difficulty tier."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tier_label: str
    tier_min: float
    tier_max: float
    total_atoms: int
    mismatches: int
    consistency_rate: float


class BlockHeatmapDTO(BaseModel):
    """Immutable metric breakdown per matrix block."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    block_id: str
    block_name: str
    total_atoms: int
    mismatches: int
    consistency_rate: float


class MacroBlockScoreDTO(BaseModel):
    """Immutable block-level normalized score drift container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    block_id: str
    block_name: str
    run1_normalized_score: float | None
    run2_normalized_score: float | None
    delta_normalized_score: float | None
    run1_pass_rate: float
    run2_pass_rate: float
    delta_pass_rate: float


def _inspect_input_file(file_path: Path) -> dict[str, str]:
    """Compute SHA-256 hash and detect injected Unicode noise variants in an input file.

    Args:
        file_path: Path to the input file.

    Returns:
        Dictionary containing 'sha256' and 'noise' description.
    """
    raw_bytes = file_path.read_bytes()
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    text = raw_bytes.decode("utf-8", errors="replace")

    known_variants = {
        "\u00a0": "No-Break Space (U+00A0)",
        "\u2002": "En Space (U+2002)",
        "\u2003": "Em Space (U+2003)",
        "\u202f": "Narrow No-Break Space (U+202F)",
    }
    found_variants: list[str] = []
    for char, name in known_variants.items():
        if char in text:
            found_variants.append(name)

    noise_desc = ", ".join(found_variants) if found_variants else "Standard ASCII"
    return {
        "sha256": sha256_hash,
        "noise": noise_desc,
    }


def get_all_evals(path: str | Path) -> dict[str, dict[str, Any]]:
    """Extract all evaluated atom dictionaries from an execution trace file.

    Args:
        path: Path to the execution_trace.json file.

    Returns:
        Mapping of atom_id to evaluation dictionary.
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    all_evals: dict[str, dict[str, Any]] = {}
    for step in data:
        if "content" in step and isinstance(step["content"], dict):
            evals = step["content"].get("evaluations")
            if isinstance(evals, list):
                for e in evals:
                    atom_id = e.get("atom_id") or e.get("tda_id")
                    if atom_id:
                        all_evals[atom_id] = e
            results = step["content"].get("results")
            if isinstance(results, list):
                for e in results:
                    atom_id = e.get("tda_id") or e.get("atom_id")
                    if atom_id:
                        all_evals[atom_id] = e
    return all_evals


def calculate_entropy(states: list[str]) -> float:
    """Calculate Shannon entropy (base 2) for a given distribution of discrete states.

    Args:
        states: List of state strings (e.g., ['passed', 'failed']).

    Returns:
        Shannon entropy in bits. Returns 0.0 for empty or homogeneous distributions.
    """
    if not states:
        return 0.0
    counts: dict[str, int] = {}
    for s in states:
        counts[s] = counts.get(s, 0) + 1
    total = len(states)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def calculate_pairwise_consistency(states: list[str]) -> float:
    """Calculate pairwise agreement ratio between multiple evaluation states.

    Args:
        states: List of categorical states across multiple runs.

    Returns:
        Pairwise consistency ratio between 0.0 and 1.0.
    """
    m = len(states)
    if m < 2:
        return 1.0
    counts: dict[str, int] = {}
    for s in states:
        counts[s] = counts.get(s, 0) + 1
    agreed_pairs = sum(c * (c - 1) / 2 for c in counts.values())
    total_pairs = m * (m - 1) / 2
    return agreed_pairs / total_pairs


def calculate_cohens_kappa(atom_states_list: list[list[str]], categories: list[str]) -> KappaMetricsDTO:
    """Calculate Cohen's Kappa for exactly two runs (M = 2) with Fleiss SE and 95% CI.

    Args:
        atom_states_list: List of 2-element lists containing categorical states.
        categories: List of unique categories present across all evaluations.

    Returns:
        Strict KappaMetricsDTO containing kappa, standard error, confidence interval, and benchmark.

    Raises:
        ValueError: If any item in atom_states_list does not contain exactly two states.
    """
    n = len(atom_states_list)
    if n == 0:
        return KappaMetricsDTO(
            kappa=0.0,
            standard_error=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            benchmark_category="🔴 Heikko sopivuus (Fair / Poor Agreement)",
            observed_agreement=0.0,
            expected_agreement=0.0,
            marginal_bias=None,
        )
    if len(atom_states_list[0]) != 2:
        msg = "Cohen's Kappa requires exactly two raters/runs (M = 2)."
        raise ValueError(msg)

    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    num_classes = len(categories)

    confusion_matrix = [[0] * num_classes for _ in range(num_classes)]
    for states in atom_states_list:
        if len(states) != 2:
            msg = "Each state item must contain exactly 2 ratings."
            raise ValueError(msg)
        idx1 = cat_to_idx.get(states[0])
        idx2 = cat_to_idx.get(states[1])
        if idx1 is not None and idx2 is not None:
            confusion_matrix[idx1][idx2] += 1

    observed_agreement = sum(confusion_matrix[i][i] for i in range(num_classes)) / n

    row_sums = [sum(confusion_matrix[i][j] for j in range(num_classes)) for i in range(num_classes)]
    col_sums = [sum(confusion_matrix[i][j] for i in range(num_classes)) for j in range(num_classes)]

    expected_agreement = sum((row_sums[i] / n) * (col_sums[i] / n) for i in range(num_classes))

    if expected_agreement >= 1.0:
        kappa = 1.0
    else:
        kappa = (observed_agreement - expected_agreement) / (1.0 - expected_agreement)

    # Singularity boundary guard
    if expected_agreement >= 1.0 or observed_agreement >= 1.0:
        se_kappa = 0.0
        ci_lower = max(-1.0, min(1.0, kappa))
        ci_upper = max(-1.0, min(1.0, kappa))
    else:
        var_num = observed_agreement * (1.0 - observed_agreement)
        var_denom = n * ((1.0 - expected_agreement) ** 2)
        se_kappa = math.sqrt(max(0.0, var_num / var_denom)) if var_denom > 0 else 0.0
        ci_lower = max(-1.0, kappa - 1.96 * se_kappa)
        ci_upper = min(1.0, kappa + 1.96 * se_kappa)

    # Landis & Koch benchmark categorization
    if kappa > 0.80:
        benchmark_category = "🏆 Lähes täydellinen sopivuus (Almost Perfect Agreement)"
    elif kappa >= 0.61:
        benchmark_category = "🟢 Huomattava / Vahva sopivuus (Substantial Agreement)"
    elif kappa >= 0.41:
        benchmark_category = "🟡 Kohtalainen sopivuus (Moderate Agreement)"
    else:
        benchmark_category = "🔴 Heikko sopivuus (Fair / Poor Agreement)"

    # Marginal bias calculation for binary/first category
    marginal_bias: float | None = None
    positive_labels = {"true", "passed", "1", "pass"}
    pos_indices = [idx for cat, idx in cat_to_idx.items() if cat.lower() in positive_labels]
    if len(pos_indices) == 1:
        p_idx = pos_indices[0]
        marginal_bias = (row_sums[p_idx] - col_sums[p_idx]) / n
    elif num_classes == 2:
        marginal_bias = (row_sums[0] - col_sums[0]) / n

    return KappaMetricsDTO(
        kappa=kappa,
        standard_error=se_kappa,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        benchmark_category=benchmark_category,
        observed_agreement=observed_agreement,
        expected_agreement=expected_agreement,
        marginal_bias=marginal_bias,
    )


def calculate_fleiss_kappa(atom_states_list: list[list[str]], categories: list[str]) -> float:
    """Calculate Fleiss' Kappa for general multi-rater evaluation consistency.

    Args:
        atom_states_list: List of state lists across all evaluated items.
        categories: List of possible categories.

    Returns:
        Fleiss' Kappa statistic.
    """
    n = len(atom_states_list)
    if n == 0:
        return 0.0
    m = len(atom_states_list[0])
    if m < 2:
        return 1.0

    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    num_classes = len(categories)

    count_matrix = [[0] * num_classes for _ in range(n)]
    for i, states in enumerate(atom_states_list):
        for s in states:
            if s in cat_to_idx:
                count_matrix[i][cat_to_idx[s]] += 1

    p_i = []
    for i in range(n):
        sum_sq = sum(count_matrix[i][c] ** 2 for c in range(num_classes))
        p_i.append((sum_sq - m) / (m * (m - 1)))
    p_mean = sum(p_i) / n

    p_j = [0.0] * num_classes
    for j in range(num_classes):
        col_sum = sum(count_matrix[i][j] for i in range(n))
        p_j[j] = col_sum / (n * m)
    p_e = sum(p**2 for p in p_j)

    if p_e >= 1.0:
        return 1.0

    return (p_mean - p_e) / (1.0 - p_e)


def get_state(e: dict[str, Any]) -> str:
    """Determine the normalized discrete status string of an atom evaluation dictionary.

    Args:
        e: Raw evaluation dictionary.

    Returns:
        Normalized state string (e.g. 'passed', 'failed', 'true', 'false').
    """
    if "status" in e and e["status"] is not None:
        return str(e["status"]).lower()
    if "decision" in e and e["decision"] is not None:
        return str(e["decision"]).lower()
    if "mapped_state" in e and e["mapped_state"] is not None:
        return str(e["mapped_state"]).lower()
    if "exact_quote" in e or "exact_quotes" in e or "source_quote" in e:
        eq = e.get("exact_quote", e.get("exact_quotes", e.get("source_quote")))
        if eq is None or eq == []:
            return "false"
        eq_lower = str(eq).strip().lower()
        blacklist = {
            "null",
            "none",
            "n/a",
            "false",
            "",
            "ei löydy",
            "not found",
            "-",
            "ei mainittu",
            "none detected",
            "[]",
            "{}",
            "ei sovelleta",
            "ei lainausta",
            "no quote",
            "ei ole",
        }
        return "true" if eq_lower not in blacklist else "false"
    return "unknown"


def get_trace(e: dict[str, Any]) -> str:
    """Extract qualitative reasoning trace string from an evaluation dictionary.

    Args:
        e: Evaluation dictionary.

    Returns:
        Extracted reasoning or trace text.
    """
    for key in (
        "evaluation_reasoning",
        "context_scan_trace",
        "semantic_reasoning",
        "reasoning_trace",
        "mechanical_trace",
    ):
        val = e.get(key)
        if val:
            return str(val)
    return ""


def has_quote(e: dict[str, Any]) -> bool:
    """Check if an evaluation record contains a non-empty, non-blacklisted quote.

    Args:
        e: Raw evaluation dictionary.

    Returns:
        True if an authentic quote string exists, False otherwise.
    """
    eq = e.get("exact_quote", e.get("exact_quotes", e.get("source_quote")))
    if eq is None or eq == []:
        return False
    if isinstance(eq, list):
        eq_str = " ".join(str(x) for x in eq)
    else:
        eq_str = str(eq)
    eq_lower = eq_str.strip().lower()
    blacklist = {
        "null",
        "none",
        "n/a",
        "false",
        "",
        "ei löydy",
        "not found",
        "-",
        "ei mainittu",
        "none detected",
        "[]",
        "{}",
        "ei sovelleta",
        "ei lainausta",
        "no quote",
        "ei ole",
    }
    return eq_lower not in blacklist


def uses_contextual_override(e: dict[str, Any]) -> bool:
    """Check if an evaluation record triggered or applied contextual override.

    Args:
        e: Evaluation dictionary.

    Returns:
        True if contextual override is active, False otherwise.
    """
    if e.get("contextual_override") is True:
        return True
    eq = e.get("exact_quote", e.get("source_quote"))
    return isinstance(eq, str) and "[INFERRED]" in eq


def classify_disagreement(eval_1: dict[str, Any], eval_2: dict[str, Any]) -> DisagreementRootCause:
    """Deterministically classify an evaluation disagreement into a root cause tier.

    Args:
        eval_1: Evaluation dictionary from the first run.
        eval_2: Evaluation dictionary from the second run.

    Returns:
        DisagreementRootCause enum indicating the primary driver of disagreement.
    """
    traces = [get_trace(eval_1), get_trace(eval_2)]
    if (
        any("[SYSTEM ERROR" in t or "Chunk Processing Failed" in t for t in traces)
        or eval_1.get("_dlq_status")
        or eval_2.get("_dlq_status")
    ):
        return DisagreementRootCause.TECHNICAL_ERROR

    if uses_contextual_override(eval_1) or uses_contextual_override(eval_2):
        return DisagreementRootCause.CONTEXTUAL_OVERRIDE

    q1 = has_quote(eval_1)
    q2 = has_quote(eval_2)
    if q1 != q2:
        return DisagreementRootCause.RETRIEVAL_GAP

    return DisagreementRootCause.REASONING_GAP


def extract_block_normalized_scores(trace_path: Path) -> dict[str, float]:
    """Extract block-level normalized scores (0-100) from an execution trace file.

    Args:
        trace_path: Path to the execution_trace.json file.

    Returns:
        Mapping of block ID to float normalized score.
    """
    scores: dict[str, float] = {}
    if not trace_path.exists():
        return scores
    try:
        with trace_path.open("r", encoding="utf-8") as tf:
            trace = json.load(tf)
        for ev in trace:
            if isinstance(ev, dict) and isinstance(ev.get("content"), dict):
                content = ev["content"]
                for k, v in content.items():
                    if isinstance(v, dict) and "normalized_score" in v and v["normalized_score"] is not None:
                        try:
                            scores[k] = float(v["normalized_score"])
                        except ValueError, TypeError:
                            pass
    except json.JSONDecodeError, OSError:
        pass
    return scores


def run_diff(execution_ids: list[str] | None = None) -> str:
    """Perform differential analysis between execution traces and generate Markdown report.

    Args:
        execution_ids: Optional list of execution IDs or directory paths to compare.

    Returns:
        Path to the generated report file.
    """
    base_executions_dir = Path("data/files/executions")
    loaded_runs: list[str] = []
    loaded_paths: list[Path] = []
    evals_list: list[dict[str, dict[str, Any]]] = []

    if execution_ids:
        for exe_id in execution_ids:
            p = Path(exe_id)
            if p.is_dir():
                trace_file = p / "execution_trace.json"
                name = p.name
            else:
                trace_file = base_executions_dir / exe_id / "execution_trace.json"
                name = exe_id

            if trace_file.exists():
                evals_list.append(get_all_evals(trace_file))
                loaded_runs.append(name)
                loaded_paths.append(trace_file)
            else:
                print(f"Path not found: {trace_file}")
    else:
        exe_dirs = sorted(
            [d for d in base_executions_dir.glob("exe_*") if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        for d in exe_dirs[:3]:
            trace_file = d / "execution_trace.json"
            if trace_file.exists():
                evals_list.append(get_all_evals(trace_file))
                loaded_runs.append(d.name)
                loaded_paths.append(trace_file)

    if len(evals_list) < 2:
        print("Error: At least two executions are required for differential comparison.")
        sys.exit(1)

    print(f"Loaded {len(evals_list)} executions for comparison:")
    for idx, name in enumerate(loaded_runs):
        print(f"  Run {idx + 1}: {name}")

    common_atoms = set(evals_list[0].keys())
    for evals in evals_list[1:]:
        common_atoms = common_atoms.intersection(set(evals.keys()))

    if not common_atoms:
        print("Error: Loaded executions share zero common atom keys.")
        sys.exit(1)

    seed_path = Path("backend_v2/seed/seed_data.json")
    seed: dict[str, Any] = {}
    try:
        with seed_path.open("r", encoding="utf-8") as f:
            seed = json.load(f)
    except UnicodeDecodeError, OSError:
        with seed_path.open("r", encoding="cp1252") as f:
            seed = json.load(f)

    atom_rules: dict[str, str] = {}
    atom_details: dict[str, dict[str, Any]] = {}
    atom_to_block: dict[str, str] = {}

    for block in seed.get("prompt_blocks", []):
        bid = block.get("id")
        bname_raw = block.get("name")
        bname = bid
        if isinstance(bname_raw, dict):
            bname = bname_raw.get("translations", {}).get("fi") or bname_raw.get("translations", {}).get("en") or bid
        elif isinstance(bname_raw, str) and bname_raw.strip():
            bname = bname_raw.strip()

        for scale in block.get("scales", []):
            sname_raw = scale.get("name")
            sname = f"Scale {scale.get('score')}"
            if isinstance(sname_raw, dict):
                sname = (
                    sname_raw.get("translations", {}).get("fi") or sname_raw.get("translations", {}).get("en") or sname
                )
            elif isinstance(sname_raw, str):
                sname = sname_raw

            for claim in scale.get("claims", []):
                for tda in claim.get("tda_assertions", []):
                    tid = tda.get("tda_id") or tda.get("id")
                    if not tid:
                        continue

                    desc = (tda.get("concept_description") or "").strip()
                    rule = (tda.get("extraction_rule") or "").strip()
                    anchor = (tda.get("anchor_target") or "").strip()
                    contrastive = (tda.get("contrastive_example") or "").strip()

                    if desc.startswith("DEPRECATED"):
                        desc = ""

                    primary_rule = desc or rule or anchor or "Määrittelemätön sääntö"
                    atom_rules[tid] = primary_rule

                    atom_details[tid] = {
                        "block_id": bid,
                        "block_name": bname or bid,
                        "scale_name": sname,
                        "scale_score": scale.get("score"),
                        "concept_description": desc,
                        "extraction_rule": rule,
                        "anchor_target": anchor,
                        "contrastive_example": contrastive,
                        "inverse_evidence": tda.get("inverse_evidence", False),
                    }
                    if bid:
                        atom_to_block[tid] = bid

    valid_common_atoms: set[str] = set()
    for atom in common_atoms:
        traces = [get_trace(evals[atom]) for evals in evals_list]
        if any("[SYSTEM ERROR" in t or "Chunk Processing Failed" in t for t in traces):
            continue
        valid_common_atoms.add(atom)

    common_atoms = valid_common_atoms

    atom_states: dict[str, list[str]] = {}
    atom_entropies: dict[str, float] = {}
    atom_consistencies: dict[str, float] = {}
    all_atom_states: list[list[str]] = []
    unique_categories: set[str] = set()

    for atom in common_atoms:
        states = [get_state(evals[atom]) for evals in evals_list]
        for s in states:
            unique_categories.add(s)

        entropy = calculate_entropy(states)
        consistency = calculate_pairwise_consistency(states)

        atom_states[atom] = states
        atom_entropies[atom] = entropy
        atom_consistencies[atom] = consistency
        all_atom_states.append(states)

    categories_list = sorted(list(unique_categories))
    global_kappa = calculate_fleiss_kappa(all_atom_states, categories_list)
    global_consistency = sum(atom_consistencies.values()) / len(common_atoms) if common_atoms else 1.0
    global_entropy = sum(atom_entropies.values()) / len(common_atoms) if common_atoms else 0.0

    cohen_kappa_dto: KappaMetricsDTO | None = None
    if len(evals_list) == 2:
        try:
            cohen_kappa_dto = calculate_cohens_kappa(all_atom_states, categories_list)
        except (ValueError, ZeroDivisionError) as e:
            print(f"Warning: Cohen's Kappa calculation error: {e}")

    mismatching_atoms = [atom for atom, entropy in atom_entropies.items() if entropy > 0]
    mismatching_atoms.sort(key=lambda a: atom_entropies[a], reverse=True)

    summary_2way = {"PASSED->FAILED": 0, "FAILED->PASSED": 0, "Other": 0}
    evals_1 = evals_list[0]
    evals_2 = evals_list[1]
    passed_states = ["true", "passed", "1"]
    failed_states = ["false", "failed", "0"]

    for atom in common_atoms:
        s1, s2 = get_state(evals_1[atom]), get_state(evals_2[atom])
        if s1 != s2:
            if s1 in passed_states and s2 in failed_states:
                summary_2way["PASSED->FAILED"] += 1
            elif s1 in failed_states and s2 in passed_states:
                summary_2way["FAILED->PASSED"] += 1
            else:
                summary_2way["Other"] += 1

    contextual_override_mismatches = 0
    for atom in mismatching_atoms:
        used_override = False
        for evals in evals_list:
            if atom in evals and uses_contextual_override(evals[atom]):
                used_override = True
                break
        if used_override:
            contextual_override_mismatches += 1

    # Disagreement Root Cause Triage
    root_cause_counts = {
        DisagreementRootCause.RETRIEVAL_GAP: 0,
        DisagreementRootCause.REASONING_GAP: 0,
        DisagreementRootCause.CONTEXTUAL_OVERRIDE: 0,
        DisagreementRootCause.TECHNICAL_ERROR: 0,
    }
    for atom in mismatching_atoms:
        cause = classify_disagreement(evals_1.get(atom, {}), evals_2.get(atom, {}))
        root_cause_counts[cause] += 1

    root_cause_breakdown = RootCauseBreakdownDTO(
        retrieval_gap_count=root_cause_counts[DisagreementRootCause.RETRIEVAL_GAP],
        reasoning_gap_count=root_cause_counts[DisagreementRootCause.REASONING_GAP],
        contextual_override_count=root_cause_counts[DisagreementRootCause.CONTEXTUAL_OVERRIDE],
        technical_error_count=root_cause_counts[DisagreementRootCause.TECHNICAL_ERROR],
        total_mismatches=len(mismatching_atoms),
    )

    Path("scratch").mkdir(exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = Path(f"scratch/diff_report_{timestamp_str}.md")

    git_info = "Ei saatavilla"
    try:
        git_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        git_commit = subprocess.check_output(["git", "log", "-1", "--pretty=format:%h - %s (%cd)"], text=True).strip()
        git_info = f"Branch: {git_branch} | Commit: {git_commit}"
    except (subprocess.SubprocessError, OSError) as e:
        git_info = f"Git-tietojen haku epäonnistui: {e}"

    sys_enums = "Ei saatavilla"
    try:
        if "." not in sys.path:
            sys.path.insert(0, ".")
        import backend_v2.models.enums as enums

        ensemble_v: str = str(enums.EvaluationRunCount.ENSEMBLE.value)
        standard_v: str = str(enums.EvaluationRunCount.STANDARD.value)
        pass_v: str = str(enums.VerificationResult.VERIFIED.value)
        fail_v: str = str(enums.VerificationResult.DEBUNKED.value)

        sys_enums = (
            f"  - **EvaluationRunCount**: ENSEMBLE = {ensemble_v}, STANDARD = {standard_v}\n"
            f"  - **VerificationResult**: VERIFIED = {pass_v}, DEBUNKED = {fail_v}"
        )

        try:
            from backend_v2.settings import get_settings

            cfg = get_settings()
            sys_enums += (
                f"\n  - **SystemConcurrency (Settings)**:\n"
                f"    - max_concurrent_llm_steps = {cfg.max_concurrent_llm_steps}\n"
                f"    - llm_max_retries = {cfg.llm_max_retries}"
            )
        except (ImportError, AttributeError, KeyError, ValueError, RuntimeError) as e:
            sys_enums += f"\n  - **SystemConcurrency**: N/A ({e})"
    except (ImportError, AttributeError, KeyError, ValueError, RuntimeError) as e:
        sys_enums = f"Virhe Enumien luvussa: {e}"

    db_executions: dict[str, Any] = {}
    db_file_path = Path("data/db_v2.json")
    if db_file_path.exists():
        try:
            with db_file_path.open("r", encoding="utf-8") as db_f:
                db_json = json.load(db_f)
                db_executions = db_json.get("executions", {})
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: db_v2.json read error: {e}")

    # Isolation Audit & SHA-256 Hashes
    input_hashes_by_run: dict[str, dict[str, str]] = {}
    for r_name, p in zip(loaded_runs, loaded_paths, strict=False):
        in_dir = p.parent / "inputs"
        r_hashes: dict[str, str] = {}
        if in_dir.is_dir():
            for in_f in sorted(in_dir.iterdir()):
                if in_f.is_file():
                    r_hashes[in_f.name] = hashlib.sha256(in_f.read_bytes()).hexdigest()
        input_hashes_by_run[r_name] = r_hashes

    shared_identical_files: list[str] = []
    if len(loaded_runs) >= 2:
        for i in range(len(loaded_runs)):
            for j in range(i + 1, len(loaded_runs)):
                r1_name = loaded_runs[i]
                r2_name = loaded_runs[j]
                common_files = set(input_hashes_by_run.get(r1_name, {}).keys()) & set(
                    input_hashes_by_run.get(r2_name, {}).keys()
                )
                for cf in common_files:
                    if input_hashes_by_run[r1_name][cf] == input_hashes_by_run[r2_name][cf]:
                        shared_identical_files.append(f"{cf} (R{i + 1} == R{j + 1})")

    disable_vertex_cache_active = os.environ.get("DISABLE_VERTEX_CACHE", "").lower() == "true"
    for p in loaded_paths:
        prompt_debug = p.parent / "llm_debug_prompts.md"
        if prompt_debug.exists():
            try:
                content_sample = prompt_debug.read_text(encoding="utf-8", errors="replace")[:2000]
                if "DISABLE_VERTEX_CACHE" in content_sample or "--no-cache" in content_sample:
                    disable_vertex_cache_active = True
            except OSError:
                pass

    isolation_audit = IsolationAuditDTO(
        input_hashes_by_run=input_hashes_by_run,
        shared_identical_files=shared_identical_files,
        is_fully_isolated=len(shared_identical_files) == 0,
        disable_vertex_cache_active=disable_vertex_cache_active,
    )

    # Execution Health Checks
    all_runs_passed = True
    any_starvation = False
    total_tech_errors = 0
    total_dlqs = 0
    for r_name, p in zip(loaded_runs, loaded_paths, strict=False):
        health_run_record: dict[str, Any] = next((v for v in db_executions.values() if v.get("id") == r_name), {})
        status_val = health_run_record.get("status")
        if status_val not in ["PASSED", "passed"]:
            all_runs_passed = False
        try:
            with p.open("r", encoding="utf-8") as exe_f:
                raw = exe_f.read()
            err_c = raw.count("Chunk Processing Failed") + raw.count("SYSTEM ERROR")
            dlq_c = raw.count('"_dlq_status": "FAILED/DLQ"')
            total_tech_errors += err_c
            total_dlqs += dlq_c
            if '"event_type": "starvation"' in raw or any(
                isinstance(s, dict) and s.get("data_starvation") is not None
                for s in health_run_record.get("profile_syntheses", {}).values()
            ):
                any_starvation = True
        except OSError:
            pass

    overall_health_passed = all_runs_passed and not any_starvation and total_tech_errors == 0 and total_dlqs == 0

    # 0-100 Difficulty Tier Breakdown
    block_extrema: dict[str, tuple[float, float]] = {}
    for block in seed.get("prompt_blocks", []):
        bid = block.get("id")
        if not bid:
            continue
        scales = block.get("scales", [])
        scores = [
            float(s.get("score"))
            for s in scales
            if s.get("score") is not None and isinstance(s.get("score"), (int, float))
        ]
        if scores:
            block_extrema[str(bid)] = (min(scores), max(scores))
        else:
            block_extrema[str(bid)] = (1.0, 5.0)

    tier_definitions = [
        ("81–100%: Korkein vaativuustaso (Top Mastery / Critical Rigor)", 81.0, 100.0),
        ("61–80%: Korkea vaativuustaso (High Standard)", 61.0, 80.0),
        ("41–60%: Keskitaso (Mid Standard)", 41.0, 60.0),
        ("21–40%: Matala vaativuustaso (Low Standard)", 21.0, 40.0),
        ("0–20%: Perustaso (Baseline / Minimum Viable)", 0.0, 20.0),
    ]

    tier_atoms: dict[str, list[str]] = {t[0]: [] for t in tier_definitions}
    for atom in common_atoms:
        det = atom_details.get(atom, {})
        bid_raw = det.get("block_id")
        bid = str(bid_raw) if bid_raw else ""
        raw_score = det.get("scale_score")
        b_min, b_max = block_extrema.get(bid, (1.0, 5.0))
        if raw_score is not None and isinstance(raw_score, (int, float)):
            if b_max > b_min:
                norm_pos = ((float(raw_score) - b_min) / (b_max - b_min)) * 100.0
            else:
                norm_pos = 50.0
        else:
            norm_pos = 50.0

        if norm_pos > 80.0:
            tier_atoms[tier_definitions[0][0]].append(atom)
        elif norm_pos > 60.0:
            tier_atoms[tier_definitions[1][0]].append(atom)
        elif norm_pos > 40.0:
            tier_atoms[tier_definitions[2][0]].append(atom)
        elif norm_pos > 20.0:
            tier_atoms[tier_definitions[3][0]].append(atom)
        else:
            tier_atoms[tier_definitions[4][0]].append(atom)

    scale_breakdowns: list[ScaleBreakdownDTO] = []
    for label, t_min, t_max in tier_definitions:
        t_atoms = tier_atoms[label]
        t_total = len(t_atoms)
        t_mismatches = sum(1 for a in t_atoms if a in mismatching_atoms)
        t_cons = (t_total - t_mismatches) / t_total if t_total > 0 else 1.0
        scale_breakdowns.append(
            ScaleBreakdownDTO(
                tier_label=label,
                tier_min=t_min,
                tier_max=t_max,
                total_atoms=t_total,
                mismatches=t_mismatches,
                consistency_rate=t_cons,
            )
        )

    # Block Heatmap Analysis
    blocks_in_play: dict[str, str] = {}
    for atom in common_atoms:
        det = atom_details.get(atom, {})
        bid = det.get("block_id")
        bname = det.get("block_name", bid or "Unknown Block")
        if bid:
            blocks_in_play[bid] = bname

    block_heatmaps: list[BlockHeatmapDTO] = []
    for bid, bname in blocks_in_play.items():
        b_atoms = [a for a in common_atoms if atom_details.get(a, {}).get("block_id") == bid]
        b_total = len(b_atoms)
        b_mismatches = sum(1 for a in b_atoms if a in mismatching_atoms)
        b_cons = (b_total - b_mismatches) / b_total if b_total > 0 else 1.0
        block_heatmaps.append(
            BlockHeatmapDTO(
                block_id=bid,
                block_name=bname,
                total_atoms=b_total,
                mismatches=b_mismatches,
                consistency_rate=b_cons,
            )
        )
    block_heatmaps.sort(key=lambda b: (b.mismatches, 1.0 - b.consistency_rate), reverse=True)

    # Macro Block Score Drift (0-100)
    run1_scores = extract_block_normalized_scores(loaded_paths[0]) if loaded_paths else {}
    run2_scores = extract_block_normalized_scores(loaded_paths[1]) if len(loaded_paths) > 1 else {}

    macro_block_scores: list[MacroBlockScoreDTO] = []
    for bid, bname in blocks_in_play.items():
        b_atoms = [a for a in common_atoms if atom_details.get(a, {}).get("block_id") == bid]
        b_total = len(b_atoms)
        if b_total == 0:
            continue
        r1_pass = sum(1 for a in b_atoms if get_state(evals_1[a]) in passed_states) / b_total
        r2_pass = sum(1 for a in b_atoms if get_state(evals_2[a]) in passed_states) / b_total
        r1_norm = run1_scores.get(bid)
        r2_norm = run2_scores.get(bid)
        d_norm = (r2_norm - r1_norm) if (r1_norm is not None and r2_norm is not None) else None
        macro_block_scores.append(
            MacroBlockScoreDTO(
                block_id=bid,
                block_name=bname,
                run1_normalized_score=r1_norm,
                run2_normalized_score=r2_norm,
                delta_normalized_score=d_norm,
                run1_pass_rate=r1_pass,
                run2_pass_rate=r2_pass,
                delta_pass_rate=r2_pass - r1_pass,
            )
        )

    # Lexical Grounding Audit
    grounding_results_by_run: list[dict[str, Any]] = []
    for idx, (r_name, p) in enumerate(zip(loaded_runs, loaded_paths, strict=False)):
        run_in_dir = p.parent / "inputs"
        corpus = ""
        if run_in_dir.is_dir():
            corpus_parts: list[str] = []
            for in_f in sorted(run_in_dir.iterdir()):
                if in_f.is_file():
                    try:
                        corpus_parts.append(in_f.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        pass
            corpus = "\n".join(corpus_parts)

        ev_map = evals_list[idx]
        total_quotes = 0
        verified_quotes = 0
        unverified_quotes = 0
        for _atom_id, ev in ev_map.items():
            if has_quote(ev):
                total_quotes += 1
                eq = ev.get("exact_quote", ev.get("exact_quotes", ev.get("source_quote")))
                eq_str = " ".join(str(x) for x in eq) if isinstance(eq, list) else str(eq)
                if corpus and corpus.find(eq_str.strip()) != -1:
                    verified_quotes += 1
                elif corpus:
                    unverified_quotes += 1

        auth_rate = (verified_quotes / total_quotes * 100.0) if total_quotes > 0 else 100.0
        grounding_results_by_run.append(
            {
                "run_name": r_name,
                "has_corpus": bool(corpus),
                "total_quotes": total_quotes,
                "verified_quotes": verified_quotes,
                "unverified_quotes": unverified_quotes,
                "authenticity_rate": auth_rate,
            }
        )

    frozen_context_info = "Ei saatavilla"
    first_run_record: dict[str, Any] = (
        next((v for v in db_executions.values() if v.get("id") == loaded_runs[0]), {}) if loaded_runs else {}
    )
    frozen_data = first_run_record.get("frozen_context")

    if not frozen_data and loaded_paths:
        disk_frozen_path = loaded_paths[0].parent / "frozen_context.json"
        if disk_frozen_path.exists():
            try:
                with disk_frozen_path.open("r", encoding="utf-8") as f:
                    frozen_data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: frozen_context.json read error: {e}")

    if frozen_data and isinstance(frozen_data, dict):
        hints = frozen_data.get("ui_hints_snapshot", {})
        if hints:
            block_stats_by_run: list[dict[str, dict[str, int]]] = []
            for evals in evals_list:
                block_stats: dict[str, dict[str, int]] = {}
                for atom_id, ev in evals.items():
                    bid = atom_to_block.get(atom_id)
                    if bid:
                        if bid not in block_stats:
                            block_stats[bid] = {"PASS": 0, "FAIL": 0, "DLQ": 0, "OTHER": 0}
                        s = get_state(ev).lower()
                        if s in ["true", "pass", "passed"]:
                            block_stats[bid]["PASS"] += 1
                        elif s in ["false", "fail", "failed"]:
                            block_stats[bid]["FAIL"] += 1
                        elif s == "dlq":
                            block_stats[bid]["DLQ"] += 1
                        else:
                            block_stats[bid]["OTHER"] += 1
                block_stats_by_run.append(block_stats)

            frozen_lines: list[str] = []
            for block_id, conf in hints.items():
                opts = conf.get("options", [])
                label_fi = "Tuntematon"
                if opts and "label" in opts[0] and "translations" in opts[0]["label"]:
                    label_fi = opts[0]["label"]["translations"].get(
                        "fi", opts[0]["label"]["translations"].get("en", "Tuntematon")
                    )

                run_strs: list[str] = []
                total_evaluated = 0
                for r_idx, stats in enumerate(block_stats_by_run):
                    b_stat = stats.get(block_id, {})
                    pass_c = b_stat.get("PASS", 0)
                    fail_c = b_stat.get("FAIL", 0)
                    dlq_c = b_stat.get("DLQ", 0)

                    if pass_c > 0 or fail_c > 0 or dlq_c > 0:
                        total_evaluated += 1

                    dlq_str = f"|DLQ:{dlq_c}" if dlq_c > 0 else ""
                    run_strs.append(f"[R{r_idx + 1}: {pass_c}P/{fail_c}F{dlq_str}]")

                if total_evaluated == 0:
                    continue

                stats_str = " ".join(run_strs)
                frozen_lines.append(f"  - **{label_fi}** (`{block_id}`) - {stats_str}")
            if frozen_lines:
                frozen_context_info = "\n" + "\n".join(frozen_lines)

    # Per-run cost and token accumulator for FinOps section
    run_finops: list[dict[str, Any]] = []

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)\n\n")

        f.write("## Ympäristö ja Konteksti (Execution State)\n")
        if overall_health_passed:
            f.write(
                "> **✅ ONNISTUNUT (Kaikki kelvollista):** Kaikki vertaillut ajot ovat valmistuneet onnistuneesti "
                "(PASSED) ilman teknisiä kaatumisia, DLQ-pudotuksia tai aineiston näivettymistä (Data Starvation).\n\n"
            )
        else:
            f.write(
                "> **⚠️ HUOMIO (Suorituksessa havaittu poikkeamia):** Vertailluissa ajoissa havaittiin teknisiä "
                "virheitä, DLQ-pudotuksia, aineiston näivettymistä tai keskeneräisiä statuksia.\n\n"
            )

        if isolation_audit.is_fully_isolated:
            f.write(
                "> **✅ TÄYSI SYÖTE-ERISTYS (Ei välimuistivuotoa):** Kaikkien syötetiedostojen SHA-256-tiivisteet "
                "poikkesivat toisistaan ajojen välillä. Googlen prefiksipohjainen KV-välimuisti ei ole voinut "
                "siirtyä ajosta toiseen.\n\n"
            )
        else:
            shared_files_str = ", ".join(isolation_audit.shared_identical_files)
            f.write(
                f"> **⚠️ MAHDOLLINEN VÄLIMUISTIVUOTO:** Seuraavat syötetiedostot olivat täysin identtisiä "
                f"ajojen välillä: {shared_files_str}.\n\n"
            )

        if isolation_audit.disable_vertex_cache_active:
            f.write("- **Palvelintason välimuistikytkin:** `DISABLE_VERTEX_CACHE=true` (Aktiivinen)\n")
        else:
            f.write("- **Palvelintason välimuistikytkin:** `DISABLE_VERTEX_CACHE=false` (Oletustila / Ei pakotettu)\n")

        f.write(f"- **Git / Epic -tila:** {git_info}\n")
        f.write(f"- **Kriittiset järjestelmäarvot (Enums):**\n{sys_enums}\n")
        f.write("- **Vertailtavat ajot (R1, R2...):**\n")
        for idx, run_name in enumerate(loaded_runs):
            f.write(f"  - **R{idx + 1}:** `{run_name}`\n")
        f.write(f"- **Aktiiviset Säännöt ja Asetukset (Frozen Context):** {frozen_context_info}\n\n")

        f.write("## Ajojen Lähdetiedostot ja Syötteet\n")
        for idx, (run_name, exe_path) in enumerate(zip(loaded_runs, loaded_paths, strict=False)):
            abs_path = str(exe_path.resolve()).replace("\\", "/")
            f.write(f"- **Run {idx + 1}:** `{run_name}` (Lähde: [{exe_path}](file:///{abs_path}))\n")

            run_record: dict[str, Any] = next((v for v in db_executions.values() if v.get("id") == run_name), {})
            meta = run_record.get("metadata", {})
            exec_summary = meta.get("execution_summary", {})
            agg_usage = exec_summary.get("aggregated_usage", {})

            prompt_tok = int(
                run_record.get("prompt_tokens") or agg_usage.get("prompt_tokens") or meta.get("prompt_tokens") or 0
            )
            comp_tok = int(
                run_record.get("completion_tokens")
                or agg_usage.get("completion_tokens")
                or meta.get("completion_tokens")
                or 0
            )
            cached_tok = int(
                run_record.get("cached_tokens") or agg_usage.get("cached_tokens") or meta.get("cached_tokens") or 0
            )
            reas_tok = int(run_record.get("reasoning_tokens") or 0)
            dag_cost = float(run_record.get("dag_cost_usd") or meta.get("dag_cost_usd") or 0.0)
            synth_tok = int(run_record.get("cumulative_synthesis_tokens") or 0)
            synth_cost = float(run_record.get("cumulative_synthesis_cost") or 0.0)

            if prompt_tok == 0 and comp_tok == 0 and dag_cost == 0.0 and exe_path.exists():
                try:
                    with exe_path.open("r", encoding="utf-8") as tf:
                        trace_data = json.load(tf)
                    for ev in trace_data:
                        if isinstance(ev, dict) and isinstance(ev.get("content"), dict):
                            meta_step = ev["content"].get("_step_metadata")
                            if isinstance(meta_step, dict):
                                u = meta_step.get("token_usage")
                                if isinstance(u, dict):
                                    prompt_tok += int(u.get("prompt_tokens") or 0)
                                    comp_tok += int(u.get("completion_tokens") or 0)
                                    cached_tok += int(u.get("cached_tokens") or 0)
                                    reas_tok += int(u.get("reasoning_tokens") or 0)
                                    dag_cost += float(u.get("cost_usd") or 0.0)
                except (json.JSONDecodeError, OSError, TypeError, ValueError) as e:
                    print(f"Warning: execution_trace.json reading error for run {run_name}: {e}")

            combined_cost = dag_cost + synth_cost
            if combined_cost == 0.0 and run_record.get("cost_estimate"):
                combined_cost = float(run_record.get("cost_estimate") or 0.0)
            combined_tokens = prompt_tok + comp_tok + reas_tok + synth_tok

            run_dir = exe_path.parent
            telem_file = run_dir / "llm_telemetry.jsonl"
            cache_hit_count = 0
            total_calls = 0
            if telem_file.exists():
                try:
                    with telem_file.open("r", encoding="utf-8") as tf:
                        calls = [json.loads(line) for line in tf if line.strip()]
                        total_calls = len(calls)
                        if combined_tokens == 0:
                            combined_tokens = sum(c.get("tokens", 0) for c in calls)
                        cache_hit_count = sum(1 for c in calls if c.get("cache_hit"))
                except (json.JSONDecodeError, OSError, ValueError) as e:
                    print(f"Warning: llm_telemetry.jsonl reading error for run {run_name}: {e}")

            duration_ms = run_record.get("duration_ms", 0)
            if not duration_ms and telem_file.exists():
                try:
                    with telem_file.open("r", encoding="utf-8") as tf:
                        calls = [json.loads(line) for line in tf if line.strip()]
                        if len(calls) >= 2:
                            t0 = datetime.datetime.fromisoformat(calls[0]["timestamp"])
                            t1 = datetime.datetime.fromisoformat(calls[-1]["timestamp"])
                            duration_ms = int((t1 - t0).total_seconds() * 1000)
                except (json.JSONDecodeError, OSError, ValueError) as e:
                    print(f"Warning: duration parsing error from telemetry for run {run_name}: {e}")

            duration_str = (
                f"{duration_ms / 1000 / 60:.1f} minuuttia ({duration_ms / 1000:.1f} s)"
                if duration_ms
                else "Keskeytyi / Tuntematon"
            )

            db_models = run_record.get("models_used") or exec_summary.get("models_used", {})
            if db_models:
                models_formatted = ", ".join(f"{m} ({tok:,} tok)" for m, tok in db_models.items() if tok > 0)
            else:
                models_formatted = "gemini/gemini-3.7-flash"

            sys_snap = exec_summary.get("system_concurrency_snapshot", {})
            snap_str = ""
            if sys_snap:
                c_size = sys_snap.get("LLM_MAX_CHUNK_SIZE")
                m_eval = sys_snap.get("SCHEMA_MAX_EVALUATIONS")
                s_lim = sys_snap.get("MATRIX_SAMPLING_LIMIT")
                snap_str = f" (Chunk size: {c_size}, Max Evals: {m_eval}, Sampling: {s_lim})"

            with exe_path.open("r", encoding="utf-8") as exe_f:
                raw_data = exe_f.read()
            error_count = raw_data.count("Chunk Processing Failed") + raw_data.count("SYSTEM ERROR")
            dlq_count = raw_data.count('"_dlq_status": "FAILED/DLQ"')

            f.write(f"  - **Malli(t):** `{models_formatted}`{snap_str}\n")
            f.write(f"  - **Kesto:** `{duration_str}`\n")
            f.write(f"  - **API-kutsut:** `{total_calls}` kpl (Välimuistiosumat: `{cache_hit_count}/{total_calls}`)\n")
            f.write(
                f"  - **Tokenit:** `{combined_tokens:,}` (Syöte: `{prompt_tok:,}`, "
                f"Tuotos: `{comp_tok:,}`, Välimuisti: `{cached_tok:,}`, Synteesi: `{synth_tok:,}`)\n"
            )
            f.write(
                f"  - **Kustannusarvio:** `${combined_cost:.4f}` "
                f"(DAG: `${dag_cost:.4f}`, Synteesi: `${synth_cost:.4f}`)\n"
            )
            f.write(f"  - **Tekniset virheet (Crash):** `{error_count}` kpl\n")
            f.write(f"  - **DLQ-pudotetut atomit:** `{dlq_count}` kpl\n")

            is_starved = '"event_type": "starvation"' in raw_data or any(
                isinstance(s, dict) and s.get("data_starvation") is not None
                for s in run_record.get("profile_syntheses", {}).values()
            )
            if is_starved:
                f.write("  - **Kelvollisuus:** ⚠️ `KELVOTON (Data Starvation: Insufficient Data)`\n")
            else:
                f.write("  - **Kelvollisuus:** ✅ `KELVOLLINEN`\n")

            inputs_dir = run_dir / "inputs"
            if inputs_dir.is_dir():
                inputs_files = sorted([f.name for f in inputs_dir.iterdir() if f.is_file()])
                if inputs_files:
                    f.write("  - **Käytetyt syötetiedostot:**\n")
                    for in_file in inputs_files:
                        in_path = inputs_dir / in_file
                        abs_in = str(in_path.resolve()).replace("\\", "/")
                        info = _inspect_input_file(in_path)
                        f.write(
                            f"    - [{in_file}](file:///{abs_in}) "
                            f"(SHA-256: `{info['sha256'][:16]}...`, Variaatio: `{info['noise']}`)\n"
                        )

            run_finops.append(
                {
                    "run_name": run_name,
                    "prompt_tok": prompt_tok,
                    "comp_tok": comp_tok,
                    "cached_tok": cached_tok,
                    "total_tok": combined_tokens,
                    "cost_usd": combined_cost,
                }
            )
        f.write("\n")

        # Global Metrics & Benchmark Section
        f.write("## Globaalit Metriikat & Tieteellinen Luotettavuus (Kappa Benchmark)\n")
        f.write(f"- **Arvioitujen ajojen määrä ($M$):** {len(evals_list)}\n")
        f.write(f"- **Yhteisten arvioitujen atomien määrä ($N$):** {len(common_atoms)}\n")
        f.write(f"- **Havaittujen luokkien kirjo:** {', '.join(categories_list)}\n")
        f.write(f"- **Parittainen konsistenssi (Self-Consistency):** {global_consistency * 100:.2f} %\n")
        f.write(
            "  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti "
            "kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*\n"
        )
        f.write(f"- **Fleissin Kappa ($\\kappa_{{Fleiss}}$):** {global_kappa:.4f}\n")
        f.write(
            "  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan "
            "sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*\n"
        )
        if cohen_kappa_dto is not None:
            f.write(f"- **Cohenin Kappa ($\\kappa_{{Cohen}}$):** {cohen_kappa_dto.kappa:.4f}\n")
            f.write(f"- **Kappan Tieteellinen Tasoluokitus:** {cohen_kappa_dto.benchmark_category}\n")
            f.write(
                f"- **Keskivirhe (SE) ja 95 % Luottamusväli:** SE = `{cohen_kappa_dto.standard_error:.4f}`, "
                f"95% CI = `[{cohen_kappa_dto.ci_lower:.4f}, {cohen_kappa_dto.ci_upper:.4f}]`\n"
            )
            # Benchmark Comparison vs Human Expert
            if cohen_kappa_dto.kappa > 0.80:
                expert_comp = "Ylittää ihmisasiantuntijoiden tyypillisen tason (0.65–0.80) — huipputason luotettavuus."
            elif cohen_kappa_dto.kappa >= 0.65:
                expert_comp = (
                    "Vastaa ihmisasiantuntijoiden tyypillistä luotettavuusaluetta (0.65–0.80) — luotettava arviointi."
                )
            else:
                expert_comp = "Jää alle ihmisasiantuntijoiden tason (0.65–0.80) — vaatii lisäsääntöjen tarkennusta."
            f.write(f"- **Vertailu Ihmisasiantuntijoiden Benchmarkiin:** {expert_comp}\n")
            if cohen_kappa_dto.marginal_bias is not None:
                f.write(
                    f"- **Marginaalinen vinouma (Marginal Bias / Run 1 vs Run 2):** "
                    f"`{cohen_kappa_dto.marginal_bias:+.4f}`\n"
                )
        f.write(f"- **Keskimääräinen Shannonin Entropia:** {global_entropy:.4f}\n")
        f.write(
            "  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. "
            "Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*\n\n"
        )

        # 0-100 Difficulty Tier Breakdown
        f.write("## Skaalatasokohtainen Erimielisyysjakauma (0–100 Vaativuustasot)\n\n")
        f.write(
            "Atomit on normalisoitu emolohkonsa ääriarvojen perusteella universaalille 0–100 % vaativuusasteikolle. "
            "Tämä eliminoi eri pituisten asteikkojen (1–5 vs 1–6) aiheuttamat vertailuvirheet.\n\n"
        )
        f.write("| Normalisoitu Vaativuustaso (0–100 %) | Yhteensä Atomeja | Erimielisyydet | Konsistenssi (%) |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for sb in scale_breakdowns:
            f.write(
                f"| **{sb.tier_label}** | {sb.total_atoms} | {sb.mismatches} | {sb.consistency_rate * 100:.1f} % |\n"
            )
        f.write("\n")

        # Block Heatmap
        f.write("## Lohkokohtainen Erimielisyyskartta (Block Heatmap)\n\n")
        f.write(
            "Taulukko havainnollistaa, missä matriisilohkoissa ilmenee eniten arviointieroja ajojen välillä. "
            "Lohkot, joissa on eniten erimielisyyksiä, on nostettu kärkeen sääntöjen kirkastamista varten.\n\n"
        )
        f.write("| Lohko / Matriisi | Lohkon ID | Atomeja Yhteensä | Erimielisyydet | Konsistenssi (%) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")
        for bh in block_heatmaps:
            f.write(
                f"| **{bh.block_name}** | `{bh.block_id}` | {bh.total_atoms} | {bh.mismatches} | "
                f"{bh.consistency_rate * 100:.1f} % |\n"
            )
        f.write("\n")

        # Disagreement Root Cause Triage
        f.write("## Erimielisyyksien Juurisyydiagnoosi (Root Cause Triage)\n\n")
        f.write(
            "Kaikki erimielisyydet on luokiteltu deterministisesti neljään kategoriaan: "
            "1) Tiedonhaun aukko (yksi ajo löysi sitaatin, toinen ei), "
            "2) Päättelyn aukko (molemmat löysivät tai molemmilta puuttui, mutta päätös eri), "
            "3) Kontekstuaalinen ohitus, ja 4) Tekninen virhe / DLQ.\n\n"
        )
        f.write("| Erimielisyyden Juurisyy | Esiintymiskerrat | Osuus Erimielisyyksistä (%) |\n")
        f.write("| :--- | :---: | :---: |\n")
        tot_m = root_cause_breakdown.total_mismatches
        p_ret = (root_cause_breakdown.retrieval_gap_count / tot_m * 100) if tot_m > 0 else 0.0
        p_rea = (root_cause_breakdown.reasoning_gap_count / tot_m * 100) if tot_m > 0 else 0.0
        p_ovr = (root_cause_breakdown.contextual_override_count / tot_m * 100) if tot_m > 0 else 0.0
        p_tec = (root_cause_breakdown.technical_error_count / tot_m * 100) if tot_m > 0 else 0.0
        rc_ret = root_cause_breakdown.retrieval_gap_count
        rc_rea = root_cause_breakdown.reasoning_gap_count
        rc_ovr = root_cause_breakdown.contextual_override_count
        rc_tec = root_cause_breakdown.technical_error_count
        f.write(f"| 🔍 **Tiedonhaun aukko (Retrieval Gap)** | {rc_ret} | {p_ret:.1f} % |\n")
        f.write(f"| 🧠 **Päättelyn aukko (Reasoning Gap)** | {rc_rea} | {p_rea:.1f} % |\n")
        f.write(f"| ⚡ **Kontekstuaalinen ohitus (Contextual Override)** | {rc_ovr} | {p_ovr:.1f} % |\n")
        f.write(f"| 🛠️ **Tekninen virhe / DLQ (Technical Error)** | {rc_tec} | {p_tec:.1f} % |\n")
        f.write(f"| **Yhteensä** | **{tot_m}** | **100.0 %** |\n\n")

        # Macro Score Drift (0-100)
        f.write("## Makrotason Pistemäärä- ja Luottamusdiffit (Macro Score Drift 0–100)\n\n")
        f.write(
            "Lohkokohtaiset pistemäärät perustuvat ajojen `normalized_score` -kenttään (0–100 asteikko) "
            "sekä atomitason läpäisyasteeseen.\n\n"
        )
        f.write(
            "| Lohko / Matriisi | Run 1 Pisteet (0–100) | Run 2 Pisteet (0–100) | $\\Delta$ Pisteet | "
            "Run 1 Läpäisy | Run 2 Läpäisy | $\\Delta$ Läpäisy |\n"
        )
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for ms in macro_block_scores:
            s1_str = f"{ms.run1_normalized_score:.1f}" if ms.run1_normalized_score is not None else "-"
            s2_str = f"{ms.run2_normalized_score:.1f}" if ms.run2_normalized_score is not None else "-"
            d_str = f"{ms.delta_normalized_score:+.1f}" if ms.delta_normalized_score is not None else "-"
            p1_str = f"{ms.run1_pass_rate * 100:.1f} %"
            p2_str = f"{ms.run2_pass_rate * 100:.1f} %"
            dp_str = f"{ms.delta_pass_rate * 100:+.1f} %"
            f.write(f"| **{ms.block_name}** | {s1_str} | {s2_str} | {d_str} | {p1_str} | {p2_str} | {dp_str} |\n")
        f.write("\n")

        # FinOps & Cache Economics
        f.write("## FinOps & Välimuistisäästöt (Cache Economics & Cost Drift)\n\n")
        if len(run_finops) >= 2:
            r1 = run_finops[0]
            r2 = run_finops[1]
            c_diff = r2["cost_usd"] - r1["cost_usd"]
            # Cached token savings: Gemini 2.5 Flash caching discount is ~75% ($0.05625 per 1M cached tokens)
            r1_savings = (r1["cached_tok"] / 1_000_000) * 0.05625
            r2_savings = (r2["cached_tok"] / 1_000_000) * 0.05625
            diff_prompt = r2["prompt_tok"] - r1["prompt_tok"]
            diff_comp = r2["comp_tok"] - r1["comp_tok"]
            diff_cached = r2["cached_tok"] - r1["cached_tok"]
            diff_savings = r2_savings - r1_savings

            f.write("| FinOps -metriikka | Run 1 | Run 2 | $\\Delta$ (R2 - R1) |\n")
            f.write("| :--- | :---: | :---: | :---: |\n")
            f.write(f"| **Kokonaiskustannus ($)** | ${r1['cost_usd']:.4f} | ${r2['cost_usd']:.4f} | ${c_diff:+.4f} |\n")
            f.write(f"| **Syötetokenit (Prompt)** | {r1['prompt_tok']:,} | {r2['prompt_tok']:,} | {diff_prompt:+,} |\n")
            f.write(f"| **Tuotostokenit (Completion)** | {r1['comp_tok']:,} | {r2['comp_tok']:,} | {diff_comp:+,} |\n")
            f.write(
                f"| **Välimuistitokenit (Cached)** | {r1['cached_tok']:,} | {r2['cached_tok']:,} | {diff_cached:+,} |\n"
            )
            f.write(
                f"| **Välimuistin tuoma säästö ($)** | ${r1_savings:.4f} | ${r2_savings:.4f} | "
                f"{diff_savings:+.4f} |\n\n"
            )
        else:
            f.write("FinOps-vertailu vaatii vähintään kaksi suoritusta.\n\n")

        # Lexical Grounding Audit
        f.write("## Lainausten Aitoustarkastus (Lexical Grounding Audit)\n\n")
        f.write(
            "Kaikki mallin poimimat suorat sitaatit tarkastetaan sanatarkasti (`str.find`) suhteessa alkuperäisiin "
            "syötetiedostoihin chimera- ja hallusinaatioriskien varalta.\n\n"
        )
        f.write("| Ajo | Syötteet Saatavilla | Sitaatteja | Verifioidut | Vahvistamattomat | Aitoustaso (%) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for gr in grounding_results_by_run:
            c_avail = "✅ Kyllä" if gr["has_corpus"] else "❌ Ei (Inputs-kansio puuttuu)"
            f.write(
                f"| **{gr['run_name']}** | {c_avail} | {gr['total_quotes']} | "
                f"{gr['verified_quotes']} | {gr['unverified_quotes']} | {gr['authenticity_rate']:.1f} % |\n"
            )
        f.write("\n")

        # Shift States
        f.write("## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)\n")
        f.write(
            f"- **Erimielisyyttä näiden välillä:** "
            f"{len([a for a in common_atoms if get_state(evals_1[a]) != get_state(evals_2[a])])} kpl\n"
        )
        f.write(
            f"- **Contextual Override -lähtöiset erimielisyydet koko setissä:** "
            f"{contextual_override_mismatches} / {len(mismatching_atoms)}\n"
        )
        f.write(f"- **PASSED -> FAILED:** {summary_2way['PASSED->FAILED']}\n")
        f.write(f"- **FAILED -> PASSED:** {summary_2way['FAILED->PASSED']}\n")
        f.write(f"- **Muut siirtymät:** {summary_2way['Other']}\n\n")

        f.write("## Epävakaimmat Testitapaukset / Kysytyt Säännöt (Järjestetty Entropian mukaan)\n")
        f.write(
            "Alla on listattu kaikki säännöt ja kysymykset, joissa ilmeni erimielisyyttä tai epävakautta "
            "eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) "
            "ovat listan alussa.\n\n"
        )

        for atom in mismatching_atoms:
            entropy = atom_entropies[atom]
            consistency = atom_consistencies[atom]
            states = atom_states[atom]
            det = atom_details.get(atom, {})

            f.write(f"### Atom-ID: `{atom}` (Entropia: {entropy:.3f}, Konsistenssi: {consistency * 100:.1f}%)\n")
            if det:
                bname = det.get("block_name", "-")
                bid = det.get("block_id", "-")
                sname = det.get("scale_name", "-")
                sscore = det.get("scale_score", "-")
                f.write(f"- **Lohko / Matriisi:** `{bname}` (`{bid}`)\n")
                f.write(f"- **Skaala / Taso:** `{sname}` (Arvo: `{sscore}`)\n")
                if det.get("concept_description"):
                    f.write(f"- **Kysymys / Konsepti:** {det['concept_description']}\n")
                if det.get("extraction_rule"):
                    f.write(f"- **Etsintäsääntö (Extraction Rule):** {det['extraction_rule']}\n")
                if det.get("anchor_target"):
                    f.write(f"- **Ankkuritargetti (Anchor Target):** {det['anchor_target']}\n")
                if det.get("contrastive_example"):
                    f.write(f"- **Esimerkki (Contrastive Example):**\n```text\n{det['contrastive_example']}\n```\n")
            else:
                f.write(f"**Arviointisääntö:** {atom_rules.get(atom, 'Unknown')}\n")

            f.write("\n**Havaitut tilat ja mallin perustelut ajoittain:**\n")
            for run_idx, (run_name, state) in enumerate(zip(loaded_runs, states, strict=False)):
                eval_item = evals_list[run_idx][atom]
                trace_content = get_trace(eval_item).replace("\n", " ")
                override_tag = " **[CONTEXTUAL OVERRIDE]**" if uses_contextual_override(eval_item) else ""
                f.write(f"- **Run {run_idx + 1} ({run_name}) - [{state.upper()}]{override_tag}:**\n")
                f.write(f"  > *{trace_content}*\n")
            f.write("\n---\n\n")

    print(f"Done! Evaluated {len(common_atoms)} common atoms.")
    print(f"Mismatching atoms: {len(mismatching_atoms)}")
    if len(common_atoms) > 0:
        print(f"Variance: {(len(mismatching_atoms) / len(common_atoms)) * 100:.1f} %")
    summary_str = (
        f"PASSED->FAILED: {summary_2way['PASSED->FAILED']}, "
        f"FAILED->PASSED: {summary_2way['FAILED->PASSED']}, "
        f"Other: {summary_2way['Other']}"
    )
    print(summary_str)
    print(f"Global Self-Consistency: {global_consistency * 100:.2f}%")
    print(f"Fleiss Kappa: {global_kappa:.4f}")
    if cohen_kappa_dto is not None:
        print(f"Cohen's Kappa: {cohen_kappa_dto.kappa:.4f} ({cohen_kappa_dto.benchmark_category})")
        print(
            f"  95% CI: [{cohen_kappa_dto.ci_lower:.4f}, {cohen_kappa_dto.ci_upper:.4f}] "
            f"(SE: {cohen_kappa_dto.standard_error:.4f})"
        )
    print(f"Average Entropy: {global_entropy:.4f}")
    print(f"Report written to: {report_path}")
    return str(report_path)


def main() -> None:
    """CLI entry point for execution diff tool."""
    parser = argparse.ArgumentParser(description="Execution Trace Differential Analysis and Kappa Suite")
    parser.add_argument(
        "execution_ids",
        nargs="*",
        default=None,
        help="Execution IDs or directory paths to compare (defaults to latest 3 executions)",
    )
    args = parser.parse_args()
    cli_args = args.execution_ids if args.execution_ids else None
    run_diff(cli_args)


if __name__ == "__main__":
    main()
