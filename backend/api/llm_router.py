from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from tinydb import Query

from backend.agents.base import BaseAgent
from backend.llm.provider import LLMFactory
from backend.database.wrapper import AbstractDatabase, get_db_client
from backend.dependencies import get_llm_handler_dep, get_db_client_dep, get_llm_factory_dep
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class LLMRequest(BaseModel):
    prompts: List[Dict[str, Any]] # {"role": "user", "parts": ["..."]}
    model: Optional[str] = None

class ModelRegistryUpdate(BaseModel):
    registry: Dict[str, Dict[str, str]]

class SimpleAgent(BaseAgent):
    """
    A simple agent wrapper to access the BaseAgent's LLM calling capabilities.
    """
    def construct_user_prompt(self, state):
        return ""
        
    def _update_state(self, state, response):
        return state

    async def generate_simple(self, prompt: str, system_instruction: str = "You are a helpful technical writer."):
        """
        Direct generation helper.
        """
        return await self.llm_provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=None
        )

@router.post("/generate")
async def generate_text(request: LLMRequest, factory = Depends(get_llm_factory_dep)):
    """
    Generates text using the configured LLM.
    """
    try:
        if not request.prompts or not request.prompts[0].get("parts"):
            raise HTTPException(status_code=400, detail="Invalid prompt format")
            
        prompt_text = request.prompts[0]["parts"][0]
        
        # Use Factory from dependency
        provider = factory.create_provider(model_name=request.model)
        
        response_text = await provider.generate(
            prompt=prompt_text,
            system_instruction="You are a helpful technical writer.",
            response_schema=None
        )
        
        return {"response": response_text}
    except Exception as e:
        logger.error(f"LLM Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-models")
def get_available_models(llm_handler = Depends(get_llm_handler_dep)):
    """
    Lists available models from Google and OpenAI.
    """
    return llm_handler.fetch_all_available_models()

@router.get("/config")
def get_model_config(llm_handler = Depends(get_llm_handler_dep)):
    """
    Gets the current model registry configuration.
    """
    return llm_handler.get_active_model_registry()

@router.post("/config")
def update_model_config(update: ModelRegistryUpdate, db_client: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Updates the model registry configuration.
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
