"""Unit tests for audit_rules_staleness.py.

Verifies extraction of backtick symbols from rules, codebase cross-referencing,
and CLI entrypoint behaviors.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_rules_staleness import (
    audit_rules_staleness,
    extract_code_symbols_from_rules,
    main,
    verify_symbols_exist,
)


def test_extract_code_symbols_from_rules(tmp_path: Path) -> None:
    """Test extracting backtick symbols from XML rule patterns."""
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


def test_verify_symbols_exist(tmp_path: Path) -> None:
    """Test checking existence of symbols across codebase search directories."""
    code_dir = tmp_path / "src"
    code_dir.mkdir()
    (code_dir / "service.py").write_text("class ModernService:\n    pass\n", encoding="utf-8")

    symbols = {"ModernService", "GhostService"}
    orphans = verify_symbols_exist(symbols, [code_dir])
    assert "GhostService" in orphans
    assert "ModernService" not in orphans


def test_audit_rules_staleness_integration(tmp_path: Path) -> None:
    """Test full audit_rules_staleness flow returning orphans and counts."""
    code_dir = tmp_path / "src"
    code_dir.mkdir()
    (code_dir / "service.py").write_text("class ModernService:\n    pass\n", encoding="utf-8")

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


def test_audit_rules_staleness_cli(tmp_path: Path) -> None:
    """Test main() CLI invocation with clean state and orphaned symbols."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    code_dir = tmp_path / "src"
    code_dir.mkdir()

    (rules_dir / "rule.md").write_text("<mandatory_pattern>`ActiveService`</mandatory_pattern>", encoding="utf-8")
    (code_dir / "app.py").write_text("class ActiveService: pass", encoding="utf-8")

    # Clean pass exits 0
    with pytest.raises(SystemExit) as exc_info:
        main(["--rules-dir", str(rules_dir), "--search-dirs", str(code_dir)])
    assert exc_info.value.code == 0

    # With warning/orphans also exits 0 (informational audit)
    (rules_dir / "rule2.md").write_text(
        "<mandatory_pattern>`UnknownMissingService`</mandatory_pattern>", encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc_info:
        main(["--rules-dir", str(rules_dir), "--search-dirs", str(code_dir)])
    assert exc_info.value.code == 0


def test_audit_rules_staleness_edge_cases(tmp_path: Path) -> None:
    """Test non-existent directories, empty sets, and bad encodings."""
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
