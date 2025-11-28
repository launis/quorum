from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from src.database.firestore_client import FirestoreClient
from src.database.tinydb_adapter import TinyDBAdapter
import os

router = APIRouter()

def get_db():
    # Factory logic: Use Firestore if configured, else TinyDB (via Adapter)
    if os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("ENV") == "CLOUD":
        return FirestoreClient()
    else:
        # Fallback to TinyDB for local dev
        print("[DB] Using TinyDB Adapter (Local Mode)")
        return TinyDBAdapter() 

@router.get("/components/{component_id}")
async def get_component(component_id: str):
    db = get_db()
    doc = db.get_document("components", component_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Component not found")
    return doc

@router.get("/workflows")
async def list_workflows():
    db = get_db()
    # Assuming 'workflows' collection exists
    return db.get_all("workflows")

@router.post("/logs")
async def add_log(log_entry: Dict[str, Any]):
    db = get_db()
    doc_id = db.add_document("logs", log_entry)
    return {"id": doc_id, "status": "logged"}

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    db = get_db()
    doc = db.get_document("jobs", job_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return doc
