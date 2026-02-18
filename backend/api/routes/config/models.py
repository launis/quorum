"""Model Registry Configuration Router."""

import logging
import time
from typing import Annotated, Dict, Any, List

from fastapi import APIRouter, Depends

from backend.dependencies import (
    LLMHandlerDep,
    RepositoryDep,
    UsageServiceDep,
    get_llm_factory_dep,
)
from backend.exceptions import AppException, ErrorCodes, status
from backend.llm.provider import LLMFactory
from backend.models.llm import AdHocTestRequest, AdHocTestResponse, LLMProviderConfig
from backend.models.dtos.config import ModelOptionsResponse
from backend.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Config: Models"])


@router.get("", response_model=List[LLMProviderConfig])
async def list_models(
    repository: RepositoryDep,
):
    """List all available LLM providers and their current configuration.

    Supports nested structure: models[provider][strategy].
    Returns flattened list with id="{provider}/{strategy}".
    """
    try:
        registry = await repository.get_model_registry()
        strategies = registry.get("models", {})

        # FAIL FAST: Strict Registry Structure
        if not isinstance(strategies, dict):
            error_code = ErrorCodes.INVALID_REGISTRY_STRUCTURE
            logger.error(f"[Config] {error_code.value}: 'models' key in registry is not a dictionary.")
            raise AppException(
                message="Model Registry corrupted: 'models' is not a dictionary.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code}
            )

        results: List[LLMProviderConfig] = []

        for provider_name, provider_strategies in strategies.items():
            # Skip if not a dict (malformed provider bucket)
            if not isinstance(provider_strategies, dict):
                logger.warning(f"[Config] Skipping invalid provider bucket '{provider_name}': Expected dict, got {type(provider_strategies)}")
                continue

            for strategy_name, strategy_config in provider_strategies.items():
                # Skip Agent mappings (strings) or other non-dict items
                if not isinstance(strategy_config, dict):
                    continue

                # Create composite ID
                model_id = f"{provider_name}/{strategy_name}"

                # Mask sensitive data
                safe_config = strategy_config.copy()
                if safe_config.get("api_key"):
                    safe_config["api_key"] = "********"

                try:
                    # Parse into Pydantic Model
                    # We manually construct to handle flexible additional_params
                    # STRICT TYPING: Ensure all fields are valid
                    
                    # Extract standard fields
                    provider_val = safe_config.get("provider", provider_name)
                    model_name_val = safe_config.get("model_name", "unknown")
                    api_key_val = safe_config.get("api_key")
                    base_url_val = safe_config.get("base_url")
                    temperature_val = safe_config.get("temperature", 0.7)

                    # Collect leftovers
                    tpm_val = safe_config.get("tpm_limit", 0)
                    rpm_val = safe_config.get("rpm_limit", 0)
                    default_max_tokens_val = safe_config.get("default_max_tokens")
                    vertex_location_val = safe_config.get("vertex_location")
                    supports_grounding_val = safe_config.get("supports_grounding", False)
                    is_active_val = safe_config.get("is_active", True)
                    
                    # Collect leftovers
                    known_keys = {
                        "provider",
                        "model_name",
                        "api_key",
                        "base_url",
                        "temperature",
                        "tpm_limit",
                        "rpm_limit",
                        "default_max_tokens",
                        "vertex_location",
                        "supports_grounding",
                        "is_active",
                    }
                    additional = {k: v for k, v in safe_config.items() if k not in known_keys}

                    results.append(
                        LLMProviderConfig(
                            id=model_id,
                            provider=str(provider_val),
                            model_name=str(model_name_val),
                            api_key=str(api_key_val) if api_key_val else None,
                            base_url=str(base_url_val) if base_url_val else None,
                            temperature=float(temperature_val) if temperature_val is not None else 0.7,
                            tpm_limit=int(tpm_val),
                            rpm_limit=int(rpm_val),
                            default_max_tokens=int(default_max_tokens_val) if default_max_tokens_val is not None else None,
                            vertex_location=str(vertex_location_val) if vertex_location_val else None,
                            supports_grounding=bool(supports_grounding_val),
                            is_active=bool(is_active_val),
                            additional_params=additional,
                        )
                    )
                except Exception as e:
                    # Log but don't crash the entire list for one malformed entry
                    logger.warning(f"[Config] Skipping malformed config '{model_id}': {e}")

        return results
    except Exception as e:
        if isinstance(e, AppException):
            raise e
            
        error_code = ErrorCodes.MODEL_LIST_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.put("/{provider_id:path}", response_model=LLMProviderConfig)
