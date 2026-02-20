from typing import Any, List, Dict, Optional

from pydantic import Field, ConfigDict

from backend.models.dtos.base import BaseDTO
from backend.models.domain.coach import BibliographyItem
from backend.models.domain.logician import LogicianData
from backend.models.domain.falsifier import FalsifierData
from backend.models.domain.causal import CausalAnalysis
from backend.models.domain.performativity import PerformativityAnalysis
from backend.models.domain.overseer import OverseerData
from backend.models.domain.retrieval import KnowledgeItem

class ReportContext(BaseDTO):
    """Context for the Jinja2 report template (The 'Fat' Report)."""
    summary: str = Field(..., description="Executive summary.")
    critical_findings: List[str] = Field(..., description="Critical findings.")
    pre_mortem_signals: List[str] = Field(..., description="Pre-mortem signals.")
    hitl_required: bool = Field(..., description="HITL required.")
    ethical_issues: List[Dict[str, Any]] = Field(..., description="Ethical issues.")
    audit_questions: List[Dict[str, Any]] = Field(..., description="Audit questions.")
    uncertainty: Dict[str, Any] = Field(..., description="Uncertainty metrics.")
    scores: Dict[str, Dict[str, Any]] = Field(..., description="Scores (arvosana, perustelu).")
    average_score: float = Field(..., description="Average score.")
    timestamp: str = Field(..., description="Report timestamp.")
    coaching_plan: Dict[str, Any] | None = Field(default=None, description="Coaching plan.")
    penalties_applied: List[str] = Field(default_factory=list, description="Penalties applied.")
    score_summary: str | None = Field(default=None, description="Score summary.")
    input_control_ratio: float | None = Field(default=None, description="Input control ratio.")
    word_count: int | None = Field(default=None, description="Total word count.")
    structural_warnings: List[str] = Field(default_factory=list, description="Structural warnings.")
    archivist_precedents: Any | None = Field(default=None, description="Archivist precedents.")
    google_search_results: List[Dict[str, Any]] = Field(default_factory=list, description="Google search results.")
    bibliography: List[BibliographyItem] = Field(default_factory=list, description="Authoritative bibliography.")

    # Specialist Agents (Deep Analysis)
    logician_data: LogicianData | None = Field(default=None, description="Logician analysis.")
    falsifier_data: FalsifierData | None = Field(default=None, description="Falsifier analysis.")
    causal_analysis: CausalAnalysis | None = Field(default=None, description="Causal analysis.")
    performativity_analysis: PerformativityAnalysis | None = Field(default=None, description="Performativity analysis.")
    overseer_data: OverseerData | None = Field(default=None, description="Overseer analysis.")
    knowledge_items: List[KnowledgeItem] = Field(default_factory=list, description="Knowledge Base items.")

    model_config = ConfigDict(frozen=False, strict=True)
