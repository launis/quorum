"""Unit tests for Tier 1 and Tier 8 audit verification scripts and AST boundary utilities.

Verifies audit_planner_output.py, audit_epic_coverage.py, and _ast_boundary_utils.py.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts directory to sys.path to allow direct unit testing of utilities
scripts_dir = Path("scripts").resolve()
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from _ast_boundary_utils import (  # noqa: E402
    SymbolDefinitionVisitor,
    extract_deprecated_symbols,
    extract_target_files,
    find_symbols_in_python_code,
    parse_line_bound,
    validate_ast_line_bound,
)
from audit_dto_parity import (  # noqa: E402
    audit_parity,
    camel_to_snake,
    extract_freezed_fields,
    extract_pydantic_fields,
    snake_to_camel,
)
from audit_dto_parity import (
    main as audit_dto_parity_main,
)
from audit_epic_coverage import (  # noqa: E402
    extract_phase_content,
    main as audit_epic_coverage_main,
    scan_for_lingering_symbols,
)
from audit_rules_staleness import (  # noqa: E402
    audit_rules_staleness,
    extract_code_symbols_from_rules,
    verify_symbols_exist,
)
from audit_rules_staleness import (
    main as audit_rules_staleness_main,
)


def test_extract_target_files_various_syntaxes() -> None:
    """Test extracting target files across diverse Markdown annotation syntaxes."""
    content = """
# Phase Target Files
* `[MODIFY]` `@[backend_v2/settings.py#L10-L20]`
* [NEW] @[backend_v2/utils/ranked_round_robin.py]
- `[DELETE]` `@[legacy_file.py]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/view.dart]`
    """
    targets = extract_target_files(content)
    assert len(targets) == 4

    actions = [t[0] for t in targets]
    paths = [t[1] for t in targets]
    bounds = [t[2] for t in targets]

    assert actions == ["MODIFY", "NEW", "DELETE", "MODIFY"]
    assert "backend_v2/settings.py" in paths
    assert "backend_v2/utils/ranked_round_robin.py" in paths
    assert "legacy_file.py" in paths
    assert "client_app_v2/lib/features/studio/view.dart" in paths
    assert bounds[0] == "#L10-L20"
    assert bounds[1] is None


def test_parse_line_bound_formats() -> None:
    """Test line bound string parsing for various valid and invalid formats."""
    assert parse_line_bound("#L10-L25") == (10, 25)
    assert parse_line_bound("#L10-25") == (10, 25)
    assert parse_line_bound("L100-L200") == (100, 200)
    assert parse_line_bound("#L30-L10") == (10, 30)
    assert parse_line_bound("invalid_bound") is None
    assert parse_line_bound("") is None


def test_validate_ast_line_bound_edge_cases(tmp_path: Path) -> None:
    """Test AST line bound validation across valid nodes, invalid bounds, and non-python files."""
    py_file = tmp_path / "test_module.py"
    py_file.write_text(
        "class TestClass:\n"
        "    def method_one(self) -> None:\n"
        "        pass\n\n"
        "async def async_func() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )

    # Valid bounds covering class or functions
    assert validate_ast_line_bound(py_file, 1, 3) is True
    assert validate_ast_line_bound(py_file, 5, 6) is True
    assert validate_ast_line_bound(py_file, 1, 6) is True

    # Invalid range with no definitions
    assert validate_ast_line_bound(py_file, 10, 20) is False

    # Non-python or non-existent file
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("not python code", encoding="utf-8")
    assert validate_ast_line_bound(txt_file, 1, 10) is False
    assert validate_ast_line_bound(tmp_path / "non_existent.py", 1, 10) is False

    # Syntax error file
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("def broken_syntax(:", encoding="utf-8")
    assert validate_ast_line_bound(bad_py, 1, 5) is False

    # Non-UTF8 raw bytes file (UnicodeDecodeError handling)
    non_utf8_file = tmp_path / "invalid_encoding.py"
    non_utf8_file.write_bytes(b"\xff\xfe\x00\x00def test(): pass")
    assert validate_ast_line_bound(non_utf8_file, 1, 5) is False


def test_find_symbols_in_python_code_various_nodes() -> None:
    """Test symbol scanning in Python AST covering classes, functions, async functions, and assignments."""
    code = """
