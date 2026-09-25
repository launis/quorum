"""Unit tests for convert_epic_to_hybrid.py.

Verifies Epic parsing, XML execution block generation, and CLI entrypoint.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.convert_epic_to_hybrid import (
    convert_epic,
    main,
)


SAMPLE_EPIC = """# EPIC: Test Migration

## 1. Overview
Test overview.

## 3. Phased Execution Plan

### Phase 1: Core Framework
This is phase 1 description.

#### [NEW] [service.py](file:///c:/src/quorum/backend_v2/service.py)
Create the core service.

### Phase 2: Secondary Extension
This is phase 2 description.

#### [MODIFY] [handler.py](file:///c:/src/quorum/backend_v2/handler.py)
Update handler.
"""


def test_convert_epic_success(tmp_path: Path) -> None:
    """Test convert_epic parses phases and generates valid XML blocks."""
    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(SAMPLE_EPIC, encoding="utf-8")

    result = convert_epic(epic_file)
    assert result.phases_converted == 2
    assert "<execution_block" in result.converted_content
    assert "</execution_block>" in result.converted_content


def test_convert_epic_missing_section(tmp_path: Path) -> None:
    """Test convert_epic handles Epics without phased execution plan section."""
    epic_file = tmp_path / "EPIC_EMPTY.md"
    epic_file.write_text("# Empty Epic\nNo execution plan here.", encoding="utf-8")

    result = convert_epic(epic_file)
    assert result.phases_converted == 0
    assert result.converted_content == "# Empty Epic\nNo execution plan here."


def test_convert_epic_already_converted_skips(tmp_path: Path) -> None:
    """Test convert_epic skips phases that already contain execution_block."""
    epic_file = tmp_path / "EPIC_ALREADY.md"
    epic_file.write_text(SAMPLE_EPIC, encoding="utf-8")

    res1 = convert_epic(epic_file)
    epic_file.write_text(res1.converted_content, encoding="utf-8")

    # Second pass should convert 0 phases
    res2 = convert_epic(epic_file)
    assert res2.phases_converted == 0


def test_main_cli_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test main() CLI with --dry-run does not modify the target file."""
    epic_file = tmp_path / "EPIC_CLI.md"
    epic_file.write_text(SAMPLE_EPIC, encoding="utf-8")

    main([str(epic_file), "--dry-run"])
    captured = capsys.readouterr()
    assert "DRY RUN -- Output below" in captured.out
    # File content on disk remains original
    assert epic_file.read_text(encoding="utf-8") == SAMPLE_EPIC


def test_main_cli_write_back(tmp_path: Path) -> None:
    """Test main() CLI writes converted content back to disk."""
    epic_file = tmp_path / "EPIC_WRITE.md"
    epic_file.write_text(SAMPLE_EPIC, encoding="utf-8")

    main([str(epic_file)])
    assert "<execution_block" in epic_file.read_text(encoding="utf-8")


def test_main_cli_already_converted(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test main() CLI when no phases need conversion."""
    epic_file = tmp_path / "EPIC_ALREADY.md"
    epic_file.write_text(SAMPLE_EPIC, encoding="utf-8")
    main([str(epic_file)])  # First pass converts
    main([str(epic_file)])  # Second pass says "No changes made."
    captured = capsys.readouterr()
    assert "No changes made." in captured.out


def test_extract_code_snippets() -> None:
    """Test extracting fenced code snippets from markdown body."""
    from scripts.convert_epic_to_hybrid import _extract_code_snippets

    body = "Text before\n```python\nx = 1\n```\nMiddle\n```xml\n<tag/>\n```"
    snippets = _extract_code_snippets(body)
    assert len(snippets) == 2
    assert "x = 1" in snippets[0]
    assert "<tag/>" in snippets[1]


def test_generate_execution_block_no_targets() -> None:
    """Test generating execution block for a phase with no explicit file targets."""
    from scripts.convert_epic_to_hybrid import PhaseBlock, generate_execution_block

    block = PhaseBlock(
        phase_id="phase_0",
        heading="### Phase 0: Setup",
        heading_level=3,
        body="Initial environment configuration without file targets. " * 10,
        start_line=1,
        end_line=5,
        file_targets=[],
    )
    xml = generate_execution_block(block)
    assert '<execution_block phase="phase_0"' in xml
    assert "<step" in xml


def test_main_cli_errors(tmp_path: Path) -> None:
    """Test main() CLI exits with 1 on missing file or non-markdown file."""
    # Missing file
    with pytest.raises(SystemExit) as exc1:
        main([str(tmp_path / "missing.md")])
    assert exc1.value.code == 1

    # Non-markdown file
    txt_file = tmp_path / "file.txt"
    txt_file.write_text("hello", encoding="utf-8")
    with pytest.raises(SystemExit) as exc2:
        main([str(txt_file)])
    assert exc2.value.code == 1


