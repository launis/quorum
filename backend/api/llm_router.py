from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.agents.base import BaseAgent
from backend.registry import DatabaseClient
from backend.core.llm_handler import LLMHandler
from tinydb import Query

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
    def _process(self, **kwargs):
        pass
    def construct_user_prompt(self, **kwargs):
        pass
    async def generate(self, prompt: str, model: str):
        self.model = model
        # Call the provider directly
        return await self.llm_provider.generate(
            prompt=prompt,
            system_instruction="You are a helpful technical writer.",
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
        
        agent = SimpleAgent(model=request.model)
        response_text = await agent.generate(prompt_text, request.model)
        
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
        
        # Upsert the registry
        # We search for type='model_registry'
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
