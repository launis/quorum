"""Specialist DTOs for various report analysis panels."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.dtos.report.matrix import MatrixFieldsMixin


class XaiReportData(MatrixFieldsMixin):
    """Xai execution step payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    executive_summary: str | None = None
    evaluation_notes: str | None = None


class JudgeReportData(MatrixFieldsMixin):
    """Judge execution step payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    critical_findings: Annotated[list[str], Field(default_factory=list)]


class OverseerData(BaseDTO):
    """Overseer critical indicators mapping."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    ethical_issues: Annotated[list[str], Field(default_factory=list)]


class OverseerReportData(MatrixFieldsMixin):
    """Overseer step wrapper payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    overseer_data: OverseerData | None = None


class LogicianScheme(BaseDTO):
    """Logician Walton critical argument analysis scheme schema."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    critical_questions: Annotated[list[str], Field(default_factory=list)]


class LogicianData(BaseDTO):
    """Logician container for argument mappings."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    walton_scheme: LogicianScheme | None = None


class LogicianReportData(MatrixFieldsMixin):
    """Logician execution step payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    logician_data: LogicianData | None = None


class PerformativityAnalysis(BaseDTO):
    """Detailed behavioral authenticity or performative actions metric structures."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    pre_mortem_analysis: str | None = None
    weak_signals: Annotated[list[str], Field(default_factory=list)]


class PerformativityReportData(MatrixFieldsMixin):
    """Detector execution step payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    performativity_analysis: PerformativityAnalysis | None = None


class AnalystReportData(MatrixFieldsMixin):
    """Analyst execution step payload model containing direct citation sources."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    rag_evidence: Annotated[list[str], Field(default_factory=list)]


class FalsifierData(BaseDTO):
    """Falsifier execution metrics payload mapping."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    vulnerabilities: Annotated[list[str], Field(default_factory=list)]


class CausalAnalysisData(BaseDTO):
    """Causal scenario testing parameters mapping."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    counterfactuals: Annotated[list[str], Field(default_factory=list)]


class PanelReportData(MatrixFieldsMixin):
    """Combined panel execution step payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    overseer_data: OverseerData | None = None
    logician_data: LogicianData | None = None
    performativity_analysis: PerformativityAnalysis | None = None
    falsifier_data: FalsifierData | None = None
    causal_analysis: CausalAnalysisData | None = None


class ProfilerMetrics(BaseDTO):
    """Linguistic profile statistics metadata representation."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    word_count: int = 0
    control_ratio: float = 0.0


class ProfilerReportData(MatrixFieldsMixin):
    """Profiler execution step payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    metrics: ProfilerMetrics | None = None
