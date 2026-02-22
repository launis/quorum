"""API Router for LLM Operations.

This module provides endpoints for direct LLM model interaction, batch processing,
and managing the Model Registry configuration.
"""

import asyncio
import logging
from typing import Annotated, Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from backend.dependencies import CurrentUserDep, LLMHandlerDep, RegistryDep, RepositoryDep
from backend.llm.provider import LLMFactory
from backend.models.dtos.llm import (
    BatchLLMResponse,
    LLMResponse,
    ModelRegistryResponse,
    ModelRegistryUpdateResponse,
    ProviderListResponse,
)

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

    model_config = ConfigDict(extra="forbid")


class BatchCompletionRequest(BaseModel):
    """Payload for batch completion requests."""

    requests: Annotated[list[CompletionRequest], Field(description="List of requests to process in parallel.")]
    model_config = ConfigDict(extra="forbid")


class ModelRegistryUpdate(BaseModel):
    """Payload for updating the model registry."""

    registry: Annotated[
        dict[str, dict[str, str]],
        Field(description="The new configuration map for model strategies (e.g. {'fast': {'model_name': '...'}})."),
    ]
    model_config = ConfigDict(extra="forbid")


# --- Endpoints ---


@router.post(
    "/completion",
    summary="Direct Completion",
    response_description="The generated text or structured object.",
    response_model=LLMResponse,
)
async def generate_completion(
    request: CompletionRequest, registry: RegistryDep, user: CurrentUserDep, repo: RepositoryDep
) -> LLMResponse:
    """Directly invokes the LLM using the specified strategy.

    Supports structured output if schema is provided.

    Args:
        request (CompletionRequest): The prompt and settings.
        registry (RegistryDep): Registry dependency to resolve strategies.
        user (CurrentUserDep): Authenticated user (required for rate limits).
        repo (RepositoryDep): Data repository.

    Returns:
        LLMResponse: Result object containing the generated content.

    Raises:
        HTTPException: If strategy is invalid (400) or generation fails (500).
    """
    try:
        # 0. Fetch Organization Limits
        limits = None
        if user.organization_id:
            org = await repo.get_organization(user.organization_id)
            if org:
                # Default safety limits if missing in DB
                limits = {"tpm": org.get("tpm_limit", 100000), "rpm": org.get("rpm_limit", 60)}

        # 1. Resolve Provider via Registry
        config = await registry.resolve_model_config(request.model_strategy)

        # 2. Create Provider with Dynamic Limits
        provider = LLMFactory.create_provider(
            provider_type=config.provider,
            model_name=config.model_name,
            organization_id=user.organization_id,
            limits=limits,
        )

        # 2. Call Generate
        # If response_schema is present, model_strategy must support JSON mode or structured generation
        response = await provider.generate(
            prompt=request.prompt,
            system_instruction=request.system_instruction,
            response_schema=request.response_schema,
        )

        return LLMResponse(result=response, usage=getattr(response, "usage", None))

    except ValueError as e:
        from backend.exceptions import AppException

        error_code = "INVALID_MODEL_STRATEGY"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=400, details={"error_code": error_code}) from e
    except Exception as e:
        from backend.exceptions import ServiceUnavailableError

        error_code = "LLM_COMPLETION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise ServiceUnavailableError(message=str(e), details={"error_code": error_code}) from e


