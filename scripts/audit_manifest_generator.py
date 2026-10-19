"""Audit Manifest Generator for Empirical Human Ground-Truth Calibration.

Provides deterministic extraction, stratified sampling, and immutable Pydantic V2
manifest export (JSON/CSV) from physical production execution traces for:
1. Type II Semantic Error (beta_sem) Ground-Truth Calibration (Section 6, Property 1).
2. Lexical Firewall Precision vs. Recall (Chimera) False-Negative Analysis (Section 8.5, Table 5).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import random
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field

# Ensure project root is in sys.path before any local imports
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from backend_v2.models.enums import ExecutionStatus

logger = logging.getLogger(__name__)

# Ensure Windows 11 PowerShell UTF-8 compatibility
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

if isinstance(sys.stderr, io.TextIOWrapper):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass


class ManifestType(StrEnum):
    """Categorical specification of audit manifest calibration target."""

    BETA_SEM = "beta_sem"
    CHIMERA = "chimera"
    ALL = "all"


class ManifestFormat(StrEnum):
    """Output serialization format for the audit manifest."""

    JSON = "json"
    CSV = "csv"


class SeedAtomMetadataDTO(BaseModel):
    """Encapsulated metadata for a proposition atom defined in seed_data.json."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_id: Annotated[str, Field(description="Canonical matrix identifier.")]
    matrix_label: Annotated[str, Field(description="Human-readable matrix name.")]
    concept_description: Annotated[str, Field(description="Proposition assertion description.")]
    target_speaker: Annotated[str, Field(description="Target speaker attribution (USER or ASSISTANT).")]


class AuditManifestItemDTO(BaseModel):
    """Immutable single proposition atom audit item within an evaluation manifest."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str, Field(description="Canonical proposition identifier.")]
    execution_id: Annotated[str, Field(description="Originating execution identifier.")]
    case_name: Annotated[str, Field(description="Domain case identifier (pair_a or pair_b).")]
    matrix_id: Annotated[str, Field(description="Target matrix block identifier.")]
    matrix_label: Annotated[str, Field(description="Human-readable matrix name.")]
    concept_description: Annotated[str, Field(description="Evaluated proposition assertion description.")]
    target_speaker: Annotated[str, Field(description="Target speaker attribution (USER or ASSISTANT).")]
    system_status: Annotated[ExecutionStatus, Field(description="Runtime system decision.")]
    raw_is_true: Annotated[bool, Field(description="Raw boolean model claim.")]
    source_quote: Annotated[str | None, Field(default=None, description="Extracted physical citation substring.")] = (
        None
    )
    is_chimera: Annotated[bool, Field(description="Whether the citation failed physical lexical anchoring.")]
    evaluation_reasoning: Annotated[
        str | None, Field(default=None, description="LLM chain-of-thought justification trace.")
    ] = None
    human_ground_truth_entailment: Annotated[
        bool | None,
        Field(default=None, description="Expert annotator determination of whether evidence entails the hypothesis."),
    ] = None
    human_underlying_competency_present: Annotated[
        bool | None,
        Field(default=None, description="Expert determination of whether competency was present in text."),
    ] = None
    human_error_classification: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Diagnostic error classification (true_negative_hallucination or false_negative_retrieval_gap)."
            ),
        ),
    ] = None
    human_annotation_notes: Annotated[
        str | None, Field(default=None, description="Expert qualitative feedback and notes.")
    ] = None


class AuditManifestDTO(BaseModel):
    """Comprehensive, immutable audit manifest container for human annotation campaigns."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    manifest_id: Annotated[str, Field(description="Unique manifest identifier.")]
    generated_at: Annotated[str, Field(description="ISO-8601 UTC timestamp of manifest compilation.")]
    manifest_type: Annotated[ManifestType, Field(description="Target calibration objective.")]
    sample_size: Annotated[int, Field(ge=0, description="Total count of sampled audit atoms.")]
    items: Annotated[list[AuditManifestItemDTO], Field(description="List of sampled proposition items.")]
    source_trace_files: Annotated[list[str], Field(description="List of physical execution trace paths.")]


DEFAULT_PRODUCTION_TRACES: Final[dict[str, list[Path]]] = {
    "pair_a": [
        Path("data/files/executions/exe_379b69df134f477a/execution_trace.json"),
        Path("data/files/executions/exe_f6f9b06e63eb4dd8/execution_trace.json"),
    ],
    "pair_b": [
        Path("data/files/executions/exe_04a02919612e45c0/execution_trace.json"),
        Path("data/files/executions/exe_a56127fa10594dc4/execution_trace.json"),
    ],
}


