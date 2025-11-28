from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from src.engine.llm_handler import LLMHandler
from pydantic import BaseModel

router = APIRouter()

class LLMRequest(BaseModel):
    prompts: List[Dict[str, Any]]
    model: str = "gemini-1.5-flash"

@router.post("/generate")
async def generate_text(request: LLMRequest):
    """
    Wraps LLMHandler.call_llm.
    """
    try:
        handler = LLMHandler()
        response = handler.call_llm(request.prompts, model=request.model)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
