import ast
import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)

State = Literal["TRUE", "FALSE", "DLQ"]


class ASTEvaluator:
    """Secure whitelisted AST evaluator for boolean logical expressions with 3-state logic."""

    @staticmethod
    def calculate_inverse_dlq_tolerance(total_chunks: int, dlq_chunks: int, inner_val: State) -> State:
        """Apply DLQ Tolerance instead of blind 'not DLQ = DLQ'.

        If the inner value was TRUE, 'not TRUE' is always FALSE.
        If the inner value was FALSE, 'not FALSE' is always TRUE.
        If the inner value was DLQ, and missing chunks are < 5%, treat as proved absence (TRUE), else DLQ.
        """
        if inner_val == "TRUE":
            return "FALSE"
        elif inner_val == "FALSE":
            return "TRUE"
        elif inner_val == "DLQ":
            ratio = dlq_chunks / total_chunks if total_chunks > 0 else 0.0
            if ratio < 0.05:
                return "TRUE"
            return "DLQ"
        return "FALSE"

    @staticmethod
    def evaluate(
        expression: str,
        facts: dict[str, Any],
        total_chunks: int = 1,
        dlq_chunks: int = 0,
    ) -> State:
        """Evaluate a boolean expression against a dictionary of facts.

        Supports whitelisted security and 3-state logical operators (and, or, not).
        """
        if not expression or not expression.strip():
            return "FALSE"

        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as e:
            logger.error(
                "ASTEvaluator: Syntax error parsing expression '%s': %s",
                expression,
                e,
            )
            raise ValueError(f"Invalid boolean expression: {expression}") from e

        return ASTEvaluator._eval_node(tree.body, facts, total_chunks, dlq_chunks)

    @staticmethod
    def _eval_node(node: ast.AST, facts: dict[str, Any], total_chunks: int, dlq_chunks: int) -> State:
        # Strict whitelisting check
        allowed_types = (
            ast.Expression,
            ast.BoolOp,
            ast.UnaryOp,
            ast.And,
            ast.Or,
            ast.Not,
            ast.Name,
        )
        if not isinstance(node, allowed_types):
            msg = f"AST Security Violation: Disallowed AST node type '{type(node).__name__}'"
            logger.error(msg)
            raise ValueError(msg)

        if isinstance(node, ast.Name):
            var_name = node.id
            val = facts.get(var_name)
            if val == "DLQ":
                return "DLQ"
            elif val is None or val == "" or val is False:
                return "FALSE"
            else:
                return "TRUE"

        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, ast.Not):
                msg = f"AST Security Violation: Disallowed UnaryOp operator '{type(node.op).__name__}'"
                logger.error(msg)
                raise ValueError(msg)

            operand_val = ASTEvaluator._eval_node(node.operand, facts, total_chunks, dlq_chunks)
            return ASTEvaluator.calculate_inverse_dlq_tolerance(total_chunks, dlq_chunks, operand_val)

        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                # and logic:
                # - If any is FALSE, result is FALSE (short-circuit)
                # - If all are TRUE, result is TRUE
                # - Otherwise DLQ
                has_dlq = False
                for value in node.values:
                    res = ASTEvaluator._eval_node(value, facts, total_chunks, dlq_chunks)
                    if res == "FALSE":
                        return "FALSE"
                    elif res == "DLQ":
                        has_dlq = True
                return "DLQ" if has_dlq else "TRUE"

            elif isinstance(node.op, ast.Or):
                # or logic:
                # - If any is TRUE, result is TRUE (short-circuit)
                # - If all are FALSE, result is FALSE
                # - Otherwise DLQ
                has_dlq = False
                for value in node.values:
                    res = ASTEvaluator._eval_node(value, facts, total_chunks, dlq_chunks)
                    if res == "TRUE":
                        return "TRUE"
                    elif res == "DLQ":
                        has_dlq = True
                return "DLQ" if has_dlq else "FALSE"

            else:
                msg = f"AST Security Violation: Disallowed BoolOp operator '{type(node.op).__name__}'"
                logger.error(msg)
                raise ValueError(msg)

        else:
            msg = f"AST Security Violation: Disallowed node '{type(node).__name__}'"
            logger.error(msg)
            raise ValueError(msg)
