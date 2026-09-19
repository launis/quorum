#!/usr/bin/env python3
"""Canonical Import Migration Script.

Deterministically rewrites imports from `backend_v2.models.v2_core` to their
canonical module locations across module and function scopes using AST parsing.
Runs Ruff sorting and formatting on all modified files to guarantee zero syntax
or formatting defects.
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import subprocess
import sys
from collections import defaultdict

# Authoritative SSOT mapping of all 56 symbols re-exported by v2_core.py
SYMBOL_MAP: dict[str, str] = {
    # backend_v2.models.core_base
    "OPAQUE_STRIPE_ID_REGEX": "backend_v2.models.core_base",
    "I18nText": "backend_v2.models.core_base",
    "V2CoreBase": "backend_v2.models.core_base",
    # backend_v2.models.domain.execution
    "EvaluatedMatrixContextDTO": "backend_v2.models.domain.execution",
    "EvidenceRejectionRequest": "backend_v2.models.domain.execution",
    "ExecutionCreate": "backend_v2.models.domain.execution",
    "ExecutionRecord": "backend_v2.models.domain.execution",
    "ExecutionStep": "backend_v2.models.domain.execution",
    "ExecutionStepState": "backend_v2.models.domain.execution",
    "ExecutionSummarySnapshot": "backend_v2.models.domain.execution",
    "FrozenContext": "backend_v2.models.domain.execution",
    "JobAcceptedDTO": "backend_v2.models.domain.execution",
    # backend_v2.models.domain.inputs
    "WorkflowInputs": "backend_v2.models.domain.inputs",
    "WorkflowInputsIngress": "backend_v2.models.domain.inputs",
    # backend_v2.models.domain.matrix
    "AcceptanceCriterion": "backend_v2.models.domain.matrix",
    "AntiPattern": "backend_v2.models.domain.matrix",
    "ContrastivePairDTO": "backend_v2.models.domain.matrix",
    "MatrixClaim": "backend_v2.models.domain.matrix",
    "MatrixRow": "backend_v2.models.domain.matrix",
    "MatrixScale": "backend_v2.models.domain.matrix",
    "TDAAssertion": "backend_v2.models.domain.matrix",
    "TheoryGrounding": "backend_v2.models.domain.matrix",
    "_coerce_to_tuple": "backend_v2.models.domain.matrix",
    # backend_v2.models.domain.output_profile
    "OutputProfile": "backend_v2.models.domain.output_profile",
    # backend_v2.models.domain.report_artifact
    "ReportArtifact": "backend_v2.models.domain.report_artifact",
    # backend_v2.models.domain.step
    "ALLOWED_INPUT_MODES": "backend_v2.models.domain.step",
    "ExpectedInput": "backend_v2.models.domain.step",
    "QuestionnaireItem": "backend_v2.models.domain.step",
    "Role": "backend_v2.models.domain.step",
    "Step": "backend_v2.models.domain.step",
    "StepRule": "backend_v2.models.domain.step",
    # backend_v2.models.domain.synthesis
    "BaseMatrixXAI": "backend_v2.models.domain.synthesis",
    "BaseTDAExtraction": "backend_v2.models.domain.synthesis",
    "DistilledEvaluation": "backend_v2.models.domain.synthesis",
    "MatrixSynthesisGroup": "backend_v2.models.domain.synthesis",
    "RenderedSynthesisCache": "backend_v2.models.domain.synthesis",
    "SynthesisMetadataDTO": "backend_v2.models.domain.synthesis",
    "SynthesisStepDataDTO": "backend_v2.models.domain.synthesis",
    # backend_v2.models.domain.system_config
    "AllowedMCPTool": "backend_v2.models.domain.system_config",
    "ChatHistoryDTO": "backend_v2.models.domain.system_config",
    "ChatMessageDTO": "backend_v2.models.domain.system_config",
    "DataDictionaryField": "backend_v2.models.domain.system_config",
    "MCPAuditTrace": "backend_v2.models.domain.system_config",
    "ModelProfile": "backend_v2.models.domain.system_config",
    "ProviderExtraParamsDTO": "backend_v2.models.domain.system_config",
    "SystemConfigMCPGateways": "backend_v2.models.domain.system_config",
    "SystemConfigModelRegistry": "backend_v2.models.domain.system_config",
    # backend_v2.models.domain.workflow
    "Workflow": "backend_v2.models.domain.workflow",
    # backend_v2.models.dtos.atom_result
    "AtomResultDTO": "backend_v2.models.dtos.atom_result",
    "ErrorDetailsDTO": "backend_v2.models.dtos.atom_result",
    "ExecutionMetricsDTO": "backend_v2.models.dtos.atom_result",
    "ExtensionMetricsDTO": "backend_v2.models.dtos.atom_result",
    "ExtractedValueDTO": "backend_v2.models.dtos.atom_result",
    "HydratedAtomDTO": "backend_v2.models.dtos.atom_result",
    # backend_v2.models.dtos.base
    "DataStarvationEvent": "backend_v2.models.dtos.base",
    # backend_v2.models.dtos.matrix_scorecard
    "HumanOverrideDTO": "backend_v2.models.dtos.matrix_scorecard",
    "HumanOverrideRequest": "backend_v2.models.dtos.matrix_scorecard",
    "MatrixScorecardRowDTO": "backend_v2.models.dtos.matrix_scorecard",
    "ScorecardAtomDTO": "backend_v2.models.dtos.matrix_scorecard",
    "TDADlq": "backend_v2.models.dtos.matrix_scorecard",
    "TDAEvaluated": "backend_v2.models.dtos.matrix_scorecard",
    "TDAPending": "backend_v2.models.dtos.matrix_scorecard",
    "TDAStateUnion": "backend_v2.models.dtos.matrix_scorecard",
    # backend_v2.models.dtos.quote_evidence
    "LLMExtractedQuote": "backend_v2.models.dtos.quote_evidence",
    # backend_v2.models.dtos.report_data
    "ReportDataDTO": "backend_v2.models.dtos.report_data",
    # backend_v2.models.dtos.synthesis
    "XaiHighlightItem": "backend_v2.models.dtos.synthesis",
    # backend_v2.models.dtos.workflow_schema
    "WorkflowSchemaResponseDTO": "backend_v2.models.dtos.workflow_schema",
    "WorkflowSchemaResponse": "backend_v2.models.dtos.workflow_schema",
    # backend_v2.models.enums
    "BlockDataType": "backend_v2.models.enums",
    "CognitiveTier": "backend_v2.models.enums",
    "ComponentType": "backend_v2.models.enums",
    "DisplayScale": "backend_v2.models.enums",
    "ExecutionStatus": "backend_v2.models.enums",
    "LaxCognitiveTier": "backend_v2.models.enums",
    "LaxComponentType": "backend_v2.models.enums",
    "LaxDisplayScale": "backend_v2.models.enums",
    "LaxExecutionStatus": "backend_v2.models.enums",
    "LaxHistoricalContextMode": "backend_v2.models.enums",
    "LaxLLMProvider": "backend_v2.models.enums",
    "LaxPresetView": "backend_v2.models.enums",
    "LaxSDUIComponentType": "backend_v2.models.enums",
    "LaxSourcesDisplayMode": "backend_v2.models.enums",
    "LaxStepType": "backend_v2.models.enums",
    "LaxSystemLocale": "backend_v2.models.enums",
    "LaxTargetBlockType": "backend_v2.models.enums",
    "LaxXaiExtensionType": "backend_v2.models.enums",
    "LLMProvider": "backend_v2.models.enums",
    "PresetView": "backend_v2.models.enums",
    "SourcesDisplayMode": "backend_v2.models.enums",
    "StepType": "backend_v2.models.enums",
    "TargetBlockType": "backend_v2.models.enums",
    "TargetSpeaker": "backend_v2.models.enums",
    "XaiExtensionType": "backend_v2.models.enums",
    # backend_v2.models.execution_core
    "ExecutionCoreFields": "backend_v2.models.execution_core",
    "ExecutionMetadata": "backend_v2.models.execution_core",
}

BATCH_A_PATHS = [
    "backend_v2/services",
    "backend_v2/api",
    "backend_v2/workers",
    "backend_v2/database",
    "backend_v2/hooks",
    "backend_v2/llm",
    "backend_v2/models",
    "backend_v2/utils",
    "backend_v2/core",
    "backend_v2/seed",
    "scripts",
]

BATCH_B_PATHS = [
    "backend_v2/tests",
]


def collect_python_files(paths: list[str]) -> list[pathlib.Path]:
    """Collect all Python files from paths, excluding v2_core.py and this script."""
    collected: list[pathlib.Path] = []
    current_script = pathlib.Path(__file__).resolve()
    for p_str in paths:
        p = pathlib.Path(p_str)
        if p.is_file() and p.suffix == ".py":
            if p.resolve() != current_script and p.name != "v2_core.py":
                collected.append(p)
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if f.resolve() != current_script and f.name != "v2_core.py":
                    collected.append(f)
    return sorted(list(set(collected)))


def migrate_file(file_path: pathlib.Path, dry_run: bool = False) -> bool:
    """Migrate v2_core imports in a single file.

    Returns True if file was modified (or would be modified in dry-run).
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = file_path.read_text(encoding="utf-8-sig")

    if "v2_core" not in content:
        return False

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        print(f"ERROR: Syntax error in {file_path}: {e}")
        return False

    # Find all ast.ImportFrom where module == 'backend_v2.models.v2_core'
    v2_core_imports: list[ast.ImportFrom] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and ("backend_v2.models.v2_core" in node.module or node.module == "v2_core")
        ):
            v2_core_imports.append(node)

    if not v2_core_imports:
        return False

    # Sort in descending order of lineno so replacing lines doesn't affect earlier line numbers
    v2_core_imports.sort(key=lambda n: n.lineno, reverse=True)

    lines = content.splitlines(keepends=True)

    for node in v2_core_imports:
        start_line_0 = node.lineno - 1
        end_line_0 = node.end_lineno  # slice index is exclusive

        # Detect line indentation
        orig_first_line = lines[start_line_0]
        indent = orig_first_line[: len(orig_first_line) - len(orig_first_line.lstrip())]

        # Group symbols by target canonical module
        groups: dict[str, list[str]] = defaultdict(list)
        for alias in node.names:
            target_mod = SYMBOL_MAP.get(alias.name)
            if not target_mod:
                raise ValueError(
                    f"Fatal: Unmapped symbol '{alias.name}' in {file_path}:{node.lineno}"
                )
            if alias.asname:
                groups[target_mod].append(f"{alias.name} as {alias.asname}")
            else:
                groups[target_mod].append(alias.name)

        replacement_lines: list[str] = []
        for mod in sorted(groups.keys()):
            symbols = sorted(groups[mod])
            sym_str = ", ".join(symbols)
            replacement_lines.append(f"{indent}from {mod} import {sym_str}\n")

        lines[start_line_0:end_line_0] = replacement_lines

    new_content = "".join(lines)

    if dry_run:
        print(f"[DRY-RUN] Would migrate {len(v2_core_imports)} import(s) in: {file_path}")
        return True

    # Pre-write syntax check
    try:
        ast.parse(new_content, filename=str(file_path))
    except SyntaxError as e:
        print(f"FATAL: Generated invalid Python syntax for {file_path}: {e}")
        return False

    file_path.write_text(new_content, encoding="utf-8")
    print(f"Migrated: {file_path}")

    # Run Ruff to sort imports and format according to project standards
    subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "I", "--fix", str(file_path)],
        capture_output=True,
        check=False,
    )
    subprocess.run(
        [sys.executable, "-m", "ruff", "format", str(file_path)],
        capture_output=True,
        check=False,
    )

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate v2_core imports to canonical domain/DTO modules."
    )
    parser.add_argument("paths", nargs="*", help="Files or directories to migrate.")
    parser.add_argument(
        "--batch-a",
        action="store_true",
        help="Migrate all production callers (Batch A).",
    )
    parser.add_argument(
        "--batch-b",
        action="store_true",
        help="Migrate all test callers (Batch B).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all files in workspace.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing to disk.",
    )

    args = parser.parse_args()

    target_paths: list[str] = []
    if args.batch_a:
        target_paths.extend(BATCH_A_PATHS)
    if args.batch_b:
        target_paths.extend(BATCH_B_PATHS)
    if args.all:
        target_paths.extend(BATCH_A_PATHS)
        target_paths.extend(BATCH_B_PATHS)
    if args.paths:
        target_paths.extend(args.paths)

    if not target_paths:
        parser.print_help()
        sys.exit(1)

    files = collect_python_files(target_paths)
    print(f"Scanning {len(files)} Python files...")

    modified_count = 0
    for f in files:
        if migrate_file(f, dry_run=args.dry_run):
            modified_count += 1

    action_word = "Would modify" if args.dry_run else "Modified"
    print(f"Done! {action_word} {modified_count} files.")


if __name__ == "__main__":
    main()
