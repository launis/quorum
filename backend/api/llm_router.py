from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Annotated
from tinydb import Query

from backend.agents.base import BaseAgent
from backend.llm.provider import LLMFactory
from backend.database.wrapper import AbstractDatabase, get_db_client
from backend.dependencies import get_llm_handler_dep, get_db_client_dep, get_llm_factory_dep, get_agent_registry_dep
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])

# --- Models ---

class LLMRequest(BaseModel):
    prompts: Annotated[List[Dict[str, Any]], Field(
        description="A list of conversation turn objects (e.g., [{'role': 'user', 'parts': ['Hello']}])"
    )]
    strategy: Annotated[str, Field(
        default="fast",
        description="The strategy identifier (e.g. 'fast', 'deep') to resolve from the Model Registry."
    )]

class ModelRegistryUpdate(BaseModel):
    registry: Annotated[Dict[str, Dict[str, str]], Field(
        description="The new configuration map for model strategies (e.g. {'fast': {'model_name': '...'}})."
    )]

# --- Endpoints ---

@router.post(
    "/generate", 
    summary="Generate Text",
    response_description="The generated text response."
)
async def generate_text(
    request: LLMRequest, 
    # We need the registry to resolve the strategy dynamically based on the request body
    registry = Depends(get_agent_registry_dep)
):
    """
    Generates text using the configured LLM provider based on the prompts.
    Resolves the model via the 'strategy' field in the request.

    Args:
        request (LLMRequest): The prompt and strategy configuration.
        registry (AgentRegistry): Dependency for model resolution.

    Returns:
        dict: The generated text inside a wrapper object.

    Raises:
        HTTPException: If the prompt is invalid or generation fails.
    """
    try:
        if not request.prompts or not request.prompts[0].get("parts"):
            raise HTTPException(status_code=400, detail="Invalid prompt format")
            
        prompt_text = request.prompts[0]["parts"][0]
        
        # 1. Resolve Configuration from DB using Request Strategy
        # This enforces that only valid, database-configured strategies can be used.
        config = await registry.resolve_model_config(request.strategy)
        
        # 2. Create Provider using the resolved config
        provider = LLMFactory.create_provider(
            provider_type=config['provider'], 
            model_name=config['model_name']
        )
        
        response_text = await provider.generate(
            prompt=prompt_text,
            system_instruction="You are a helpful technical writer.",
            response_schema=None
        )
        
        return {"response": response_text}
    except Exception as e:
        logger.error(f"LLM Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/available-models", 
    summary="List External Models",
    response_description="A list of model identifiers available from the providers."
)
def get_available_models(llm_handler = Depends(get_llm_handler_dep)):
    """
    Fetches the list of available models from external APIs (e.g., Google Gemini, OpenAI).

    Args:
        llm_handler: Dependency for LLM management.

    Returns:
        List[str]: A list of model names.
    """
    return llm_handler.fetch_all_available_models()

@router.get(
    "/config", 
    summary="Get Model Registry",
    response_description="The current internal model mapping configuration."
)
def get_model_config(llm_handler = Depends(get_llm_handler_dep)):
    """
    Retrieves the active model registry, which maps abstract strategies (e.g., 'fast') to concrete models.

    Args:
        llm_handler: Dependency.

    Returns:
        dict: The registry configuration object.
    """
    return llm_handler.get_active_model_registry()

@router.post(
    "/config", 
    summary="Update Model Registry",
    response_description="Confirmation of the configuration update."
)
def update_model_config(
    update: ModelRegistryUpdate, 
    db_client: AbstractDatabase = Depends(get_db_client_dep)
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
