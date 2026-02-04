from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SectionType(str, Enum):
    SCORE_CARD = "SCORE_CARD"
    MARKDOWN_BLOCK = "MARKDOWN_BLOCK"
    TIMELINE_FEED = "TIMELINE_FEED"
    # Future extensibility
    HEADER = "HEADER"
    KEY_METRICS = "KEY_METRICS"
    KEY_VALUE_GRID = "KEY_VALUE_GRID" # For structured properties (e.g. Guard flags)
    DATA_TABLE = "DATA_TABLE"         # For lists of rows (e.g. Hypotheses)
    ACCORDION = "ACCORDION"           # For nested details

    # Specialist Agent Sections (Courtroom 3.0 Backbone)
    LOGIC_ANALYSIS = "LOGIC_ANALYSIS"             # Toulmin & Cognitive Level
    STRESS_TEST = "STRESS_TEST"                   # Walton Falsification
    CAUSAL_ANALYSIS = "CAUSAL_ANALYSIS"           # Counterfactuals
    PERFORMATIVITY_CHECK = "PERFORMATIVITY_CHECK" # Illusion of Competence
    FACT_CHECK = "FACT_CHECK"                     # Hallucination & Ethics
    PROFILER_ANALYSIS = "PROFILER_ANALYSIS"       # Biases & Psych Profile
    ARCHIVIST_CHECK = "ARCHIVIST_CHECK"           # Compliance & Precedents
    DRIVER_PROFILE = "DRIVER_PROFILE"             # Interaction / Driver Classification

class UiSection(BaseModel):
    """Abstract UI Section.
    Frontend renders the component based on 'type'.
    """
    id: str = Field(..., description="Unique identifier for the section (e.g. 'verdict-card')")
    type: SectionType = Field(..., description="Determines which UI component to render")
    title: str = Field(..., description="User-facing title of the section")
    data: dict[str, Any] = Field(default_factory=dict, description="Flexible payload specific to the section type")

class ReportView(BaseModel):
    """Top-level View Model for the Execution Report.
    This replaces the raw 'Execution' object for frontend consumption.
    """
    view_id: str = Field(..., description="The Execution ID")
    title: str = Field(default="Auditintiraportti", description="Page title")
    status_theme: str = Field(default="success", description="Visual theme: 'success' | 'warning' | 'danger'")
    sections: list[UiSection] = Field(default_factory=list, description="Ordered list of UI sections")