def load_seed_atom_metadata(seed_path: Path | None = None) -> dict[str, SeedAtomMetadataDTO]:
    """Load rubric descriptions and matrix labels from seed_data.json.

    Args:
        seed_path: Optional explicit path to seed_data.json.

    Returns:
        Mapping of tda_id to SeedAtomMetadataDTO containing matrix_id, matrix_label,
        concept_description, and target_speaker.
    """
    path = seed_path or Path("backend_v2/seed/seed_data.json")
    if not path.exists():
        logger.warning("Seed data file not found at %s. Returning empty metadata.", path)
        return {}

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    meta_map: dict[str, SeedAtomMetadataDTO] = {}
    prompt_blocks = data["prompt_blocks"] if "prompt_blocks" in data else []
    for block in prompt_blocks:
        block_id = block["id"] if "id" in block else "unknown_block"
        label_raw = block["label"] if "label" in block else {}
        slug = block["slug"] if "slug" in block else block_id
        en_val = label_raw["en"] if "en" in label_raw else None
        fi_val = label_raw["fi"] if "fi" in label_raw else None
        matrix_label = str(en_val or fi_val or slug or block_id)

        # Check in scales -> claims/rows
        scales = block["scales"] if "scales" in block else []
        for scale in scales:
            claims = scale["claims"] if "claims" in scale else []
            rows = scale["rows"] if "rows" in scale else []
            containers = claims + rows
            for c in containers:
                assertions = c["tda_assertions"] if "tda_assertions" in c else []
                for assertion in assertions:
                    tda_id = assertion["tda_id"] if "tda_id" in assertion else None
                    if tda_id:
                        desc = (
                            assertion["concept_description"]
                            if "concept_description" in assertion and assertion["concept_description"]
                            else (
                                assertion["anchor_target"]
                                if "anchor_target" in assertion and assertion["anchor_target"]
                                else ""
                            )
                        )
                        speaker = assertion["target_speaker"] if "target_speaker" in assertion else "USER"
                        meta_map[tda_id] = SeedAtomMetadataDTO(
                            matrix_id=block_id,
                            matrix_label=matrix_label,
                            concept_description=desc,
                            target_speaker=speaker,
                        )

    return meta_map


def extract_combined_source_text(trace_path: Path) -> str:
    """Extract combined source text payload from an execution trace file.

    Args:
        trace_path: Path to the execution_trace.json file.

    Returns:
        Concatenated source text payload from the inputs step.
    """
    if not trace_path.exists():
        return ""

    with trace_path.open("r", encoding="utf-8") as f:
        events = json.load(f)

    text_parts: list[str] = []
    for ev in events:
        step_name = ev["step_name"] if "step_name" in ev else None
        if step_name == "inputs":
            content = ev["content"] if "content" in ev else {}
            data = content["data"] if "data" in content else {}
            for key in ("product_text", "chat_log_user_only", "reflection_text", "chat_log"):
                val = data[key] if key in data else None
                if isinstance(val, str) and val.strip():
                    text_parts.append(val)
            break

    return "\n\n".join(text_parts)


