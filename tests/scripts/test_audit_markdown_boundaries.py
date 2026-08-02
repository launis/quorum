from pathlib import Path
from scripts.audit_markdown_boundaries import MarkdownAuditor

def test_markdown_auditor_ambiguity(tmp_path: Path) -> None:
    # Test that the auditor correctly identifies ambiguous language
    md_file = tmp_path / "test.md"
    md_file.write_text("This is an ambiguous line, e.g. something.", encoding="utf-8")
    
    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_ambiguity()
    
    assert len(auditor.errors) == 1
    assert "Ambiguous language detected" in auditor.errors[0]

def test_markdown_auditor_xml_truncation(tmp_path: Path) -> None:
    # Test unclosed tags
    md_file = tmp_path / "test.md"
    md_file.write_text("<execution_protocol>\n<step>", encoding="utf-8")
    
    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_xml_truncation()
    
    assert len(auditor.errors) == 2
    assert "Unclosed tag <step>" in auditor.errors[0] or "Unclosed tag <execution_protocol>" in auditor.errors[0]

def test_markdown_auditor_xml_valid(tmp_path: Path) -> None:
    # Test valid tags
    md_file = tmp_path / "test.md"
    md_file.write_text("<execution_protocol>\n<step>\n</step>\n</execution_protocol>", encoding="utf-8")
    
    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_xml_truncation()
    
    assert len(auditor.errors) == 0

def test_markdown_auditor_missing_file_reference(tmp_path: Path) -> None:
    # Test missing file
    md_file = tmp_path / "test.md"
    md_file.write_text("See @[nonexistent.py#L1-L2]", encoding="utf-8")
    
    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()
    
    assert len(auditor.errors) == 1
    assert "Referenced file does not exist" in auditor.errors[0]

def test_markdown_auditor_new_file_reference(tmp_path: Path) -> None:
    # Test missing file but marked as NEW
    md_file = tmp_path / "test.md"
    md_file.write_text("#### [NEW] @[new_file.py]", encoding="utf-8")
    
    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()
    
    assert len(auditor.errors) == 0
