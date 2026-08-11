import ast
from pathlib import Path


class ConcurrencyVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.semaphore_aliases: set[str] = set()
        self.taskgroup_aliases: set[str] = set()
        self.asyncio_aliases: set[str] = {"asyncio"}

        self.found_semaphore = False
        self.found_taskgroup = False
        self.found_enqueue_job = False

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "asyncio":
                self.asyncio_aliases.add(alias.asname or "asyncio")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "asyncio":
            for alias in node.names:
                if alias.name == "Semaphore":
                    self.semaphore_aliases.add(alias.asname or "Semaphore")
                elif alias.name == "TaskGroup":
                    self.taskgroup_aliases.add(alias.asname or "TaskGroup")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id in self.asyncio_aliases:
            if node.attr == "Semaphore":
                self.found_semaphore = True
            elif node.attr == "TaskGroup":
                self.found_taskgroup = True

        if node.attr == "enqueue_job":
            self.found_enqueue_job = True

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.semaphore_aliases:
            self.found_semaphore = True
        if node.id in self.taskgroup_aliases:
            self.found_taskgroup = True
        if node.id == "enqueue_job":
            self.found_enqueue_job = True
        self.generic_visit(node)


def scan_code_for_concurrency(code: str) -> dict[str, bool]:
    tree = ast.parse(code)
    visitor = ConcurrencyVisitor()
    visitor.visit(tree)
    return {
        "semaphore": visitor.found_semaphore,
        "taskgroup": visitor.found_taskgroup,
        "enqueue_job": visitor.found_enqueue_job,
    }


def scan_file_for_concurrency(filepath: Path) -> dict[str, bool]:
    if not filepath.exists():
        return {"semaphore": False, "taskgroup": False, "enqueue_job": False}
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_concurrency(code)


def test_ast_semaphore_guardrail() -> None:
    base = Path("backend_v2")
    provider_path = base / "llm" / "provider.py"
    dag_executor_path = base / "services" / "orchestrator" / "dag_executor.py"

    if provider_path.exists():
        res = scan_file_for_concurrency(provider_path)
        assert res["semaphore"] is True, f"Missing asyncio.Semaphore in {provider_path}"

    if dag_executor_path.exists():
        res = scan_file_for_concurrency(dag_executor_path)
        assert res["semaphore"] is True, f"Missing asyncio.Semaphore in {dag_executor_path}"


def test_ast_taskgroup_guardrail() -> None:
    base = Path("backend_v2")
    files = [
        base / "services" / "orchestrator" / "dag_executor.py",
        base / "worker.py",
        base / "services" / "execution.py",
    ]
    for path in files:
        if path.exists():
            res = scan_file_for_concurrency(path)
            assert res["taskgroup"] is True, f"Missing asyncio.TaskGroup in {path}"


def test_ast_enqueue_job_guardrail() -> None:
    base = Path("backend_v2")
    files = [
        base / "worker.py",
        base / "services" / "execution.py",
    ]
    for path in files:
        if path.exists():
            res = scan_file_for_concurrency(path)
            assert res["enqueue_job"] is True, f"Missing enqueue_job in {path}"


def test_negative_missing_construct_detection() -> None:
    code = """
import asyncio
async def task():
    await asyncio.sleep(1)
"""
    res = scan_code_for_concurrency(code)
    assert res["semaphore"] is False
    assert res["taskgroup"] is False


def test_negative_false_positive_prevention() -> None:
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
