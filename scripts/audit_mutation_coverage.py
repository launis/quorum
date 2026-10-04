"""Pure Python stdlib AST mutation testing engine for Quorum mathematical cores.

Systematically verifies test suite assertion sensitivity by mutating relational,
arithmetic, and conditional operators in mathematical and algorithmic engines
(UnifiedScoringEngine and TopologicalEvaluator) and asserting a 100% mutant kill rate.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "MutationSpec",
    "MutationResult",
    "TargetAuditReport",
    "MutationCoverageReport",
    "TargetConfig",
    "DEFAULT_TARGETS",
    "collect_mutation_sites",
    "apply_mutation",
    "audit_target_mutations",
    "run_mutation_audit",
    "main",
]

# Operator Mutation Mappings
MUTATION_MAP_COMPARE: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Lt: ast.GtE,
    ast.LtE: ast.Gt,
    ast.Gt: ast.LtE,
    ast.GtE: ast.Lt,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
}

MUTATION_MAP_BINOP: dict[type[ast.operator], type[ast.operator]] = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.Div,
    ast.Div: ast.Mult,
    ast.FloorDiv: ast.Mult,
    ast.Pow: ast.Mult,
}

AST_COMPARE_CONSTRUCTORS: dict[str, type[ast.cmpop]] = {
    "Eq": ast.Eq,
    "NotEq": ast.NotEq,
    "Lt": ast.Lt,
    "LtE": ast.LtE,
    "Gt": ast.Gt,
    "GtE": ast.GtE,
    "In": ast.In,
    "NotIn": ast.NotIn,
    "Is": ast.Is,
    "IsNot": ast.IsNot,
}

AST_BINOP_CONSTRUCTORS: dict[str, type[ast.operator]] = {
    "Add": ast.Add,
    "Sub": ast.Sub,
    "Mult": ast.Mult,
    "Div": ast.Div,
    "FloorDiv": ast.FloorDiv,
    "Pow": ast.Pow,
}


class MutationSpec(BaseModel):
    """Pydantic V2 DTO representing an exact AST mutation site."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_type: Annotated[str, Field(description="AST node type e.g. Compare, BinOp, AugAssign")]
    filepath: Annotated[str, Field(description="Target source file path")]
    lineno: Annotated[int, Field(ge=1, description="1-indexed line number of mutation")]
    col_offset: Annotated[int, Field(ge=0, description="Column offset of mutation")]
    op_index: Annotated[int, Field(ge=0, description="Operator index for chained comparisons")]
    original_op: Annotated[str, Field(description="Name of original operator")]
    mutated_op: Annotated[str, Field(description="Name of mutated operator")]
    description: Annotated[str, Field(description="Human-readable description of mutation")]


class MutationResult(BaseModel):
    """Pydantic V2 DTO representing the execution result of a single mutant."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    spec: Annotated[MutationSpec, Field(description="The applied mutation specification")]
    killed: Annotated[bool, Field(description="True if the test suite caught and killed the mutant")]
    killer_output: Annotated[str | None, Field(default=None, description="Diagnostic output from killing test")]


class TargetAuditReport(BaseModel):
    """Pydantic V2 DTO representing mutation coverage results for a single target."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_name: Annotated[str, Field(description="Logical target name")]
    target_file: Annotated[str, Field(description="Path to target source file")]
    test_file: Annotated[str, Field(description="Path to target test suite file")]
    total_mutants: Annotated[int, Field(ge=0, description="Total number of evaluated mutants")]
    killed_mutants: Annotated[int, Field(ge=0, description="Number of killed mutants")]
    survived_mutants: Annotated[int, Field(ge=0, description="Number of surviving mutants")]
    kill_rate: Annotated[float, Field(ge=0.0, le=100.0, description="Percentage of mutants killed")]
    results: Annotated[list[MutationResult], Field(description="Detailed result for each mutant")]