class TargetClass:
    pass

def target_func() -> None:
    pass

async def target_async_func() -> None:
    pass

target_ann_var: int = 10
target_var = "value"
other_var = "ignored"
"""
    symbols = {
        "TargetClass",
        "target_func",
        "target_async_func",
        "target_ann_var",
        "target_var",
        "missing_symbol",
    }
    found = find_symbols_in_python_code(code, symbols)

    assert "TargetClass" in found
    assert "target_func" in found
    assert "target_async_func" in found
    assert "target_ann_var" in found
    assert "target_var" in found
    assert "missing_symbol" not in found

    # Syntax error test
    assert find_symbols_in_python_code("def broken(:", symbols) == {}


def test_symbol_definition_visitor_direct() -> None:
    """Test SymbolDefinitionVisitor standalone behavior."""
    visitor = SymbolDefinitionVisitor({"SymA", "SymB"})
    assert visitor.target_symbols == {"SymA", "SymB"}
    assert visitor.found_symbols == {"SymA": [], "SymB": []}


def test_audit_planner_output_success_on_valid_inputs(tmp_path: Path) -> None:
    """Test that audit_planner_output passes when all line bounds, KIs, and targets match."""
    py_file = tmp_path / "sample_service.py"
    py_file.write_text(
        "class SampleClass:\n    def sample_method(self) -> None:\n        pass\n",
        encoding="utf-8",
    )

    epic_file = tmp_path / "EPIC_TEST.md"
    rel_py_path = py_file.as_posix()
    epic_file.write_text(
        f"# Epic Test\n\n"
        f"- `[MODIFY]` `@[{rel_py_path}#L1-L3]`\n"
        f"Line bound reference: #{rel_py_path}#L1-L3\n"
        f"KI reference: knowledge/sample/artifacts/ki_sample.md\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        f"# Plan 1\n\n"
        f"Target: `@[{rel_py_path}#L1-L3]`\n"
        f"KI reference: knowledge/sample/artifacts/ki_sample.md\n"
        f"<required_context_rules>\n"
        f"  <rule>00-antigravity-core.md</rule>\n"
        f"  <rule>01-python-backend.md</rule>\n"
        f"</required_context_rules>\n"
        f"<anti_targets>\n</anti_targets>\n"
        f"<dod_checklist>\n</dod_checklist>\n"
        f"<validation_gate>\n</validation_gate>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_planner_output.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script_path), "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "AUDIT PASSED" in result.stdout


def test_audit_planner_output_fails_on_dropped_bounds(tmp_path: Path) -> None:
    """Test that audit_planner_output fails when line bounds from Epic are missing from plans."""
    py_file = tmp_path / "sample_service.py"
    py_file.write_text(
        "class SampleClass:\n    def sample_method(self) -> None:\n        pass\n",
        encoding="utf-8",
    )

    epic_file = tmp_path / "EPIC_TEST.md"
    rel_py_path = py_file.as_posix()
    epic_file.write_text(
        f"# Epic Test\n\n- `[MODIFY]` `@[{rel_py_path}#L1-L3]`\nCritical bound: #L100-L200\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        f"# Plan 1\n\n"
        f"Target: `@[{rel_py_path}]`\n"
        f"<required_context_rules>\n"
        f"  <rule>00-antigravity-core.md</rule>\n"
        f"  <rule>01-python-backend.md</rule>\n"
        f"</required_context_rules>\n"
        f"<anti_targets>\n</anti_targets>\n"
        f"<dod_checklist>\n</dod_checklist>\n"
        f"<validation_gate>\n</validation_gate>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_planner_output.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script_path), "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAILED" in result.stdout
    assert "#L100-L200" in result.stdout


def test_audit_planner_output_fails_on_missing_ki(tmp_path: Path) -> None:
    """Test that audit_planner_output fails when a KI in Epic is not inherited by plans."""
    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "# Epic Test\n\n"
        "<required_knowledge_items>\n"
        "  <ki>knowledge/architecture/artifacts/ki_critical_arch.md</ki>\n"
        "</required_knowledge_items>\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan 1\n\n"
        "<required_context_rules>\n"
        "  <rule>00-antigravity-core.md</rule>\n"
        "  <rule>01-python-backend.md</rule>\n"
        "</required_context_rules>\n"
        "<anti_targets>\n</anti_targets>\n"
        "<dod_checklist>\n</dod_checklist>\n"
        "<validation_gate>\n</validation_gate>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_planner_output.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script_path), "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAILED" in result.stdout
    assert "ki_critical_arch.md" in result.stdout


def test_audit_epic_coverage_clean_state(tmp_path: Path) -> None:
    """Test that audit_epic_coverage passes when all specified target files exist and symbols are clean."""
    workspace = tmp_path / "workspace"
    backend_dir = workspace / "backend_v2"
    backend_dir.mkdir(parents=True)

    target_file = backend_dir / "existing_service.py"
    target_file.write_text("class ExistingService:\n    pass\n", encoding="utf-8")

    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "## Phase 1: Service Update\n\n"
        "- `[MODIFY]` `@[backend_v2/existing_service.py]`\n"
        "<demolish>\n"
        "  `old_deprecated_symbol_none`\n"
        "</demolish>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_epic_coverage.py").resolve()
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--epic",
            str(epic_file),
            "--phase",
            "1",
            "--workspace-root",
            str(workspace),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "AUDIT PASSED" in result.stdout


def test_audit_epic_coverage_detects_deprecated_symbol(tmp_path: Path) -> None:
    """Test that audit_epic_coverage detects un-eradicated deprecated symbols in Python AST."""
    workspace = tmp_path / "workspace"
    backend_dir = workspace / "backend_v2"
    backend_dir.mkdir(parents=True)

    target_file = backend_dir / "legacy_module.py"
    target_file.write_text(
        "def old_feature_symbol() -> None:\n    pass\n",
        encoding="utf-8",
    )

    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "## Phase 1: Demolition\n\n"
        "- `[MODIFY]` `@[backend_v2/legacy_module.py]`\n"
        "<demolish>\n"
        "  `old_feature_symbol`\n"
        "</demolish>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_epic_coverage.py").resolve()
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--epic",
            str(epic_file),
            "--phase",
            "1",
            "--workspace-root",
            str(workspace),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "NOT ERADICATED" in result.stdout
    assert "old_feature_symbol" in result.stdout


def test_audit_epic_coverage_missing_new_file(tmp_path: Path) -> None:
    """Test that audit_epic_coverage fails when a specified [NEW] target file does not exist on disk."""
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)

    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "## Phase 1: New Component\n\n- `[NEW]` `@[backend_v2/missing_new_component.py]`\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_epic_coverage.py").resolve()
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--epic",
            str(epic_file),
            "--phase",
            "1",
            "--workspace-root",
            str(workspace),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "missing_new_component.py" in result.stdout


def test_extract_deprecated_symbols_utility() -> None:
    """Test extract_deprecated_symbols SSOT helper for demolish blocks and inline phrases."""
    content = """
    <demolish>
      `old_symbol_one`
      - old_symbol_two
    </demolish>
    Please deprecate `old_symbol_three` and remove `old_symbol_four`.
    """
    symbols = extract_deprecated_symbols(content)
    assert "old_symbol_one" in symbols
    assert "old_symbol_two" in symbols
    assert "old_symbol_three" in symbols
    assert "old_symbol_four" in symbols
    assert "True" not in symbols


def test_audit_planner_demolish_propagation_success(tmp_path: Path) -> None:
    """Test that audit_planner_output passes when Epic demolish symbols are present in plan demolish blocks."""
    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "# Epic\n- `[MODIFY]` `@[backend_v2/module.py]`\n<demolish>\n  `old_deprecated_fn`\n</demolish>\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan\n"
        "- `[MODIFY]` `@[backend_v2/module.py]`\n"
        "<required_context_rules>\n"
        "  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        "  <rule>@[.agents/rules/01-python-backend.md]</rule>\n"
        "</required_context_rules>\n"
        "<demolish>\n"
        "  `old_deprecated_fn`\n"
        "</demolish>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_planner_output.py").resolve()
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--epic",
            str(epic_file),
            "--plan-dir",
            str(plan_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "All 1 demolish symbols from Epic are propagated into plans" in result.stdout


def test_audit_planner_demolish_propagation_failure(tmp_path: Path) -> None:
    """Test that audit_planner_output fails when Epic has demolish symbols but plan has none."""
    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "# Epic\n- `[MODIFY]` `@[backend_v2/module.py]`\n<demolish>\n  `old_deprecated_fn`\n</demolish>\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan\n"
        "- `[MODIFY]` `@[backend_v2/module.py]`\n"
        "<required_context_rules>\n"
        "  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        "  <rule>@[.agents/rules/01-python-backend.md]</rule>\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_planner_output.py").resolve()
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--epic",
            str(epic_file),
            "--plan-dir",
            str(plan_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "demolish" in result.stdout.lower()
    assert "FAILED" in result.stdout


def test_extract_phase_content_direct() -> None:
    """Test extract_phase_content helper function directly."""
    sample = "# Epic\n## Phase 1: Foundation\nPhase 1 content\n## Phase 2: Logic\nPhase 2 content\n"
    assert "Phase 1 content" in extract_phase_content(sample, 1)
    assert "Phase 2 content" in extract_phase_content(sample, 2)
    assert extract_phase_content(sample, None) == sample


def test_scan_for_lingering_symbols_direct(tmp_path: Path) -> None:
    """Test scan_for_lingering_symbols helper function directly."""
    assert scan_for_lingering_symbols(tmp_path, set()) == []

    backend = tmp_path / "backend_v2"
    backend.mkdir()
    py_file = backend / "test_module.py"
    py_file.write_text("def legacy_fn():\n    pass\n", encoding="utf-8")

    # Non-utf8 py file in backend
    bad_py = backend / "bad_encoding.py"
    bad_py.write_bytes(b"\xff\xfe\x00\x00def broken(): pass")

    client = tmp_path / "client_app_v2"
    client.mkdir()
    dart_file = client / "widget.dart"
    dart_file.write_text("class DartLegacyClass {\n  void legacy_fn() {}\n}\n", encoding="utf-8")

    bad_dart = client / "bad_dart.dart"
    bad_dart.write_bytes(b"\xff\xfe\x00\x00class Invalid {}")

    findings = scan_for_lingering_symbols(tmp_path, {"legacy_fn"})
    assert len(findings) == 2
    symbols_found = {f[0] for f in findings}
    assert symbols_found == {"legacy_fn"}


def test_dto_parity_casing_conversions() -> None:
    """Test snake_to_camel and camel_to_snake converters."""
    assert snake_to_camel("matrix_id") == "matrixId"
    assert snake_to_camel("tda_id") == "tdaId"
    assert snake_to_camel("single") == "single"

    assert camel_to_snake("matrixId") == "matrix_id"
    assert camel_to_snake("tdaId") == "tda_id"
    assert camel_to_snake("single") == "single"


def test_extract_pydantic_fields_direct(tmp_path: Path) -> None:
    """Test AST extraction of Pydantic model fields."""
    py_file = tmp_path / "models.py"
    py_file.write_text(
        "class TestDTO:\n"
        "    model_config = {}\n"
        "    _private_var: str\n"
        "    tda_id: str\n"
        "    status: str\n"
        "    score: float = 1.0\n",
        encoding="utf-8",
    )
    models = extract_pydantic_fields(py_file)
    assert "TestDTO" in models
    assert models["TestDTO"] == {"tda_id", "status", "score"}


def test_extract_freezed_fields_direct(tmp_path: Path) -> None:
    """Test extraction of Freezed model fields and @JsonKey mapping."""
    dart_file = tmp_path / "model.dart"
    dart_file.write_text(
        "@freezed\n"
        "abstract class TestDTO with _$TestDTO {\n"
        "  const factory TestDTO({\n"
        "    @JsonKey(name: 'tda_id') required String tdaId,\n"
        "    required String status,\n"
        "    @Default(1.0) double score,\n"
        "  }) = _TestDTO;\n"
        "}\n",
        encoding="utf-8",
    )
    models = extract_freezed_fields(dart_file)
    assert "TestDTO" in models
    assert models["TestDTO"] == {"tda_id", "status", "score"}


def test_audit_parity_scenarios(tmp_path: Path) -> None:
    """Test audit_parity on matching, extra field, and mismatched field scenarios."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    # 1. Matching DTO
    (backend_dir / "atom.py").write_text(
        "class AtomDTO:\n    tda_id: str\n    status: str\n",
        encoding="utf-8",
    )
    (frontend_dir / "atom.dart").write_text(
        "@freezed\n"
        "abstract class AtomDTO with _$AtomDTO {\n"
        "  const factory AtomDTO({\n"
        "    @JsonKey(name: 'tda_id') required String tdaId,\n"
        "    required String status,\n"
        "  }) = _AtomDTO;\n"
        "}\n",
        encoding="utf-8",
    )
    success, reports = audit_parity(backend_dir, frontend_dir)
    assert success is True
    assert reports == []

    # 2. Negative Scenario 1: Pydantic model has extra field missing in Freezed
    (backend_dir / "atom.py").write_text(
        "class AtomDTO:\n    tda_id: str\n    status: str\n    extra_field: str\n",
        encoding="utf-8",
    )
    success, reports = audit_parity(backend_dir, frontend_dir)
    assert success is False
    assert len(reports) == 1
    assert "Missing in Frontend" in reports[0]
    assert "extra_field" in reports[0]

    # 3. Negative Scenario 2: Freezed model has extra field missing in Backend
    (backend_dir / "atom.py").write_text(
        "class AtomDTO:\n    tda_id: str\n",
        encoding="utf-8",
    )
    success, reports = audit_parity(backend_dir, frontend_dir)
    assert success is False
    assert len(reports) == 1
    assert "Missing in Backend" in reports[0]
    assert "status" in reports[0]