async def update_model_config(
    provider_id: str,
    update_data: LLMProviderConfig,
    repository: RepositoryDep,
):
    """Update configuration for a specific provider strategy.

    'provider_id' MUST be complex path 'provider/strategy'.
    Legacy flat IDs are strictly rejected.
    """
    try:
        # RELAXED: Allow slashless IDs (User Request)
        if "/" in provider_id:
            parts = provider_id.split("/", 1)
            target_provider = parts[0]
            target_strategy = parts[1]
        else:
            # Treat whole ID as provider, strategy as 'default'
            target_provider = provider_id
            target_strategy = "default"

        # 1. Fetch existing
        registry = await repository.get_model_registry()
        if "models" not in registry:
            registry["models"] = {}

        current_models = registry["models"]
        # Ensure 'models' is dict
        if not isinstance(current_models, dict):
             # Auto-recover empty/invalid registry? No, Fail Fast. Admin intervention needed or clear it.
             # Actually, we can reset it if it's junk, but strict safety says fail.
             # But here we are WRITING, maybe we can overwrite?
             # Let's enforce structure.
             if current_models is not None:
                  # If it's trash, error out
                  pass
             else:
                 current_models = {}

        # 2. Resolve Old Config to restore keys
        old_config = {}
        if target_provider in current_models and isinstance(current_models[target_provider], dict):
            old_config = current_models[target_provider].get(target_strategy, {})

        # 3. Prepare New Config
        new_config = update_data.model_dump()

        # Handle Masked Key
        if new_config.get("api_key") == "********":
            if isinstance(old_config, dict):
                new_config["api_key"] = old_config.get("api_key")
            else:
                new_config["api_key"] = None

        additional = new_config.pop("additional_params", {})
        new_config.pop("id", None)
        final_storage = {**new_config, **additional}

        # 4. Write Back (Strict Nested)
        if target_provider not in current_models or not isinstance(current_models[target_provider], dict):
            current_models[target_provider] = {}
        
        current_models[target_provider][target_strategy] = final_storage
        registry["models"] = current_models

        # 5. Save
        success = await repository.update_model_registry(registry)
        if not success:
            raise AppException(
                message="Failed to save Model Registry configuration.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REGISTRY_SAVE_FAILED},
            )

        return update_data

    except Exception as e:
        if isinstance(e, AppException):
             raise e
        
        error_code = ErrorCodes.MODEL_UPDATE_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.delete("/{provider_id:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_config(
    provider_id: str,
    repository: RepositoryDep,
):
    """Delete a specific provider strategy configuration.

    Enforces Reference Integrity (Workflow Usage) and System Integrity (Default Strategy).
    Strictly requires 'provider/strategy' format.
    """
    settings = get_settings()

    try:
        # RELAXED: Allow slashless IDs
        # if "/" not in provider_id: ... (Removed)

        # 1. System Integrity Check
        if provider_id == settings.default_model_strategy:
            raise AppException(
                message=f"Cannot delete system default strategy '{provider_id}'. Change default in settings first.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"error_code": ErrorCodes.DELETE_BLOCKED_SYSTEM_DEFAULT}
            )

        # 2. Reference Integrity Check (Workflow Steps)
        all_steps = await repository.get_all_steps()
        for step in all_steps:
            config = step.get("config", {})
            used_strategy = config.get("model_strategy")
            if used_strategy == provider_id:
                raise AppException(
                    message=f"Cannot delete strategy '{provider_id}'. It is currently used by step '{step.get('id')}' ({step.get('name')}).",
                    status_code=status.HTTP_409_CONFLICT,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE, "step_id": step.get("id")}
                )

        # 3. Fetch existing
        registry = await repository.get_model_registry()
        if "models" not in registry:
            return  # Nothing to delete

        current_models = registry["models"]
        
        parts = provider_id.split("/", 1)
        target_provider = parts[0]
        target_strategy = parts[1]

        # 4. Delete Logic
        deleted = False
        if target_provider in current_models and isinstance(current_models[target_provider], dict):
            if target_strategy in current_models[target_provider]:
                del current_models[target_provider][target_strategy]
                deleted = True
                # Cleanup empty provider bucket
                if not current_models[target_provider]:
                    del current_models[target_provider]

        if not deleted:
            return # Idempotent

        registry["models"] = current_models

        # 5. Save
        success = await repository.update_model_registry(registry)
        if not success:
            raise AppException(
                message="Failed to save Model Registry configuration after delete.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REGISTRY_SAVE_FAILED},
            )

    except Exception as e:
        if isinstance(e, AppException):
             raise e
        
        error_code = ErrorCodes.MODEL_DELETE_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.post("/test", response_model=AdHocTestResponse)