@router.post(
    "/batch-completion",
    summary="Batch Completion",
    response_description="List of results.",
    response_model=BatchLLMResponse,
)
async def batch_completion(
    batch: BatchCompletionRequest, registry: RegistryDep, user: CurrentUserDep, repo: RepositoryDep
) -> BatchLLMResponse:
    """Processes multiple completion requests in parallel.

    Args:
        batch (BatchCompletionRequest): List of requests.
        registry (RegistryDep): Registry dependency.
        user (CurrentUserDep): Authenticated user.
        repo (RepositoryDep): Data repository.

    Returns:
        BatchLLMResponse: List of results (success or error) for each request.
    """
    # 0. Fetch Organization Limits
    limits = None
    if user.organization_id:
        org = await repo.get_organization(user.organization_id)
        if org:
            limits = {"tpm": org.get("tpm_limit", 100000), "rpm": org.get("rpm_limit", 60)}

    async def _process_one(req: CompletionRequest) -> dict[str, Any]:
        try:
            config = await registry.resolve_model_config(req.model_strategy)

            provider = LLMFactory.create_provider(
                provider_type=config.provider,
                model_name=config.model_name,
                organization_id=user.organization_id,
                limits=limits,
            )

            res = await provider.generate(
                prompt=req.prompt, system_instruction=req.system_instruction, response_schema=req.response_schema
            )
            return {"status": "success", "result": res}
        except Exception as e:
            error_code = "LLM_BATCH_ITEM_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            # In batch mode, we return the error structure rather than raising to allow partial success
            return {"status": "error", "message": str(e), "error_code": error_code}

    results = await asyncio.gather(*[_process_one(r) for r in batch.requests])
    return BatchLLMResponse(results=list(results))


@router.get(
    "/providers",
    summary="List Providers",
    response_description="Active providers configuration.",
    response_model=ProviderListResponse,
)
async def list_providers(handler: LLMHandlerDep) -> ProviderListResponse:
    """Returns information about active LLM providers and availability.

    Args:
        handler (LLMHandlerDep): LLM Handler.

    Returns:
        ProviderListResponse: Strategies map and API key status.
    """
    # LLMHandler manages the high level interface, but factory has the config.
    # We can inspect the factory via the handler if exposed, or just return static info about supported types.
    # Currently handler doesn't expose much metadata.
    # Let's return the strategies configured in settings via common method
    from backend.settings import get_settings

    settings = get_settings()

    # Dynamic Discovery: Fetch available models
    available_models = handler.fetch_all_available_models(providers=["google", "openai"])

    strategies_map: dict[str, str] = {}
    if getattr(settings, "model_strategies", None):
        for k, v in settings.model_strategies.items():
            strategies_map[k] = v.model_name

    clean_avail: dict[str, list[str]] = {}
    for p, mods in available_models.items():
        if isinstance(mods, list):
            clean_avail[str(p)] = [str(m) for m in mods]
        elif isinstance(mods, str):
            clean_avail[str(p)] = [mods]

    return ProviderListResponse(
        strategies=strategies_map,
        api_keys_set={"google": bool(settings.google_api_key), "openai": bool(settings.openai_api_key)},
        available_models=clean_avail,
    )


@router.get(
    "/config",
    summary="Get Model Registry",
    response_description="The current internal model mapping configuration.",
    response_model=ModelRegistryResponse,
)
def get_model_config(handler: LLMHandlerDep) -> ModelRegistryResponse:
    """Retrieves the active model registry, which maps abstract strategies (e.g., 'fast') to concrete models.

    Args:
        handler: Dependency.

    Returns:
        ModelRegistryResponse: The registry configuration object.

    """
    registry = handler.get_active_model_registry()
    return ModelRegistryResponse(models=registry)


@router.post(
    "/config",
    summary="Update Model Registry",
    response_description="Confirmation of the configuration update.",
    response_model=ModelRegistryUpdateResponse,
)
async def update_model_config(update: ModelRegistryUpdate, registry: RegistryDep) -> ModelRegistryUpdateResponse:
    """Updates the system's model registry configuration in the database.

    Args:
        update (ModelRegistryUpdate): The new configuration.
        registry (RegistryDep): Registry dependency.

    Returns:
        ModelRegistryUpdateResponse: Status and the updated registry.

    Raises:
        HTTPException: If database update fails (500).
    """
    try:
        await registry.update_model_registry_config(update.registry)
        return ModelRegistryUpdateResponse(status="success", registry=update.registry)
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "MODEL_REGISTRY_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