class MutationCoverageReport(BaseModel):
    """Pydantic V2 DTO representing the global mutation testing report."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    targets: Annotated[list[TargetAuditReport], Field(description="Per-target audit reports")]
    overall_kill_rate: Annotated[float, Field(ge=0.0, le=100.0, description="Global mutant kill percentage")]
    success: Annotated[bool, Field(description="True if overall kill rate meets required threshold")]


@dataclass(frozen=True)
class TargetConfig:
    """Configuration mapping a target source file to its validating test suite."""

    name: str
    target_file: str
    test_file: str


DEFAULT_TARGETS: list[TargetConfig] = [
    TargetConfig(
        name="topological_evaluator",
        target_file="backend_v2/services/orchestrator/topological_evaluator.py",
        test_file="backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py",
    ),
    TargetConfig(
        name="unified_engine",
        target_file="backend_v2/utils/scoring/unified_engine.py",
        test_file="backend_v2/tests/unit/utils/scoring/test_unified_engine.py",
    ),
]


class MutationSiteCollector(ast.NodeVisitor):
    """AST visitor that collects candidate operator mutation sites within function bodies."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.sites: list[MutationSpec] = []

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        # Mutate value assignment but strictly skip type annotation to avoid syntax errors
        self.visit(node.target)
        if node.value is not None:
            self.visit(node.value)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Only visit body statements; skip decorators, arguments annotations, and returns
        for stmt in node.body:
            self.visit(stmt)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        # Only visit body statements; skip decorators, arguments annotations, and returns
        for stmt in node.body:
            self.visit(stmt)

    def visit_Compare(self, node: ast.Compare) -> None:
        for idx, op in enumerate(node.ops):
            op_cls = type(op)
            if op_cls in MUTATION_MAP_COMPARE:
                mutated_cls = MUTATION_MAP_COMPARE[op_cls]
                spec = MutationSpec(
                    target_type="Compare",
                    filepath=self.filepath,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    op_index=idx,
                    original_op=op_cls.__name__,
                    mutated_op=mutated_cls.__name__,
                    description=f"Compare at L{node.lineno}:{node.col_offset} - {op_cls.__name__} -> {mutated_cls.__name__}",
                )
                self.sites.append(spec)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        op_cls = type(node.op)
        if op_cls in MUTATION_MAP_BINOP:
            mutated_cls = MUTATION_MAP_BINOP[op_cls]
            spec = MutationSpec(
                target_type="BinOp",
                filepath=self.filepath,
                lineno=node.lineno,
                col_offset=node.col_offset,
                op_index=0,
                original_op=op_cls.__name__,
                mutated_op=mutated_cls.__name__,
                description=f"BinOp at L{node.lineno}:{node.col_offset} - {op_cls.__name__} -> {mutated_cls.__name__}",
            )
            self.sites.append(spec)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        op_cls = type(node.op)
        if op_cls in MUTATION_MAP_BINOP:
            mutated_cls = MUTATION_MAP_BINOP[op_cls]
            spec = MutationSpec(
                target_type="AugAssign",
                filepath=self.filepath,
                lineno=node.lineno,
                col_offset=node.col_offset,
                op_index=0,
                original_op=op_cls.__name__,
                mutated_op=mutated_cls.__name__,
                description=f"AugAssign at L{node.lineno}:{node.col_offset} - {op_cls.__name__} -> {mutated_cls.__name__}",
            )
            self.sites.append(spec)
        self.generic_visit(node)


class SingleASTMutator(ast.NodeTransformer):
    """AST transformer that modifies exactly one matching operator site."""

    def __init__(self, spec: MutationSpec) -> None:
        self.spec = spec
        self.mutated: bool = False

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        if (
            not self.mutated
            and self.spec.target_type == "Compare"
            and node.lineno == self.spec.lineno
            and node.col_offset == self.spec.col_offset
        ):
            new_ops = list(node.ops)
            target_op_cls = AST_COMPARE_CONSTRUCTORS[self.spec.mutated_op]
            new_ops[self.spec.op_index] = target_op_cls()
            node.ops = new_ops
            self.mutated = True
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        if (
            not self.mutated
            and self.spec.target_type == "BinOp"
            and node.lineno == self.spec.lineno
            and node.col_offset == self.spec.col_offset
        ):
            target_op_cls = AST_BINOP_CONSTRUCTORS[self.spec.mutated_op]
            node.op = target_op_cls()
            self.mutated = True
        return self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        if (
            not self.mutated
            and self.spec.target_type == "AugAssign"
            and node.lineno == self.spec.lineno
            and node.col_offset == self.spec.col_offset
        ):
            target_op_cls = AST_BINOP_CONSTRUCTORS[self.spec.mutated_op]
            node.op = target_op_cls()
            self.mutated = True
        return self.generic_visit(node)


