from typing import Type
from pydantic import BaseModel
from src.models.interfaces import (
    RawInput, TaintedData, EvidenceMap, AnalysisSummary, 
    HypothesisArgument, AuditResult, FinalVerdict, XAIReport
)

class SchemaRegistry:
    _registry = {
        "RawInput": RawInput,
        "TaintedData": TaintedData,
        "EvidenceMap": EvidenceMap,
        "AnalysisSummary": AnalysisSummary,
        "HypothesisArgument": HypothesisArgument,
        "AuditResult": AuditResult,
        "FinalVerdict": FinalVerdict,
        "XAIReport": XAIReport
    }

    @classmethod
    def get_schema(cls, schema_name: str) -> Type[BaseModel]:
        schema = cls._registry.get(schema_name)
        if not schema:
            raise ValueError(f"Schema '{schema_name}' not found in registry.")
        return schema
