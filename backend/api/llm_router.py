from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Annotated
from tinydb import Query
import logging
import asyncio

from backend.dependencies import RegistryDep, LLMHandlerDep, DatabaseDep, get_db_client_dep
from backend.llm.provider import LLMFactory
# from backend.llm.handler import LLMHandler # LLMHandlerDep already provides access to LLMHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])

# --- Models ---

class CompletionRequest(BaseModel):
    prompt: Annotated[str, Field(description="The primary prompt text.")]
    system_instruction: Annotated[Optional[str], Field(description="Optional system instruction.")] = None
    model_strategy: Annotated[str, Field(description="Strategy key (fast, deep, etc) or direct model name.")] = "fast"
    response_schema: Annotated[Optional[Dict[str, Any]], Field(description="Optional JSON Schema for structured output.")] = None

class BatchCompletionRequest(BaseModel):
    requests: Annotated[List[CompletionRequest], Field(description="List of requests to process in parallel.")]

class ModelRegistryUpdate(BaseModel):
    registry: Annotated[Dict[str, Dict[str, str]], Field(
        description="The new configuration map for model strategies (e.g. {'fast': {'model_name': '...'}})."
    )]

# --- Endpoints ---

@router.post(
    "/completion", 
    summary="Direct Completion",
    response_description="The generated text or structured object."
)
async def generate_completion(
    request: CompletionRequest,
    registry: RegistryDep
):
    """
    Directly invokes the LLM using the specified strategy.
    Supports structured output if schema is provided.
    """
    try:
        # 1. Resolve Provider via Registry
        config = await registry.resolve_model_config(request.model_strategy)
        provider = LLMFactory.create_provider(config['provider'], config['model_name'])
        
        # 2. Call Generate
        # If response_schema is present, model_strategy must support JSON mode or structured generation
        response = await provider.generate(
            prompt=request.prompt,
            system_instruction=request.system_instruction,
            response_schema=request.response_schema
        )
        
        return {"result": response}

    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Completion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/batch-completion", 
    summary="Batch Completion",
    response_description="List of results."
)
async def batch_completion(
    batch: BatchCompletionRequest,
    registry: RegistryDep
):
    """
    Processes multiple completion requests in parallel.
    """
    async def _process_one(req: CompletionRequest):
        try:
            config = await registry.resolve_model_config(req.model_strategy)
            provider = LLMFactory.create_provider(config['provider'], config['model_name'])
            return await provider.generate(
                prompt=req.prompt,
                system_instruction=req.system_instruction,
                response_schema=req.response_schema
            )
        except Exception as e:
            return {"error": str(e)}

    results = await asyncio.gather(*[_process_one(r) for r in batch.requests])
    return {"results": results}


@router.get(
    "/providers", 
    summary="List Providers",
    response_description="Active providers configuration."
)
async def list_providers(handler: LLMHandlerDep):
    """
    Returns information about active LLM providers and availability.
    """
    # LLMHandler manages the high level interface, but factory has the config.
    # We can inspect the factory via the handler if exposed, or just return static info about supported types.
    # Currently handler doesn't expose much metadata.
    # Let's return the strategies configured in settings via common method
    from backend.settings import get_settings
    settings = get_settings()
    
    return {
        "strategies": settings.model_strategies,
        "api_keys_set": {
            "google": bool(settings.google_api_key),
            "openai": bool(settings.openai_api_key)
        }
    }

@router.get(
    "/config", 
    summary="Get Model Registry",
    response_description="The current internal model mapping configuration."
)
def get_model_config(handler: LLMHandlerDep):
    """
    Retrieves the active model registry, which maps abstract strategies (e.g., 'fast') to concrete models.

    Args:
        handler: Dependency.

    Returns:
        dict: The registry configuration object.
    """
    return handler.get_active_model_registry()

@router.post(
    "/config", 
    summary="Update Model Registry",
    response_description="Confirmation of the configuration update."
)
def update_model_config(
    update: ModelRegistryUpdate, 
    db_client: DatabaseDep
):
    """
    Updates the system's model registry configuration in the database.

    Args:
        update (ModelRegistryUpdate): The new configuration.
        db_client (AbstractDatabase): Database dependency.

    Returns:
        dict: Status and the updated registry.
    """
    try:
        table = db_client.table('system_config')
        
        Config = Query()
        table.upsert(
            {
                'type': 'model_registry',
                'models': update.registry
            },
            Config.type == 'model_registry'
        )
        return {"status": "success", "registry": update.registry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
