from typing import Any

from pydantic import ConfigDict, Field

from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.coach import BibliographyItem
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.logician import LogicianData
from backend_v2.models.domain.overseer import OverseerData
from backend_v2.models.domain.performativity import PerformativityAnalysis
from backend_v2.models.domain.retrieval import KnowledgeItem
from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.view.sdui import ReferenceItem


class ReportContext(BaseDTO):
    """Context for the Jinja2 report template (The 'Fat' Report)."""

    summary: str | None = Field(default=None, description="Executive summary.")
    critical_findings: list[str] = Field(default_factory=list, description="Critical findings.")
    pre_mortem_signals: list[str] = Field(default_factory=list, description="Pre-mortem signals.")
    hitl_required: bool | None = Field(default=None, description="HITL required.")
    ethical_issues: list[dict[str, Any]] = Field(default_factory=list, description="Ethical issues.")
    audit_questions: list[dict[str, Any]] = Field(default_factory=list, description="Audit questions.")
    uncertainty: dict[str, Any] = Field(default_factory=dict, description="Uncertainty metrics.")
    scores: dict[str, dict[str, Any]] = Field(default_factory=dict, description="Scores (arvosana, perustelu).")
    average_score: float | None = Field(default=None, description="Average score.")
    timestamp: str | None = Field(default=None, description="Report timestamp.")
    coaching_plan: dict[str, Any] | None = Field(default=None, description="Coaching plan.")
    penalties_applied: list[str] = Field(default_factory=list, description="Penalties applied.")
    score_summary: str | None = Field(default=None, description="Score summary.")
    input_control_ratio: float | None = Field(default=None, description="Input control ratio.")
    word_count: int | None = Field(default=None, description="Total word count.")
    structural_warnings: list[str] = Field(default_factory=list, description="Structural warnings.")
    archivist_precedents: Any | None = Field(default=None, description="Archivist precedents.")
    google_search_results: list[dict[str, Any]] = Field(default_factory=list, description="Google search results.")
    bibliography: list[BibliographyItem] = Field(default_factory=list, description="Authoritative bibliography.")
    references: list[ReferenceItem] = Field(default_factory=list, description="Global references list.")

    # Specialist Agents (Deep Analysis)
    logician_data: LogicianData | None = Field(default=None, description="Logician analysis.")
    falsifier_data: FalsifierData | None = Field(default=None, description="Falsifier analysis.")
    causal_analysis: CausalAnalysis | None = Field(default=None, description="Causal analysis.")
    performativity_analysis: PerformativityAnalysis | None = Field(default=None, description="Performativity analysis.")
    overseer_data: OverseerData | None = Field(default=None, description="Overseer analysis.")
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list, description="Knowledge Base items.")

    # Allow type coercion (e.g. string "1" to integer 1) for LLM friendliness, but keep fields frozen
    model_config = ConfigDict(frozen=True, strict=False)