def test_audit_dto_parity_edge_cases(tmp_path: Path) -> None:
    """Test non-utf8 and syntax error handling in audit_dto_parity extractors."""
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("def broken(:", encoding="utf-8")
    assert extract_pydantic_fields(bad_py) == {}

    bad_py_bytes = tmp_path / "bad_bytes.py"
    bad_py_bytes.write_bytes(b"\xff\xfe\x00\x00")
    assert extract_pydantic_fields(bad_py_bytes) == {}

    assert extract_pydantic_fields(tmp_path / "non_existent.py") == {}

    bad_dart = tmp_path / "bad.dart"
    bad_dart.write_bytes(b"\xff\xfe\x00\x00")
    assert extract_freezed_fields(bad_dart) == {}

    assert extract_freezed_fields(tmp_path / "non_existent.dart") == {}


def test_audit_dto_parity_cli_success(tmp_path: Path) -> None:
    """Test CLI execution for audit_dto_parity on success."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    (backend_dir / "atom.py").write_text("class AtomDTO:\n    tda_id: str\n", encoding="utf-8")
    (frontend_dir / "atom.dart").write_text(
        "@freezed\nabstract class AtomDTO with _$AtomDTO {\n  const factory AtomDTO({\n    @JsonKey(name: 'tda_id') required String tdaId,\n  }) = _AtomDTO;\n}\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_dto_parity.py").resolve()
    res = subprocess.run(
        [sys.executable, str(script_path), "--backend-dir", str(backend_dir), "--frontend-dir", str(frontend_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert res.returncode == 0
    assert "DTO Parity Audit Passed" in res.stdout


def test_audit_dto_parity_cli_failure(tmp_path: Path) -> None:
    """Test CLI execution for audit_dto_parity on mismatch failure."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    (backend_dir / "atom.py").write_text("class AtomDTO:\n    tda_id: str\n    extra: str\n", encoding="utf-8")
    (frontend_dir / "atom.dart").write_text(
        "@freezed\nabstract class AtomDTO with _$AtomDTO {\n  const factory AtomDTO({\n    @JsonKey(name: 'tda_id') required String tdaId,\n  }) = _AtomDTO;\n}\n",
        encoding="utf-8",
    )

    script_path = Path("scripts/audit_dto_parity.py").resolve()
    res = subprocess.run(
        [sys.executable, str(script_path), "--backend-dir", str(backend_dir), "--frontend-dir", str(frontend_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert res.returncode == 1
    assert "DTO Parity Mismatches Found" in res.stdout


def test_audit_dto_parity_main_direct(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test audit_dto_parity_main in-process invocation for complete coverage."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    (backend_dir / "atom.py").write_text("class AtomDTO:\n    tda_id: str\n", encoding="utf-8")
    (frontend_dir / "atom.dart").write_text(
        "@freezed\nabstract class AtomDTO with _$AtomDTO {\n  const factory AtomDTO({\n    @JsonKey(name: 'tda_id') required String tdaId,\n  }) = _AtomDTO;\n}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys, "argv", ["audit_dto_parity.py", "--backend-dir", str(backend_dir), "--frontend-dir", str(frontend_dir)]
    )
    try:
        audit_dto_parity_main()
    except SystemExit as e:
        assert e.code == 0

    # Failure case in-process
    (backend_dir / "atom.py").write_text("class AtomDTO:\n    tda_id: str\n    extra: str\n", encoding="utf-8")
    try:
        audit_dto_parity_main()
    except SystemExit as e:
        assert e.code == 1


def test_extract_code_symbols_from_rules_direct(tmp_path: Path) -> None:
    """Test extracting backtick-enclosed symbols from banned/mandatory pattern XML blocks."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    rule_file = rules_dir / "01-test-rule.md"
    rule_file.write_text(
        "# Rule Test\n"
        "<banned_pattern>Using `LegacyGodService` or `legacy_func`.</banned_pattern>\n"
        "<mandatory_pattern>Must use `ModernService` and `ConfigDict`.</mandatory_pattern>\n"
        "Outside block: `IgnoredOutsideSymbol`\n",
        encoding="utf-8",
    )

    extracted = extract_code_symbols_from_rules(rules_dir)
    assert "01-test-rule.md" in extracted
    symbols = extracted["01-test-rule.md"]
    assert "LegacyGodService" in symbols
    assert "legacy_func" in symbols
    assert "ModernService" in symbols
    assert "ConfigDict" not in symbols  # Excluded keyword
    assert "IgnoredOutsideSymbol" not in symbols  # Outside XML tags


def test_verify_symbols_exist_and_staleness_audit(tmp_path: Path) -> None:
    """Test checking existence of symbols across codebase search dirs."""
    code_dir = tmp_path / "src"
    code_dir.mkdir()
    (code_dir / "service.py").write_text("class ModernService:\n    pass\n", encoding="utf-8")

    symbols = {"ModernService", "GhostService"}
    orphans = verify_symbols_exist(symbols, [code_dir])
    assert "GhostService" in orphans
    assert "ModernService" not in orphans

    # Audit integration
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "rule.md").write_text(
        "<mandatory_pattern>`ModernService` and `GhostService`</mandatory_pattern>",
        encoding="utf-8",
    )

    file_orphans, total = audit_rules_staleness(rules_dir, [code_dir])
    assert total == 2
    assert "rule.md" in file_orphans
    assert file_orphans["rule.md"] == {"GhostService"}


def test_audit_rules_staleness_main_direct(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test audit_rules_staleness_main in-process invocation."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    code_dir = tmp_path / "src"
    code_dir.mkdir()

    (rules_dir / "rule.md").write_text("<mandatory_pattern>`ActiveService`</mandatory_pattern>", encoding="utf-8")
    (code_dir / "app.py").write_text("class ActiveService: pass", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["audit_rules_staleness.py", "--rules-dir", str(rules_dir), "--search-dirs", str(code_dir)],
    )
    try:
        audit_rules_staleness_main()
    except SystemExit as e:
        assert e.code == 0

    # With warning/orphans
    (rules_dir / "rule2.md").write_text(
        "<mandatory_pattern>`UnknownMissingService`</mandatory_pattern>", encoding="utf-8"
    )
    try:
        audit_rules_staleness_main()
    except SystemExit as e:
        assert e.code == 0


def test_audit_rules_staleness_edge_cases(tmp_path: Path) -> None:
    """Test non-existent dirs, empty sets, and bad encodings in audit_rules_staleness."""
    assert extract_code_symbols_from_rules(tmp_path / "non_existent_rules") == {}
    assert verify_symbols_exist(set(), [tmp_path]) == set()
    assert verify_symbols_exist({"Sym"}, [tmp_path / "non_existent_src"]) == {"Sym"}

    # Bad encoding rule file
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    bad_rule = rules_dir / "bad_rule.md"
    bad_rule.write_bytes(b"\xff\xfe\x00\x00<mandatory_pattern>`Sym`</mandatory_pattern>")
    assert extract_code_symbols_from_rules(rules_dir) == {}

    # Bad encoding source file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    bad_src = src_dir / "bad_src.py"
    bad_src.write_bytes(b"\xff\xfe\x00\x00class Sym: pass")
    assert verify_symbols_exist({"Sym"}, [src_dir]) == {"Sym"}


def test_audit_epic_coverage_main_direct(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test audit_epic_coverage main() CLI execution in-process for full coverage."""
    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "# Epic Test\n"
        "### Phase 1: Implementation\n"
        "- #### [NEW] `src/new_file.py`\n"
        "- #### [MODIFY] `src/mod_file.py`\n"
        "- #### [DELETE] `src/del_file.py`\n"
        "- Deprecate `OldSymbol`\n",
        encoding="utf-8",
    )

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "new_file.py").write_text("x = 1", encoding="utf-8")
    (src_dir / "mod_file.py").write_text("y = 2", encoding="utf-8")

    out_report = tmp_path / "report.md"

    # Non-existent epic
    monkeypatch.setattr(sys, "argv", ["audit_epic_coverage.py", "--epic", str(tmp_path / "missing.md")])
    try:
        audit_epic_coverage_main()
    except SystemExit as e:
        assert e.code == 1

    # Successful run with report output
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_epic_coverage.py",
            "--epic",
            str(epic_file),
            "--phase",
            "1",
            "--workspace-root",
            str(tmp_path),
            "--output-report",
            str(out_report),
        ],
    )
    try:
        audit_epic_coverage_main()
    except SystemExit as e:
        assert e.code == 0
    assert out_report.exists()

    # Failure on missing file
    (src_dir / "new_file.py").unlink()
    try:
        audit_epic_coverage_main()
    except SystemExit as e:
        assert e.code == 1

