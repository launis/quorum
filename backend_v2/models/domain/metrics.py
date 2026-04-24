"""Metrics Domain Models.

Provides strict Pydantic V2 validation schemas for the metrics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import ConfigDict, RootModel


class MetricsPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for metrics analysis.

    By utilizing RootModel, we strictly enforce that the incoming state
    payload is explicitly a dictionary before any iterative logic executes,
    satisfying the Phase 9 Zero-Compromise mandate.
    """  # noqa: W293

    model_config = ConfigDict(frozen=True)