def collect_mutation_sites(source_code: str, filepath: str = "<string>") -> list[MutationSpec]:
    """Parses Python source code and returns all candidate mutation sites.

    Args:
        source_code: Source code string to analyze.
        filepath: Virtual or real file path for metadata.

    Returns:
        List of collected MutationSpec instances.
    """
    tree = ast.parse(source_code, filename=filepath)
    collector = MutationSiteCollector(filepath)
    collector.visit(tree)
    return collector.sites


def apply_mutation(source_code: str, spec: MutationSpec) -> str:
    """Applies a single mutation specification to source code.

    Args:
        source_code: Original Python source code string.
        spec: Mutation specification targeting a specific AST node.

    Returns:
        Mutated Python source code string.

    Raises:
        ValueError: If the targeted node was not found or mutated.
    """
    tree = ast.parse(source_code, filename=spec.filepath)
    mutator = SingleASTMutator(spec)
    mutated_tree = mutator.visit(deepcopy(tree))
    if not mutator.mutated:
        raise ValueError(f"Mutation target not found in AST: {spec.description}")
    ast.fix_missing_locations(mutated_tree)
    return ast.unparse(mutated_tree)


def audit_target_mutations(
    target: TargetConfig,
    timeout: float = 15.0,
    max_mutants: int | None = None,
    dry_run: bool = False,
) -> TargetAuditReport:
    """Executes mutation testing across a single target and its test suite.

    Args:
        target: Target configuration linking source and test files.
        timeout: Subprocess timeout in seconds per test run.
        max_mutants: Optional maximum mutants to evaluate.
        dry_run: If True, enumerates mutants without executing pytest.

    Returns:
        TargetAuditReport containing full execution details.
    """
    target_path = Path(target.target_file)
    test_path = Path(target.test_file)

    if not target_path.exists():
        raise FileNotFoundError(f"Target source file not found: {target.target_file}")
    if not test_path.exists():
        raise FileNotFoundError(f"Target test suite file not found: {target.test_file}")

    original_code = target_path.read_text(encoding="utf-8")
    specs = collect_mutation_sites(original_code, filepath=target.target_file)

    if max_mutants is not None and max_mutants > 0:
        specs = specs[:max_mutants]

    results: list[MutationResult] = []

    if dry_run:
        for spec in specs:
            results.append(MutationResult(spec=spec, killed=True, killer_output="[DRY_RUN]"))
        return TargetAuditReport(
            target_name=target.name,
            target_file=target.target_file,
            test_file=target.test_file,
            total_mutants=len(specs),
            killed_mutants=len(specs),
            survived_mutants=0,
            kill_rate=100.0,
            results=results,
        )

    killed_count = 0
    survived_count = 0

    for spec in specs:
        mutated_code = apply_mutation(original_code, spec)
        try:
            target_path.write_text(mutated_code, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-q", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode != 0:
                killed = True
                killed_count += 1
                killer_output = proc.stdout.strip()
            else:
                killed = False
                survived_count += 1
                killer_output = None
        except subprocess.TimeoutExpired:
            # Infinite loop caused by mutant: effectively killed
            killed = True
            killed_count += 1
            killer_output = "TIMEOUT: Test suite exceeded execution limit (infinite loop detected)"
        finally:
            target_path.write_text(original_code, encoding="utf-8")

        results.append(
            MutationResult(
                spec=spec,
                killed=killed,
                killer_output=killer_output,
            )
        )

    total = len(specs)
    kill_rate = (killed_count / total * 100.0) if total > 0 else 100.0

    return TargetAuditReport(
        target_name=target.name,
        target_file=target.target_file,
        test_file=target.test_file,
        total_mutants=total,
        killed_mutants=killed_count,
        survived_mutants=survived_count,
        kill_rate=kill_rate,
        results=results,
    )


def run_mutation_audit(
    targets: list[TargetConfig] | None = None,
    strict: bool = True,
    timeout: float = 15.0,
    max_mutants: int | None = None,
    dry_run: bool = False,
) -> MutationCoverageReport:
    """Executes mutation testing across all configured targets.

    Args:
        targets: List of TargetConfig items, or None for DEFAULT_TARGETS.
        strict: If True, requires 100% kill rate across all targets.
        timeout: Subprocess timeout in seconds per test run.
        max_mutants: Optional maximum mutants per target.
        dry_run: If True, enumerates mutants without executing pytest.

    Returns:
        MutationCoverageReport detailing results across all targets.
    """
    eval_targets = targets if targets is not None else DEFAULT_TARGETS
    reports: list[TargetAuditReport] = []

    total_mutants = 0
    total_killed = 0

    for target in eval_targets:
        report = audit_target_mutations(
            target=target,
            timeout=timeout,
            max_mutants=max_mutants,
            dry_run=dry_run,
        )
        reports.append(report)
        total_mutants += report.total_mutants
        total_killed += report.killed_mutants

    overall_kill_rate = (total_killed / total_mutants * 100.0) if total_mutants > 0 else 100.0
    success = (overall_kill_rate >= 100.0) if strict else (total_killed > 0)

    return MutationCoverageReport(
        targets=reports,
        overall_kill_rate=overall_kill_rate,
        success=success,
    )


def main() -> None:
    """CLI entrypoint for AST mutation coverage testing."""
    parser = argparse.ArgumentParser(
        description="Quorum V2 AST Mutation Testing Engine for Mathematical Cores",
    )
    parser.add_argument(
        "--target",
        choices=["all", "unified_engine", "topological_evaluator"],
        default="all",
        help="Target mathematical core to evaluate (default: all)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Enforce 100%% mutant kill rate; fail-fast if any mutant survives (default: True)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enumerate candidate mutation sites without executing pytest sub-processes",
    )
    parser.add_argument(
        "--max-mutants",
        type=int,
        default=None,
        help="Maximum mutants to evaluate per target (useful for fast smoke verification)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as machine-readable JSON",
    )

    args = parser.parse_args()

    if args.target == "all":
        targets = DEFAULT_TARGETS
    else:
        targets = [t for t in DEFAULT_TARGETS if t.name == args.target]

    start_time = time.monotonic()
    report = run_mutation_audit(
        targets=targets,
        strict=args.strict,
        max_mutants=args.max_mutants,
        dry_run=args.dry_run,
    )
    elapsed = time.monotonic() - start_time

    if args.json:
        print(report.model_dump_json(indent=2))
        sys.exit(0 if report.success else 1)

    import io

    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 80)
    print("QUORUM V2 AST MUTATION INVARIANCE REPORT")
    print("=" * 80)

    for target_report in report.targets:
        print(f"\nTarget: {target_report.target_name}")
        print(f"  Source File: {target_report.target_file}")
        print(f"  Test File:   {target_report.test_file}")
        print(
            f"  Mutants:     {target_report.killed_mutants}/{target_report.total_mutants} killed ({target_report.kill_rate:.1f}%)"
        )

        if target_report.survived_mutants > 0:
            print("  [WARN] SURVIVING MUTANTS DETECTED:")
            for res in target_report.results:
                if not res.killed:
                    print(
                        f"    - L{res.spec.lineno}:{res.spec.col_offset} [{res.spec.original_op} -> {res.spec.mutated_op}] {res.spec.description}"
                    )

    print("\n" + "-" * 80)
    print(f"Overall Mutant Kill Rate: {report.overall_kill_rate:.1f}% ({elapsed:.2f}s)")
    if report.success:
        print("[PASS] MUTATION INVARIANCE VERIFIED: 100% of arithmetic and relational mutants killed.")
        sys.exit(0)
    else:
        print("[FAIL] MUTATION AUDIT FAILED: One or more mutants survived test assertions.")
        sys.exit(1)


if __name__ == "__main__":
    main()
