import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.ast_evaluator import ASTEvaluator


def test_ast_evaluator_basic_logic() -> None:
    """Verify that ASTEvaluator correctly processes standard boolean expressions."""
    facts = {
        "fact_a": "Evidence present",
        "fact_b": "",  # Empty string is treated as FALSE
        "fact_c": None,  # None is treated as FALSE
        "fact_d": "Other evidence",
    }

    # Basic variable lookup
    assert ASTEvaluator.evaluate("fact_a", facts) == "TRUE"
    assert ASTEvaluator.evaluate("fact_b", facts) == "FALSE"
    assert ASTEvaluator.evaluate("fact_c", facts) == "FALSE"
    assert ASTEvaluator.evaluate("fact_unknown", facts) == "FALSE"

    # AND operator
    assert ASTEvaluator.evaluate("fact_a and fact_d", facts) == "TRUE"
    assert ASTEvaluator.evaluate("fact_a and fact_b", facts) == "FALSE"

    # OR operator
    assert ASTEvaluator.evaluate("fact_a or fact_b", facts) == "TRUE"
    assert ASTEvaluator.evaluate("fact_b or fact_c", facts) == "FALSE"

    # NOT operator
    assert ASTEvaluator.evaluate("not fact_a", facts) == "FALSE"
    assert ASTEvaluator.evaluate("not fact_b", facts) == "TRUE"

    # Complex combination
    assert ASTEvaluator.evaluate("fact_a and not fact_b", facts) == "TRUE"
    assert ASTEvaluator.evaluate("fact_a or (fact_b and fact_c)", facts) == "TRUE"
    assert ASTEvaluator.evaluate("not (fact_a and fact_b)", facts) == "TRUE"


def test_ast_evaluator_three_state_logic() -> None:
    """Verify that ASTEvaluator handles DLQ state mathematically with short-circuiting."""
    facts = {
        "fact_a": "Evidence present",
        "fact_b": "",
        "fact_dlq": "DLQ",
    }

    # Basic DLQ evaluation
    assert ASTEvaluator.evaluate("fact_dlq", facts) == "DLQ"

    # FALSE and DLQ = FALSE (Short-circuit!)
    assert ASTEvaluator.evaluate("fact_b and fact_dlq", facts) == "FALSE"
    assert ASTEvaluator.evaluate("fact_dlq and fact_b", facts) == "FALSE"

    # TRUE and DLQ = DLQ
    assert ASTEvaluator.evaluate("fact_a and fact_dlq", facts) == "DLQ"
    assert ASTEvaluator.evaluate("fact_dlq and fact_a", facts) == "DLQ"

    # TRUE or DLQ = TRUE (Short-circuit!)
    assert ASTEvaluator.evaluate("fact_a or fact_dlq", facts) == "TRUE"
    assert ASTEvaluator.evaluate("fact_dlq or fact_a", facts) == "TRUE"

    # FALSE or DLQ = DLQ
    assert ASTEvaluator.evaluate("fact_b or fact_dlq", facts) == "DLQ"
    assert ASTEvaluator.evaluate("fact_dlq or fact_b", facts) == "DLQ"

    # Double DLQ operations
    assert ASTEvaluator.evaluate("fact_dlq and fact_dlq", facts) == "DLQ"
    assert ASTEvaluator.evaluate("fact_dlq or fact_dlq", facts) == "DLQ"


def test_ast_evaluator_dlq_tolerance() -> None:
    """Verify that DLQ tolerance is correctly applied to 'not DLQ' expressions."""
    facts = {
        "fact_dlq": "DLQ",
    }

    # Case 1: Missing chunks ratio is < 5% (e.g. 2/50 = 4% < 5%) -> Proved absence (TRUE)
    assert ASTEvaluator.evaluate("not fact_dlq", facts, total_chunks=50, dlq_chunks=2) == "TRUE"

    # Case 2: Missing chunks ratio is >= 5% (e.g. 3/50 = 6% >= 5%) -> DLQ
    assert ASTEvaluator.evaluate("not fact_dlq", facts, total_chunks=50, dlq_chunks=3) == "DLQ"

    # Case 3: Default parameters (ratio is 0.0 < 0.05) -> TRUE
    assert ASTEvaluator.evaluate("not fact_dlq", facts) == "TRUE"


def test_ast_evaluator_security_whitelist() -> None:
    """Verify that ASTEvaluator strictly blocks disallowed AST operations (no eval allowed)."""
    facts = {"fact_a": "Evidence present"}

    # Disallowed binary operator (BinOp)
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("fact_a + 'test'", facts)
    assert "AST Security Violation" in str(exc.value.message)

    # Disallowed function call (Call)
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("print(fact_a)", facts)
    assert "AST Security Violation" in str(exc.value.message)

    # Disallowed attribute access (Attribute)
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("fact_a.lower()", facts)
    assert "AST Security Violation" in str(exc.value.message)

    # Disallowed constant numbers (Constant)
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("1 and fact_a", facts)
    assert "AST Security Violation" in str(exc.value.message)

    # Disallowed malicious input
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("__import__('os').system('clear')", facts)
    assert "AST Security Violation" in str(exc.value.message)
