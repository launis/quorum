from typing import Any

from pydantic import ConfigDict, Field

from backend.models.domain.causal import CausalAnalysis
from backend.models.domain.coach import BibliographyItem
from backend.models.domain.falsifier import FalsifierData
from backend.models.domain.logician import LogicianData
from backend.models.domain.overseer import OverseerData
from backend.models.domain.performativity import PerformativityAnalysis
from backend.models.domain.retrieval import KnowledgeItem
from backend.models.dtos.base import BaseDTO


class ReportContext(BaseDTO):
    """Context for the Jinja2 report template (The 'Fat' Report)."""

    summary: str = Field(..., description="Executive summary.")
    critical_findings: list[str] = Field(..., description="Critical findings.")
    pre_mortem_signals: list[str] = Field(..., description="Pre-mortem signals.")
    hitl_required: bool = Field(..., description="HITL required.")
    ethical_issues: list[dict[str, Any]] = Field(..., description="Ethical issues.")
    audit_questions: list[dict[str, Any]] = Field(..., description="Audit questions.")
    uncertainty: dict[str, Any] = Field(..., description="Uncertainty metrics.")
    scores: dict[str, dict[str, Any]] = Field(..., description="Scores (arvosana, perustelu).")
    average_score: float = Field(..., description="Average score.")
    timestamp: str = Field(..., description="Report timestamp.")
    coaching_plan: dict[str, Any] | None = Field(default=None, description="Coaching plan.")
    penalties_applied: list[str] = Field(default_factory=list, description="Penalties applied.")
    score_summary: str | None = Field(default=None, description="Score summary.")
    input_control_ratio: float | None = Field(default=None, description="Input control ratio.")
    word_count: int | None = Field(default=None, description="Total word count.")
    structural_warnings: list[str] = Field(default_factory=list, description="Structural warnings.")
    archivist_precedents: Any | None = Field(default=None, description="Archivist precedents.")
    google_search_results: list[dict[str, Any]] = Field(default_factory=list, description="Google search results.")
    bibliography: list[BibliographyItem] = Field(default_factory=list, description="Authoritative bibliography.")

    # Specialist Agents (Deep Analysis)
    logician_data: LogicianData | None = Field(default=None, description="Logician analysis.")
    falsifier_data: FalsifierData | None = Field(default=None, description="Falsifier analysis.")
    causal_analysis: CausalAnalysis | None = Field(default=None, description="Causal analysis.")
    performativity_analysis: PerformativityAnalysis | None = Field(default=None, description="Performativity analysis.")
    overseer_data: OverseerData | None = Field(default=None, description="Overseer analysis.")
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list, description="Knowledge Base items.")

    model_config = ConfigDict(frozen=False, strict=True)
