"""
Abstract interface for projecting execution results into standardized DTOs.
"""

from abc import ABC, abstractmethod
from typing import Any

from backend_v2.models.dtos.report import ReportDataDto


class ResultProjector(ABC):
    """
    Abstract interface responsible for converting atom-level engine results 
    to the new ReportDataDto.
    """

    @abstractmethod
    def project(self, engine_output: dict[str, Any]) -> ReportDataDto:
        """
        Project the raw engine output into a typed ReportDataDto.

        Args:
            engine_output: Raw output dict from the V1 or V2 engine.

        Returns:
            ReportDataDto: The strictly typed projection.
        """
        pass
