"""Execution Trace Comparison and Consistency Metric Suite.

Provides forensic cross-execution differential analysis, Fleiss/Cohen Kappa metrics,
Shannon entropy calculations, and Markdown report synthesis.

Usage Examples:
    # 1. Compare specific executions by ID:
    uv run python scripts/diff_executions.py exe_6c9e2f3b2ea14f9d exe_f16d8b0e40e44316

    # 2. Compare executions by directory path:
    uv run python scripts/diff_executions.py \
        data/files/executions/exe_6c9e2f3b2ea14f9d data/files/executions/exe_f16d8b0e40e44316

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
import re
import subprocess
import sys
import unicodedata
from enum import StrEnum
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path before any local or third-party project imports
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.v2_core import ContrastivePairDTO
from backend_v2.settings import get_settings

__all__ = [
    "AtomEvaluationSnapshotDTO",
    "BlockHeatmapDTO",
    "DiffReportSnapshotDTO",
    "DisagreementRootCause",
    "EvidenceDistributionDTO",
    "InputFileInspectionDTO",
    "IsolationAuditDTO",
    "KappaMetricsDTO",
    "MacroBlockScoreDTO",
    "PhysicalModelBindingDTO",
    "PromptProvenanceDTO",
    "RootCauseBreakdownDTO",
    "ScaleBreakdownDTO",
    "TdaAtomDefinitionDTO",
    "TraceTelemetryDTO",
    "UNICODE_SPACE_REGISTRY",
    "UserDocumentationVolumeDTO",
    "WorkflowProvenanceDTO",
    "calculate_cohens_kappa",
    "calculate_entropy",
    "calculate_fleiss_kappa",
    "calculate_pairwise_consistency",
    "calculate_user_documentation_volume",
    "classify_disagreement",
    "classify_input_ontology",
    "extract_block_normalized_scores",
    "extract_block_scoring_diagnostics",
    "extract_evidence_distribution",
    "extract_trace_telemetry",
    "extract_workflow_provenance",
    "get_all_evals",
    "get_state",
    "get_trace",
    "has_quote",
    "main",
    "resolve_physical_model_bindings",
    "run_diff",
    "uses_contextual_override",
    "verify_quote_in_corpus",
]

# Phase 1, Step 1.5: Canonical SSOT for typographic Unicode space markers
UNICODE_SPACE_REGISTRY: dict[str, str] = {
    "\u00a0": "No-Break Space (U+00A0)",
    "\u2002": "En Space (U+2002)",
    "\u2003": "Em Space (U+2003)",
    "\u202f": "Narrow No-Break Space (U+202F)",
    "\u2004": "Three-Per-Em Space (U+2004)",
    "\u2005": "Four-Per-Em Space (U+2005)",
    "\u2006": "Six-Per-Em Space (U+2006)",
    "\u2007": "Figure Space (U+2007)",
    "\u2008": "Punctuation Space (U+2008)",
    "\u2009": "Thin Space (U+2009)",
    "\u200a": "Hair Space (U+200A)",
}

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
    run1_raw_score: float | None = None
    run2_raw_score: float | None = None
    delta_raw_score: float | None = None
    scale_min: float = 1.0
    scale_max: float = 5.0
    run1_waterfall_breakpoint: str | None = None
    run2_waterfall_breakpoint: str | None = None
    run1_level_breakdown: dict[str, int] = Field(default_factory=dict)
    run2_level_breakdown: dict[str, int] = Field(default_factory=dict)


class EvidenceDistributionDTO(BaseModel):
    """Immutable aggregate distribution of evaluation evidence classes per run."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    run_name: str
    empirical_quotes: int
    inverse_passes: int
    contextual_overrides: int
    demoted_by_policy: int
    failures: int
    total_evaluated: int


class WorkflowProvenanceDTO(BaseModel):
    """Immutable workflow provenance and governance switches snapshot."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    workflow_id: str
    name_fi: str
    name_en: str
    version: int
    enable_contextual_overrides: bool
    default_strictness_level: int
    total_active_steps: int
    total_workflow_atoms: int


class PhysicalModelBindingDTO(BaseModel):
    """Immutable resolved physical model binding and execution parameters."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    strategy_name: str
    physical_model: str
    temperature: float
    max_tokens: int
    thinking_budget: int = 0
    provider: str = ""
    tpm_limit: int | None = None
    rpm_limit: int | None = None
    reasoning_effort: str | None = None


class UserDocumentationVolumeDTO(BaseModel):
    """Immutable aggregated volume metrics across user-authored deliverable files."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    run_name: str
    total_words: int
    total_sentences: int
    total_characters: int
    total_paragraphs: int
    total_bullets: int
    user_file_count: int


# Phase 1, Step 1.4: Strongly typed, immutable input file inspection DTO
class InputFileInspectionDTO(BaseModel):
    """Immutable input file forensic inspection DTO."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    sha256: str
    noise: str
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    bullet_count: int
    normalized_text: str


class TraceTelemetryDTO(BaseModel):
    """Immutable execution trace telemetry container extracted from execution_trace.json."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_count: int
    cache_hit_count: int
    reasoning_tokens: int
    mcp_calls: int
    step_latencies: dict[str, int]
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    dag_cost: float = 0.0


class TdaAtomDefinitionDTO(BaseModel):
    """Immutable snapshot of the 13 canonical TDA parameters for an evaluated atom."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    atom_id: str
    block_id: str
    block_name: str
    scale_score: float
    scale_name: str
    concept_description: str
    extraction_rule: str | None = None
    anchor_target: str | None = None
    contrastive_example: ContrastivePairDTO | None = None
    anti_patterns: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    syntactic_anchors: list[str] = Field(default_factory=list)
    target_speaker: str = "USER"
    bounding_box_scope: str = "paragraph"
    inverse_evidence: bool = False
    evaluation_track: str = "COGNITIVE_JUDGEMENT"
    enforce_pre_flight: bool = False
    aggregation_mode: str = "EXISTS"


class AtomEvaluationSnapshotDTO(BaseModel):
    """Immutable single-run evaluation state snapshot for an atom."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    run_name: str
    state: str
    has_quote: bool
    quote_text: str
    quote_length: int
    quote_verified: bool
    contextual_override: bool
    reasoning_trace: str


class PromptProvenanceDTO(BaseModel):
    """Immutable snapshot of system directives, model bindings, and workflow provenance."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    directives_hash: str
    directives_char_count: int
    physical_models_by_run: dict[str, list[PhysicalModelBindingDTO]]
    workflow_provenance: WorkflowProvenanceDTO | None = None