def load_physical_execution_items(
    trace_paths_by_case: Mapping[str, Sequence[Path]] | None = None,
    seed_path: Path | None = None,
) -> list[AuditManifestItemDTO]:
    """Extract and validate evaluated proposition atoms from physical production execution traces.

    Args:
        trace_paths_by_case: Mapping of case name to list of trace file paths.
        seed_path: Optional path to seed_data.json for metadata enrichment.

    Returns:
        List of strictly typed AuditManifestItemDTO records.

    Raises:
        FileNotFoundError: If any explicitly provided trace file does not exist.
    """
    from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
    from scripts.diff_executions import get_all_evals

    traces_map = trace_paths_by_case or DEFAULT_PRODUCTION_TRACES
    seed_meta = load_seed_atom_metadata(seed_path)
    items: list[AuditManifestItemDTO] = []

    for case_name, trace_list in traces_map.items():
        for trace_path in trace_list:
            if not trace_path.exists():
                msg = f"Execution trace file not found: {trace_path}"
                raise FileNotFoundError(msg)

            exe_id = trace_path.parent.name
            evals = get_all_evals(trace_path)
            source_text = extract_combined_source_text(trace_path)

            norm_doc = ""
            if source_text:
                norm_doc, _ = AnchorValidationService.normalize_text_with_mapping(source_text)

            for tda_id, ev in evals.items():
                status_raw = ev["status"] if "status" in ev else "FAILED"
                st = (
                    ExecutionStatus(status_raw)
                    if status_raw in ExecutionStatus._value2member_map_
                    else ExecutionStatus.FAILED
                )
                quote = (
                    ev["source_quote"]
                    if "source_quote" in ev and ev["source_quote"] is not None
                    else (ev["quote"] if "quote" in ev and ev["quote"] is not None else None)
                )
                reasoning = (
                    ev["evaluation_reasoning"]
                    if "evaluation_reasoning" in ev and ev["evaluation_reasoning"] is not None
                    else (ev["reasoning"] if "reasoning" in ev and ev["reasoning"] is not None else None)
                )

                # Lexical verification check against physical document
                is_valid_quote = True
                if quote is not None and norm_doc:
                    norm_q, _ = AnchorValidationService.normalize_text_with_mapping(quote)
                    is_valid_quote = AnchorValidationService._is_lexically_valid(
                        quote=quote,
                        norm_quote=norm_q,
                        norm_text=norm_doc,
                        strictness_level=50,
                    ).is_valid
                is_chimera = (quote is not None) and (not is_valid_quote)

                meta = seed_meta[tda_id] if tda_id in seed_meta else None
                ev_mid = ev["matrix_id"] if "matrix_id" in ev and ev["matrix_id"] else None
                meta_mid = meta.matrix_id if meta is not None else None
                matrix_id = ev_mid or meta_mid or "matrix_unknown"

                meta_label = meta.matrix_label if meta is not None else None
                matrix_label = meta_label or matrix_id

                meta_desc = meta.concept_description if meta is not None else None
                concept_desc = meta_desc or f"Criterion assertion for {tda_id}"

                meta_speaker = meta.target_speaker if meta is not None else None
                speaker = meta_speaker or "USER"

                items.append(
                    AuditManifestItemDTO(
                        tda_id=tda_id,
                        execution_id=exe_id,
                        case_name=case_name,
                        matrix_id=matrix_id,
                        matrix_label=matrix_label,
                        concept_description=concept_desc,
                        target_speaker=speaker,
                        system_status=st,
                        raw_is_true=(st == ExecutionStatus.PASSED),
                        source_quote=quote,
                        is_chimera=is_chimera,
                        evaluation_reasoning=reasoning,
                    )
                )

    return items


