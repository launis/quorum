"""Synchronous reduction of three-state logic (Passed, Failed, DLQ)."""

from typing import Literal

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import TDAAssertion

State = Literal["PASSED", "FAILED", "DLQ"]


class MatrixReducer:
    """Evaluates the final state of an assertion based on its evaluated chunks/atoms.

    Implements Three-State Logic (Passed, Failed, DLQ).
    """

    @staticmethod
    def reduce_exists(states: list[State]) -> State:
        """ANY(Passed) -> Passed. ALL(Failed) -> Failed. Else DLQ."""
        if not states:
            return "DLQ"
        if "PASSED" in states:
            return "PASSED"
        if all(s == "FAILED" for s in states):
            return "FAILED"
        return "DLQ"

    @staticmethod
    def reduce_all_must_comply(states: list[State]) -> State:
        """1. ANY(Failed) -> Failed. 2. ANY(DLQ) -> DLQ. 3. ALL(Passed) -> Passed."""
        if not states:
            return "DLQ"
        if "FAILED" in states:
            return "FAILED"
        if "DLQ" in states:
            return "DLQ"
        return "PASSED"

    @classmethod
    def reduce(cls, assertion: TDAAssertion, states: list[State]) -> State:
        """Reduces states according to the assertion's aggregation_mode."""
        if assertion.aggregation_mode == "EXISTS":
            return cls.reduce_exists(states)
        elif assertion.aggregation_mode == "ALL_MUST_COMPLY":
            return cls.reduce_all_must_comply(states)

        raise AppException(
            message=f"Unknown aggregation mode: {assertion.aggregation_mode}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        )
