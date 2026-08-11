import ast
from pathlib import Path
from typing import Any

import pytest


class DomainSecurityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.found_llmclient_strategy = False
        self.found_safe_commit = False
        self.found_streaming_response = False
        self.found_run_chat = False
        self.found_hasattr = False
        self.found_html_escape = False

        self.pydantic_classes: list[tuple[str, bool, bool]] = []

    def visit_Call(self, node: ast.Call) -> None:
        if getattr(node.func, "id", "") == "hasattr":
            self.found_hasattr = True
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr == "from_strategy" and getattr(node.func.value, "id", "") == "LLMClient":
                self.found_llmclient_strategy = True
            if node.func.attr == "run_chat":
                self.found_run_chat = True
            if node.func.attr == "escape" and getattr(node.func.value, "id", "") == "html":
                self.found_html_escape = True
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node.name == "_safe_commit":
            self.found_safe_commit = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name == "_safe_commit":
            self.found_safe_commit = True
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "StreamingResponse":
            self.found_streaming_response = True
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "StreamingResponse":
            self.found_streaming_response = True
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        is_enum = False
        is_model = False
        for base in node.bases:
            base_id = getattr(base, "id", "")
            if base_id in ("Enum", "StrEnum", "IntEnum"):
                is_enum = True
            if isinstance(base, ast.Attribute) and base.attr in ("Enum", "StrEnum", "IntEnum"):
                is_enum = True
            if (
                base_id in ("BaseModel", "BaseResponseDTO", "RootModel", "SduiBlockDTO")
                or base_id.endswith("DTO")
                or base_id.endswith("Model")
            ):
                is_model = True

        if not is_enum and (is_model or node.name.endswith("DTO") or node.name.endswith("Model")):
            has_strict = False
            has_forbid = False
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if getattr(target, "id", "") == "model_config":
                            if isinstance(stmt.value, ast.Call) and getattr(stmt.value.func, "id", "") == "ConfigDict":
                                allowed_exceptions = {"SystemWarningsStateDTO"}
                                for kw in stmt.value.keywords:
                                    if kw.arg == "strict" and getattr(kw.value, "value", None) is True:
                                        has_strict = True
                                    if kw.arg == "extra" and (
                                        getattr(kw.value, "value", None) == "forbid"
                                        or (
                                            node.name in allowed_exceptions
                                            and getattr(kw.value, "value", None) == "ignore"
                                        )
                                    ):
                                        has_forbid = True
            self.pydantic_classes.append((node.name, has_strict, has_forbid))

        self.generic_visit(node)


def scan_code_for_domain_security(code: str) -> dict[str, Any]:
    tree = ast.parse(code)
    visitor = DomainSecurityVisitor()
    visitor.visit(tree)
    return {
        "llmclient_strategy": visitor.found_llmclient_strategy,
        "safe_commit": visitor.found_safe_commit,
        "streaming_response": visitor.found_streaming_response,
        "run_chat": visitor.found_run_chat,
        "hasattr": visitor.found_hasattr,
        "html_escape": visitor.found_html_escape,
        "pydantic_classes": visitor.pydantic_classes,
    }


def scan_file_for_domain_security(filepath: Path) -> dict[str, Any]:
    if not filepath.exists():
        return {
            "llmclient_strategy": False,
            "safe_commit": False,
            "streaming_response": False,
            "run_chat": False,
            "hasattr": False,
            "html_escape": False,
            "pydantic_classes": [],
        }
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_domain_security(code)


def test_ast_hasattr_ban() -> None:
    api_dir = Path("backend_v2/api")
    if api_dir.exists():
        for filepath in api_dir.rglob("*.py"):
            res = scan_file_for_domain_security(filepath)
            assert not res["hasattr"], f"Banned hasattr() found in API layer: {filepath}"


def test_ast_run_chat_ban() -> None:
    orch_dir = Path("backend_v2/services/orchestrator")
    if orch_dir.exists():
        for filepath in orch_dir.rglob("*.py"):
            res = scan_file_for_domain_security(filepath)
            assert not res["run_chat"], f"Banned unstructured run_chat() found in orchestrator layer: {filepath}"


def test_ast_pydantic_strictness_guardrail() -> None:
    models_dir = Path("backend_v2/models")
    if models_dir.exists():
        for filepath in models_dir.rglob("*.py"):
            res = scan_file_for_domain_security(filepath)
            for class_name, has_strict, has_forbid in res["pydantic_classes"]:
                assert has_strict and has_forbid, (
                    f"Model {class_name} in {filepath} lacks ConfigDict(strict=True, extra='forbid')"
                )


def test_ast_required_constructs() -> None:
    base_dir = Path("backend_v2")
    found_llm = False
    found_commit = False
    found_streaming = False

    if base_dir.exists():
        for filepath in base_dir.rglob("*.py"):
            res = scan_file_for_domain_security(filepath)
            if res["llmclient_strategy"]:
                found_llm = True
            if res["safe_commit"]:
                found_commit = True
            if res["streaming_response"]:
                found_streaming = True

    assert found_llm, "LLMClient.from_strategy not found anywhere"
    assert found_commit, "_safe_commit not found anywhere"
    assert found_streaming, "StreamingResponse not found anywhere"


def test_negative_banned_node_detection() -> None:
    code = "hasattr(obj, 'field')"
    res = scan_code_for_domain_security(code)
    assert res["hasattr"] is True


def test_negative_false_positive_prevention() -> None:
    code = "a = 'hasattr'"
    res = scan_code_for_domain_security(code)
    assert res["hasattr"] is False


def test_negative_missing_pydantic_strictness() -> None:
    code = """
class BadModel(BaseModel):
    model_config = ConfigDict(strict=True)
"""
    res = scan_code_for_domain_security(code)
    class_name, has_strict, has_forbid = res["pydantic_classes"][0]
    assert has_strict is True
    assert has_forbid is False


def test_negative_banned_run_chat_call() -> None:
    code = "await client.run_chat(messages)"
    res = scan_code_for_domain_security(code)
    assert res["run_chat"] is True


@pytest.mark.skip(reason="Awaiting prompt sanitization implementation")
def test_aspirational_html_escape() -> None:
    base_dir = Path("backend_v2")
    found_escape = False
    if base_dir.exists():
        for filepath in base_dir.rglob("*.py"):
            res = scan_file_for_domain_security(filepath)
            if res["html_escape"]:
                found_escape = True
                break
    assert found_escape, "html.escape not found for payload sanitization"
