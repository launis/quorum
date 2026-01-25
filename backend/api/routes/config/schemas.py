"""API Router for Dynamic Schema Registry."""

import logging
from typing import Any

from fastapi import APIRouter

from backend.exceptions import ResourceNotFoundError
from backend.models.domain import (
    ArchivistOutput,
    ArgumentaatioAnalyysi,
    CoachingPlan,
    EtiikkaJaFakta,
    EvaluationMatrixConfig,
    EvaluationResult,
    InteractionAnalysis,
    KausaalinenAuditointi,
    LogiikkaAuditointi,
    PanelAudit,
    PerformatiivisuusAuditointi,
    ProfilerAnalysis,
    TaintedData,
    TodistusKartta,
    XAIReport,
)
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config/schemas", tags=["Configuration"])

# Registry Mapping
# Maps 'friendly' names to Pydantic models
MODEL_REGISTRY = {
    # Configuration Models
    "workflow_definition": WorkflowDefinition,
    "evaluation_matrix": EvaluationMatrixConfig,

    # Agent Output Models (Domain)
    "tainted_data": TaintedData,  # Guard
    "todistus_kartta": TodistusKartta,  # Analyst
    "profiler_analysis": ProfilerAnalysis,  # Profiler
    "argumentaatio_analyysi": ArgumentaatioAnalyysi,  # Logician
    "logiikka_auditointi": LogiikkaAuditointi,  # Falsifier
    "etiikka_ja_fakta": EtiikkaJaFakta,  # Overseer
    "kausaalinen_auditointi": KausaalinenAuditointi,  # Causal
    "performatiivisuus_auditointi": PerformatiivisuusAuditointi,  # Performativity
    "coaching_plan": CoachingPlan, # Coach
    "archivist_output": ArchivistOutput, # Archivist
    "interaction_analysis": InteractionAnalysis, # Interaction
    "xai_report": XAIReport,  # XAI

    # Aggregates
    "panel_audit": PanelAudit,
    "evaluation_result": EvaluationResult,
}


@router.get(
    "/{model_name}",
    summary="Get Model JSON Schema",
    response_model=dict[str, Any],
    description="Returns the JSON Schema for a registered Pydantic model. citations: dynamic",
)
def get_model_schema(model_name: str):
    """Dynamic Registry Lookup for SDUI."""
    if model_name not in MODEL_REGISTRY:
        error_code = "SCHEMA_NOT_FOUND"
        logger.warning(f"{error_code}: Requested model '{model_name}'")
        raise ResourceNotFoundError(
            resource_type="Schema",
            resource_id=model_name,
            details={"available_models": list(MODEL_REGISTRY.keys()), "error_code": error_code}
        )

    from typing import cast

    from pydantic import BaseModel
    # Validated existence above
    model_class = cast(type[BaseModel], MODEL_REGISTRY[model_name])
    return model_class.model_json_schema()