def generate_audit_manifest(
    manifest_type: ManifestType = ManifestType.BETA_SEM,
    sample_size: int = 40,
    seed: int = 42,
    trace_paths_by_case: Mapping[str, Sequence[Path]] | None = None,
    seed_path: Path | None = None,
) -> AuditManifestDTO:
    """Generate a stratified, reproducible audit manifest for human expert annotation.

    Args:
        manifest_type: Target calibration scope (BETA_SEM, CHIMERA, or ALL).
        sample_size: Desired total count of sampled atoms (for BETA_SEM or stratified sampling).
        seed: Random seed for deterministic reproducibility.
        trace_paths_by_case: Optional custom trace paths mapping.
        seed_path: Optional custom path to seed_data.json.

    Returns:
        Strictly typed AuditManifestDTO container.
    """
    all_items = load_physical_execution_items(trace_paths_by_case=trace_paths_by_case, seed_path=seed_path)

    # Deterministic RNG initialization
    rng = random.Random(seed)

    selected_items: list[AuditManifestItemDTO] = []
    trace_files: list[str] = []
    if trace_paths_by_case:
        for paths in trace_paths_by_case.values():
            trace_files.extend(str(p) for p in paths)
    else:
        for paths in DEFAULT_PRODUCTION_TRACES.values():
            trace_files.extend(str(p) for p in paths)

    match manifest_type:
        case ManifestType.BETA_SEM:
            # Beta_sem calibration: verified positive claims (system_status == PASSED and quote verified)
            eligible = [
                item
                for item in all_items
                if item.system_status == ExecutionStatus.PASSED
                and item.source_quote is not None
                and not item.is_chimera
            ]
            if len(eligible) <= sample_size:
                selected_items = eligible
            else:
                # Stratify proportionally across matrix_id
                by_matrix: dict[str, list[AuditManifestItemDTO]] = defaultdict(list)
                for item in eligible:
                    by_matrix[item.matrix_id].append(item)

                target_per_matrix = max(1, sample_size // max(1, len(by_matrix)))
                remainder = sample_size
                for mid in sorted(by_matrix.keys()):
                    m_items = by_matrix[mid]
                    rng.shuffle(m_items)
                    take = min(len(m_items), target_per_matrix, remainder)
                    selected_items.extend(m_items[:take])
                    remainder -= take

                # Fill any remaining quota from leftover eligible items
                if len(selected_items) < sample_size:
                    chosen_ids = {it.tda_id + it.execution_id for it in selected_items}
                    leftovers = [it for it in eligible if (it.tda_id + it.execution_id) not in chosen_ids]
                    rng.shuffle(leftovers)
                    selected_items.extend(leftovers[: sample_size - len(selected_items)])

        case ManifestType.CHIMERA:
            # Chimera / False-negative audit: unanchored quotes or rejected system decisions (evaluating retrieval gaps)
            eligible = [
                item
                for item in all_items
                if item.is_chimera
                or (item.raw_is_true and item.system_status == ExecutionStatus.FAILED)
                or (item.system_status == ExecutionStatus.FAILED)
            ]
            if sample_size > 0 and len(eligible) > sample_size:
                rng.shuffle(eligible)
                selected_items = eligible[:sample_size]
            else:
                selected_items = eligible

        case ManifestType.ALL:
            selected_items = all_items
            if sample_size > 0 and len(selected_items) > sample_size:
                rng.shuffle(selected_items)
                selected_items = selected_items[:sample_size]

    manifest_id = f"man_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{manifest_type.value}"

    return AuditManifestDTO(
        manifest_id=manifest_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        manifest_type=manifest_type,
        sample_size=len(selected_items),
        items=selected_items,
        source_trace_files=trace_files,
    )


def export_manifest_to_json(manifest: AuditManifestDTO, output_path: Path) -> Path:
    """Export the audit manifest to a formatted JSON file with Pydantic validation.

    Args:
        manifest: Strictly typed AuditManifestDTO container.
        output_path: Destination file path.

    Returns:
        Path to the persisted JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Audit manifest (JSON) written to %s", output_path)
    return output_path


def export_manifest_to_csv(manifest: AuditManifestDTO, output_path: Path) -> Path:
    """Export the audit manifest to an RFC-4180 compliant CSV file for human annotation.

    Args:
        manifest: Strictly typed AuditManifestDTO container.
        output_path: Destination file path.

    Returns:
        Path to the persisted CSV file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "tda_id",
        "execution_id",
        "case_name",
        "matrix_id",
        "matrix_label",
        "concept_description",
        "target_speaker",
        "system_status",
        "raw_is_true",
        "source_quote",
        "is_chimera",
        "evaluation_reasoning",
        "human_ground_truth_entailment",
        "human_underlying_competency_present",
        "human_error_classification",
        "human_annotation_notes",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for item in manifest.items:
            writer.writerow(item.model_dump(mode="json"))

    logger.info("Audit manifest (CSV) written to %s", output_path)
    return output_path


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for the audit manifest generator.

    Returns:
        Configured argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        description="Quorum Audit Manifest Generator for Ground-Truth Calibration (Section 6, Section 8.5)."
    )
    parser.add_argument(
        "--type",
        dest="manifest_type",
        choices=["beta_sem", "chimera", "all"],
        default="beta_sem",
        help=(
            "Calibration objective: 'beta_sem' (pilot N=40), 'chimera' (false negatives), or 'all'. Default: beta_sem."
        ),
    )
    parser.add_argument(
        "--format",
        dest="manifest_format",
        choices=["json", "csv"],
        default="json",
        help="Output serialization format (json or csv). Default: json.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=40,
        help="Target sample size for stratified selection. Default: 40.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic pseudo-random generator seed for reproducible sampling. Default: 42.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Destination path for the manifest file (defaults to data/files/manifests/manifest_<type>.<format>).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for generating audit manifests from physical execution traces.

    Args:
        argv: Optional list of argument strings (defaults to sys.argv[1:]).

    Returns:
        0 on success, non-zero on error.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        m_type = ManifestType(args.manifest_type)
        m_fmt = ManifestFormat(args.manifest_format)

        manifest = generate_audit_manifest(
            manifest_type=m_type,
            sample_size=args.sample_size,
            seed=args.seed,
        )

        if args.output_file:
            out_path = Path(args.output_file)
        else:
            ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            ext = "json" if m_fmt == ManifestFormat.JSON else "csv"
            out_path = Path(f"data/files/manifests/manifest_{m_type.value}_{ts_str}.{ext}")

        if m_fmt == ManifestFormat.JSON:
            export_manifest_to_json(manifest, out_path)
        else:
            export_manifest_to_csv(manifest, out_path)

        print(
            f"Successfully compiled audit manifest '{manifest.manifest_id}' with {len(manifest.items)} "
            f"items to: {out_path}"
        )
        return 0

    except (RuntimeError, ValueError, OSError, FileNotFoundError) as e:
        logger.error("Audit manifest generation failed: %s", e, exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
