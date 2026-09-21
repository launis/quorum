"""Module for AST logical evaluation engine in 3-state boolean networks.

Provides standard and inverse evaluation rules handling DLQ state and tolerance parameters.
"""

from __future__ import annotations

import ast
import logging
from collections.abc import Mapping
from typing import Literal

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = ["ASTEvaluator", "State"]

# PEP 695 type alias for evaluation statuses
type State = Literal["TRUE", "FALSE", "DLQ"]


class ASTEvaluator:
    """Secure whitelisted AST evaluator for boolean logical expressions with 3-state logic.

    Adheres to PEP 257 docstring conventions and strictly uses fail-fast validation.
    """

    @staticmethod
    def calculate_inverse_dlq_tolerance(total_chunks: int, dlq_chunks: int, inner_val: State | str | None) -> State:
        """Apply DLQ Tolerance instead of blind 'not DLQ = DLQ'.

        Args:
            total_chunks: Number of chunks processed.
            dlq_chunks: Number of chunks landing in DLQ.
            inner_val: Inner boolean/DLQ string value evaluated.

        Returns:
            Computed state boolean representation including tolerance.
        """
        match inner_val:
            case "TRUE":
                return "FALSE"
            case "FALSE":
                return "TRUE"
            case "DLQ":
                if total_chunks <= 0:
                    return "TRUE"
                ratio = dlq_chunks / total_chunks
                if ratio < 0.05:
                    return "TRUE"
                return "DLQ"
            case _:
                return "FALSE"

    @staticmethod
    def evaluate(
        expression: str,
        facts: Mapping[str, bool | str | State | None],
        total_chunks: int = 1,
        dlq_chunks: int = 0,
    ) -> State:
        """Evaluate a boolean expression against a dictionary of facts.

        Supports whitelisted security and 3-state logical operators (and, or, not).

        Args:
            expression: Raw logical boolean expression string.
            facts: Lookup table mapping variable keys to their derived states.
            total_chunks: Total number of chunks available.
            dlq_chunks: Total number of dead-letter-queue chunks.

        Returns:
            Computed state (TRUE, FALSE, or DLQ).

        Raises:
            AppException: Triggered with VALIDATION_FAILED error code if AST syntax is invalid.
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
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"Invalid boolean expression syntax: {expression}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        return ASTEvaluator._eval_node(tree.body, facts, total_chunks, dlq_chunks)

    @staticmethod
    def _eval_node(
        node: ast.AST, facts: Mapping[str, bool | str | State | None], total_chunks: int, dlq_chunks: int
    ) -> State:
        """Internal AST evaluation step with strict whitelisting.

        Args:
            node: AST node to parse.
            facts: Lookup database mapping state outputs.
            total_chunks: Number of segments for tolerance.
            dlq_chunks: Number of DLQ segments.

        Returns:
            State computed from current branch.

        Raises:
            AppException: Raised with VALIDATION_FAILED error code if non-whitelisted node structure or operator is supplied.
        """
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
            logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        match node:
            case ast.Name(id=var_name):
                if var_name in facts:
                    val = facts[var_name]
                    if val == "DLQ":
                        return "DLQ"
                    elif val is None or val == "" or val is False:
                        return "FALSE"
                    else:
                        return "TRUE"
                return "FALSE"

            case ast.UnaryOp(op=ast.Not(), operand=operand):
                operand_val = ASTEvaluator._eval_node(operand, facts, total_chunks, dlq_chunks)
                return ASTEvaluator.calculate_inverse_dlq_tolerance(total_chunks, dlq_chunks, operand_val)

            case ast.UnaryOp(op=non_not_op):
                msg = f"AST Security Violation: Disallowed UnaryOp operator '{type(non_not_op).__name__}'"
                logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            case ast.BoolOp(op=ast.And(), values=values):
                has_dlq = False
                for value in values:
                    res = ASTEvaluator._eval_node(value, facts, total_chunks, dlq_chunks)
                    if res == "FALSE":
                        return "FALSE"
                    elif res == "DLQ":
                        has_dlq = True
                if has_dlq:
                    return "DLQ"
                return "TRUE"

            case ast.BoolOp(op=ast.Or(), values=values):
                has_dlq = False
                for value in values:
                    res = ASTEvaluator._eval_node(value, facts, total_chunks, dlq_chunks)
                    if res == "TRUE":
                        return "TRUE"
                    elif res == "DLQ":
                        has_dlq = True
                if has_dlq:
                    return "DLQ"
                return "FALSE"

            case ast.BoolOp(op=disallowed_op):
                msg = f"AST Security Violation: Disallowed BoolOp operator '{type(disallowed_op).__name__}'"
                logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            case _:
                msg = f"AST Security Violation: Disallowed node '{type(node).__name__}'"
                logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
