"""Execution Trace Comparison and Consistency Metric Suite.

Provides forensic cross-execution differential analysis, Fleiss/Cohen Kappa metrics,
Shannon entropy calculations, and Markdown report synthesis.
"""

from __future__ import annotations

import datetime
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

__all__ = [
    "calculate_cohens_kappa",
    "calculate_entropy",
    "calculate_fleiss_kappa",
    "calculate_pairwise_consistency",
    "get_all_evals",
    "get_state",
    "get_trace",
    "run_diff",
    "uses_contextual_override",
]


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


def calculate_cohens_kappa(atom_states_list: list[list[str]], categories: list[str]) -> float:
    """Calculate Cohen's Kappa for exactly two runs (M = 2).

    Args:
        atom_states_list: List of 2-element lists containing binary/categorical states.
        categories: List of unique categories present across all evaluations.

    Returns:
        Cohen's Kappa agreement coefficient.

    Raises:
        ValueError: If any item in atom_states_list does not contain exactly two states.
    """
    n = len(atom_states_list)
    if n == 0:
        return 0.0
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
        return 1.0

    return (observed_agreement - expected_agreement) / (1.0 - expected_agreement)


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

    cohen_kappa = None
    if len(evals_list) == 2:
        try:
            cohen_kappa = calculate_cohens_kappa(all_atom_states, categories_list)
        except Exception:
            pass

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

    Path("scratch").mkdir(exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = Path(f"scratch/diff_report_{timestamp_str}.md")

    git_info = "Ei saatavilla"
    try:
        git_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        git_commit = subprocess.check_output(["git", "log", "-1", "--pretty=format:%h - %s (%cd)"], text=True).strip()
        git_info = f"Branch: {git_branch} | Commit: {git_commit}"
    except Exception:
        pass

    sys_enums = "Ei saatavilla"
    try:
        if "." not in sys.path:
            sys.path.insert(0, ".")
        import backend_v2.models.enums as enums

        eval_run_count = getattr(enums, "EvaluationRunCount", None)
        ensemble_val = getattr(eval_run_count, "ENSEMBLE", None)
        standard_val = getattr(eval_run_count, "STANDARD", None)
        ensemble_v = ensemble_val.value if ensemble_val else "N/A"
        standard_v = standard_val.value if standard_val else "N/A"

        verif_result = getattr(enums, "VerificationResult", None)
        pass_val = getattr(verif_result, "VERIFIED", None)
        fail_val = getattr(verif_result, "DEBUNKED", None)
        pass_v = pass_val.value if pass_val else "N/A"
        fail_v = fail_val.value if fail_val else "N/A"

        sys_enums = (
            f"  - **EvaluationRunCount**: ENSEMBLE = {ensemble_v}, STANDARD = {standard_v}\n"
            f"  - **VerificationResult**: VERIFIED = {pass_v}, DEBUNKED = {fail_v}"
        )

        sys_concurrency = getattr(enums, "SystemConcurrency", None)
        if sys_concurrency:
            sc_items = [f"{k} = {v.value}" for k, v in sys_concurrency.__members__.items()]
            sys_enums += "\n  - **SystemConcurrency**:\n    - " + "\n    - ".join(sc_items)
    except Exception as e:
        sys_enums = f"Virhe Enumien luvussa: {e}"

    db_executions: dict[str, Any] = {}
    db_file_path = Path("data/db_v2.json")
    if db_file_path.exists():
        try:
            with db_file_path.open("r", encoding="utf-8") as db_f:
                db_json = json.load(db_f)
                db_executions = db_json.get("executions", {})
        except Exception as e:
            print(f"Warning: db_v2.json read error: {e}")

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
            except Exception:
                pass

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

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)\n\n")
        f.write("## Ympäristö ja Konteksti (Execution State)\n")
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

            prompt_tok = agg_usage.get("prompt_tokens") or meta.get("prompt_tokens", 0)
            comp_tok = agg_usage.get("completion_tokens") or meta.get("completion_tokens", 0)
            cached_tok = agg_usage.get("cached_tokens") or meta.get("cached_tokens", 0)
            total_tokens = prompt_tok + comp_tok

            run_dir = exe_path.parent
            telem_file = run_dir / "llm_telemetry.jsonl"
            cache_hit_count = 0
            total_calls = 0
            if telem_file.exists():
                try:
                    with telem_file.open("r", encoding="utf-8") as tf:
                        calls = [json.loads(line) for line in tf if line.strip()]
                        total_calls = len(calls)
                        if total_tokens == 0:
                            total_tokens = sum(c.get("tokens", 0) for c in calls)
                        cache_hit_count = sum(1 for c in calls if c.get("cache_hit"))
                except Exception:
                    pass

            cost = run_record.get("cost_estimate") or exec_summary.get("cost_estimate") or meta.get("dag_cost_usd", 0.0)
            duration_ms = run_record.get("duration_ms", 0)
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
                f"  - **Tokenit:** `{total_tokens:,}` (Syöte: `{prompt_tok:,}`, "
                f"Tuotos: `{comp_tok:,}`, Välimuisti: `{cached_tok:,}`)\n"
            )
            f.write(f"  - **Kustannusarvio:** `${cost:.4f}`\n")
            f.write(f"  - **Tekniset virheet (Crash):** `{error_count}` kpl\n")
            f.write(f"  - **DLQ-pudotetut atomit:** `{dlq_count}` kpl\n")

            inputs_dir = run_dir / "inputs"
            if inputs_dir.is_dir():
                inputs_files = [f.name for f in inputs_dir.iterdir() if f.is_file()]
                if inputs_files:
                    f.write("  - **Käytetyt syötetiedostot:**\n")
                    for in_file in inputs_files:
                        in_path = inputs_dir / in_file
                        abs_in = str(in_path.resolve()).replace("\\", "/")
                        f.write(f"    - [{in_file}](file:///{abs_in})\n")
        f.write("\n")

        f.write("## Globaalit Metriikat\n")
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
        if cohen_kappa is not None:
            f.write(f"- **Cohenin Kappa ($\\kappa_{{Cohen}}$):** {cohen_kappa:.4f}\n")
            f.write(
                "  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. "
                "Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen "
                "jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*\n"
            )
        f.write(f"- **Keskimääräinen Shannonin Entropia:** {global_entropy:.4f}\n")
        f.write(
            "  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. "
            "Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*\n\n"
        )

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
    if cohen_kappa is not None:
        print(f"Cohen's Kappa: {cohen_kappa:.4f}")
    print(f"Average Entropy: {global_entropy:.4f}")
    print(f"Report written to: {report_path}")
    return str(report_path)


if __name__ == "__main__":
    cli_args = sys.argv[1:] if len(sys.argv) > 1 else None
    run_diff(cli_args)
