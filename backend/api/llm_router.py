from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.agents.base import BaseAgent

router = APIRouter()

class LLMRequest(BaseModel):
    prompts: List[Dict[str, Any]] # {"role": "user", "parts": ["..."]}
    model: str = "gemini-2.5-pro"

class SimpleAgent(BaseAgent):
    """
    A simple agent wrapper to access the BaseAgent's LLM calling capabilities.
    """
    def _process(self, **kwargs):
        pass
    def construct_user_prompt(self, **kwargs):
        pass
    def generate(self, prompt: str, model: str):
        self.model = model
        return self._call_llm(prompt)

@router.post("/generate")
async def generate_text(request: LLMRequest):
    """
    Generates text using the configured LLM.
    Expects a simplified prompt structure compatible with the frontend/scripts.
    """
    try:
        # Extract text from the first prompt part
        # The script sends: "prompts": [{"role": "user", "parts": [prompt_text]}]
        if not request.prompts or not request.prompts[0].get("parts"):
            raise HTTPException(status_code=400, detail="Invalid prompt format")
            
        prompt_text = request.prompts[0]["parts"][0]
        
        agent = SimpleAgent(model=request.model)
        response_text = agent.generate(prompt_text, request.model)
        
        return {"response": response_text}
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
def get_available_models():
    """
    Lists available Google AI models.
    """
    import google.generativeai as genai
    import os
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"models": ["gpt-4o", "gemini-1.5-pro", "local-model"]} # Fallback
        
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Clean up model name (remove 'models/' prefix)
                name = m.name.replace("models/", "")
                models.append(name)
        
        # Add some common aliases or non-Google models if needed
        if "gpt-4o" not in models: models.append("gpt-4o")
        
        return {"models": sorted(models)}
    except Exception as e:
        print(f"Error listing models: {e}")
        return {"models": ["gpt-4o", "gemini-1.5-pro", "local-model"]} # Fallback
