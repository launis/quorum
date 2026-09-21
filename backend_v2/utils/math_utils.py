"""Core Mathematical Utilities for the Cognitive Quorum System.

Contains deterministic calculation logic (Part 18.7 Python Authority),
prioritizing strict validation and Fail Fast principles.
"""

import collections.abc
import logging
from typing import Any

from fastapi import status
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes, MissingInputMappingError
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO

__all__ = [
    "calculate_linear_ratio_score",
    "calculate_scaled_score",
    "clamp_score",
    "normalize_score_to_100",
    "resolve_dot_notation",
    "scale_to_custom_range",
]

logger = logging.getLogger(__name__)


def clamp_score(score: float, math_min: float, math_max: float) -> float:
    """Ensure the score is strictly within the mathematical bounds.

    Args:
        score: The raw score to clamp.
        math_min: The minimum allowed score.
        math_max: The maximum allowed score.

    Returns:
        The clamped score.

    Raises:
        AppException: If math_min >= math_max (INVALID_OUTPUT_SCHEMA).
    """
    if math_min >= math_max:
        msg = f"Invalid bounds for clamping: min ({math_min}) >= max ({math_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )
    return float(max(math_min, min(math_max, score)))


def normalize_score_to_100(score: float, math_min: float, math_max: float) -> float:
    """Normalize any score to a proportional 0.0 - 100.0 percentage scale.

    Normalizes according to absolute mathematical bounds.

    Args:
        score: The score to normalize (computed value).
        math_min: The minimum possible score in the calculation matrix.
        math_max: The maximum possible score in the calculation matrix.

    Returns:
        The normalized proportional score between 0.0 and 100.0.

    Raises:
        AppException: If math_min >= math_max (INVALID_OUTPUT_SCHEMA).
    """
    if math_min >= math_max:
        msg = f"Invalid bounds for normalization: min ({math_min}) >= max ({math_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    proportional_fraction = (score - math_min) / (math_max - math_min)
    normalized = proportional_fraction * 100.0

    return max(0.0, min(100.0, normalized))


def calculate_scaled_score(score: float, number_of_options: int, math_min: float, math_max: float) -> float:
    """Calculate the absolute scaled position mathematically from raw output to configured scale.

    Args:
        score: The score to scale.
        number_of_options: The number of available options in the scale.
        math_min: The minimum bound of the scale.
        math_max: The maximum bound of the scale.

    Returns:
        The scaled score clamped within bounds.

    Raises:
        AppException: If math_min >= math_max (INVALID_OUTPUT_SCHEMA).
    """
    if math_min >= math_max:
        msg = f"Invalid scale definition: math_min ({math_min}) >= math_max ({math_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    # In V2, the score is mathematically ALREADY expected to be on the `math_min` to `math_max` scale!
    # Especially if it comes from waterfall_scoring_hook.
    # Therefore, we simply clamp it into bounds.
    return float(max(math_min, min(math_max, score)))


def scale_to_custom_range(score: float, raw_min: float, raw_max: float, target_min: float, target_max: float) -> float:
    """Scale a score from a raw range to a custom target range linearly.

    Args:
        score: The score to scale.
        raw_min: The minimum possible score of the original scale.
        raw_max: The maximum possible score of the original scale.
        target_min: The minimum value of the desired target scale (e.g. 4.0).
        target_max: The maximum value of the desired target scale (e.g. 10.0).

    Returns:
        The proportionally scaled score.

    Raises:
        AppException: If raw_min >= raw_max (INVALID_OUTPUT_SCHEMA).
    """
    if raw_min >= raw_max:
        msg = f"Invalid raw scale definition: raw_min ({raw_min}) >= raw_max ({raw_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    scaled = target_min + (score - raw_min) / (raw_max - raw_min) * (target_max - target_min)

    # Clamp to target bounds
    actual_min = min(target_min, target_max)
    actual_max = max(target_min, target_max)

    return max(actual_min, min(actual_max, scaled))


def calculate_linear_ratio_score(
    level_stats: dict[float, LevelStatsDTO], math_min: float, math_max: float, exponent: float = 1.0
) -> float:
    """Calculate the global weighted average of all matrix atoms.

    Score is mapped proportionally to the scale based on the absolute ratio of achieved
    weighted points versus the maximum possible weighted points. An exponent can be applied
    for non-linear curve scaling based on strictness.

    Args:
        level_stats: Dictionary mapping scale levels to LevelStatsDTO.
        math_min: The minimum value of the scale (e.g. 1.0).
        math_max: The maximum value of the scale (e.g. 5.0).
        exponent: Non-linear exponent to apply to the proportional fraction.

    Returns:
        The exact weighted score.

    Raises:
        AppException: If math_min >= math_max (INVALID_OUTPUT_SCHEMA).
    """
    if math_min >= math_max:
        msg = f"Invalid scale definition: math_min ({math_min}) >= math_max ({math_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    achieved_weights = 0.0
    max_weights = 0.0

    for level, stats in level_stats.items():
        total = stats.total - stats.dlqs
        hits = stats.hits

        # Weighted mathematics calculation
        achieved_weights += hits * level
        max_weights += total * level

    if max_weights <= 0:
        return float(math_min)

    proportional_fraction = achieved_weights / max_weights
    proportional_fraction = proportional_fraction**exponent
    scaled_val = math_min + (proportional_fraction * (math_max - math_min))

    return float(max(math_min, min(math_max, scaled_val)))


def resolve_dot_notation(state: Any, path: str) -> Any:
    """Safely resolve a dot-notation path against a state mapping, sequence, or model.

    Uses strictly typed iterative traversal. Never uses eval, exec, dict.get, or getattr.

    Args:
        state: Root state object or data structure to traverse.
        path: Dot-separated attribute or key path string.

    Returns:
        The resolved value at the designated path.

    Raises:
        MissingInputMappingError: If any path component is missing or invalid.
    """
    if not path:
        return state

    parts = path.split(".")
    curr = state

    for part in parts:
        try:
            match curr:
                case collections.abc.Mapping():
                    curr = curr[part]
                case collections.abc.Sequence() if not isinstance(curr, (str, bytes)):
                    curr = curr[int(part)]
                case BaseModel():
                    if part in type(curr).model_fields:
                        curr = object.__getattribute__(curr, part)
                    else:
                        raise KeyError(part)
                case _:
                    curr = object.__getattribute__(curr, part)
        except (KeyError, AttributeError, IndexError, ValueError) as e:
            raise MissingInputMappingError(
                path=path, state_type=type(curr).__name__, reason=f"Failed at '{part}': {type(e).__name__}"
            ) from e

    return curr
