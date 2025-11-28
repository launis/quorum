from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import List, Dict, Any
import uuid
import shutil
import os
from src.engine.orchestrator import Orchestrator
from src.api.routers.db_router import get_db

router = APIRouter()

# Helper for background execution
def run_workflow_background(job_id: str, file_paths: Dict[str, str], workflow_id: str):
    """
    Background task to run the workflow.
    Updates job status in DB.
    """
    db = get_db()
    try:
        # Update status to RUNNING
        db.upsert_document("jobs", job_id, {"status": "RUNNING"})
        
        # Parse files (Simplified: Read text)
        # In a real app, use PyMuPDF etc. here or inside Orchestrator
        # For now, let's assume Orchestrator can handle paths or we read them here.
        # The current Orchestrator expects a dictionary of strings (text content).
        
        inputs = {}
        for key, path in file_paths.items():
            try:
                # Determine file type by extension
                ext = os.path.splitext(path)[1].lower()
                
                if ext == ".pdf":
                    import fitz  # PyMuPDF
                    text = ""
                    with fitz.open(path) as doc:
                        for page in doc:
                            text += page.get_text()
                    inputs[key] = text
                else:
                    # Default to text reading
                    with open(path, "r", encoding="utf-8") as f:
                        inputs[key] = f.read()
                        
            except Exception as e:
                print(f"Error parsing file {path}: {e}")
                inputs[key] = f"[Error parsing file: {os.path.basename(path)} - {str(e)}]"

        # Run Orchestrator
        orchestrator = Orchestrator()
        # We might need to inject the DB client or configure it to use API?
        # For now, Orchestrator uses local DB client. 
        # Ideally, Orchestrator should use the same DB abstraction.
        
        result = orchestrator.run_workflow(workflow_id, inputs)
        
        # Update status to COMPLETED
        db.upsert_document("jobs", job_id, {
            "status": "COMPLETED",
            "result": result
        })
        
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        db.upsert_document("jobs", job_id, {
            "status": "FAILED",
            "error": str(e)
        })
    finally:
        # Cleanup temp files
        for path in file_paths.values():
            if os.path.exists(path):
                os.remove(path)

@router.post("/run")
async def run_workflow(
    background_tasks: BackgroundTasks,
    workflow_id: str,
    history_file: UploadFile = File(...),
    product_file: UploadFile = File(...),
    reflection_file: UploadFile = File(...)
):
    """
    Starts a workflow execution job.
    Accepts 3 files. Returns job_id.
    """
    job_id = str(uuid.uuid4())
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded files temporarily
    file_paths = {}
    files = {
        "history_text": history_file,
        "product_text": product_file,
        "reflection_text": reflection_file
    }
    
    for key, file in files.items():
        file_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths[key] = file_path

    # Create Job Record
    db = get_db()
    # Use upsert or add. If using Firestore, we can set ID.
    db.upsert_document("jobs", job_id, {
        "id": job_id,
        "status": "PENDING",
        "workflow_id": workflow_id,
        "created_at": str(uuid.uuid1()) # Timestamp proxy
    })

    # Trigger Background Task
    background_tasks.add_task(run_workflow_background, job_id, file_paths, workflow_id)

    return {"job_id": job_id, "status": "PENDING"}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    db = get_db()
    doc = db.get_document("jobs", job_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": doc.get("status"),
        "result": doc.get("result"),
        "error": doc.get("error")
    }
