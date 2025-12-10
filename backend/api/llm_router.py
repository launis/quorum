from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from tinydb import Query

from backend.agents.base import BaseAgent
from backend.core.registry import DatabaseClient
from backend.llm.handler import LLMHandler
from backend.llm.provider import LLMFactory

router = APIRouter()
llm_handler = LLMHandler()

class LLMRequest(BaseModel):
    prompts: List[Dict[str, Any]] # {"role": "user", "parts": ["..."]}
    model: str = "gemini-2.5-pro"

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
async def generate_text(request: LLMRequest):
    """
    Generates text using the configured LLM.
    """
    try:
        if not request.prompts or not request.prompts[0].get("parts"):
            raise HTTPException(status_code=400, detail="Invalid prompt format")
            
        prompt_text = request.prompts[0]["parts"][0]
        
        # Use SimpleAgent correctly
        agent = SimpleAgent(model=request.model)
        response_text = await agent.generate_simple(prompt_text)
        
        return {"response": response_text}
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-models")
def get_available_models():
    """
    Lists available models from Google and OpenAI.
    """
    return llm_handler.fetch_all_available_models()

@router.get("/config")
def get_model_config():
    """
    Gets the current model registry configuration.
    """
    return llm_handler.get_active_model_registry()

@router.post("/config")
def update_model_config(update: ModelRegistryUpdate):
    """
    Updates the model registry configuration.
    """
    try:
        db_client = DatabaseClient()
        table = db_client.get_table('system_config')
        
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
