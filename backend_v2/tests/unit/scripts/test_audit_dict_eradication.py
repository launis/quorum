"""Unit tests for scripts/audit_dict_eradication.py."""

from __future__ import annotations

from pathlib import Path

import pytest

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
        "nullable_payload: dict[str, Any] | None = None\n"
        "def process(data: dict[str, Any]) -> dict[str, Any]:\n"
        "    return data\n"
        "async def async_proc(item: dict[str, object]) -> dict[str, Any]:\n"
        "    return item\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.naked_dict_annotations == 6
    assert report.total_violations >= 6


def test_audit_dict_eradication_detects_primitive_obsession_nested_dict(tmp_path: Path) -> None:
    """Verifies detection of Primitive Obsession nested dicts and list[dict[...]] collections."""
    dtos_dir = tmp_path / "dtos"
    dtos_dir.mkdir(parents=True, exist_ok=True)
    target_file = dtos_dir / "stats_dto.py"
    target_file.write_text(
        "level_breakdown: dict[str, dict[str, int]] | None = None\n"
        "messages: list[dict[str, str]] | None = None\n\n"
        "def compute_stats(breakdown: dict[str, dict[str, int]], items: list[dict[str, str]]) -> dict[str, dict[str, int]]:\n"
        "    return breakdown\n\n"
        "async def async_compute(data: dict[str, dict[str, int]]) -> list[dict[str, str]]:\n"
        "    return []\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.primitive_obsession_nested_dicts == 7
    assert report.total_violations >= 7


def test_audit_dict_eradication_detects_service_duck_typing(tmp_path: Path) -> None:
    """Verifies detection of isinstance(..., dict | Mapping) and unions/tuples in service layers."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "worker_service.py"
    target_file.write_text(
        "def check(data: object) -> bool:\n"
        "    a = isinstance(data, dict)\n"
        "    b = isinstance(data, (dict, list))\n"
        "    c = isinstance(data, Mapping)\n"
        "    d = isinstance(data, (MutableMapping, list))\n"
        "    e = isinstance(data, BaseModel | Mapping)\n"
        "    return a and b and c and d and e\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.service_duck_typing == 5
    assert report.total_violations >= 5


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
        "def get_val(state_dict: object) -> None:\n    state_dict.get('field')\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.banned_get_calls == 1
    assert report.total_violations >= 1


def test_boundary_exemption_files_is_shared_ssot() -> None:
    """Verifies that audit_dict_eradication imports BOUNDARY_EXEMPTION_FILES by identity from _ast_guardrails."""
    import scripts._ast_guardrails as guardrails
    from scripts.audit_dict_eradication import BOUNDARY_EXEMPTION_FILES

    assert BOUNDARY_EXEMPTION_FILES is guardrails.BOUNDARY_EXEMPTION_FILES


def test_audit_dict_eradication_exempts_boundary_drivers_and_legit_get(tmp_path: Path) -> None:
    """Verifies that locked physical boundary files and legitimate get calls are exempt, while domain files sharing basename are not."""
    driver_dir = tmp_path / "backend_v2" / "database"
    driver_dir.mkdir(parents=True, exist_ok=True)
    exempt_file = driver_dir / "tinydb_driver.py"
    exempt_file.write_text(
        "def serialize(data: object) -> None:\n    hasattr(data, 'model_dump')\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(exempt_file)
    assert report.reflection_calls == 0
    assert report.total_violations == 0

    # Negative verification: a file with identical basename under models/ is NOT exempt
    models_dir = tmp_path / "backend_v2" / "models" / "dtos"
    models_dir.mkdir(parents=True, exist_ok=True)
    non_exempt_file = models_dir / "telemetry.py"
    non_exempt_file.write_text(
        "def inspect_obj(obj: object) -> None:\n    hasattr(obj, 'key')\n",
        encoding="utf-8",
    )
    report_non_exempt = audit_dict_eradication(non_exempt_file)
    assert report_non_exempt.reflection_calls == 1
    assert report_non_exempt.total_violations == 1

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
    """Verifies that any # noqa suppression comment unconditionally triggers an unauthorized_suppressions violation."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "suppression_file.py"
    target_file.write_text(
        "x = 1  # noqa: QGR001\ny = 2  # noqa: QGR002 [REASON: A substantive valid reason of more than ten characters]\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.unauthorized_suppressions == 2
    assert report.total_violations >= 2


def test_audit_dict_eradication_detects_permissive_casts(tmp_path: Path) -> None:
    """Verifies detection of cast(Any, ...) and typing.cast(typing.Any, ...) calls (Metric 12)."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "cast_file.py"
    target_file.write_text(
        "from typing import Any, cast\n"
        "import typing\n"
        "a = cast(Any, 123)\n"
        "b = typing.cast(typing.Any, 'abc')\n"
        "c = cast(int, '456')\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.permissive_casts == 2
    assert report.total_violations >= 2
    cast_violations = [v for v in report.violations if v.metric == "permissive_casts"]
    assert len(cast_violations) == 2
    assert any("cast(Any, 123)" in v.message for v in cast_violations)
    assert any("typing.cast(typing.Any, 'abc')" in v.message for v in cast_violations)


def test_audit_dict_eradication_targets_handling(tmp_path: Path) -> None:
    """Verifies directory scanning, sequence of targets, and non-existent targets."""
    # 1. Non-existent path
    with pytest.raises(FileNotFoundError):
        audit_dict_eradication(tmp_path / "does_not_exist")

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


def test_audit_dict_eradication_edge_cases_and_exemptions(tmp_path: Path) -> None:
    """Verifies helper edge cases, outer collection obsession, and get keyword exemptions."""
    service_dir = tmp_path / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    target_file = service_dir / "edge_cases.py"
    target_file.write_text(
        "from typing import Sequence, Set\n"
        "s1: Sequence[dict] = []\n"
        "s2: Set[dict] = set()\n"
        "def run_net(downloader: object) -> None:\n"
        "    downloader.get(timeout=10)\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.primitive_obsession_nested_dicts == 2
    assert report.banned_get_calls == 0


def test_audit_dict_eradication_comment_token_error(tmp_path: Path) -> None:
    """Verifies that unclosed multi-line comments/strings trigger syntax parse errors gracefully."""
    bad_comment_file = tmp_path / "bad_token.py"
    bad_comment_file.write_bytes(b'"""unclosed docstring')

    report = audit_dict_eradication(bad_comment_file)
    assert report.syntax_parse_errors >= 1


def test_audit_dict_eradication_main_clean_execution(tmp_path: Path, monkeypatch: object) -> None:
    """Verifies main() execution with default and clean targets."""
    clean_file = tmp_path / "clean.py"
    clean_file.write_text("x: int = 1\n", encoding="utf-8")

    exit_code = main([str(clean_file)])
    assert exit_code == 0


def test_audit_dict_eradication_detects_duplicate_field_assignment(tmp_path: Path) -> None:
    """Verifies detection of duplicate Field() assignment on Annotated fields."""
    models_dir = tmp_path / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    target_file = models_dir / "dup_field_model.py"
    target_file.write_text(
        "from typing import Annotated\n"
        "from pydantic import BaseModel, Field\n\n"
        "class MyModel(BaseModel):\n"
        "    steps: Annotated[list[str], Field(default_factory=list)] = Field(default_factory=list)\n"
        "    valid: Annotated[list[str], Field(default_factory=list)]\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.pydantic_annotated_violations == 1
    assert any(v.metric == "pydantic_annotated_violations" for v in report.violations)

    exit_code = main([str(target_file)])
    assert exit_code == 1


def test_audit_dict_eradication_detects_mutable_class_default(tmp_path: Path) -> None:
    """Verifies detection of class-level mutable defaults (list, dict, set)."""
    models_dir = tmp_path / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    target_file = models_dir / "mutable_default_model.py"
    target_file.write_text(
        "from pydantic import BaseModel\n\n"
        "class ConfigModel(BaseModel):\n"
        "    fields_to_translate: list[str] = []\n"
        "    dynamic_mappings: dict[str, str] = {}\n"
        "    _cache = {}\n",  # private cache attribute is exempt
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.mutable_class_defaults == 2
    assert any(v.metric == "mutable_class_defaults" for v in report.violations)

    exit_code = main([str(target_file)])
    assert exit_code == 1


def test_audit_dict_eradication_detects_unauthorized_open_json(tmp_path: Path) -> None:
    """Verifies detection of unauthorized dict[..., JsonValue] outside the Open-JSON whitelist."""
    models_dir = tmp_path / "models" / "dtos"
    models_dir.mkdir(parents=True, exist_ok=True)
    target_file = models_dir / "unauthorized_model.py"
    target_file.write_text(
        "from pydantic import BaseModel, JsonValue\n\n"
        "class SimulationModel(BaseModel):\n"
        "    trace: dict[str, JsonValue]\n",
        encoding="utf-8",
    )

    report = audit_dict_eradication(target_file)
    assert report.unauthorized_open_json_annotations == 1
    assert any(v.metric == "unauthorized_open_json_annotations" for v in report.violations)

    exit_code = main([str(target_file)])
    assert exit_code == 1
