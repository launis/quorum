"""API Router for LLM Operations.

This module provides endpoints for direct LLM model interaction, batch processing,
and managing the Model Registry configuration.
"""

import asyncio
import logging
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep, LLMHandlerDep, RegistryDep
from backend.llm.provider import LLMFactory

# from backend.llm.handler import LLMHandler # LLMHandlerDep already provides access to LLMHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])

# --- Models ---


class CompletionRequest(BaseModel):
    """Payload for a single LLM completion request.

    Attributes:
        prompt (str): The primary input text.
        system_instruction (str): Optional system context.
        model_strategy (str): Strategy key ('fast', 'deep') or direct model name.
        response_schema (dict): JSON Schema for structured output validation.
    """

    prompt: Annotated[str, Field(description="The primary prompt text.")]
    system_instruction: Annotated[str | None, Field(description="Optional system instruction.")] = None
    model_strategy: Annotated[str, Field(description="Strategy key (fast, deep, etc) or direct model name.")] = "fast"
    response_schema: Annotated[
        dict[str, Any] | None, Field(description="Optional JSON Schema for structured output.")
    ] = None


class BatchCompletionRequest(BaseModel):
    """Payload for batch completion requests."""

    requests: Annotated[list[CompletionRequest], Field(description="List of requests to process in parallel.")]


class ModelRegistryUpdate(BaseModel):
    """Payload for updating the model registry."""

    registry: Annotated[
        dict[str, dict[str, str]],
        Field(description="The new configuration map for model strategies (e.g. {'fast': {'model_name': '...'}})."),
    ]


# --- Endpoints ---


@router.post(
    "/completion", summary="Direct Completion", response_description="The generated text or structured object."
)
async def generate_completion(request: CompletionRequest, registry: RegistryDep):
    """Directly invokes the LLM using the specified strategy.

    Supports structured output if schema is provided.

    Args:
        request (CompletionRequest): The prompt and settings.
        registry (RegistryDep): Registry dependency to resolve strategies.

    Returns:
        dict: Result object containing the generated content.

    Raises:
        HTTPException: If strategy is invalid (400) or generation fails (500).
    """
    try:
        # 1. Resolve Provider via Registry
        config = await registry.resolve_model_config(request.model_strategy)
        provider = LLMFactory.create_provider(config["provider"], config["model_name"])

        # 2. Call Generate
        # If response_schema is present, model_strategy must support JSON mode or structured generation
        response = await provider.generate(
            prompt=request.prompt,
            system_instruction=request.system_instruction,
            response_schema=request.response_schema,
        )

        return {"result": response}

    except ValueError as e:
        error_code = "INVALID_MODEL_STRATEGY"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=error_code) from e
    except Exception as e:
        error_code = "LLM_COMPLETION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e


@router.post("/batch-completion", summary="Batch Completion", response_description="List of results.")
async def batch_completion(batch: BatchCompletionRequest, registry: RegistryDep):
    """Processes multiple completion requests in parallel.

    Args:
        batch (BatchCompletionRequest): List of requests.
        registry (RegistryDep): Registry dependency.

    Returns:
        dict: List of results (success or error) for each request.
    """

    async def _process_one(req: CompletionRequest):
        try:
            config = await registry.resolve_model_config(req.model_strategy)
            provider = LLMFactory.create_provider(config["provider"], config["model_name"])
            return await provider.generate(
                prompt=req.prompt, system_instruction=req.system_instruction, response_schema=req.response_schema
            )
        except Exception as e:
            error_code = "LLM_BATCH_ITEM_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            return {"error": str(e), "error_code": error_code}

    results = await asyncio.gather(*[_process_one(r) for r in batch.requests])
    return {"results": results}


@router.get("/providers", summary="List Providers", response_description="Active providers configuration.")
async def list_providers(handler: LLMHandlerDep):
    """Returns information about active LLM providers and availability.

    Args:
        handler (LLMHandlerDep): LLM Handler.

    Returns:
        dict: Strategies map and API key status.
    """
    # LLMHandler manages the high level interface, but factory has the config.
    # We can inspect the factory via the handler if exposed, or just return static info about supported types.
    # Currently handler doesn't expose much metadata.
    # Let's return the strategies configured in settings via common method
    from backend.settings import get_settings

    settings = get_settings()

    return {
        "strategies": settings.model_strategies,
        "api_keys_set": {"google": bool(settings.google_api_key), "openai": bool(settings.openai_api_key)},
    }


@router.get(
    "/config", summary="Get Model Registry", response_description="The current internal model mapping configuration."
)
def get_model_config(handler: LLMHandlerDep):
    """Retrieves the active model registry, which maps abstract strategies (e.g., 'fast') to concrete models.

    Args:
        handler: Dependency.

    Returns:
        dict: The registry configuration object.

    """
    return handler.get_active_model_registry()


@router.post(
    "/config", summary="Update Model Registry", response_description="Confirmation of the configuration update."
)
def update_model_config(update: ModelRegistryUpdate, db_client: DatabaseDep):
    """Updates the system's model registry configuration in the database.

    Args:
        update (ModelRegistryUpdate): The new configuration.
        db_client (DatabaseDep): Database dependency.

    Returns:
        dict: Status and the updated registry.

    Raises:
        HTTPException: If database update fails (500).
    """
    try:
        table = db_client.table("system_config")

        Config = Query()
        table.upsert({"type": "model_registry", "models": update.registry}, Config.type == "model_registry")
        return {"status": "success", "registry": update.registry}
    except Exception as e:
        error_code = "MODEL_REGISTRY_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e