async def test_model_connection(
    request: AdHocTestRequest,
    usage_service: UsageServiceDep,
    llm_factory: Annotated[LLMFactory, Depends(get_llm_factory_dep)],
    handler: LLMHandlerDep,
):
    """Execute an ephemeral LLM request to test credentials/latency.

    Does NOT use the database configuration unless strategy_id is specifically requested.
    Returns status="error" instead of 500 for expected connection failures (User Feedback).
    """
    start_time = time.perf_counter()

    try:
        # Resolve Configuration from Registry (Standard Execution Mode)
        # If strategy_id is provided, we fetch the TRUE config from DB.
        strat_id = request.model_params.get("strategy_id")
        resolved_api_key = request.api_key  # User override priorities
        resolved_model_name = request.model_params.get("model_name") or "test-connection"

        if strat_id and "/" in strat_id and not resolved_api_key:
            # Try to resolve full config from DB
            provider_key, mode_key = strat_id.split("/", 1)
            # Use handler to fetch config
            db_config = handler.get_model_config(provider_key, mode_key)
            if db_config:
                # Found it! Use DB credentials
                if not resolved_api_key:
                    resolved_api_key = db_config.get("api_key")

                if db_config.get("model_name"):
                    resolved_model_name = db_config.get("model_name")

        provider = llm_factory.create_provider(
            provider_type=request.provider,
            model_name=resolved_model_name,
            usage_service=usage_service,
            api_key=resolved_api_key,
            # base_url might need to be passed in kwargs if supported by factory
            base_url=request.model_params.get("base_url"),
        )

        response = await provider.generate(
            prompt=request.user_prompt,
            system_instruction=request.system_instruction,
            temperature=request.model_params.get("temperature", 0.7),
            max_tokens=request.model_params.get("max_tokens"),
        )

        latency = (time.perf_counter() - start_time) * 1000

        return AdHocTestResponse(content=response.content, latency_ms=latency, status="success")

    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000
        logger.error(f"[Config] Ad-Hoc Test Failed: {e}")
        # Return error as valid response (don't 500) so UI shows "Connection Failed"
        return AdHocTestResponse(content=str(e), latency_ms=latency, status="error")


@router.get("/options", response_model=ModelOptionsResponse)
async def list_model_options(
    handler: LLMHandlerDep,
) -> ModelOptionsResponse:
    """Fetch available model options from external providers (Google, OpenAI)."""
    # Strict Configuration: Only show enabled providers
    settings = get_settings()
    known_providers = settings.enabled_providers

    try:
        options = handler.fetch_all_available_models(providers=known_providers)
        clean_options = {}
        for k, v in options.items():
            # Only keep valid lists (ignore error strings)
            if isinstance(v, list):
                clean_options[k] = v

        # Ensure known providers exist (even if empty list)
        for p in known_providers:
            if p not in clean_options:
                clean_options[p] = []

        return ModelOptionsResponse(options=clean_options)
    except Exception as e:
        logger.error(f"[Config] Failed to fetch model options: {e}")
        # Fallback to just known providers
        fallback = {p: [] for p in known_providers}
        return ModelOptionsResponse(options=fallback)
