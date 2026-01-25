"""API Router for Dynamic Schema Registry."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Header
from pydantic import BaseModel

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

# ... (imports)
from backend.services.localization import localize_schema

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
def get_model_schema(
    model_name: str,
    accept_language: Annotated[str | None, Header()] = "en"
):
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

    schema = model_class.model_json_schema()
    return localize_schema(schema, accept_language or "en")


@router.get("", summary="List Schemas", response_description="All Pydantic Schemas.")
def get_schemas(accept_language: Annotated[str | None, Header()] = "en"):
    """Get all available JSON Schemas (Global Registry)."""
    import inspect
    from backend.models import auth as auth_schemas
    from backend.models import domain as schemas
    from backend.models import settings as setting_schemas

    schema_data = {}

    # Combined source of truth: Registry + Modules
    # 1. Registry (Preferred for SDUI)
    for name, model_cls in MODEL_REGISTRY.items():
         try:
            json_schema = model_cls.model_json_schema()
            json_schema = localize_schema(json_schema, accept_language or "en")
            schema_data[name] = {"schema": json_schema}
         except Exception:
             pass

    # 2. Legacy Module Scans
    modules = [schemas, auth_schemas, setting_schemas]
    for mod in modules:
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
                if name in schema_data:
                     continue
                try:
                    json_schema = obj.model_json_schema()
                    json_schema = localize_schema(json_schema, accept_language or "en")

                    example = None
                    if hasattr(obj, "model_config"):
                        config: dict[str, Any] = dict(obj.model_config)
                        if "json_schema_extra" in config:
                            extra = config["json_schema_extra"]
                            if isinstance(extra, dict) and "examples" in extra and extra["examples"]:
                                example = extra["examples"][0]

                    schema_data[name] = {"schema": json_schema, "example": example}
                except Exception:
                    pass

    return schema_data
