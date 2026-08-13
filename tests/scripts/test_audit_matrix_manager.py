"""Tests for audit_matrix_manager.py."""

import pytest
from scripts.audit_matrix_manager import check_anti_laziness

def test_check_anti_laziness_short():
    """Test that a short justification fails."""
    err = check_anti_laziness("Too short.")
    assert err is not None
    assert "Justification too short" in err

def test_check_anti_laziness_pass():
    """Test that a valid justification passes."""
    err = check_anti_laziness("This is a sufficiently long and detailed justification.")
    assert err is None
