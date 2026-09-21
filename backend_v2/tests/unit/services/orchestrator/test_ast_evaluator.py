import ast

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


def test_ast_evaluator_empty_expression_and_syntax_error() -> None:
    """Verify that ASTEvaluator handles empty strings and invalid syntax with fail-fast."""
    facts = {"fact_a": "Evidence"}
    assert ASTEvaluator.evaluate("", facts) == "FALSE"
    assert ASTEvaluator.evaluate("   ", facts) == "FALSE"

    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("fact_a and and fact_b", facts)
    assert "Invalid boolean expression syntax" in str(exc.value.message)


def test_ast_evaluator_unary_and_bool_op_security_violations() -> None:
    """Verify that ASTEvaluator rejects disallowed UnaryOp, Compare, and BoolOp operators."""
    facts = {"fact_a": "Evidence"}

    # Disallowed UnaryOp (positive / negative / invert)
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("+fact_a", facts)
    assert "Disallowed UnaryOp operator" in str(exc.value.message)

    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("~fact_a", facts)
    assert "Disallowed UnaryOp operator" in str(exc.value.message)

    # Disallowed Compare operator
    with pytest.raises(AppException) as exc:
        ASTEvaluator.evaluate("fact_a == 'Evidence'", facts)
    assert "Disallowed AST node type 'Compare'" in str(exc.value.message)

    # Disallowed BoolOp operator via synthetic AST node
    class UnsupportedBoolOp(ast.boolop):
        pass

    with pytest.raises(AppException) as exc:
        ASTEvaluator._eval_node(
            ast.BoolOp(op=UnsupportedBoolOp(), values=[ast.Name(id="fact_a", ctx=ast.Load())]),
            facts,
            total_chunks=1,
            dlq_chunks=0,
        )
    assert "Disallowed BoolOp operator" in str(exc.value.message)


def test_ast_evaluator_tolerance_edge_cases() -> None:
    """Verify calculate_inverse_dlq_tolerance with edge cases (total_chunks <= 0, unknown state)."""
    # Total chunks <= 0
    assert ASTEvaluator.calculate_inverse_dlq_tolerance(total_chunks=0, dlq_chunks=0, inner_val="DLQ") == "TRUE"
    assert ASTEvaluator.calculate_inverse_dlq_tolerance(total_chunks=-1, dlq_chunks=0, inner_val="DLQ") == "TRUE"

    # Unknown inner_val state
    assert ASTEvaluator.calculate_inverse_dlq_tolerance(total_chunks=10, dlq_chunks=0, inner_val="UNKNOWN") == "FALSE"
    assert ASTEvaluator.calculate_inverse_dlq_tolerance(total_chunks=10, dlq_chunks=0, inner_val=None) == "FALSE"
