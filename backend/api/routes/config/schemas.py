"""API Router for Dynamic Schema Registry."""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.exceptions import AppException, ResourceNotFoundError
from backend.models.domain import (
    AnalystOutput,
    ArchivistOutput,
    CausalAnalysis,
    CoachingPlan,
    EvaluationMatrixConfig,
    EvaluationResult,
    FalsifierData,
    InteractionAnalysis,
    LogicianData,
    OverseerData,
    PanelOutput,
    PerformativityAnalysis,
    ProfilerOutput,
    TaintedDataContent,
    XAIOutput,
)
from backend.models.dtos.config import (
    SchemaInfo,
    SchemaListResponse,
    SchemaResponse,
)
from backend.models.workflow import WorkflowDefinition

# ... (imports)
from backend.services.localization import localize_schema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schemas", tags=["Configuration"])

# Registry Mapping
# Maps 'friendly' names to Pydantic models
MODEL_REGISTRY = {
    # Configuration Models
    "workflow_definition": WorkflowDefinition,
    "evaluation_matrix": EvaluationMatrixConfig,
    # Agent Output Models (Domain)
    "tainted_data": TaintedDataContent,  # Guard
    "todistus_kartta": AnalystOutput,  # Analyst
    "profiler_analysis": ProfilerOutput,  # Profiler
    "argumentaatio_analyysi": LogicianData,  # Logician
    "logiikka_auditointi": FalsifierData,  # Falsifier
    "etiikka_ja_fakta": OverseerData,  # Overseer
    "kausaalinen_auditointi": CausalAnalysis,  # Causal
    "performatiivisuus_auditointi": PerformativityAnalysis,  # Performativity
    "coaching_plan": CoachingPlan,  # Coach
    "archivist_output": ArchivistOutput,  # Archivist
    "interaction_analysis": InteractionAnalysis,  # Interaction
    "xai_report": XAIOutput,  # XAI
    # Aggregates
    "panel_audit": PanelOutput,
    "evaluation_result": EvaluationResult,
}


@router.get(
    "/{model_name}",
    summary="Get Model JSON Schema",
    response_model=SchemaResponse,
    description="Returns the JSON Schema for a registered Pydantic model. citations: dynamic",
)
def get_model_schema(
    model_name: str,
) -> SchemaResponse:
    """Dynamic Registry Lookup for SDUI."""
    try:
        if model_name not in MODEL_REGISTRY:
            error_code = "SCHEMA_NOT_FOUND"
            logger.warning(f"{error_code}: Requested model '{model_name}'")
            raise ResourceNotFoundError(
                resource_type="Schema",
                resource_id=model_name,
                details={"available_models": list(MODEL_REGISTRY.keys()), "error_code": error_code},
            )

        from typing import cast

        from pydantic import BaseModel

        # Validated existence above
        model_class = cast(type[BaseModel], MODEL_REGISTRY[model_name])

        schema = model_class.model_json_schema()
        localized = localize_schema(schema)

        return SchemaResponse(model_name=model_name, schema_def=localized)

    except Exception as e:
        if isinstance(e, (ResourceNotFoundError, AppException)):
            raise e

        error_code = "SCHEMA_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.get("", summary="List Schemas", response_description="All Pydantic Schemas.", response_model=SchemaListResponse)
def get_schemas() -> SchemaListResponse:
    """Get all available JSON Schemas (Global Registry)."""
    try:
        import inspect

        from backend.models import auth as auth_schemas
        from backend.models import domain as schemas
        from backend.models import settings as setting_schemas

        schema_data = {}

        # Combined source of truth: Registry + Modules
        # 1. Registry (Preferred for SDUI)
        for name, model_cls in MODEL_REGISTRY.items():
            try:
                json_schema = model_cls.model_json_schema()  # type: ignore
                json_schema = localize_schema(json_schema)
                # SchemaInfo has alias="schema", so we use that key in dict construction
                schema_data[name] = SchemaInfo(schema=json_schema)
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
                        json_schema = localize_schema(json_schema)

                        example = None
                        if hasattr(obj, "model_config"):
                            config: dict[str, Any] = dict(obj.model_config)
                            if "json_schema_extra" in config:
                                extra = config["json_schema_extra"]
                                if isinstance(extra, dict) and "examples" in extra and extra["examples"]:
                                    example = extra["examples"][0]

                        schema_data[name] = SchemaInfo(schema=json_schema, example=example)
                    except Exception:
                        pass

        return SchemaListResponse(items=schema_data)

    except Exception as e:
        error_code = "SCHEMA_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
