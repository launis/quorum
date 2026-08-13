"""Tests for audit_matrix_manager.py."""

import pytest
from pathlib import Path
from scripts.audit_matrix_manager import check_anti_laziness, extract_rule_blocks, get_repo_root

def test_check_anti_laziness_short():
    """Test that a short justification fails."""
    err = check_anti_laziness("Too short.")
    assert err is not None
    assert "Justification too short" in err

def test_check_anti_laziness_few_words():
    """Test that justification with few words fails."""
    err = check_anti_laziness("ThisIsAVeryLongWordThatIsLongerThanTwentyFiveCharacters.")
    assert err is not None
    assert "Justification lacks detail" in err

def test_check_anti_laziness_pass():
    """Test that a valid justification passes."""
    err = check_anti_laziness("This is a sufficiently long and detailed justification.")
    assert err is None

def test_extract_rule_blocks(tmp_path: Path):
    """Test extracting rule blocks from a markdown file."""
    md_file = tmp_path / "rules.md"
    md_file.write_text('''
<rule_block id="test_rule">
    <banned_pattern>banned</banned_pattern>
    <mandatory_pattern>mandatory</mandatory_pattern>
</rule_block>
    ''')
    
    rules = extract_rule_blocks(md_file)
    assert len(rules) == 1
    assert rules[0]["rule_id"] == "test_rule"
    assert rules[0]["banned_pattern"] == "banned"
    assert rules[0]["mandatory_pattern"] == "mandatory"

def test_get_repo_root():
    """Test getting repo root."""
    root = get_repo_root()
    assert root.name == "quorum" or root.name == "antigravity-ide"

def test_cmd_generate_invalid_type():
    """Test generating with invalid type."""
    import argparse
    from scripts.audit_matrix_manager import cmd_generate
    args = argparse.Namespace(type="invalid")
    with pytest.raises(SystemExit):
        cmd_generate(args)

