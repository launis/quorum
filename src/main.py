from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.database.initialization import initialize_database
from src.engine.orchestrator import Orchestrator
import src.components.hooks # Ensure hooks are registered

app = FastAPI(title="Cognitive Quorum v2 API")

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    initialize_database()

class WorkflowRequest(BaseModel):
    workflow_id: str
    initial_inputs: Dict[str, Any]

@app.post("/run_workflow")
async def run_workflow(request: WorkflowRequest):
    orchestrator = Orchestrator()
    try:
        result = orchestrator.run_workflow(request.workflow_id, request.initial_inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
