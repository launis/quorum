from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
import subprocess
import logging
import os
import sys
import json
from pydantic import BaseModel
from tinydb import TinyDB, Query
import uuid

from backend.config import BASE_DIR, SCRIPTS_DIR, INITIAL_MODEL, DB_PATH
from backend.dependencies import get_db_client_dep, get_llm_provider, get_llm_handler_dep
from backend.database.wrapper import AbstractDatabase
from backend.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/admin", tags=["Admin"])

def run_script(script_name: str, args: list = []):
    """
    Helper to run a script from the scripts directory.
    """
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Use the same python interpreter
    cmd = [sys.executable, script_path] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

@router.post("/docs/update")
def update_documentation(background_tasks: BackgroundTasks, ai_enhanced: bool = False, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Triggers the documentation update via AdministrationService.
    """
    return _start_admin_task(background_tasks, db, "update_documentation", ai_enhanced)

@router.post("/import/rules")
def import_rules(background_tasks: BackgroundTasks, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Triggers the rules import via AdministrationService.
    """
    return _start_admin_task(background_tasks, db, "import_rules")

@router.post("/import/references")
def import_references(background_tasks: BackgroundTasks, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Triggers the references import via AdministrationService.
    """
    return _start_admin_task(background_tasks, db, "import_references")

@router.post("/export/seed-data")
def export_seed_data(background_tasks: BackgroundTasks, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Triggers the seed data export via AdministrationService.
    """
    return _start_admin_task(background_tasks, db, "export_seed_data")

@router.post("/database/rebuild")
def rebuild_database(background_tasks: BackgroundTasks, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Triggers database rebuild via AdministrationService.
    """
    return _start_admin_task(background_tasks, db, "rebuild_database")

# --- Helper ---
def _start_admin_task(background_tasks: BackgroundTasks, db: AbstractDatabase, method_name: str, *args):
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Initializing", "percent": 0}
    
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db)
    from backend.services.administration_service import AdministrationService
    from backend.services.progress import InMemoryProgressTracker
    
    service = AdministrationService(repo)
    method = getattr(service, method_name)
    
    def _run_task():
        def tracker_callback(payload):
            admin_task_status[job_id] = payload
            
        tracker = InMemoryProgressTracker(callback=tracker_callback)
        try:
            if args:
                # Some methods might take extra args? update_documentation takes none in logic but maybe toggle?
                # Keeping simple for now, logic didn't show args for service methods yet.
                # update_docs in scripts had args, but service logic I wrote didn't. 
                # I'll update service later if needed.
                res = method(tracker) 
            else:
                res = method(tracker)
            logger.info(f"Admin Task {method_name} result: {res}")
        except Exception as e:
            logger.error(f"Admin Task {method_name} failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(_run_task)
    return {"status": "started", "job_id": job_id, "task": method_name}


@router.post("/self-test")
async def run_self_test(
    db_client: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Runs a quick self-test of the LLM connection and Database.
    Returns a health report.
    """
    report = {
        "llm_status": "unknown",
        "db_status": "unknown",
        "details": {}
    }
    
    # 1. Test LLM
    try:
        response = await llm_provider.generate(
            prompt="Hello, reply with 'OK' if you can hear me.",
            system_instruction="You are a health check bot. Reply briefly."
        )
        if response:
             report["llm_status"] = "ok"
             report["details"]["llm_response"] = str(response)[:100]
        else:
             report["llm_status"] = "empty_response"

    except Exception as e:
        report["llm_status"] = "error"
        report["details"]["llm_error"] = str(e)

    # 2. Test DB
    try:
         count = len(db_client.table('workflows').all())
         report["db_status"] = "ok"
         report["details"]["db_path"] = DB_PATH
         report["details"]["workflow_count"] = count
              
    except Exception as e:
        report["db_status"] = "error"
        report["details"]["db_error"] = str(e)

    return report


# --- centralized task status ---
admin_task_status = {}

@router.get("/status/{job_id}")
def get_task_status(job_id: str):
    """
    Returns progress of any admin task (including ingestion).
    """
    # Check both dicts for backward compatibility or merge them
    # For now, let's use admin_task_status as the master, and make ingestion endpoints write to it.
    status = admin_task_status.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

# Redirect legacy knowledge-base status to generic
@router.get("/knowledge-base/status/{job_id}")
def get_ingestion_status(job_id: str):
    return get_task_status(job_id)

class IngestRequest(BaseModel):
    file_path: str = "data/Holistinen Mestaruus.docx"

@router.post("/knowledge-base/ingest")
def ingest_knowledge_base(
    request: IngestRequest, 
    background_tasks: BackgroundTasks,
    repository: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Initializing", "percent": 0}

    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(repository)
    from backend.services.knowledge_base_service import KnowledgeBaseService
    service = KnowledgeBaseService(repo, llm_provider=llm_provider)
    
    async def _run_ingest():
        try:
            if not os.path.exists(request.file_path):
                admin_task_status[job_id] = {"status": "failed", "error": "File not found"}
                return

            with open(request.file_path, 'rb') as f:
                content = f.read()
            filename = os.path.basename(request.file_path)
            
            from backend.services.progress import InMemoryProgressTracker
            tracker = InMemoryProgressTracker(callback=lambda p: admin_task_status.update({job_id: p}))
            
            await service.ingest_from_bytes(content, filename, tracker=tracker, job_id=job_id)
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(_run_ingest)
    return {"status": "started", "job_id": job_id, "message": f"Ingestion started."}

from fastapi import UploadFile, File

@router.post("/knowledge-base/upload")
async def upload_knowledge_base(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db_client: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Reading Upload", "percent": 0}
    
    content = await file.read()
    filename = file.filename
    
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db_client)
    from backend.services.knowledge_base_service import KnowledgeBaseService
    service = KnowledgeBaseService(repo, llm_provider=llm_provider)
    
    async def _run_ingest():
        try:
            from backend.services.progress import InMemoryProgressTracker
            tracker = InMemoryProgressTracker(callback=lambda p: admin_task_status.update({job_id: p}))
            await service.ingest_from_bytes(content, filename, tracker=tracker, job_id=job_id)
        except Exception as e:
            logger.error(f"Upload ingestion failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    if background_tasks:
        background_tasks.add_task(_run_ingest)
    else:
        await _run_ingest()
        
    return {"status": "started", "job_id": job_id, "filename": filename}

# --- Banned Phrases Management ---

class BannedPhraseRequest(BaseModel):
    phrase: str

@router.get("/banned-phrases")
def get_banned_phrases(db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Get all banned phrases.
    """
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db)
    return repo.get_banned_phrases()

@router.post("/banned-phrases")
def add_banned_phrase(request: BannedPhraseRequest, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Add a new banned phrase.
    """
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db)
    # Validate
    if not request.phrase or len(request.phrase.strip()) < 2:
        raise HTTPException(status_code=400, detail="Phrase too short")
    
    repo.add_banned_phrase(request.phrase.strip())
    return {"status": "added", "phrase": request.phrase}

@router.delete("/banned-phrases/{phrase}")
def delete_banned_phrase(phrase: str, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Delete a banned phrase.
    """
    from backend.dependencies import get_repository_dep
    from urllib.parse import unquote
    repo = get_repository_dep(db)
    
    decoded_phrase = unquote(phrase)
    repo.remove_banned_phrase(decoded_phrase)
    return {"status": "deleted", "phrase": decoded_phrase}
