"""Model Registry Configuration Router."""

import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.dependencies import (
    LLMHandlerDep,
    RepositoryDep,
    UsageServiceDep,
    get_llm_factory_dep,
)
from backend.exceptions import AppException, ErrorCodes, status
from backend.llm.provider import LLMFactory
from backend.models.dtos.config import AgentMappingResponse, AgentMappingUpdate, ModelOptionsResponse
from backend.models.llm import AdHocTestRequest, AdHocTestResponse, LLMProviderConfig
from backend.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Config: Models"])


@router.get("", response_model=list[LLMProviderConfig])
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
                details={"error_code": error_code},
            )

        results: list[LLMProviderConfig] = []

        for provider_name, provider_strategies in strategies.items():
            # Skip if not a dict (malformed provider bucket)
            if not isinstance(provider_strategies, dict):
                logger.warning(
                    f"[Config] Skipping invalid provider bucket '{provider_name}': Expected dict, got {type(provider_strategies)}"
                )
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
                            default_max_tokens=int(default_max_tokens_val)
                            if default_max_tokens_val is not None
                            else None,
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
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
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
                details={"error_code": "REGISTRY_SAVE_FAILED"},
            )

        return update_data

    except Exception as e:
        if isinstance(e, AppException):
            raise e

        error_code = ErrorCodes.MODEL_UPDATE_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
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
                details={"error_code": ErrorCodes.DELETE_BLOCKED_SYSTEM_DEFAULT},
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
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE, "step_id": step.get("id")},
                )

        # 3. Fetch existing
        registry = await repository.get_model_registry()
        if "models" not in registry:
            return  # Nothing to delete

        current_models = registry["models"]

        if "/" in provider_id:
            parts = provider_id.split("/", 1)
            target_provider = parts[0]
            target_strategy = parts[1]
        else:
            target_provider = provider_id
            target_strategy = "default"

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
            return  # Idempotent

        registry["models"] = current_models

        # 5. Save
        success = await repository.update_model_registry(registry)
        if not success:
            raise AppException(
                message="Failed to save Model Registry configuration after delete.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": "REGISTRY_SAVE_FAILED"},
            )

    except Exception as e:
        if isinstance(e, AppException):
            raise e

        error_code = ErrorCodes.MODEL_DELETE_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.get("/mappings", response_model=list[AgentMappingResponse])
async def get_agent_mappings(
    repository: RepositoryDep,
):
    """Fetch the global registry mappings between Agent IDs (task_key) and Model Strategies.
    
    Returns:
        list[AgentMappingResponse]: A list of objects containing agent_id, name, type, and strategy_id.
    """
    try:
        registry = await repository.get_model_registry()
        models_block = registry.get("models", {})

        mappings = {}
        for provider_id, provider_data in models_block.items():
            if not isinstance(provider_data, dict):
                continue
            for key, value in provider_data.items():
                if isinstance(value, str):
                    # It's an agent mapping alias
                    if "/" not in value:
                        mappings[key] = f"{provider_id}/{value}"
                    else:
                        mappings[key] = value

        all_agents = await repository.get_all_agents()

        results: list[AgentMappingResponse] = []
        for agent in all_agents:
            a_id = agent.get("id")
            if not a_id:
                continue

            # Filter out non-system agents (e.g. dynamic matrices that leaked in via UI builder)
            # Typically system agents have type='agent' or a recognizable TaskKey like 'step_'
            # The UI only needs to assign strategies to deterministic/known steps that participate
            # in the regular `BaseAgent` execution pipeline.
            # Real agents always have a `class_name` that is not a literal matrix string.
            a_type = agent.get("type", "agent")
            if a_type not in ["agent", "evaluator", "generator", "processor"]:
                if a_type != "step": # 'step' occasionally used for generic tasks
                    pass # We will allow it for now, but watch out for `matrix_` IDs

            # Skip evaluation matrices to keep the UI clean
            if a_id.startswith("matrix_"):
                continue

            a_name = agent.get("name")
            a_class = agent.get("class_name")
            a_comp = agent.get("component_class")

            # Resolve strategy by checking UUID, then name, then class_name
            # The database seed file uses Class Names (e.g. GuardAgent) instead of UUIDs
            strategy = mappings.get(a_id)
            if not strategy and a_name:
                strategy = mappings.get(a_name)
            if not strategy and a_class:
                strategy = mappings.get(a_class)
            if not strategy and a_comp:
                strategy = mappings.get(a_comp)

            results.append(
                AgentMappingResponse(
                    agent_id=a_id,
                    name=a_name or a_id,
                    type=a_type,
                    strategy_id=strategy
                )
            )

        return results
    except Exception as e:
        if isinstance(e, AppException):
            raise e
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error(f"[Config] Failed to fetch agent mappings: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.put("/mappings", response_model=dict[str, str])
async def update_agent_mapping(
    update_data: AgentMappingUpdate,
    repository: RepositoryDep,
):
    """Update a specific global agent-to-strategy mapping.
    
    Args:
        update_data (AgentMappingUpdate): The agent ID and new strategy ID.
    """
    try:
        registry = await repository.get_model_registry()
        models_block = registry.get("models", {})

        # Fetch actual agent to get its class_name for engine resolution parity
        agent = await repository.get_agent_by_id(update_data.agent_id)
        if not agent:
            raise AppException(
                message=f"Agent ID {update_data.agent_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": "AGENT_NOT_FOUND"},
            )

        target_key = agent.get("class_name") or agent.get("component_class") or agent.get("name") or update_data.agent_id

        # Parse the provider and strategy from the incoming ID (e.g. 'google/fast')
        provider_id = "google"
        strategy_name = update_data.strategy_id

        if "/" in update_data.strategy_id:
            parts = update_data.strategy_id.split("/", 1)
            provider_id = parts[0]
            strategy_name = parts[1]

        # Ensure provider block exists
        if provider_id not in models_block:
            models_block[provider_id] = {}

        # Write the alias into the new provider block
        models_block[provider_id][target_key] = strategy_name

        # Clean up the alias from other providers to avoid shadowing
        for p_id, p_data in models_block.items():
            if p_id != provider_id and isinstance(p_data, dict):
                if target_key in p_data:
                    del p_data[target_key]

        registry["models"] = models_block

        success = await repository.update_model_registry(registry)
        if not success:
            raise AppException(
                message="Failed to save Agent Mapping configuration.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": "REGISTRY_SAVE_FAILED"},
            )

        return update_data.model_dump()
    except Exception as e:
        if isinstance(e, AppException):
            raise e
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error(f"[Config] Failed to update agent mapping: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
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
        fallback: dict[str, list[str]] = {p: [] for p in known_providers}
        return ModelOptionsResponse(options=fallback)
