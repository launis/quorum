from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import backend.hooks as hooks

router = APIRouter(prefix="/hooks", tags=["Hooks"])

@router.post("/sanitize")
async def run_sanitize(inputs: Dict[str, Any]):
    """
    Executes the sanitize_and_anonymize_input hook.
    """
    try:
        return hooks.sanitize_and_anonymize_input(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def run_search(inputs: Dict[str, Any]):
    """
    Executes the execute_google_search hook.
    """
    try:
        return hooks.execute_google_search(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def run_report(inputs: Dict[str, Any]):
    """
    Executes the generate_jinja2_report hook.
    """
    try:
        # The hook expects (inputs, output) but usually modifies output based on inputs.
        # For testing, we can pass inputs as both or handle it specifically.
        # generate_jinja2_report(inputs, output) -> output
        
        # We'll treat the incoming body as 'inputs' and initialize an empty 'output'
        # or allow the user to provide 'output' in the body if needed.
        
        # Let's assume the body IS the inputs (context).
        output = {}
        return hooks.generate_jinja2_report(inputs, output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
