"""AST guardrails for verifying concurrency patterns in key modules."""

import ast
from pathlib import Path


class ConcurrencyVisitor(ast.NodeVisitor):
    """AST visitor scanning for concurrency constructs."""

    def __init__(self) -> None:
        """Initialize tracking sets and flags."""
        self.semaphore_aliases: set[str] = set()
        self.taskgroup_aliases: set[str] = set()
        self.asyncio_aliases: set[str] = {"asyncio"}

        self.found_semaphore = False
        self.found_taskgroup = False
        self.found_enqueue_job = False

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements to track asyncio aliases."""
        for alias in node.names:
            if alias.name == "asyncio":
                self.asyncio_aliases.add(alias.asname or "asyncio")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements to track concurrency aliases."""
        if node.module == "asyncio":
            for alias in node.names:
                if alias.name == "Semaphore":
                    self.semaphore_aliases.add(alias.asname or "Semaphore")
                elif alias.name == "TaskGroup":
                    self.taskgroup_aliases.add(alias.asname or "TaskGroup")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute nodes to detect semaphore and taskgroup usages."""
        if isinstance(node.value, ast.Name) and node.value.id in self.asyncio_aliases:
            if node.attr == "Semaphore":
                self.found_semaphore = True
            elif node.attr == "TaskGroup":
                self.found_taskgroup = True

        if node.attr == "enqueue_job":
            self.found_enqueue_job = True

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Visit name nodes to detect imported concurrency aliases."""
        if node.id in self.semaphore_aliases:
            self.found_semaphore = True
        if node.id in self.taskgroup_aliases:
            self.found_taskgroup = True
        if node.id == "enqueue_job":
            self.found_enqueue_job = True
        self.generic_visit(node)


def scan_code_for_concurrency(code: str) -> dict[str, bool]:
    """Scan Python source code string for concurrency constructs."""
    tree = ast.parse(code)
    visitor = ConcurrencyVisitor()
    visitor.visit(tree)
    return {
        "semaphore": visitor.found_semaphore,
        "taskgroup": visitor.found_taskgroup,
        "enqueue_job": visitor.found_enqueue_job,
    }


def scan_file_for_concurrency(filepath: Path) -> dict[str, bool]:
    """Scan Python file for concurrency constructs, asserting existence."""
    assert filepath.exists(), f"Guardrail target missing: {filepath}"
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_concurrency(code)


def test_ast_semaphore_guardrail() -> None:
    """Verify that semaphore usage is present in required modules."""
    base = Path(__file__).resolve().parents[2]
    provider_path = base / "llm" / "provider.py"
    dag_executor_path = base / "services" / "orchestrator" / "dag_executor.py"

    assert provider_path.exists(), f"Target missing: {provider_path}"
    res = scan_file_for_concurrency(provider_path)
    assert res["semaphore"] is True, f"Missing asyncio.Semaphore in {provider_path}"

    assert dag_executor_path.exists(), f"Target missing: {dag_executor_path}"
    res = scan_file_for_concurrency(dag_executor_path)
    assert res["semaphore"] is True, f"Missing asyncio.Semaphore in {dag_executor_path}"


def test_ast_taskgroup_guardrail() -> None:
    """Verify that TaskGroup usage is present in required modules."""
    base = Path(__file__).resolve().parents[2]
    files = [
        base / "services" / "orchestrator" / "dag_executor.py",
        base / "workers" / "synthesis_worker.py",
    ]
    for path in files:
        assert path.exists(), f"Target missing: {path}"
        res = scan_file_for_concurrency(path)
        assert res["taskgroup"] is True, f"Missing asyncio.TaskGroup in {path}"


def test_ast_enqueue_job_guardrail() -> None:
    """Verify that enqueue_job usage is present in required modules."""
    base = Path(__file__).resolve().parents[2]
    files = [
        base / "services" / "report_service.py",
        base / "services" / "execution" / "ingress_service.py",
    ]
    for path in files:
        assert path.exists(), f"Target missing: {path}"
        res = scan_file_for_concurrency(path)
        assert res["enqueue_job"] is True, f"Missing enqueue_job in {path}"


def test_negative_missing_construct_detection() -> None:
    """Verify that missing constructs return False."""
    code = """
import asyncio
async def task():
    await asyncio.sleep(1)
"""
    res = scan_code_for_concurrency(code)
    assert res["semaphore"] is False
    assert res["taskgroup"] is False


def test_negative_false_positive_prevention() -> None:
    """Verify that string literals do not trigger false positive detections."""
    code = """
def test():
    a = "asyncio.Semaphore"
    b = 'TaskGroup'
    c = "enqueue_job"
"""
    res = scan_code_for_concurrency(code)
    assert res["semaphore"] is False
    assert res["taskgroup"] is False
    assert res["enqueue_job"] is False
