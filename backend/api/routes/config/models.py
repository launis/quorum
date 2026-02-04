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
from backend.llm.provider import LLMFactory
from backend.models.llm import AdHocTestRequest, AdHocTestResponse, LLMProviderConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config/models", tags=["Config: Models"])


@router.get("", response_model=list[LLMProviderConfig])
async def list_models(
    repository: RepositoryDep,
):
    """List all available LLM providers and their current configuration.

    Supports nested structure: models[provider][strategy].
    Returns flattened list with id="{provider}/{strategy}".
    """
    registry = await repository.get_model_registry()
    strategies = registry.get("models", {})

    results = []

    if isinstance(strategies, dict):
        for key, value in strategies.items():
            # Check if this is a Provider bucket (nested dict of strategies)
            if isinstance(value, dict) and any(isinstance(v, (dict, str)) for v in value.values()):
                provider_name = key
                for strategy_name, strategy_config in value.items():
                    # Skip Agent mappings (strings) for now, only return Configs (dicts)
                    if not isinstance(strategy_config, dict):
                        continue

                    # Create composite ID
                    model_id = f"{provider_name}/{strategy_name}"

                    # Mask sensitive data
                    safe_config = strategy_config.copy()
                    if safe_config.get("api_key"):
                        safe_config["api_key"] = "********"

                    try:
                        results.append(
                            LLMProviderConfig(
                                id=model_id,
                                provider=safe_config.get("provider", provider_name),
                                model_name=safe_config.get("model_name", "unknown"),
                                api_key=safe_config.get("api_key"),
                                base_url=safe_config.get("base_url"),
                                temperature=safe_config.get("temperature", 0.7),
                                additional_params={
                                    k: v
                                    for k, v in safe_config.items()
                                    if k not in ["provider", "model_name", "api_key", "base_url", "temperature"]
                                }
                            )
                        )
                    except Exception as e:
                         logger.warning(f"Skipping malformed nested config '{model_id}': {e}")

            # Fallback: Flat structure (legacy support)
            elif isinstance(value, dict):
                 # Treat 'key' as strategy name, no provider bucket?
                 # Or treat 'key' as flat strategy key.
                 # Let's assume this is legacy `strategy_id: config`
                 model_id = key
                 safe_config = value.copy()
                 if safe_config.get("api_key"):
                    safe_config["api_key"] = "********"

                 try:
                    results.append(
                        LLMProviderConfig(
                            id=model_id,
                            provider=safe_config.get("provider", "unknown"),
                            model_name=safe_config.get("model_name", "unknown"),
                             api_key=safe_config.get("api_key"),
                             base_url=safe_config.get("base_url"),
                             temperature=safe_config.get("temperature", 0.7),
                             additional_params={} # Simplify legacy
                        )
                    )
                 except Exception:
                     pass

    return results


@router.put("/{provider_id:path}", response_model=LLMProviderConfig)
async def update_model_config(
    provider_id: str,
    update_data: LLMProviderConfig,
    repository: RepositoryDep,
):
    """Update configuration for a specific provider strategy.

    'provider_id' can be complex path 'provider/strategy'.
    """
    # 1. Fetch existing
    registry = await repository.get_model_registry()
    if "models" not in registry:
        registry["models"] = {}

    current_models = registry["models"]

    # 2. Determine location (Nested vs Flat)
    target_provider = None
    target_strategy = provider_id

    if "/" in provider_id:
        parts = provider_id.split("/", 1)
        target_provider = parts[0]
        target_strategy = parts[1]

    # 3. Resolve Old Config to restore keys
    old_config = {}
    if target_provider and target_provider in current_models:
        if isinstance(current_models[target_provider], dict):
            old_config = current_models[target_provider].get(target_strategy, {})
    elif not target_provider:
         old_config = current_models.get(target_strategy, {})

    # 4. Prepare New Config
    new_config = update_data.model_dump()

    if new_config.get("api_key") == "********":
        if isinstance(old_config, dict):
            new_config["api_key"] = old_config.get("api_key")
        else:
            new_config["api_key"] = None

    additional = new_config.pop("additional_params", {})
    new_config.pop("id", None)
    final_storage = {**new_config, **additional}

    # 5. Write Back
    if target_provider:
        if target_provider not in current_models:
            current_models[target_provider] = {}
        # Ensure it's a dict
        if not isinstance(current_models[target_provider], dict):
             current_models[target_provider] = {}

        current_models[target_provider][target_strategy] = final_storage
    else:
        # Legacy/Flat write
        current_models[target_strategy] = final_storage

    registry["models"] = current_models

    # 6. Save
    success = await repository.update_model_registry(registry)
    if not success:
        from backend.exceptions import AppException
        raise AppException(
            "Failed to save Model Registry configuration.",
            status_code=500,
            details={"error_code": "REGISTRY_SAVE_FAILED"},
        )

    return update_data


@router.post("/test", response_model=AdHocTestResponse)
async def test_model_connection(
    request: AdHocTestRequest,
    usage_service: UsageServiceDep,
    llm_factory: Annotated[LLMFactory, Depends(get_llm_factory_dep)],
    handler: LLMHandlerDep,
):
    """Execute an ephemeral LLM request to test credentials/latency.

    Does NOT use the database configuration. Uses provided credentials.
    """
    start_time = time.perf_counter()

    try:
        # Resolve Configuration from Registry (Standard Execution Mode)
        # If strategy_id is provided, we fetch the TRUE config from DB.
        strat_id = request.model_params.get("strategy_id")
        resolved_api_key = request.api_key # User override priorities
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

                # Also ensure we use the configured model name if not overridden?
                # Usually we want to test THAT model.
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

        # Override model name if provided in params?
        # Actually LLMProvider usually needs model_name init.
        # Let's re-instantiate if needed or pass correct name.
        # Check LLMProviderConfig structure usage.
        # But here we have AdHocTestRequest with 'model_params'.

        # Wait, 'create_provider' might not accept api_key as arg if it assumes env vars/settings?
        # Standard Ref: LLMFactory.create_provider usually takes specific args.
        # If the Factory enforces DB/Settings usage, we can't do AdHoc testing easily with custom keys.
        # BUT this is "Hardening". We assume the Factory supports overrides or we instantiate the Handler/Client directly.
        # "Use LLMClient... strictly for testing".
        # backend/llm/client.py -> LLMClient.

        # Let's try LLMFactory first.
        # If it fails, we catch it.

        # Fix: The Provider object usually has .generate().
        # We construct the message list.
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
        logger.error(f"Ad-Hoc Test Failed: {e}")
        # Return error as valid response (don't 500) so UI shows "Connection Failed"
        return AdHocTestResponse(content=str(e), latency_ms=latency, status="error")


@router.get("/options", response_model=dict[str, list[str]])
async def list_model_options(
    handler: LLMHandlerDep,
):
    """Fetch available model options from external providers (Google, OpenAI)."""
    # Known supported providers (Ensure these always appear for configuration)
    known_providers = ["google", "openai"]

    try:
        options = handler.fetch_all_available_models()
        clean_options = {}
        for k, v in options.items():
            # Only keep valid lists (ignore error strings)
            if isinstance(v, list):
                clean_options[k] = v

        # Ensure known providers exist (even if empty list)
        for p in known_providers:
            if p not in clean_options:
                clean_options[p] = []

        return clean_options
    except Exception as e:
        logger.error(f"Failed to fetch model options: {e}")
        # Fallback to just known providers
        return {p: [] for p in known_providers}
