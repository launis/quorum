"""Unit tests for diff_executions.py differential inspection and SSOT registry.

Verifies InputFileInspectionDTO instantiation, dot-notation field access,
noise detection, missing file handling, and cross-script SSOT registry reuse.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from scripts.diff_executions import (
    UNICODE_SPACE_REGISTRY,
    InputFileInspectionDTO,
    _inspect_input_file,
)
from scripts.run_e2e_variance_test import (
    UNICODE_SPACE_REGISTRY as IMPORTED_UNICODE_SPACE_REGISTRY,
)


class TestInspectInputFile:
    """Test suite for _inspect_input_file and InputFileInspectionDTO."""

    def test_inspect_input_file_ascii_text(self) -> None:
        """Verify inspecting plain ASCII text returns typed InputFileInspectionDTO."""
        content = "Hello world. This is a clean ASCII document.\n\nSecond paragraph with text."
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_ascii.md"
            file_path.write_text(content, encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert info.noise == "Standard ASCII"
            assert info.word_count == 12
            assert info.paragraph_count == 2
            assert info.sentence_count >= 2
            assert len(info.sha256) == 64
            assert info.normalized_text.startswith("Helloworld.")

    def test_inspect_input_file_with_unicode_noise(self) -> None:
        """Verify inspecting file with Unicode non-breaking space detects noise correctly."""
        content = "Hello\u00a0world with a non-breaking space."
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_noise.md"
            file_path.write_text(content, encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert "U+00A0" in info.noise
            assert "No-Break Space" in info.noise

    def test_inspect_input_file_multiple_unicode_spaces(self) -> None:
        """Verify multiple distinct Unicode space characters are all reported."""
        content = "Word\u00a0One\u2002Two\u2003Three"
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_multi_noise.md"
            file_path.write_text(content, encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert "U+00A0" in info.noise
            assert "U+2002" in info.noise
            assert "U+2003" in info.noise

    def test_inspect_input_file_missing_file(self) -> None:
        """Negative: Inspecting non-existent file returns default DTO with Missing noise."""
        missing_path = Path("non_existent_directory_12345") / "missing.md"
        info = _inspect_input_file(missing_path)

        assert isinstance(info, InputFileInspectionDTO)
        assert info.noise == "Missing"
        assert info.sha256 == "MISSING"
        assert info.char_count == 0
        assert info.word_count == 0

    def test_inspect_input_file_empty_file(self) -> None:
        """Negative: Inspecting 0-byte file returns DTO with Empty noise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.md"
            file_path.write_text("", encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert info.noise == "Empty"
            assert info.char_count == 0
            assert info.word_count == 0


class TestUnicodeSpaceRegistrySSOT:
    """Test suite for UNICODE_SPACE_REGISTRY SSOT governance."""

    def test_unicode_space_registry_identical_reference(self) -> None:
        """Verify run_e2e_variance_test re-exports exact registry instance from diff_executions."""
        assert IMPORTED_UNICODE_SPACE_REGISTRY is UNICODE_SPACE_REGISTRY

    def test_unicode_space_registry_contains_required_markers(self) -> None:
        """Verify registry contains canonical typographical spaces."""
        assert "\u00a0" in UNICODE_SPACE_REGISTRY
        assert "\u2002" in UNICODE_SPACE_REGISTRY
        assert "\u2003" in UNICODE_SPACE_REGISTRY
        assert "\u2009" in UNICODE_SPACE_REGISTRY