class DiffReportSnapshotDTO(BaseModel):
    """Immutable aggregated archaeological benchmark snapshot across compared runs."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    execution_ids: list[str]
    timestamp: str
    global_consistency: float
    fleiss_kappa: float
    cohen_kappa: KappaMetricsDTO | None = None
    average_entropy: float
    total_common_atoms: int
    mismatch_count: int
    variance_rate: float
    summary_2way: dict[str, int]
    root_causes: RootCauseBreakdownDTO | None = None
    isolation_audit: IsolationAuditDTO | None = None
    scale_breakdowns: list[ScaleBreakdownDTO] = Field(default_factory=list)
    block_heatmaps: list[BlockHeatmapDTO] = Field(default_factory=list)
    macro_scores: list[MacroBlockScoreDTO] = Field(default_factory=list)
    evidence_distributions: list[EvidenceDistributionDTO] = Field(default_factory=list)
    prompt_provenance: PromptProvenanceDTO
    atom_definitions: dict[str, TdaAtomDefinitionDTO]
    all_evaluations: dict[str, list[AtomEvaluationSnapshotDTO]]
    environment: str = "development"
    dev_max_thinking_budget: int = 0
    ensemble_parallelism: int = 1
    matrix_sampling_strategy: str = "full"


def _extract_level_breakdown_counts(raw_levels: Any) -> dict[str, int]:
    """Normalize raw level breakdown into strictly typed dict[str, int] of hits per level.

    Args:
        raw_levels: Raw level breakdown mapping from trace or model.

    Returns:
        Mapping of scale level string to integer hit count.
    """
    if not isinstance(raw_levels, dict):
        return {}
    res: dict[str, int] = {}
    for k, v in raw_levels.items():
        if isinstance(v, dict):
            res[str(k)] = int(v.get("hits", 0))
        elif isinstance(v, (int, float)):
            res[str(k)] = int(v)
        elif isinstance(v, str):
            if "/" in v:
                try:
                    res[str(k)] = int(v.split("/")[0])
                except ValueError:
                    res[str(k)] = 0
            else:
                try:
                    res[str(k)] = int(v)
                except ValueError:
                    res[str(k)] = 0
    return res


def extract_trace_telemetry(trace_data: list[Any]) -> TraceTelemetryDTO:
    """Extract step counts, token usage, cache hits, MCP tool traces, and latencies from raw trace events.

    Args:
        trace_data: List of raw event dictionaries from execution_trace.json.

    Returns:
        TraceTelemetryDTO containing aggregated steps, tokens, cache hits, tool calls, and latencies.
    """
    step_count = 0
    cache_hit_count = 0
    reasoning_tokens = 0
    mcp_calls = 0
    step_latencies: dict[str, int] = {}
    first_ts: str | None = None
    last_ts: str | None = None
    prompt_tokens = 0
    completion_tokens = 0
    cached_tokens = 0
    dag_cost = 0.0

    for ev in trace_data:
        if not isinstance(ev, dict):
            continue
        etype = ev.get("event_type")
        content = ev.get("content")
        ev_meta = ev.get("metadata") or {}

        # Timestamps for duration fallback
        ts = None
        if isinstance(content, dict) and "_step_metadata" in content:
            ts = content["_step_metadata"].get("timestamp_isot")
        if not ts and "timestamp" in ev:
            ts = ev.get("timestamp")
        if ts:
            if not first_ts:
                first_ts = str(ts)
            last_ts = str(ts)

        # Extract MCP / tool call traces
        if etype == "decision":
            if isinstance(content, dict):
                mcp_traces = content.get("mcp_audit_traces")
                if isinstance(mcp_traces, list):
                    mcp_calls += len(mcp_traces)
            if isinstance(ev_meta, dict):
                mcp_traces = ev_meta.get("mcp_audit_traces")
                if isinstance(mcp_traces, list):
                    mcp_calls += len(mcp_traces)

        # Output steps FinOps and latency
        if etype == "output" and isinstance(content, dict):
            meta_step = content.get("_step_metadata")
            if isinstance(meta_step, dict):
                u = meta_step.get("token_usage")
                if isinstance(u, dict):
                    step_count += 1
                    c_tok = int(u.get("cached_tokens") or 0)
                    if c_tok > 0:
                        cache_hit_count += 1
                    r_tok = int(u.get("reasoning_tokens") or 0)
                    reasoning_tokens += r_tok
                    prompt_tokens += int(u.get("prompt_tokens") or 0)
                    completion_tokens += int(u.get("completion_tokens") or 0)
                    cached_tokens += c_tok
                    dag_cost += float(u.get("cost_usd") or 0.0)

            step_name = ev.get("step_name")
            if step_name and isinstance(ev_meta, dict) and "latency_ms" in ev_meta:
                step_latencies[step_name] = int(ev_meta["latency_ms"] or 0)

    return TraceTelemetryDTO(
        step_count=step_count,
        cache_hit_count=cache_hit_count,
        reasoning_tokens=reasoning_tokens,
        mcp_calls=mcp_calls,
        step_latencies=step_latencies,
        first_timestamp=first_ts,
        last_timestamp=last_ts,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cached_tokens=cached_tokens,
        dag_cost=dag_cost,
    )


def _inspect_input_file(file_path: Path) -> InputFileInspectionDTO:
    """Compute SHA-256 hash, detect injected Unicode noise variants, and analyze text volume/structure.

    Args:
        file_path: Path to the input file.

    Returns:
        InputFileInspectionDTO containing file inspection metadata, counts, and normalized text.
    """
    if not file_path.exists() or not file_path.is_file():
        return InputFileInspectionDTO(
            sha256="MISSING",
            noise="Missing",
            char_count=0,
            word_count=0,
            sentence_count=0,
            paragraph_count=0,
            bullet_count=0,
            normalized_text="",
        )

    raw_bytes = file_path.read_bytes()
    if not raw_bytes:
        return InputFileInspectionDTO(
            sha256=hashlib.sha256(b"").hexdigest(),
            noise="Empty",
            char_count=0,
            word_count=0,
            sentence_count=0,
            paragraph_count=0,
            bullet_count=0,
            normalized_text="",
        )

    text = raw_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")

    found_variants: list[str] = []
    for char, name in UNICODE_SPACE_REGISTRY.items():
        if char in text:
            found_variants.append(name)

    noise_desc = ", ".join(found_variants) if found_variants else "Standard ASCII"

    # Canonical normalization: Unicode NFKC + uniform whitespace standardization
    canonical_text = unicodedata.normalize("NFKC", text)
    canonical_text = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in canonical_text.splitlines()).strip()
    sha256_hash = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()

    char_count = len(text)
    word_count = len(text.split())
    sentences = [s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    sentence_count = len(sentences)
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    paragraph_count = len(paragraphs) if paragraphs else (1 if text.strip() else 0)
    bullet_count = sum(
        1
        for line in text.splitlines()
        if line.strip().startswith(("-", "*", "•"))
        or (len(line.strip()) > 2 and line.strip()[:2].isdigit() and line.strip()[2] == ".")
    )
    normalized_text = "".join(text.split())

    return InputFileInspectionDTO(
        sha256=sha256_hash,
        noise=noise_desc,
        char_count=char_count,
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        bullet_count=bullet_count,
        normalized_text=normalized_text,
    )


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
            benchmark_category="Heikko sopivuus (Fair / Poor Agreement)",
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
        benchmark_category = "Lähes täydellinen sopivuus (Almost Perfect Agreement)"
    elif kappa >= 0.61:
        benchmark_category = "Huomattava / Vahva sopivuus (Substantial Agreement)"
    elif kappa >= 0.41:
        benchmark_category = "Kohtalainen sopivuus (Moderate Agreement)"
    else:
        benchmark_category = "Heikko sopivuus (Fair / Poor Agreement)"

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


_HTML_TAG_PATTERN = re.compile(
    r"</?(?:br|p|div|span|b|strong|i|em|u|a|table|thead|tbody|tr|th|td|ul|ol|li|code|pre|blockquote|sub|sup|hr|img)\b[^>]*>|<!--.*?-->",
    re.IGNORECASE,
)
_MARKDOWN_DECORATOR_PATTERN = re.compile(r"\*\*|__|~~|(?<!\w)[*_~`]+|[*_~`]+(?!\w)")


def verify_quote_in_corpus(
    quote: str,
    corpus: str,
    norm_corpus: str | None = None,
    html_norm_corpus: str | None = None,
    md_norm_corpus: str | None = None,
) -> bool:
    """Verify whether an extracted quote exists in the corpus using tiered forensic search.

    Tier 1: Exact literal match (corpus.find).
    Tier 2: Whitespace-normalized match (collapsing newlines, tabs, and unicode spaces).
    Tier 3: HTML-tag-normalized match, substituting known HTML tags with space before whitespace normalization.
    Tier 4: Markdown-boundary-relaxed match, stripping markdown delimiters while preserving adjacent punctuation.

    Args:
        quote: Raw quote string extracted from LLM evaluation.
        corpus: Raw concatenated corpus text from input files.
        norm_corpus: Pre-normalized corpus text for O(1) matching, or computed on demand.
        html_norm_corpus: Pre-normalized HTML-stripped corpus for O(1) matching, or computed on demand.
        md_norm_corpus: Pre-normalized Markdown-stripped corpus for O(1) matching, or computed on demand.

    Returns:
        True if the quote is verified in corpus, False otherwise.
    """
    eq_clean = quote.strip()
    if not eq_clean or not corpus:
        return False

    # Quotes consisting exclusively of HTML tags and whitespace lack substantive text
    if not _HTML_TAG_PATTERN.sub("", eq_clean).strip():
        return False

    # 1. Tier 1: Exact literal match
    if corpus.find(eq_clean) != -1:
        return True

    # 2. Tier 2: Whitespace-normalized match (Unicode NFKC & Zero-Width stripped)
    eq_nfkc = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", eq_clean))
    norm_eq = " ".join(eq_nfkc.split())
    if not norm_eq:
        return False

    if norm_corpus is None:
        corpus_nfkc = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", corpus))
        norm_corpus = " ".join(corpus_nfkc.split())

    if norm_corpus.find(norm_eq) != -1:
        return True

    # 3. Tier 3: HTML-tag-normalized match (tags replaced with space)
    html_eq = " ".join(_HTML_TAG_PATTERN.sub(" ", eq_clean).split())
    if not html_eq:
        return False

    if html_norm_corpus is None:
        html_norm_corpus = " ".join(_HTML_TAG_PATTERN.sub(" ", corpus).split())

    if html_norm_corpus.find(html_eq) != -1:
        return True

    # 4. Tier 4: Markdown-boundary-relaxed match (decorators removed with empty string)
    md_eq = " ".join(_MARKDOWN_DECORATOR_PATTERN.sub("", _HTML_TAG_PATTERN.sub(" ", eq_clean)).split())
    if not md_eq:
        return False

    if md_norm_corpus is None:
        md_norm_corpus = " ".join(_MARKDOWN_DECORATOR_PATTERN.sub("", _HTML_TAG_PATTERN.sub(" ", corpus)).split())

    return md_norm_corpus.find(md_eq) != -1


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


def extract_block_scoring_diagnostics(trace_path: Path) -> dict[str, dict[str, Any]]:
    """Extract block-level raw scores, normalized scores, and waterfall diagnostics from trace.

    Args:
        trace_path: Path to execution_trace.json.

    Returns:
        Mapping of block ID to dict with normalized_score, raw_score, level_breakdown, waterfall_breakpoint.
    """
    diagnostics: dict[str, dict[str, Any]] = {}
    if not trace_path.exists():
        return diagnostics
    try:
        with trace_path.open("r", encoding="utf-8") as tf:
            trace = json.load(tf)
        for ev in trace:
            if isinstance(ev, dict) and isinstance(ev.get("content"), dict):
                content = ev["content"]
                for k, v in content.items():
                    if isinstance(v, dict) and "normalized_score" in v and v["normalized_score"] is not None:
                        try:
                            norm_sc = float(v["normalized_score"])
                            raw_sc = float(v["raw_score"]) if "raw_score" in v and v["raw_score"] is not None else None
                            levels = v.get("level_breakdown", {})

                            bp: str | None = None
                            if isinstance(levels, dict) and levels:
                                try:
                                    sorted_lvls = sorted(levels.keys(), key=lambda x: float(x))
                                    for lvl in sorted_lvls:
                                        stats = levels[lvl]
                                        if isinstance(stats, dict):
                                            hits = stats.get("hits", 0)
                                            tot = stats.get("total", 0)
                                            if hits < tot:
                                                bp = f"Taso {lvl} ({hits}/{tot} osumaa)"
                                                break
                                    if bp is None:
                                        bp = "Kaikki tasot läpäisty"
                                except ValueError, TypeError:
                                    pass

                            diagnostics[k] = {
                                "normalized_score": norm_sc,
                                "raw_score": raw_sc,
                                "level_breakdown": levels if isinstance(levels, dict) else {},
                                "waterfall_breakpoint": bp,
                            }
                        except ValueError, TypeError:
                            pass
    except json.JSONDecodeError, OSError:
        pass
    return diagnostics


def classify_input_ontology(filename: str) -> str:
    """Classify an input file into the Two-Tier Input Ontology.

    Candidate Deliverables (User Documentation):
        - chat_log_user_only (candidate steering prompts)
        - product_text (candidate deliverables)
        - reflection_text (candidate reflection)

    External Normative Context (Quarantined):
        - assignment_context (assignment briefs)
        - compliance_framework (regulatory framework)
        - source_evidence (empirical ground truth)
        - chat_log_ai_only (AI dialogue responses)

    Raw Combined:
        - chat_log (unseparated full conversation)

    Args:
        filename: Name of the input file.

    Returns:
        One of 'candidate_deliverable', 'external_context', or 'raw_log'.
    """
    fn = filename.lower()
    if "user_only" in fn or "product_text" in fn or "reflection_text" in fn:
        return "candidate_deliverable"
    if "assignment" in fn or "compliance" in fn or "source_evidence" in fn or "ai_only" in fn:
        return "external_context"
    if "chat_log" in fn and "user_only" not in fn and "ai_only" not in fn:
        return "raw_log"
    return "candidate_deliverable"


def calculate_user_documentation_volume(
    input_files: dict[str, InputFileInspectionDTO],
    run_name: str = "",
) -> UserDocumentationVolumeDTO:
    """Aggregate volume metrics across user-authored deliverable files only.

    Filters out external frameworks, assignment briefs, and AI-generated dialogue.

    Args:
        input_files: Mapping of filename to InputFileInspectionDTO.
        run_name: Name of the execution run.

    Returns:
        UserDocumentationVolumeDTO with sum of words, sentences, characters, paragraphs, bullets.
    """
    tot_words = 0
    tot_sentences = 0
    tot_chars = 0
    tot_paragraphs = 0
    tot_bullets = 0
    user_file_count = 0

    for fname, dto in input_files.items():
        if classify_input_ontology(fname) == "candidate_deliverable":
            tot_words += dto.word_count
            tot_sentences += dto.sentence_count
            tot_chars += dto.char_count
            tot_paragraphs += dto.paragraph_count
            tot_bullets += dto.bullet_count
            user_file_count += 1

    return UserDocumentationVolumeDTO(
        run_name=run_name,
        total_words=tot_words,
        total_sentences=tot_sentences,
        total_characters=tot_chars,
        total_paragraphs=tot_paragraphs,
        total_bullets=tot_bullets,
        user_file_count=user_file_count,
    )


def extract_workflow_provenance(seed: dict[str, Any], workflow_id: str | None) -> WorkflowProvenanceDTO | None:
    """Extract workflow provenance and governance switches snapshot from seed data.

    Args:
        seed: Complete seed data dictionary containing workflows, steps, and prompt blocks.
        workflow_id: Target workflow ID to resolve.

    Returns:
        WorkflowProvenanceDTO containing metadata and total atom population, or None if not resolvable.
    """
    workflows = seed.get("workflows", [])
    if not workflows:
        return None

    target_wf: dict[str, Any] | None = None
    if workflow_id:
        target_wf = next((w for w in workflows if w.get("id") == workflow_id), None)
    if target_wf is None and workflows:
        target_wf = workflows[0]

    if target_wf is None:
        return None

    wf_id = str(target_wf.get("id", ""))
    name_dict = target_wf.get("name", {})
    if isinstance(name_dict, dict):
        translations = name_dict.get("translations", {})
        name_fi = str(translations.get("fi") or target_wf.get("slug") or wf_id)
        name_en = str(translations.get("en") or target_wf.get("slug") or wf_id)
    else:
        name_fi = str(name_dict or target_wf.get("slug") or wf_id)
        name_en = name_fi

    version = int(target_wf.get("version", 1))
    enable_contextual_overrides = bool(target_wf.get("enable_contextual_overrides", False))
    default_strictness_level = int(target_wf.get("default_strictness_level", 50))
    steps = target_wf.get("steps", [])
    total_active_steps = len(steps)

    step_blueprints = {s["id"]: s for s in seed.get("steps", []) if isinstance(s, dict) and "id" in s}
    prompt_blocks_map = {b["id"]: b for b in seed.get("prompt_blocks", []) if isinstance(b, dict) and "id" in b}

    wf_criteria_blocks: set[str] = set()
    for st in steps:
        if isinstance(st, dict):
            bp_id = st.get("task_blueprint")
            bp = step_blueprints.get(bp_id)
            if bp:
                for bid in bp.get("criteria_block_ids", []):
                    wf_criteria_blocks.add(bid)

    total_atoms = 0
    for bid in wf_criteria_blocks:
        blk = prompt_blocks_map.get(bid)
        if blk:
            for sc in blk.get("scales", []):
                for cl in sc.get("claims", []):
                    total_atoms += len(cl.get("tda_assertions", []))

    return WorkflowProvenanceDTO(
        workflow_id=wf_id,
        name_fi=name_fi,
        name_en=name_en,
        version=version,
        enable_contextual_overrides=enable_contextual_overrides,
        default_strictness_level=default_strictness_level,
        total_active_steps=total_active_steps,
        total_workflow_atoms=total_atoms,
    )


def resolve_physical_model_bindings(seed: dict[str, Any], registry_id: str) -> list[PhysicalModelBindingDTO]:
    """Resolve physical model bindings and execution hyperparameters from system config for a specific registry.

    Args:
        seed: Complete seed data dictionary containing system_config.
        registry_id: Mandatory identifier of the target ModelRegistry (e.g. 'sys_e26807f3bfa3454d').

    Returns:
        List of PhysicalModelBindingDTOs for active strategies (e.g. fast, reasoning, synthesis).

    Raises:
        ResourceNotFoundError: If the model registry or its tier bindings cannot be found in seed.
    """
    if not registry_id or not registry_id.strip():
        raise ResourceNotFoundError(
            resource_type="ModelRegistry",
            resource_id="",
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    sys_configs = seed.get("system_config", [])
    configs_list: list[dict[str, Any]] = []
    if isinstance(sys_configs, dict):
        configs_list = [v for v in sys_configs.values() if isinstance(v, dict)]
    elif isinstance(sys_configs, list):
        configs_list = [v for v in sys_configs if isinstance(v, dict)]

    target_cfg = next(
        (cfg for cfg in configs_list if cfg.get("id") == registry_id and cfg.get("type") == "model_registry"),
        None,
    )

    if not target_cfg:
        raise ResourceNotFoundError(
            resource_type="ModelRegistry",
            resource_id=registry_id,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    bindings: list[PhysicalModelBindingDTO] = []
    tier_defs = target_cfg.get("tier_definitions")
    default_provider = str(target_cfg.get("default_provider", "google"))

    if isinstance(tier_defs, dict):
        ordered_tiers = ["fast", "balanced", "deep", "reasoning"]
        is_direct = any(t in tier_defs for t in ordered_tiers)
        if is_direct:
            for tier_name in ordered_tiers:
                if tier_name in tier_defs and isinstance(tier_defs[tier_name], dict):
                    model_cfg = tier_defs[tier_name]
                    add_params = model_cfg.get("additional_params", {})
                    reasoning_effort = add_params.get("reasoning_effort") if isinstance(add_params, dict) else None
                    provider_val = str(model_cfg["provider"]) if "provider" in model_cfg else default_provider
                    if not any(b.strategy_name == tier_name for b in bindings):
                        bindings.append(
                            PhysicalModelBindingDTO(
                                strategy_name=tier_name,
                                physical_model=str(model_cfg.get("model_name", "unknown")),
                                temperature=float(model_cfg.get("temperature", 0.0)),
                                max_tokens=int(model_cfg.get("max_tokens", 32768)),
                                thinking_budget=int(model_cfg.get("thinking_budget_tokens", 0) or 0),
                                provider=provider_val,
                                tpm_limit=int(model_cfg["tpm_limit"])
                                if model_cfg.get("tpm_limit") is not None
                                else None,
                                rpm_limit=int(model_cfg["rpm_limit"])
                                if model_cfg.get("rpm_limit") is not None
                                else None,
                                reasoning_effort=reasoning_effort,
                            )
                        )
        else:
            for provider_name, tiers in tier_defs.items():
                if isinstance(tiers, dict):
                    for tier_name in ordered_tiers:
                        if tier_name in tiers and isinstance(tiers[tier_name], dict):
                            model_cfg = tiers[tier_name]
                            add_params = model_cfg.get("additional_params", {})
                            reasoning_effort = (
                                add_params.get("reasoning_effort") if isinstance(add_params, dict) else None
                            )
                            bindings.append(
                                PhysicalModelBindingDTO(
                                    strategy_name=f"{tier_name} ({provider_name})",
                                    physical_model=str(model_cfg.get("model_name", "unknown")),
                                    temperature=float(model_cfg.get("temperature", 0.0)),
                                    max_tokens=int(model_cfg.get("max_tokens", 32768)),
                                    thinking_budget=int(model_cfg.get("thinking_budget_tokens", 0) or 0),
                                    provider=str(provider_name),
                                    tpm_limit=int(model_cfg["tpm_limit"])
                                    if model_cfg.get("tpm_limit") is not None
                                    else None,
                                    rpm_limit=int(model_cfg["rpm_limit"])
                                    if model_cfg.get("rpm_limit") is not None
                                    else None,
                                    reasoning_effort=reasoning_effort,
                                )
                            )

    models = target_cfg.get("models", {})
    if isinstance(models, dict):
        ordered_keys = ["fast", "reasoning", "synthesis", "deep", "strict"]
        all_keys = [k for k in ordered_keys if k in models] + [k for k in models if k not in ordered_keys]
        for strat_name in all_keys:
            model_cfg = models[strat_name]
            if isinstance(model_cfg, dict):
                add_params = model_cfg.get("additional_params", {})
                reasoning_effort = add_params.get("reasoning_effort") if isinstance(add_params, dict) else None
                provider_val = str(model_cfg["provider"]) if "provider" in model_cfg else default_provider
                bindings.append(
                    PhysicalModelBindingDTO(
                        strategy_name=strat_name,
                        physical_model=str(model_cfg.get("model_name", "unknown")),
                        temperature=float(model_cfg.get("temperature", 0.0)),
                        max_tokens=int(model_cfg.get("max_tokens", 32768)),
                        thinking_budget=int(model_cfg.get("thinking_budget_tokens", 0) or 0),
                        provider=provider_val,
                        tpm_limit=int(model_cfg["tpm_limit"]) if model_cfg.get("tpm_limit") is not None else None,
                        rpm_limit=int(model_cfg["rpm_limit"]) if model_cfg.get("rpm_limit") is not None else None,
                        reasoning_effort=reasoning_effort,
                    )
                )

    strat_names = {b.strategy_name for b in bindings}
    if "synthesis" not in strat_names:
        synth_source = next((b for b in bindings if b.strategy_name in ("deep", "balanced", "reasoning")), None)
        if synth_source:
            bindings.append(
                PhysicalModelBindingDTO(
                    strategy_name="synthesis",
                    physical_model=synth_source.physical_model,
                    temperature=0.3,
                    max_tokens=synth_source.max_tokens,
                    thinking_budget=2048,
                    provider=synth_source.provider,
                    tpm_limit=synth_source.tpm_limit,
                    rpm_limit=synth_source.rpm_limit,
                    reasoning_effort=synth_source.reasoning_effort,
                )
            )

    if not bindings:
        raise ResourceNotFoundError(
            resource_type="ModelTierDefinitions",
            resource_id=registry_id,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    return bindings


def extract_evidence_distribution(
    evals: dict[str, dict[str, Any]],
    atom_details: dict[str, dict[str, Any]] | None = None,
    enable_contextual_overrides: bool = True,
    run_name: str = "",
) -> EvidenceDistributionDTO:
    """Aggregate distribution of evaluation evidence classes per execution run.

    Counts:
        - empirical_quotes: passed with verified quotes
        - inverse_passes: null hypothesis passed assertions without quotes
        - contextual_overrides: subjective overrides without quotes
        - demoted_by_policy: demoted because overrides were disabled
        - failures: failed assertions

    Args:
        evals: Mapping of atom ID to evaluation dictionaries.
        atom_details: Optional mapping of atom ID to prompt block atom definitions.
        enable_contextual_overrides: Workflow governance switch.
        run_name: Name of the execution run.

    Returns:
        EvidenceDistributionDTO containing counts for each evidence class.
    """
    empirical_quotes = 0
    inverse_passes = 0
    contextual_overrides = 0
    demoted_by_policy = 0
    failures = 0
    details_map = atom_details or {}

    passed_states = {"true", "passed", "1", "pass"}

    for aid, ev in evals.items():
        st = get_state(ev).lower()
        is_passed = st in passed_states
        has_q = has_quote(ev)
        det = details_map.get(aid, {})
        is_inv = bool(ev.get("is_inverse_evidence") or det.get("inverse_evidence", False))
        is_ovr = bool(ev.get("contextual_override") or uses_contextual_override(ev))
        was_demoted = bool(
            ev.get("demoted_by_override_policy") or (is_ovr and not is_inv and not enable_contextual_overrides)
        )

        if was_demoted:
            demoted_by_policy += 1
        elif not is_passed:
            failures += 1
        else:
            if is_inv and not has_q:
                inverse_passes += 1
            elif is_ovr and not is_inv:
                contextual_overrides += 1
            elif has_q:
                empirical_quotes += 1
            else:
                empirical_quotes += 1

    return EvidenceDistributionDTO(
        run_name=run_name,
        empirical_quotes=empirical_quotes,
        inverse_passes=inverse_passes,
        contextual_overrides=contextual_overrides,
        demoted_by_policy=demoted_by_policy,
        failures=failures,
        total_evaluated=len(evals),
    )


def _ensure_trace_file(trace_file: Path, run_name: str) -> bool:
    """Ensure trace_file exists on disk, reconstituting from db_v2.json if needed.

    Args:
        trace_file: Target path to execution_trace.json.
        run_name: Execution ID (e.g. exe_...).

    Returns:
        True if trace_file exists or was successfully reconstituted, False otherwise.
    """
    if trace_file.exists():
        return True
    db_path = Path("data/db_v2.json")
    if not db_path.exists():
        return False
    try:
        with db_path.open("r", encoding="utf-8") as db_f:
            db_data = json.load(db_f)
        exec_record = next(
            (rec for rec in db_data.get("executions", {}).values() if rec.get("id") == run_name),
            None,
        )
        if exec_record and "execution_trace" in exec_record:
            trace_file.parent.mkdir(parents=True, exist_ok=True)
            with trace_file.open("w", encoding="utf-8") as tf:
                json.dump(exec_record["execution_trace"], tf, indent=2)
            return True
    except json.JSONDecodeError, OSError:
        pass
    return False


def run_diff(execution_ids: list[str] | None = None, output_file: str | Path | None = None) -> str:
    """Perform differential analysis between execution traces and generate Markdown report.

    Args:
        execution_ids: Optional list of execution IDs or directory paths to compare.
        output_file: Optional explicit file path to write the differential Markdown report.

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

            if _ensure_trace_file(trace_file, name):
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
        for d in exe_dirs:
            trace_file = d / "execution_trace.json"
            if _ensure_trace_file(trace_file, d.name):
                evals_list.append(get_all_evals(trace_file))
                loaded_runs.append(d.name)
                loaded_paths.append(trace_file)
                if len(loaded_runs) >= 3:
                    break

    if len(evals_list) < 1:
        print("Error: At least one execution is required for analysis.")
        sys.exit(1)

    print(f"Loaded {len(evals_list)} executions for comparison:")
    for idx, name in enumerate(loaded_runs):
        print(f"  Run {idx + 1}: {name}")

    common_atoms = set(evals_list[0].keys())
    for evals in evals_list[1:]:
        common_atoms = common_atoms.intersection(set(evals.keys()))

    if not common_atoms:
        print(
            "[WARNING] Zero common atoms found across compared executions (likely due to dev sampling). "
            "Generating macro telemetry and diagnostic report without atom-level kappa metrics."
        )

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
    atom_definitions: dict[str, TdaAtomDefinitionDTO] = {}

    for block in seed.get("prompt_blocks", []):
        bid = block.get("id")
        bname_raw = block.get("label") or block.get("name")
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
                    c_ex = tda.get("contrastive_example")
                    contrastive_pair_dto: ContrastivePairDTO | None = None
                    contrastive_pair_dict: dict[str, str] | None = None
                    if isinstance(c_ex, dict) and c_ex.get("acceptable") and c_ex.get("rejected"):
                        try:
                            contrastive_pair_dto = ContrastivePairDTO(
                                acceptable=str(c_ex["acceptable"]),
                                rejected=str(c_ex["rejected"]),
                            )
                            contrastive_pair_dict = {
                                "acceptable": contrastive_pair_dto.acceptable,
                                "rejected": contrastive_pair_dto.rejected,
                            }
                        except ValidationError:
                            contrastive_pair_dto = None
                            contrastive_pair_dict = None

                    raw_anti = tda.get("anti_patterns", [])
                    anti_patterns: list[str] = []
                    if isinstance(raw_anti, list):
                        for ap in raw_anti:
                            if isinstance(ap, dict) and "pattern" in ap:
                                anti_patterns.append(str(ap["pattern"]))
                            elif isinstance(ap, str) and ap.strip():
                                anti_patterns.append(ap.strip())

                    raw_crit = tda.get("acceptance_criteria", [])
                    acceptance_criteria: list[str] = []
                    if isinstance(raw_crit, list):
                        for ac in raw_crit:
                            if isinstance(ac, dict) and "instruction" in ac:
                                acceptance_criteria.append(str(ac["instruction"]))
                            elif isinstance(ac, str) and ac.strip():
                                acceptance_criteria.append(ac.strip())

                    raw_anchors = tda.get("syntactic_anchors", [])
                    syntactic_anchors: list[str] = (
                        [str(x) for x in raw_anchors if x] if isinstance(raw_anchors, list) else []
                    )

                    target_speaker = str(tda.get("target_speaker") or "USER")
                    bounding_box_scope = str(tda.get("bounding_box_scope") or "paragraph")
                    inverse_evidence = bool(tda.get("inverse_evidence", False))
                    evaluation_track = str(tda.get("evaluation_track") or "COGNITIVE_JUDGEMENT")
                    enforce_pre_flight = bool(tda.get("enforce_pre_flight", False))
                    aggregation_mode = str(tda.get("aggregation_mode") or "EXISTS")

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
                        "contrastive_example": contrastive_pair_dict,
                        "inverse_evidence": inverse_evidence,
                        "bounding_box_scope": bounding_box_scope,
                    }
                    if bid:
                        atom_to_block[tid] = bid

                    atom_definitions[tid] = TdaAtomDefinitionDTO(
                        atom_id=tid,
                        block_id=bid or "",
                        block_name=bname or bid or "",
                        scale_score=float(scale.get("score") or 0.0),
                        scale_name=sname,
                        concept_description=desc,
                        extraction_rule=rule if rule else None,
                        anchor_target=anchor if anchor else None,
                        contrastive_example=contrastive_pair_dto,
                        anti_patterns=anti_patterns,
                        acceptance_criteria=acceptance_criteria,
                        syntactic_anchors=syntactic_anchors,
                        target_speaker=target_speaker,
                        bounding_box_scope=bounding_box_scope,
                        inverse_evidence=inverse_evidence,
                        evaluation_track=evaluation_track,
                        enforce_pre_flight=enforce_pre_flight,
                        aggregation_mode=aggregation_mode,
                    )

    valid_common_atoms: set[str] = set()
    for atom in common_atoms:
        traces = [get_trace(evals[atom]) for evals in evals_list]
        if any("[SYSTEM ERROR" in t or "Chunk Processing Failed" in t for t in traces):
            continue
        valid_common_atoms.add(atom)

    common_atoms = valid_common_atoms

    # Ensure all common atoms have a TdaAtomDefinitionDTO entry even if missing from seed
    for atom in common_atoms:
        if atom not in atom_definitions:
            atom_definitions[atom] = TdaAtomDefinitionDTO(
                atom_id=atom,
                block_id=atom_to_block.get(atom, "blk_unknown"),
                block_name=atom_to_block.get(atom, "Unknown Block"),
                scale_score=1.0,
                scale_name="Scale 1",
                concept_description=atom_rules.get(atom, f"Evaluation atom {atom}"),
                extraction_rule=None,
                anchor_target=None,
                contrastive_example=None,
                anti_patterns=[],
                acceptance_criteria=[],
                syntactic_anchors=[],
                target_speaker="USER",
                bounding_box_scope="paragraph",
                inverse_evidence=False,
                evaluation_track="COGNITIVE_JUDGEMENT",
                enforce_pre_flight=False,
                aggregation_mode="EXISTS",
            )

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
    if common_atoms:
        global_kappa = calculate_fleiss_kappa(all_atom_states, categories_list)
        global_consistency = sum(atom_consistencies.values()) / len(common_atoms)
        global_entropy = sum(atom_entropies.values()) / len(common_atoms)
    else:
        global_kappa = 0.0
        global_consistency = 0.0
        global_entropy = 0.0

    cohen_kappa_dto: KappaMetricsDTO | None = None
    if len(evals_list) == 2 and common_atoms:
        try:
            cohen_kappa_dto = calculate_cohens_kappa(all_atom_states, categories_list)
        except (ValueError, ZeroDivisionError) as e:
            print(f"Warning: Cohen's Kappa calculation error: {e}")

    mismatching_atoms = [atom for atom, entropy in atom_entropies.items() if entropy > 0]
    mismatching_atoms.sort(key=lambda a: atom_entropies[a], reverse=True)

    summary_2way = {"PASSED->FAILED": 0, "FAILED->PASSED": 0, "Other": 0}
    evals_1 = evals_list[0]
    evals_2 = evals_list[1] if len(evals_list) > 1 else {}
    passed_states = ["true", "passed", "1"]
    failed_states = ["false", "failed", "0"]

    if len(evals_list) >= 2:
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
    if len(evals_list) >= 2:
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

    if output_file:
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
    else:
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
        import backend_v2.models.enums as enums

        def _format_enum(enum_cls: Any) -> str:
            return ", ".join(f"{item.name} = {item.value}" for item in enum_cls)

        sys_enums = (
            f"  - **ExecutionStatus**: {_format_enum(enums.ExecutionStatus)}\n"
            f"  - **VerificationResult**: {_format_enum(enums.VerificationResult)}\n"
            f"  - **EvaluationRunCount**: {_format_enum(enums.EvaluationRunCount)}\n"
            f"  - **EvaluationCategory**: {_format_enum(enums.EvaluationCategory)}\n"
            f"  - **StrictnessAnchor**: {_format_enum(enums.StrictnessAnchor)}\n"
            f"  - **LLMProviderName**: {_format_enum(enums.LLMProviderName)}\n"
            f"  - **LLMCachingStrategy**: {_format_enum(enums.LLMCachingStrategy)}"
        )

        try:
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
    run1_diag = extract_block_scoring_diagnostics(loaded_paths[0]) if loaded_paths else {}
    run2_diag = extract_block_scoring_diagnostics(loaded_paths[1]) if len(loaded_paths) > 1 else {}

    macro_block_scores: list[MacroBlockScoreDTO] = []
    for bid, bname in blocks_in_play.items():
        b_atoms = [a for a in common_atoms if atom_details.get(a, {}).get("block_id") == bid]
        b_total = len(b_atoms)
        if b_total == 0:
            continue
        r1_pass = sum(1 for a in b_atoms if a in evals_1 and get_state(evals_1[a]) in passed_states) / b_total
        r2_pass = (
            (sum(1 for a in b_atoms if a in evals_2 and get_state(evals_2[a]) in passed_states) / b_total)
            if evals_2
            else r1_pass
        )
        r1_norm = run1_scores.get(bid)
        r2_norm = run2_scores.get(bid)
        d_norm = (r2_norm - r1_norm) if (r1_norm is not None and r2_norm is not None) else None

        d1 = run1_diag.get(bid, {})
        d2 = run2_diag.get(bid, {})
        r1_raw = d1.get("raw_score")
        r2_raw = d2.get("raw_score")
        d_raw = (r2_raw - r1_raw) if (r1_raw is not None and r2_raw is not None) else None
        b_min, b_max = block_extrema.get(bid, (1.0, 5.0))
        delta_p = (r2_pass - r1_pass) if evals_2 else 0.0

        macro_block_scores.append(
            MacroBlockScoreDTO(
                block_id=bid,
                block_name=bname,
                run1_normalized_score=r1_norm,
                run2_normalized_score=r2_norm,
                delta_normalized_score=d_norm,
                run1_pass_rate=r1_pass,
                run2_pass_rate=r2_pass,
                delta_pass_rate=delta_p,
                run1_raw_score=r1_raw,
                run2_raw_score=r2_raw,
                delta_raw_score=d_raw,
                scale_min=b_min,
                scale_max=b_max,
                run1_waterfall_breakpoint=d1.get("waterfall_breakpoint"),
                run2_waterfall_breakpoint=d2.get("waterfall_breakpoint"),
                run1_level_breakdown=_extract_level_breakdown_counts(d1.get("level_breakdown")),
                run2_level_breakdown=_extract_level_breakdown_counts(d2.get("level_breakdown")),
            )
        )

    # Lexical Grounding Audit
    run_corpuses: list[str] = []
    run_norm_corpuses: list[str] = []
    run_html_norm_corpuses: list[str] = []
    run_md_norm_corpuses: list[str] = []
    grounding_results_by_run: list[dict[str, Any]] = []
    for idx, (r_name, p) in enumerate(zip(loaded_runs, loaded_paths, strict=False)):
        run_in_dir = p.parent / "inputs"
        corpus = ""
        norm_corpus = ""
        html_norm_corpus = ""
        md_norm_corpus = ""
        if run_in_dir.is_dir():
            corpus_parts: list[str] = []
            for in_f in sorted(run_in_dir.iterdir()):
                if in_f.is_file():
                    try:
                        corpus_parts.append(in_f.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        pass
            corpus = "\n".join(corpus_parts)
            corpus_nfkc = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", corpus))
            norm_corpus = " ".join(corpus_nfkc.split())
            html_norm_corpus = " ".join(_HTML_TAG_PATTERN.sub(" ", corpus_nfkc).split())
            md_norm_corpus = " ".join(
                _MARKDOWN_DECORATOR_PATTERN.sub("", _HTML_TAG_PATTERN.sub(" ", corpus_nfkc)).split()
            )
        run_corpuses.append(corpus)
        run_norm_corpuses.append(norm_corpus)
        run_html_norm_corpuses.append(html_norm_corpus)
        run_md_norm_corpuses.append(md_norm_corpus)

        ev_map = evals_list[idx]
        total_quotes = 0
        verified_quotes = 0
        unverified_quotes = 0
        for _atom_id, ev in ev_map.items():
            if has_quote(ev):
                total_quotes += 1
                eq = ev.get("exact_quote", ev.get("exact_quotes", ev.get("source_quote")))
                eq_str = " ".join(str(x) for x in eq) if isinstance(eq, list) else str(eq)
                if verify_quote_in_corpus(
                    eq_str,
                    corpus,
                    norm_corpus,
                    html_norm_corpus=html_norm_corpus,
                    md_norm_corpus=md_norm_corpus,
                ):
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

    all_evaluations: dict[str, list[AtomEvaluationSnapshotDTO]] = {}
    for atom in sorted(list(common_atoms)):
        atom_snapshots: list[AtomEvaluationSnapshotDTO] = []
        for r_idx, (r_name, evals) in enumerate(zip(loaded_runs, evals_list, strict=False)):
            ev = evals.get(atom, {})
            st = get_state(ev)
            has_q = has_quote(ev)
            eq = ev.get("exact_quote", ev.get("exact_quotes", ev.get("source_quote")))
            if isinstance(eq, list):
                eq_text = " ".join(str(x) for x in eq)
            elif eq is not None:
                eq_text = str(eq)
            else:
                eq_text = ""

            is_verified = False
            if has_q and eq_text:
                is_verified = verify_quote_in_corpus(
                    eq_text,
                    run_corpuses[r_idx],
                    run_norm_corpuses[r_idx],
                    html_norm_corpus=run_html_norm_corpuses[r_idx],
                    md_norm_corpus=run_md_norm_corpuses[r_idx],
                )

            atom_snapshots.append(
                AtomEvaluationSnapshotDTO(
                    run_name=r_name,
                    state=st,
                    has_quote=has_q,
                    quote_text=eq_text,
                    quote_length=len(eq_text),
                    quote_verified=is_verified,
                    contextual_override=uses_contextual_override(ev),
                    reasoning_trace=get_trace(ev),
                )
            )
        all_evaluations[atom] = atom_snapshots

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

        if not common_atoms:
            f.write(
                "> [!WARNING]\n"
                "> **Yhteisiä arvioituja atomeja ei löytynyt "
                "(Zero common atoms found across compared executions, likely due to dev sampling).**\n"
                "> Makrotason telemetria, kustannusarviot ja diagnostiikkaraportti generoitu "
                "ilman atomitason kappa-metriikoita.\n\n"
            )

        f.write("## Ympäristö ja Konteksti (Execution State)\n")
        if overall_health_passed:
            f.write(
                "> **[ONNISTUNUT] (Kaikki kelvollista):** Kaikki vertaillut ajot ovat valmistuneet onnistuneesti "
                "(PASSED) ilman teknisiä kaatumisia, DLQ-pudotuksia tai aineiston näivettymistä (Data Starvation).\n\n"
            )
        else:
            f.write(
                "> **[HUOMIO] (Suorituksessa havaittu poikkeamia):** Vertailluissa ajoissa havaittiin teknisiä "
                "virheitä, DLQ-pudotuksia, aineiston näivettymistä tai keskeneräisiä statuksia.\n\n"
            )

        if isolation_audit.is_fully_isolated:
            f.write(
                "> **[ERISTETTY] TÄYSI SYÖTE-ERISTYS (Ei välimuistivuotoa):** "
                "Kaikkien syötetiedostojen SHA-256-tiivisteet poikkesivat toisistaan ajojen välillä. "
                "Googlen prefiksipohjainen KV-välimuisti ei ole voinut siirtyä ajosta toiseen.\n\n"
            )
        else:
            shared_files_str = ", ".join(isolation_audit.shared_identical_files)
            f.write(
                f"> **[VAROITUS] MAHDOLLINEN VÄLIMUISTIVUOTO:** Seuraavat syötetiedostot olivat täysin identtisiä "
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
        f.write(f"- **Aktiiviset Säännöt ja Asetukset (Frozen Context):** {frozen_context_info}\n")

        # Prompt Provenance Snapshot
        first_wf_id = first_run_record.get("workflow_id") or first_run_record.get("metadata", {}).get("workflow_id")
        wf_prov = extract_workflow_provenance(seed, first_wf_id)
        physical_models_by_run: dict[str, list[PhysicalModelBindingDTO]] = {}
        for idx, run_name in enumerate(loaded_runs):
            run_rec: dict[str, Any] = next((v for v in db_executions.values() if v.get("id") == run_name), {})
            reg_id = run_rec.get("model_registry_id") or run_rec.get("metadata", {}).get("model_registry_id")
            if not reg_id and idx < len(loaded_paths):
                run_frozen_path = loaded_paths[idx].parent / "frozen_context.json"
                if run_frozen_path.exists():
                    try:
                        with run_frozen_path.open("r", encoding="utf-8") as rf_f:
                            rf_data = json.load(rf_f)
                            if isinstance(rf_data, dict):
                                reg_id = rf_data.get("model_registry_id")
                    except json.JSONDecodeError, OSError:
                        pass
            if not reg_id and frozen_data and isinstance(frozen_data, dict):
                reg_id = frozen_data.get("model_registry_id")
            if not reg_id:
                raise AppException(
                    message=f"Execution '{run_name}' is missing mandatory model_registry_id metadata.",
                    status_code=422,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "execution_id": run_name},
                )
            physical_models_by_run[run_name] = resolve_physical_model_bindings(seed, registry_id=str(reg_id))

        blocks_json = json.dumps(seed.get("prompt_blocks", []), sort_keys=True, ensure_ascii=False)
        directives_hash = hashlib.sha256(blocks_json.encode("utf-8")).hexdigest()
        directives_char_count = len(blocks_json)
        prompt_provenance = PromptProvenanceDTO(
            directives_hash=directives_hash,
            directives_char_count=directives_char_count,
            physical_models_by_run=physical_models_by_run,
            workflow_provenance=wf_prov,
        )

        if wf_prov:
            ovr_switch_str = "SALLITTU (ENABLED)" if wf_prov.enable_contextual_overrides else "ESTETTY (DISABLED)"
            f.write("- **Työnkulun Provenienssi ja Hallintokytkimet (Workflow Provenance & Invariants):**\n")
            f.write(f"  - **Työnkulku:** {wf_prov.name_fi} ({wf_prov.name_en}) [`{wf_prov.workflow_id}`]\n")
            f.write(
                f"  - **Versio:** v{wf_prov.version} | **Aktiivisia askeleita:** {wf_prov.total_active_steps} kpl | "
                f"**Koko atomipopulaatio:** {wf_prov.total_workflow_atoms} atomia\n"
            )
            f.write(
                f"  - **Hallintokytkimet:** Kontekstuaaliset ohitukset: `{ovr_switch_str}`, "
                f"Tiukkuustaso: `{wf_prov.default_strictness_level}%`\n"
            )
            f.write(
                f"  - **Prompt-direktiivien tiiviste (SHA-256):** `{directives_hash[:16]}...` "
                f"({directives_char_count:,} merkkiä)\n"
            )

        if physical_models_by_run:
            f.write("- **Fyysiset Mallisidokset (Physical Model Bindings):**\n")
            for idx, run_name in enumerate(loaded_runs):
                run_rec = next((v for v in db_executions.values() if v.get("id") == run_name), {})
                reg_id = run_rec.get("model_registry_id") or run_rec.get("metadata", {}).get("model_registry_id")
                if not reg_id and idx < len(loaded_paths):
                    run_frozen_path = loaded_paths[idx].parent / "frozen_context.json"
                    if run_frozen_path.exists():
                        try:
                            with run_frozen_path.open("r", encoding="utf-8") as rf_f:
                                rf_data = json.load(rf_f)
                                if isinstance(rf_data, dict):
                                    reg_id = rf_data.get("model_registry_id")
                        except json.JSONDecodeError, OSError:
                            pass
                if not reg_id and frozen_data and isinstance(frozen_data, dict):
                    reg_id = frozen_data.get("model_registry_id")

                reg_name = str(reg_id)
                sys_configs = seed.get("system_config", [])
                configs_list = sys_configs.values() if isinstance(sys_configs, dict) else sys_configs
                for cfg in configs_list:
                    if isinstance(cfg, dict) and cfg.get("id") == str(reg_id):
                        reg_name = cfg.get("name_fi") or cfg.get("name") or str(reg_id)
                        break

                f.write(f"  - **R{idx + 1} (`{run_name}` - {reg_name} [`{reg_id}`]):**\n")
                run_bindings = physical_models_by_run.get(run_name, [])
                for mb in run_bindings:
                    provider_title = (
                        "Google Vertex AI"
                        if mb.provider == "google"
                        else (
                            "Google AI Studio"
                            if mb.provider == "ai_studio"
                            else ("OpenAI" if mb.provider == "openai" else (mb.provider or "Google").capitalize())
                        )
                    )
                    limits_str = ""
                    if mb.tpm_limit or mb.rpm_limit:
                        limits_str = f", Limits=[TPM: {mb.tpm_limit or 'N/A'}, RPM: {mb.rpm_limit or 'N/A'}]"
                    model_lower = mb.physical_model.lower()
                    is_gemini_v3 = ("gemini-3" in model_lower) or ("gemini-2.5" in model_lower)
                    is_openai_reasoning = any(p in model_lower for p in ("o1", "o3", "o4", "o5", "gpt-5"))

                    if is_gemini_v3:
                        provider_backend = "AI Studio" if "gemini/" in model_lower else "Vertex AI"
                        f.write(
                            f"    - {mb.strategy_name}: `{mb.physical_model}` ({provider_title} / {provider_backend}) "
                            f"(Todellinen T=1.0 [DB={mb.temperature} suodatettu pois; {provider_backend}], "
                            f"MaxTok={mb.max_tokens}, Thinking Budget={mb.thinking_budget} tok{limits_str})\n"
                        )
                    elif is_openai_reasoning:
                        if mb.thinking_budget == 0:
                            f.write(
                                f"    - {mb.strategy_name}: `{mb.physical_model}` ({provider_title}) "
                                f"(T={mb.temperature}, MaxTok={mb.max_tokens}{limits_str})\n"
                            )
                        else:
                            effort = mb.reasoning_effort or (
                                "low"
                                if mb.thinking_budget <= 2048
                                else "medium"
                                if mb.thinking_budget <= 4096
                                else "high"
                            )
                            f.write(
                                f"    - {mb.strategy_name}: `{mb.physical_model}` ({provider_title}) "
                                f"(Todellinen T=1.0 [DB={mb.temperature} suodatettu pois], "
                                f"MaxTok={mb.max_tokens}, Thinking={mb.thinking_budget} tok "
                                f"-> Reasoning Effort='{effort}'{limits_str})\n"
                            )
                    else:
                        think_str = f", Thinking={mb.thinking_budget} tok" if mb.thinking_budget > 0 else ""
                        f.write(
                            f"    - {mb.strategy_name}: `{mb.physical_model}` ({provider_title}) "
                            f"(T={mb.temperature}, MaxTok={mb.max_tokens}{think_str}{limits_str})\n"
                        )
        f.write("\n")

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

            trace_step_count = 0
            trace_cache_hit_count = 0
            trace_mcp_calls = 0
            trace_step_latencies: dict[str, int] = {}
            first_ts: str | None = None
            last_ts: str | None = None

            if exe_path.exists():
                try:
                    with exe_path.open("r", encoding="utf-8") as tf:
                        trace_data = json.load(tf)
                    if isinstance(trace_data, list):
                        telemetry_dto = extract_trace_telemetry(trace_data)
                        trace_step_count = telemetry_dto.step_count
                        trace_cache_hit_count = telemetry_dto.cache_hit_count
                        trace_mcp_calls = telemetry_dto.mcp_calls
                        trace_step_latencies = telemetry_dto.step_latencies
                        first_ts = telemetry_dto.first_timestamp
                        last_ts = telemetry_dto.last_timestamp

                        if prompt_tok == 0 and comp_tok == 0 and dag_cost == 0.0:
                            prompt_tok = telemetry_dto.prompt_tokens
                            comp_tok = telemetry_dto.completion_tokens
                            cached_tok = telemetry_dto.cached_tokens
                            dag_cost = telemetry_dto.dag_cost

                        if reas_tok == 0 and telemetry_dto.reasoning_tokens > 0:
                            reas_tok = telemetry_dto.reasoning_tokens
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

            # Fallback to execution_trace.json steps when telemetry is absent (e.g. production runs)
            if total_calls == 0 and trace_step_count > 0:
                total_calls = trace_step_count
                cache_hit_count = trace_cache_hit_count

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

            if not duration_ms and first_ts and last_ts:
                try:
                    t0 = datetime.datetime.fromisoformat(first_ts)
                    t1 = datetime.datetime.fromisoformat(last_ts)
                    duration_ms = int((t1 - t0).total_seconds() * 1000)
                except ValueError, TypeError:
                    pass

            duration_str = (
                f"{duration_ms / 1000 / 60:.1f} minuuttia ({duration_ms / 1000:.1f} s)"
                if duration_ms
                else "Keskeytyi / Tuntematon"
            )

            db_models = run_record.get("models_used") or exec_summary.get("models_used", {})
            if not db_models and idx < len(loaded_paths):
                run_frozen_path = loaded_paths[idx].parent / "frozen_context.json"
                if run_frozen_path.exists():
                    try:
                        with run_frozen_path.open("r", encoding="utf-8") as rf_f:
                            rf_data = json.load(rf_f)
                            if isinstance(rf_data, dict):
                                db_models = rf_data.get("models_used", {})
                    except json.JSONDecodeError, OSError:
                        pass
            if not db_models:
                raise AppException(
                    message=f"Execution '{run_name}' is missing mandatory models_used telemetry.",
                    status_code=422,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "execution_id": run_name},
                )
            models_formatted = ", ".join(f"{m} ({tok:,} tok)" for m, tok in db_models.items() if tok > 0)

            sys_snap = exec_summary.get("system_concurrency_snapshot", {})
            c_size = sys_snap.get("LLM_MAX_CHUNK_SIZE")
            m_eval = sys_snap.get("SCHEMA_MAX_EVALUATIONS")
            s_lim = sys_snap.get("MATRIX_SAMPLING_LIMIT")

            wf_prov_run = extract_workflow_provenance(seed, run_record.get("workflow_id") or meta.get("workflow_id"))
            tot_wf_atoms = wf_prov_run.total_workflow_atoms if wf_prov_run else len(common_atoms)
            sampling_val = meta.get("matrix_sampling_strategy") if isinstance(meta, dict) else None
            if sampling_val is None and idx < len(loaded_paths):
                run_frozen_path = loaded_paths[idx].parent / "frozen_context.json"
                if run_frozen_path.exists():
                    try:
                        with run_frozen_path.open("r", encoding="utf-8") as rf_f:
                            rf_data = json.load(rf_f)
                            if isinstance(rf_data, dict) and "matrix_sampling_strategy" in rf_data:
                                sampling_val = rf_data.get("matrix_sampling_strategy")
                    except json.JSONDecodeError, OSError:
                        pass
            if sampling_val == 0:
                sampling_display = f"0 (Kaikki {tot_wf_atoms} atomia, Tuotanto)"
            elif sampling_val is not None and sampling_val > 0:
                sampling_display = f"{sampling_val} (Kehitystilan otanta)"
            elif s_lim is not None:
                sampling_display = str(s_lim)
            else:
                sampling_display = "-"

            snap_str = (
                f" (Chunk size: {c_size}, Max Evals: {m_eval}, Sampling: {sampling_display})"
                if sys_snap or sampling_val is not None
                else ""
            )

            with exe_path.open("r", encoding="utf-8") as exe_f:
                raw_data = exe_f.read()
            error_count = raw_data.count("Chunk Processing Failed") + raw_data.count("SYSTEM ERROR")
            dlq_count = raw_data.count('"_dlq_status": "FAILED/DLQ"')

            dev_mode = (
                run_record.get("environment")
                or meta.get("environment")
                or run_record.get("dev_execution_mode")
                or meta.get("dev_execution_mode")
                or "production"
            )
            retries = run_record.get("llm_max_retries") or meta.get("llm_max_retries") or 2
            f.write(f"  - **Malli(t):** `{models_formatted}`{snap_str}\n")
            f.write(
                f"  - **Ajotila ja Rinnakkaisuus:** Tila: `{dev_mode}`, Max retries: `{retries}`, "
                f"Chunk size: `{c_size or '-'}`, Max Evals: `{m_eval or '-'}`, Sampling: `{sampling_display}`\n"
            )
            f.write(f"  - **Kesto:** `{duration_str}`\n")
            cache_pct_str = f" ({cache_hit_count / total_calls * 100:.1f} %)" if total_calls > 0 else ""
            f.write(
                f"  - **API-kutsut:** `{total_calls}` kpl "
                f"(Välimuistiosumat: `{cache_hit_count}/{total_calls}`{cache_pct_str})\n"
            )
            reas_str = f", Ajattelu: `{reas_tok:,}`" if reas_tok > 0 else ""
            f.write(
                f"  - **Tokenit:** `{combined_tokens:,}` (Syöte: `{prompt_tok:,}`, "
                f"Tuotos: `{comp_tok:,}`{reas_str}, Välimuisti: `{cached_tok:,}`, Synteesi: `{synth_tok:,}`)\n"
            )
            f.write(
                f"  - **Kustannusarvio:** `${combined_cost:.4f}` "
                f"(DAG: `${dag_cost:.4f}`, Synteesi: `${synth_cost:.4f}`)\n"
            )
            if trace_mcp_calls > 0:
                f.write(f"  - **Työkalukutsut (MCP / RAG):** `{trace_mcp_calls}` kpl faktojen tarkistuksia\n")
            if trace_step_latencies:
                slowest_step = max(trace_step_latencies.items(), key=lambda item: item[1])
                slowest_s = slowest_step[1] / 1000
                f.write(f"  - **Hitain askel (Pullonkaula):** `{slowest_step[0]}` ({slowest_s:.1f} s)\n")
            f.write(f"  - **Tekniset virheet (Crash):** `{error_count}` kpl\n")
            f.write(f"  - **DLQ-pudotetut atomit:** `{dlq_count}` kpl\n")

            is_starved = '"event_type": "starvation"' in raw_data or any(
                isinstance(s, dict) and s.get("data_starvation") is not None
                for s in run_record.get("profile_syntheses", {}).values()
            )
            if is_starved:
                f.write("  - **Kelvollisuus:** [KELVOTON] (Data Starvation: Insufficient Data)\n")
            else:
                f.write("  - **Kelvollisuus:** [KELVOLLINEN]\n")

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
                            f"(SHA-256: `{info.sha256[:16]}...`, Variaatio: `{info.noise}`)\n"
                        )

            run_finops.append(
                {
                    "run_name": run_name,
                    "prompt_tok": prompt_tok,
                    "comp_tok": comp_tok,
                    "cached_tok": cached_tok,
                    "reas_tok": reas_tok,
                    "total_tok": combined_tokens,
                    "cost_usd": combined_cost,
                    "total_calls": total_calls,
                    "cache_hit_count": cache_hit_count,
                }
            )
        f.write("\n")

        # Input Corpus Profiling & Structural Volume Table
        # Phase 3, Step 3.3: Strongly typed InputFileInspectionDTO storage
        all_input_files: dict[str, dict[str, InputFileInspectionDTO]] = {}
        for r_name, p in zip(loaded_runs, loaded_paths, strict=False):
            r_in_dir = p.parent / "inputs"
            if r_in_dir.is_dir():
                for in_f in sorted(r_in_dir.iterdir()):
                    if in_f.is_file():
                        if in_f.name not in all_input_files:
                            all_input_files[in_f.name] = {}
                        all_input_files[in_f.name][r_name] = _inspect_input_file(in_f)

        if all_input_files:
            f.write("### Syöteaineiston Profiili ja Rakenneanalyysi (Input Corpus Profile)\n\n")
            f.write(
                "Taulukko erittelee syötetiedostojen volyymin (sanat, lauseet, merkit) ja "
                "rakenteen (kappaleet, luetelmat) kustakin ajosta. Tämä todentaa aineiston riittävyyden "
                "(Data Sparsity vs. Cognitive Failure) sekä semanttisen ekvivalenssin.\n\n"
            )
            f.write(
                "| Ajo | Tiedosto | Ontologinen Rooli | Sanat | Lauseet | Merkit | "
                "Kappaleet | Luetelmat | Variaatio / Kohina |\n"
            )
            f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n")
            for fname, run_dict in all_input_files.items():
                role_key = classify_input_ontology(fname)
                if role_key == "candidate_deliverable":
                    role_desc = "Käyttäjädokumentaatio (Candidate Deliverable)"
                elif role_key == "external_context":
                    role_desc = "Ulkoinen konteksti (External Normative Context)"
                else:
                    role_desc = "Raakaloki (Combined Raw Dialogue)"
                for r_idx, r_name in enumerate(loaded_runs):
                    if r_name in run_dict:
                        fi = run_dict[r_name]
                        f.write(
                            f"| **R{r_idx + 1} ({r_name})** | `{fname}` | {role_desc} | {fi.word_count:,} | "
                            f"{fi.sentence_count:,} | {fi.char_count:,} | {fi.paragraph_count} | "
                            f"{fi.bullet_count} | {fi.noise} |\n"
                        )
            f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
            for r_idx, r_name in enumerate(loaded_runs):
                r_in_files = {fn: rd[r_name] for fn, rd in all_input_files.items() if r_name in rd}
                vol = calculate_user_documentation_volume(r_in_files, run_name=r_name)
                f.write(
                    f"| **YHTEENSÄ R{r_idx + 1}** | **{vol.user_file_count} tiedostoa** | "
                    f"**Käyttäjädokumentaation volyymi** | **{vol.total_words:,}** | "
                    f"**{vol.total_sentences:,}** | **{vol.total_characters:,}** | "
                    f"**{vol.total_paragraphs:,}** | **{vol.total_bullets:,}** | "
                    "**Puhdas kandidaattisisältö** |\n"
                )
            f.write("\n")

            if len(loaded_runs) >= 2:
                all_identities: list[bool] = []
                for _fname, run_dict in all_input_files.items():
                    texts = [run_dict[r].normalized_text for r in loaded_runs if r in run_dict]
                    if len(texts) >= 2:
                        all_identities.append(all(t == texts[0] for t in texts))

                if all_identities and all(all_identities):
                    f.write(
                        "> **[100% SEMANTTINEN IDENTTISYYS]:** Kaikkien syötetiedostojen teksti on 100% "
                        "identtistä normalisoidun tekstivertailun (whitespace-stripped) perusteella. "
                        "Syötteiden sanallinen sisältö on identtinen riippumatta injektoiduista Unicode-välimerkeistä "
                        "(Data Sparsity poissuljettu).\n\n"
                    )
                elif all_identities:
                    f.write(
                        "> **[HUOMIO]:** Syötetiedostoissa havaittiin asiasisällöllisiä eroja "
                        "normalisoidun tekstivertailun perusteella.\n\n"
                    )

        # Mathematical and Empirical Isolation Proofs (Cache Bypass Proofs)
        f.write("### Syöte-eristyksen ja Välimuistiohituksen Matemaattiset Todisteet\n\n")
        f.write(
            "Tämä osio todentaa matemaattisesti ja empiirisesti, että jokainen ajo on suoritettu toisistaan "
            "täysin eristetyillä syötteillä ilman pilvitarjoajan kontekstivälimuistivuotoa (Context Cache Bleed).\n\n"
        )

        f.write("#### 1. Kryptografinen SHA-256 Hajautustiiviste-erottelu\n")
        f.write("| Ajo | Tiedosto | SHA-256 Tiiviste (Hash) | Status |\n")
        f.write("| :--- | :--- | :--- | :---: |\n")
        if all_input_files:
            for fname, run_dict in all_input_files.items():
                seen_hashes: dict[str, str] = {}
                for r_idx, r_name in enumerate(loaded_runs):
                    if r_name in run_dict:
                        h = run_dict[r_name].sha256
                        is_unique = h not in seen_hashes.values()
                        status_str = "ERISTETTY" if is_unique else "KOLLISIO"
                        seen_hashes[r_name] = h
                        f.write(f"| **R{r_idx + 1} ({r_name})** | `{fname}` | `{h}` | `{status_str}` |\n")
        f.write("\n")

        f.write("#### 2. Pilvitarjoajan Telemetriavahvistus (Zero Cached Tokens)\n")
        f.write("| Ajo | Välimuistitokenit (Cached Tokens) | Välimuistiaste (Osumat) | Telemetriatodiste | Tulos |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for fin_item in run_finops:
            r_name = fin_item["run_name"]
            c_tok = fin_item["cached_tok"]
            t_calls = fin_item.get("total_calls", 0)
            c_hits = fin_item.get("cache_hit_count", 0)
            c_rate = f"{c_hits}/{t_calls} ({c_hits / t_calls * 100:.1f} %)" if t_calls > 0 else "-"
            c_status = "OHITETTU (0 tok)" if c_tok == 0 else f"VÄLIMUISTIOSUMA ({c_tok:,} tok)"
            proof_label = "100% Tuore inferenssi" if c_tok == 0 else "Osittainen välimuistihyödyntäminen"
            f.write(f"| **{r_name}** | {c_tok:,} | {c_rate} | {proof_label} | `{c_status}` |\n")
        f.write("\n")

        f.write("#### 3. Hajautettu Variaatiosyvyys ja Unicode-avaruus\n")
        f.write("| Ajo | Tiedosto | Havaittu Unicode-avaruus | Sanat | Semanttinen Invarianssi |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: |\n")
        if all_input_files:
            for fname, run_dict in all_input_files.items():
                first_wc: int | None = None
                for r_idx, r_name in enumerate(loaded_runs):
                    if r_name in run_dict:
                        fi = run_dict[r_name]
                        if first_wc is None:
                            first_wc = fi.word_count
                        wc_invariance = "TÄYSI (100%)" if fi.word_count == first_wc else "POIKKEAMA"
                        noise_lbl = fi.noise
                        w_cnt = fi.word_count
                        f.write(
                            f"| **R{r_idx + 1} ({r_name})** | `{fname}` | {noise_lbl} | "
                            f"{w_cnt:,} | `{wc_invariance}` |\n"
                        )
        f.write("\n")
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
        f.write("| Lohko / Matriisi | Lohkon ID | Asteikko | Atomeja Yhteensä | Erimielisyydet | Konsistenssi (%) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: |\n")
        for bh in block_heatmaps:
            b_min, b_max = block_extrema.get(bh.block_id, (1.0, 5.0))
            f.write(
                f"| **{bh.block_name}** | `{bh.block_id}` | {b_min:.0f}–{b_max:.0f} | "
                f"{bh.total_atoms} | {bh.mismatches} | {bh.consistency_rate * 100:.1f} % |\n"
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
        f.write(f"| **Tiedonhaun aukko (Retrieval Gap)** | {rc_ret} | {p_ret:.1f} % |\n")
        f.write(f"| **Päättelyn aukko (Reasoning Gap)** | {rc_rea} | {p_rea:.1f} % |\n")
        f.write(f"| **Kontekstuaalinen ohitus (Contextual Override)** | {rc_ovr} | {p_ovr:.1f} % |\n")
        f.write(f"| **Tekninen virhe / DLQ (Technical Error)** | {rc_tec} | {p_tec:.1f} % |\n")
        f.write(f"| **Yhteensä** | **{tot_m}** | **100.0 %** |\n\n")

        # Macro Score Drift (0-100)
        f.write("## Makrotason Pistemäärä- ja Luottamusdiffit (Macro Score Drift 0–100)\n\n")
        f.write(
            "Lohkokohtaiset pistemäärät perustuvat ajojen `normalized_score` -kenttään (0–100 asteikko) "
            "sekä atomitason läpäisyasteeseen.\n\n"
        )
        valid_score_deltas = [
            abs(ms.delta_normalized_score) for ms in macro_block_scores if ms.delta_normalized_score is not None
        ]
        mad_score = (sum(valid_score_deltas) / len(valid_score_deltas)) if valid_score_deltas else 0.0
        max_drift = max(valid_score_deltas) if valid_score_deltas else 0.0

        f.write(f"- **Keskimääräinen itseisarvopoikkeama (MAD - Mean Absolute Delta):** `{mad_score:.2f}` pistettä\n")
        f.write(f"- **Suurin yksittäisen lohkon poikkeama (Max Drift):** `{max_drift:.2f}` pistettä\n\n")
        f.write(
            "| Lohko / Matriisi | Run 1 Pisteet (Raaka & Norm) | Run 2 Pisteet (Raaka & Norm) | $\\Delta$ Norm | "
            "Run 1 Waterfall-katkos | Run 2 Waterfall-katkos | Run 1 Läpäisy | Run 2 Läpäisy | $\\Delta$ Läpäisy |\n"
        )
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for ms in macro_block_scores:
            s1_norm = f"{ms.run1_normalized_score:.1f} %" if ms.run1_normalized_score is not None else "-"
            s2_norm = f"{ms.run2_normalized_score:.1f} %" if ms.run2_normalized_score is not None else "-"
            s1_raw = f"{ms.run1_raw_score:.1f} / {ms.scale_max:.0f}" if ms.run1_raw_score is not None else "-"
            s2_raw = f"{ms.run2_raw_score:.1f} / {ms.scale_max:.0f}" if ms.run2_raw_score is not None else "-"
            s1_full = f"Raw: {s1_raw} | Norm: {s1_norm}" if ms.run1_normalized_score is not None else "-"
            s2_full = f"Raw: {s2_raw} | Norm: {s2_norm}" if ms.run2_normalized_score is not None else "-"
            d_str = f"{ms.delta_normalized_score:+.1f} %" if ms.delta_normalized_score is not None else "-"
            bp1_str = ms.run1_waterfall_breakpoint or "-"
            bp2_str = ms.run2_waterfall_breakpoint or "-"
            p1_str = f"{ms.run1_pass_rate * 100:.1f} %"
            p2_str = f"{ms.run2_pass_rate * 100:.1f} %"
            dp_str = f"{ms.delta_pass_rate * 100:+.1f} %"
            b_label = f"`{ms.block_id}` ({ms.block_name}, Asteikko {ms.scale_min:.0f}–{ms.scale_max:.0f})"
            f.write(
                f"| **{b_label}** | {s1_full} | {s2_full} | {d_str} | "
                f"{bp1_str} | {bp2_str} | {p1_str} | {p2_str} | {dp_str} |\n"
            )
        f.write("\n")

        # Evidence Class & Override Distribution
        f.write("## Evidenssiluokkien ja Ohitusten Jakauma (Evidence Class & Override Distribution)\n\n")
        f.write(
            "Taulukko erittelee arvioitujen atomien jakauman kussakin ajossa: "
            "suorat empiiriset sitaatit, käänteisen evidenssin läpäisyt (Null Hypothesis), "
            "kontekstuaaliset ohitukset, sääntödemootiot ja hylkäykset.\n\n"
        )
        f.write(
            "| Ajo | Empiiriset sitaatit | Käänteiset läpäisyt (Null Hypothesis) | "
            "Kontekstuaaliset ohitukset | Sääntödemootiot | Hylätyt (FAILED) | Yhteensä arvioitu |\n"
        )
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        evidence_distributions: list[EvidenceDistributionDTO] = []
        for r_idx, (r_name, ev_map) in enumerate(zip(loaded_runs, evals_list, strict=False)):
            r_rec: dict[str, Any] = next((v for v in db_executions.values() if v.get("id") == r_name), {})
            r_wf_id = r_rec.get("workflow_id") or r_rec.get("metadata", {}).get("workflow_id")
            r_prov = extract_workflow_provenance(seed, r_wf_id)
            r_override_enabled = r_prov.enable_contextual_overrides if r_prov else True
            dist = extract_evidence_distribution(
                ev_map, atom_details, enable_contextual_overrides=r_override_enabled, run_name=r_name
            )
            evidence_distributions.append(dist)
            f.write(
                f"| **R{r_idx + 1} ({r_name})** | {dist.empirical_quotes} | {dist.inverse_passes} | "
                f"{dist.contextual_overrides} | {dist.demoted_by_policy} | {dist.failures} | {dist.total_evaluated} |\n"
            )
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
            "Kaikki mallin poimimat suorat sitaatit tarkastetaan sanatarkasti ja whitespace-normalisoidusti "
            "(`str.find`) suhteessa alkuperäisiin syötetiedostoihin chimera- ja hallusinaatioriskien varalta.\n\n"
        )
        f.write("| Ajo | Syötteet Saatavilla | Sitaatteja | Verifioidut | Vahvistamattomat | Aitoustaso (%) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for gr in grounding_results_by_run:
            c_avail = "Kyllä" if gr["has_corpus"] else "Ei (Inputs-kansio puuttuu)"
            f.write(
                f"| **{gr['run_name']}** | {c_avail} | {gr['total_quotes']} | "
                f"{gr['verified_quotes']} | {gr['unverified_quotes']} | {gr['authenticity_rate']:.1f} % |\n"
            )
        f.write("\n")

        # Shift States
        if len(loaded_runs) >= 2:
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
        else:
            f.write("## Suoritustila (Single Run Inspection)\n")
            f.write(
                "- **Tila:** Yksittäinen suoritus. "
                "Differentiaalianalyysi ja tilasiirtymät vaativat vähintään 2 ajoa.\n\n"
            )

        f.write("## Epävakaimmat Testitapaukset / Kysytyt Säännöt (Järjestetty Entropian mukaan)\n")
        f.write(
            "Alla on listattu kaikki säännöt ja kysymykset, joissa ilmeni erimielisyyttä tai epävakautta "
            "eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) "
            "ovat listan alussa.\n\n"
        )

        for atom in mismatching_atoms:
            det = atom_details.get(atom, {})
            entropy = atom_entropies[atom]
            consistency = atom_consistencies[atom]
            states = atom_states[atom]
            bname = det.get("block_name", "-") if det else "-"
            sname = det.get("scale_name", "-") if det else "-"
            header_title = f"{bname} – {sname}" if bname != "-" else f"Atom-ID: `{atom}`"
            f.write(f"### {header_title} (Entropia: {entropy:.3f}, Konsistenssi: {consistency * 100:.1f}%)\n")
            f.write(f"- **Atom-ID:** `{atom}`\n")
            if det:
                bname = det.get("block_name", "-")
                bid = det.get("block_id", "-")
                sname = det.get("scale_name", "-")
                sscore = det.get("scale_score", "-")
                scope = det.get("bounding_box_scope", "sentence")
                inv = "Kyllä (True)" if det.get("inverse_evidence") else "Ei (False)"
                f.write(f"- **Lohko / Matriisi:** `{bname}` (`{bid}`)\n")
                f.write(f"- **Skaala / Taso:** `{sname}` (Arvo: `{sscore}`)\n")
                f.write(f"- **Skooppi (Scope):** `{scope}` | **Käänteinen evidenssi (Inverse):** `{inv}`\n")
                if det.get("concept_description"):
                    f.write(f"- **Kysymys / Konsepti:** {det['concept_description']}\n")
                if det.get("extraction_rule"):
                    f.write(f"- **Etsintäsääntö (Extraction Rule):** {det['extraction_rule']}\n")
                if det.get("anchor_target"):
                    f.write(f"- **Ankkuritargetti (Anchor Target):** {det['anchor_target']}\n")
                if det.get("contrastive_example"):
                    c_pair = det["contrastive_example"]
                    f.write(
                        f"- **Esimerkki (Contrastive Example):**\n"
                        f"  - *Acceptable:* {c_pair['acceptable']}\n"
                        f"  - *Rejected:* {c_pair['rejected']}\n"
                    )
            else:
                f.write(f"**Arviointisääntö:** {atom_rules.get(atom, 'Unknown')}\n")

            f.write("\n**Havaitut tilat, sitaatit ja perustelut ajoittain:**\n")
            for run_idx, (run_name, state) in enumerate(zip(loaded_runs, states, strict=False)):
                eval_item = evals_list[run_idx][atom]
                trace_content = get_trace(eval_item).replace("\n", " ")
                override_tag = " **[CONTEXTUAL OVERRIDE]**" if uses_contextual_override(eval_item) else ""
                quote_present = has_quote(eval_item)
                eq = eval_item.get("exact_quote", eval_item.get("exact_quotes", eval_item.get("source_quote")))
                if isinstance(eq, list):
                    eq_text = " ".join(str(x) for x in eq)
                elif eq is not None:
                    eq_text = str(eq)
                else:
                    eq_text = ""
                quote_len = len(eq_text)
                quote_status = "Löytyi" if quote_present else "Ei sitaattia"

                f.write(f"- **Run {run_idx + 1} ({run_name}) - [{state.upper()}]{override_tag}:**\n")
                if quote_present:
                    f.write(f"  - **Sitaatti ({quote_status}, {quote_len} merkkiä):** `{eq_text}`\n")
                else:
                    f.write(f"  - **Sitaatti ({quote_status}):** -\n")
                f.write(f"  - **Perustelu:** *{trace_content}*\n")
            f.write("\n---\n\n")

        # Complete Atom Consensus Manifest
        f.write("## Kaikkien Arvioitujen Atomien Yhteenvetotaulukko (Complete Atom Consensus Manifest)\n\n")
        f.write(
            "Taulukko listaa kaikki vertailluissa ajoissa arvioidut yhteiset atomit, "
            "niiden tason ja lohkon, suoritustilat sekä lainausten aitoustarkastuksen tilan.\n\n"
        )
        if len(loaded_runs) == 2:
            f.write(
                "| Atom-ID | Lohko (Block) | Taso (Scale) | Run 1 | Run 2 | Konsistenssi | Sitaatti | Verifioitu |\n"
            )
            f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n")
            for atom in sorted(list(common_atoms)):
                a_def = atom_definitions.get(atom)
                b_name = a_def.block_name if a_def else "-"
                s_name = a_def.scale_name if a_def else "-"
                snaps = all_evaluations.get(atom, [])
                r1_st = snaps[0].state.upper() if len(snaps) > 0 else "-"
                r2_st = snaps[1].state.upper() if len(snaps) > 1 else "-"
                cons = f"{atom_consistencies.get(atom, 1.0) * 100:.0f}%"
                any_q = any(s.has_quote for s in snaps)
                any_v = any(s.quote_verified for s in snaps)
                q_label = "Kyllä" if any_q else "Ei"
                v_label = "Kyllä" if any_v else ("-" if not any_q else "Ei")
                f.write(f"| `{atom}` | `{b_name}` | {s_name} | {r1_st} | {r2_st} | {cons} | {q_label} | {v_label} |\n")
        else:
            run_headers = " | ".join(f"R{idx + 1}" for idx in range(len(loaded_runs)))
            align_headers = " | ".join(":---:" for _ in range(len(loaded_runs)))
            f.write(
                f"| Atom-ID | Lohko (Block) | Taso (Scale) | {run_headers} | Konsistenssi | Sitaatti | Verifioitu |\n"
            )
            f.write(f"| :--- | :--- | :--- | {align_headers} | :---: | :---: | :---: |\n")
            for atom in sorted(list(common_atoms)):
                a_def = atom_definitions.get(atom)
                b_name = a_def.block_name if a_def else "-"
                s_name = a_def.scale_name if a_def else "-"
                snaps = all_evaluations.get(atom, [])
                run_cells = " | ".join(s.state.upper() for s in snaps)
                cons = f"{atom_consistencies.get(atom, 1.0) * 100:.0f}%"
                any_q = any(s.has_quote for s in snaps)
                any_v = any(s.quote_verified for s in snaps)
                q_label = "Kyllä" if any_q else "Ei"
                v_label = "Kyllä" if any_v else ("-" if not any_q else "Ei")
                f.write(f"| `{atom}` | `{b_name}` | {s_name} | {run_cells} | {cons} | {q_label} | {v_label} |\n")
        f.write("\n")

    # Structured JSON snapshot sidecar
    if common_atoms:
        variance_rate = len(mismatching_atoms) / len(common_atoms)
    else:
        variance_rate = 0.0

    runtime_env = "development"
    runtime_dev_budget = 0
    try:
        _cur_cfg = get_settings()
        runtime_env = _cur_cfg.environment
        runtime_dev_budget = _cur_cfg.dev_max_thinking_budget
    except AttributeError, KeyError, ValueError, RuntimeError:
        runtime_env = "development"
        runtime_dev_budget = 0

    if runtime_env == "development":
        runtime_parallelism = 1
        runtime_matrix_sampling = "dev_sampled"
    else:
        runtime_parallelism = 3
        runtime_matrix_sampling = "full"

    snapshot_dto = DiffReportSnapshotDTO(
        execution_ids=loaded_runs,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        global_consistency=global_consistency,
        fleiss_kappa=global_kappa,
        cohen_kappa=cohen_kappa_dto,
        average_entropy=global_entropy,
        total_common_atoms=len(common_atoms),
        mismatch_count=len(mismatching_atoms),
        variance_rate=variance_rate,
        summary_2way=summary_2way,
        root_causes=root_cause_breakdown,
        isolation_audit=isolation_audit,
        scale_breakdowns=scale_breakdowns,
        block_heatmaps=block_heatmaps,
        macro_scores=macro_block_scores,
        evidence_distributions=evidence_distributions,
        prompt_provenance=prompt_provenance,
        atom_definitions=atom_definitions,
        all_evaluations=all_evaluations,
        environment=runtime_env,
        dev_max_thinking_budget=runtime_dev_budget,
        ensemble_parallelism=runtime_parallelism,
        matrix_sampling_strategy=runtime_matrix_sampling,
    )
    json_path = report_path.with_suffix(".json")
    json_path.write_text(snapshot_dto.model_dump_json(indent=2), encoding="utf-8")

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
    print(f"JSON snapshot written to: {json_path}")
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
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Explicit file path to write the differential Markdown report",
    )
    args = parser.parse_args()
    cli_args = args.execution_ids if args.execution_ids else None
    run_diff(cli_args, output_file=args.output)


if __name__ == "__main__":
    main()
