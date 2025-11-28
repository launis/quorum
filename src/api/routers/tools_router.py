from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from pydantic import BaseModel

# Import hooks directly for now, but in a real microservice these might be separate
from src.components.hooks.search import execute_google_search
from src.components.hooks.sanitization import sanitize_and_anonymize_input

router = APIRouter()

class SearchRequest(BaseModel):
    data: Dict[str, Any] # Contains 'lopputuote', 'reflektiodokumentti' etc.
    hypothesis_argument: str = ""
    prompt_text: str = ""

@router.post("/search")
async def search_tool(request: SearchRequest):
    """
    Exposes execute_google_search hook.
    """
    try:
        # Convert Pydantic model to dict expected by hook
        input_data = request.dict()
        result = execute_google_search(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SanitizeRequest(BaseModel):
    data: Dict[str, Any]

@router.post("/sanitize")
async def sanitize_tool(request: SanitizeRequest):
    """
    Exposes sanitize_and_anonymize_input hook.
    """
    try:
        input_data = request.data
        # Hook modifies in-place usually, but returns dict of changes
        # sanitize_and_anonymize_input(data) -> returns dict with 'data' key containing sanitized content
        # Let's check the hook signature. It returns Dict[str, Any].
        result = sanitize_and_anonymize_input(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
