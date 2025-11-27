from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

class Citation(BaseSchema):
    source: str
    explanation: str

class RawInput(BaseSchema):
    prompt_text: str
    history_text: str
    product_text: str
    reflection_text: str

class TaintedData(BaseSchema):
    safe_data: Dict[str, str]
    threat_assessment: str
    is_safe: bool

class EvidenceMap(BaseSchema):
    prompt_evidence: str
    history_evidence: str
    product_evidence: str
    reflection_evidence: str

class AnalysisSummary(BaseSchema):
    evidence_map: EvidenceMap
    analysis_summary: str
    citations: List[Citation] = Field(default_factory=list)

class HypothesisArgument(BaseSchema):
    hypothesis_argument: str
    toulmin_structure: Dict[str, Any]
    citations: List[Citation] = Field(default_factory=list)

class AuditResult(BaseSchema):
    audit_report: str
    citations: List[Citation] = Field(default_factory=list)

class FinalVerdict(BaseSchema):
    final_verdict: str
    citations: List[Citation] = Field(default_factory=list)

class XAIReport(BaseSchema):
    xai_report: str
    reliability_score: str
