"""Validation reporting models."""

from pydantic import ConfigDict

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.dtos.report.matrix import MatrixFieldsMixin


class ValidationWarningData(BaseDTO):
    """Preflight system warning structural model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    warning_type: str
    message: str


class ValidationReportData(MatrixFieldsMixin):
    """Validator execution step output payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    warnings: list[ValidationWarningData] | None = None
