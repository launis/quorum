from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from backend.llm.client import LLMClient

router = APIRouter(prefix="/playground", tags=["Playground"])

class PlaygroundRequest(BaseModel):
    system_instruction: str
    user_message: str
    variables: Dict[str, str] = {}
    model_params: Dict[str, Any] = {}

@router.post("/run")
async def run_prompt(request: PlaygroundRequest) -> str:
    """Executes a prompt template with variables against the LLM."""
    
    # 1. Inject Variables
    try:
        system_content = request.system_instruction.format(**request.variables)
    except KeyError as e:
        # Simple format uses {var}. If var missing, raises KeyError.
        return f"Error: Missing variable {e}"
    except ValueError as e:
        return f"Error: Formatting failed: {e}"

    # 2. Initialize Client
    client = LLMClient() 
    
    # 3. Construct Messages
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": request.user_message},
    ]

    # 4. Execute
    try:
        response = await client.run_chat(
            messages=messages,
            # Pass explicit params if provided in request, otherwise defaults
            **request.model_params
        )
        return response
    except Exception as e:
        return f"Error executing prompt: {e}"
