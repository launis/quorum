"""Unit tests for scripts/audit_dict_eradication.py."""

from __future__ import annotations

from pathlib import Path

from scripts.audit_dict_eradication import (
    audit_dict_eradication,
    main,
)


def test_audit_dict_eradication_fails_on_syntax_error(tmp_path: Path) -> None:
    """Test contract: Malformed Python file causing AST parse failure must fail the audit."""
    bad_file = tmp_path / "syntax_error.py"
    bad_file.write_text("def broken_syntax(:\n    pass\n", encoding="utf-8")

    report = audit_dict_eradication(bad_file)
    assert report.syntax_parse_errors > 0
    assert report.total_violations > 0
    assert any(v.metric == "syntax_parse_error" for v in report.violations)

    exit_code = main([str(bad_file)])
    assert exit_code == 1


def test_audit_dict_eradication_passes_clean_file(tmp_path: Path) -> None:
    """Verifies that a clean, strictly typed file reports 0 violations and exit code 0."""
    clean_file = tmp_path / "clean_module.py"
    clean_file.write_text(
        "from pydantic import BaseModel\n\nclass CleanModel(BaseModel):\n    name: str\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(clean_file)
    assert report.total_violations == 0
    assert report.syntax_parse_errors == 0

    exit_code = main([str(clean_file)])
    assert exit_code == 0


def test_audit_dict_eradication_detects_naked_dict(tmp_path: Path) -> None:
    """Verifies detection of naked dict[str, Any] in variable and function annotations."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "my_service.py"
    target_file.write_text(
        "import typing\nfrom typing import Any, Dict\n\n"
        "x: Dict[str, typing.Any] = {}\n"
        "def process(data: dict[str, Any]) -> dict[str, Any]:\n"
        "    return data\n"
        "async def async_proc(item: dict[str, object]) -> dict[str, Any]:\n"
        "    return item\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.naked_dict_annotations == 5
    assert report.total_violations >= 5


def test_audit_dict_eradication_detects_service_duck_typing(tmp_path: Path) -> None:
    """Verifies detection of isinstance(..., dict) and tuple in service layers."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "worker_service.py"
    target_file.write_text(
        "def check(data: object) -> bool:\n"
        "    a = isinstance(data, dict)\n"
        "    b = isinstance(data, (dict, list))\n"
        "    return a and b\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.service_duck_typing == 2
    assert report.total_violations >= 2


def test_audit_dict_eradication_detects_dynamic_reflection(tmp_path: Path) -> None:
    """Verifies detection of getattr/hasattr/setattr/vars in domain and service layers."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "reflection_service.py"
    target_file.write_text(
        "def inspect_obj(obj: object) -> None:\n"
        "    getattr(obj, 'key')\n"
        "    hasattr(obj, 'key')\n"
        "    setattr(obj, 'key', 1)\n"
        "    vars(obj)\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.reflection_calls == 4
    assert report.total_violations >= 4


def test_audit_dict_eradication_detects_banned_get_lookup(tmp_path: Path) -> None:
    """Verifies detection of .get() lookups on internal variables."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "lookup_service.py"
    target_file.write_text(
        "def get_val(state_dict: object) -> None:\n"
        "    state_dict.get('field')\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.banned_get_calls == 1
    assert report.total_violations >= 1


def test_audit_dict_eradication_exempts_boundary_drivers_and_legit_get(tmp_path: Path) -> None:
    """Verifies that locked physical boundary files and legitimate get calls are exempt."""
    exempt_file = tmp_path / "tinydb_driver.py"
    exempt_file.write_text(
        "def serialize(data: object) -> None:\n    hasattr(data, 'model_dump')\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(exempt_file)
    assert report.reflection_calls == 0
    assert report.total_violations == 0

    # Test legitimate get calls
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    legit_file = service_dir / "legit_calls.py"
    legit_file.write_text(
        "import os\n"
        "def run(ctx_var: object, client: object, headers: object) -> None:\n"
        "    os.environ.get('KEY')\n"
        "    headers.get('auth')\n"
        "    client.get('http://test', headers={})\n"
        "    ctx_var.get()\n",
        encoding="utf-8",
    )
    report_legit = audit_dict_eradication(legit_file)
    assert report_legit.banned_get_calls == 0


def test_audit_dict_eradication_detects_dict_utils_imports(tmp_path: Path) -> None:
    """Verifies detection of legacy dict_utils imports."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "legacy_importer.py"
    target_file.write_text(
        "import dict_utils\nfrom legacy import dict_utils\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.dict_utils_references == 2
    assert report.total_violations >= 2


def test_audit_dict_eradication_detects_unauthorized_suppressions(tmp_path: Path) -> None:
    """Verifies detection of missing and placeholder # noqa: QGR reasons."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "suppression_file.py"
    target_file.write_text(
        "x = 1  # noqa: QGR001\n"
        "y = 2  # noqa: QGR002 [REASON: todo]\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.unauthorized_suppressions == 2
    assert report.total_violations >= 2


def test_audit_dict_eradication_targets_handling(tmp_path: Path) -> None:
    """Verifies directory scanning, sequence of targets, and non-existent targets."""
    # 1. Non-existent path
    empty_report = audit_dict_eradication(tmp_path / "does_not_exist")
    assert empty_report.total_violations == 0

    # 2. Directory with multiple files
    f1 = tmp_path / "f1.py"
    f2 = tmp_path / "f2.py"
    f1.write_text("a = 1\n", encoding="utf-8")
    f2.write_text("b = 2\n", encoding="utf-8")

    dir_report = audit_dict_eradication(tmp_path)
    assert dir_report.total_violations == 0

    # 3. Sequence of paths
    seq_report = audit_dict_eradication([f1, f2])
    assert seq_report.total_violations == 0


def test_audit_dict_eradication_main_many_violations(tmp_path: Path) -> None:
    """Verifies main() prints truncated violation list when > 5 violations exist in a file."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "many_violations.py"
    content = "\n".join(f"x_{i}: dict[str, object] = {{}}" for i in range(8))
    target_file.write_text(content, encoding="utf-8")

    exit_code = main([str(target_file)])
    assert exit_code == 1
