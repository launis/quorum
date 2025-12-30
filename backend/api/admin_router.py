from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, UploadFile, File, Query, Path
import subprocess
import logging
import os
import sys
import json
import uuid
from typing import Dict, Any, List, Annotated

from pydantic import BaseModel, Field
from backend.dependencies import get_db_client_dep, get_llm_provider
from backend.database.wrapper import AbstractDatabase
from backend.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/admin", tags=["Admin"])

# --- Models ---

class IngestRequest(BaseModel):
    file_path: Annotated[str, Field(
        description="The relative or absolute file path to the source document for ingestion."
    )] = "data/Holistinen Mestaruus.docx"
    
    reset_db: Annotated[bool, Field(
        description="If True, the existing knowledge base will be cleared before ingesting the new file."
    )] = False

class BannedPhraseRequest(BaseModel):
    phrase: Annotated[str, Field(
        description="The text phrase that should be banned from user inputs or agent outputs."
    )]

class GenerateBannedPhrasesRequest(BaseModel):
    language: Annotated[str, Field(
        description="The target language for generating banned phrases (e.g., 'en', 'fi')."
    )] = "en"

# --- Centralized Status ---
admin_task_status: Dict[str, Dict[str, Any]] = {}

# --- Helper Functions ---

def run_script(script_name: str, args: List[str] = []) -> subprocess.CompletedProcess:
    """
    Helper to run a script from the scripts directory in a subprocess.

    Args:
        script_name (str): Name of the script file.
        args (List[str]): Additional arguments for the script.

    Returns:
        subprocess.CompletedProcess: The result of the execution.
    """
    from backend.settings import get_settings
    settings = get_settings()
    script_path = os.path.join(settings.scripts_dir, script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Use the same python interpreter
    cmd = [sys.executable, script_path] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def _start_admin_task(background_tasks: BackgroundTasks, db: AbstractDatabase, method_name: str, *args) -> Dict[str, str]:
    """
    Starts an administrative task in the background using AdministrationService.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task handler.
        db (AbstractDatabase): Database connection.
        method_name (str): The method name to call on AdministrationService.
        *args: Additional arguments for the method.

    Returns:
        Dict[str, str]: A dictionary containing the 'job_id' and 'status'.
    """
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
            # Execute the method
            if args:
                 res = method(tracker, *args) 
            else:
                res = method(tracker)
            logger.info(f"Admin Task {method_name} result: {res}")
        except Exception as e:
            logger.error(f"Admin Task {method_name} failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(_run_task)
    return {"status": "started", "job_id": job_id, "task": method_name}


# --- Endpoints ---

@router.post(
    "/export/seed-data",
    summary="Export Seed Data",
    response_description="Confirmation that the export task has started."
)
def export_seed_data(
    background_tasks: BackgroundTasks, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Triggers the seed data export process via AdministrationService in the background.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        db (AbstractDatabase): The database connection dependency.

    Returns:
        dict: A dictionary containing the job ID and status.
    """
    return _start_admin_task(background_tasks, db, "export_seed_data")

@router.post(
    "/database/rebuild",
    summary="Rebuild Database",
    response_description="Confirmation that the rebuild task has started."
)
def rebuild_database(
    background_tasks: BackgroundTasks, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Triggers a complete database rebuild (drop and re-seed) in the background.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        db (AbstractDatabase): The database connection dependency.

    Returns:
        dict: A dictionary containing the job ID and status.
    """
    return _start_admin_task(background_tasks, db, "rebuild_database")


@router.post(
    "/database/reset/mock",
    summary="Reset Mock Database",
    response_description="Confirmation that the Mock DB reset task has started."
)
def reset_mock_db(
    background_tasks: BackgroundTasks, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Triggers 'rebuild_mock_db.py' in the background.
    """
    return _start_admin_task(background_tasks, db, "reset_mock_db")


@router.post(
    "/database/reset/prod",
    summary="Reset Production Database (Local)",
    response_description="Confirmation that the Prod (TinyDB) reset task has started."
)
def reset_prod_db(
    background_tasks: BackgroundTasks, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Triggers 'rebuild_prod_db.py' in the background.
    WARNING: This wipes the local production database.
    """
    return _start_admin_task(background_tasks, db, "reset_prod_db")


@router.post(
    "/database/reset/firestore",
    summary="Reset Firestore Database",
    response_description="Confirmation that the Firestore reset task has started."
)
def reset_firestore_db(
    background_tasks: BackgroundTasks, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Triggers 'seed_firestore.py' in the background.
    WARNING: This wipes the Firestore database!
    """
    return _start_admin_task(background_tasks, db, "reset_firestore")


@router.post(
    "/self-test",
    summary="Run System Self-Test",
    response_description="A health report detailing LLM and Database connectivity."
)
async def run_self_test(
    db_client: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Executes a quick self-test of the LLM connection and Database state.

    Args:
        db_client (AbstractDatabase): Database dependency.
        llm_provider (LLMProvider): LLM provider dependency.

    Returns:
        dict: A health report with 'llm_status' and 'db_status'.
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
         from backend.settings import get_settings
         settings = get_settings()
         # Assuming 'workflows' table exists
         count = len(db_client.table('workflows').all())
         report["db_status"] = "ok"
         report["details"]["db_path"] = settings.start_db_path
         report["details"]["workflow_count"] = count
              
    except Exception as e:
        report["db_status"] = "error"
        report["details"]["db_error"] = str(e)

    return report


@router.get(
    "/status/{job_id}",
    summary="Get Task Status",
    response_description="The current status and progress of the background task."
)
def get_task_status(job_id: str = Path(..., description="UUID of the background job.")):
    """
    Retrieves the progress/status of a specific background task.

    Args:
        job_id (str): The unique identifier of the job.

    Returns:
        dict: The status object (e.g., {'status': 'running', 'percent': 50}).

    Raises:
        HTTPException: If the job ID is not found.
    """
    status = admin_task_status.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


@router.get(
    "/knowledge-base/status/{job_id}",
    summary="Get Ingestion Status (Legacy)",
    response_description="The current status of the ingestion task.",
    deprecated=True
)
def get_ingestion_status(job_id: str = Path(..., description="UUID of the background job.")):
    """
    Legacy endpoint for checking ingestion status. Redirects to get_task_status.

    Args:
        job_id (str): The unique identifier of the job.

    Returns:
        dict: The status object.
    """
    return get_task_status(job_id)


@router.post(
    "/knowledge-base/ingest",
    summary="Ingest from File (Path)",
    response_description="Confirmation that ingestion has started."
)
def ingest_knowledge_base(
    request: IngestRequest, 
    background_tasks: BackgroundTasks,
    repository: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Starts the process of ingesting a document into the knowledge base from a local file path.

    Args:
        request (IngestRequest): The ingestion configuration.
        background_tasks (BackgroundTasks): Background task handler.
        repository (AbstractDatabase): Database dependency.
        llm_provider (LLMProvider): LLM provider dependency.

    Returns:
        dict: Job ID and status message.
    """
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
            
            # Read file in binary mode
            with open(request.file_path, 'rb') as f:
                content = f.read()
            filename = os.path.basename(request.file_path)
            
            from backend.services.progress import InMemoryProgressTracker
            tracker = InMemoryProgressTracker(callback=lambda p: admin_task_status.update({job_id: p}))
            
            await service.ingest_from_bytes(content, filename, tracker=tracker, job_id=job_id, reset_db=request.reset_db)
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(_run_ingest)
    return {"status": "started", "job_id": job_id, "message": f"Ingestion started. (Reset: {request.reset_db})"}


@router.post(
    "/knowledge-base/upload",
    summary="Upload and Ingest File",
    response_description="Confirmation that upload ingestion has started."
)
async def upload_knowledge_base(
    file: UploadFile = File(..., description="The file to be uploaded and ingested."),
    reset_db: bool = Query(False, description="Whether to clear the KB before ingestion."),
    background_tasks: BackgroundTasks = None,
    db_client: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Uploads a file and triggers the ingestion process.

    Args:
        file (UploadFile): The binary file to upload.
        reset_db (bool): If True, resets the database.
        background_tasks (BackgroundTasks): Background handler (optional).
        db_client (AbstractDatabase): Database dependency.
        llm_provider (LLMProvider): LLM provider dependency.

    Returns:
        dict: Job ID and file details.
    """
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
            await service.ingest_from_bytes(content, filename, tracker=tracker, job_id=job_id, reset_db=reset_db)
        except Exception as e:
            logger.error(f"Upload ingestion failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    if background_tasks:
        background_tasks.add_task(_run_ingest)
    else:
        # If no background tasks context (e.g. testing), await directly
        await _run_ingest()
        
    return {"status": "started", "job_id": job_id, "filename": filename, "reset_db": reset_db}


@router.get(
    "/banned-phrases",
    summary="List Banned Phrases",
    response_description="A list of all currently banned phrases."
)
def get_banned_phrases(db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Retrieves all banned phrases from the database.

    Args:
        db (AbstractDatabase): Database dependency.

    Returns:
        List[Dict]: A list of banned phrase objects.
    """
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db)
    return repo.get_banned_phrases()


@router.post(
    "/banned-phrases",
    summary="Add Banned Phrase",
    response_description="Confirmation of the added phrase."
)
def add_banned_phrase(
    request: BannedPhraseRequest, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Adds a new phrase to the blocklist.

    Args:
        request (BannedPhraseRequest): The phrase data.
        db (AbstractDatabase): Database dependency.

    Returns:
        dict: Status and the added phrase.

    Raises:
        HTTPException: If the phrase is too short.
    """
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db)
    # Validate
    if not request.phrase or len(request.phrase.strip()) < 2:
        raise HTTPException(status_code=400, detail="Phrase too short")
    
    repo.add_banned_phrase(request.phrase.strip())
    return {"status": "added", "phrase": request.phrase}


@router.delete(
    "/banned-phrases/{phrase}",
    summary="Delete Banned Phrase",
    response_description="Confirmation of deletion."
)
def delete_banned_phrase(
    phrase: str = Path(..., description="The URL-encoded phrase to delete."),
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Removes a phrase from the blocklist.

    Args:
        phrase (str): The phrase to remove (URL encoded).
        db (AbstractDatabase): Database dependency.

    Returns:
        dict: Status and the deleted phrase.
    """
    from backend.dependencies import get_repository_dep
    from urllib.parse import unquote
    repo = get_repository_dep(db)
    
    decoded_phrase = unquote(phrase)
    repo.remove_banned_phrase(decoded_phrase)
    return {"status": "deleted", "phrase": decoded_phrase}


@router.post(
    "/banned-phrases/generate",
    summary="Generate Banned Phrases",
    response_description="A list of newly generated and added banned phrases."
)
async def generate_banned_phrases(
    request: GenerateBannedPhrasesRequest,
    db: AbstractDatabase = Depends(get_db_client_dep),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Uses the LLM to generate new potential banned phrases based on common adversarial patterns.

    Args:
        request (GenerateBannedPhrasesRequest): Configuration for generation (e.g. language).
        db (AbstractDatabase): Database dependency.
        llm_provider (LLMProvider): LLM provider dependency.

    Returns:
        dict: Report containing added phrases.

    Raises:
        HTTPException: If generation fails.
    """
    from backend.dependencies import get_repository_dep
    repo = get_repository_dep(db)
    
    # 1. Get existing to provide context
    existing = [p['phrase'] for p in repo.get_banned_phrases()]
    
    # 2. Prompt LLM
    lang_map = {"fi": "Finnish", "en": "English"}
    language_name = lang_map.get(request.language, "English")
    
    system_prompt = (
        "You are a security expert for AI systems. "
        "Your task is to identify common adversarial prompts, jailbreak attempts, "
        "and phrases used to bypass safety filters."
    )
    
    user_prompt = (
        f"Generate 10 NEW unique banned phrases in {language_name}. "
        "Focus on common jailbreak patterns (e.g. 'ignore previous instructions', 'roleplay as', 'DAN mode') "
        "and potentially harmful requests. \n"
        "Return strictly a JSON object with a single key 'phrases' containing a list of strings. \n"
        f"Do NOT include these existing phrases: {json.dumps(existing[:20])}..." 
    )
    
    try:
        response = await llm_provider.generate(user_prompt, system_instruction=system_prompt)
        
        # 3. Parse Response
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        candidates = data.get("phrases", [])
        
        added = []
        for phrase in candidates:
            if phrase not in existing:
                repo.add_banned_phrase(phrase, language=request.language)
                added.append(phrase)
                existing.append(phrase) # Update local list
                
        return {
            "status": "success", 
            "message": f"Generated {len(candidates)} candidates, added {len(added)} new phrases.",
            "added_phrases": added
        }
        
    except Exception as e:
        logger.error(f"Failed to generate banned phrases: {e}")
        raise HTTPException(status_code=500, detail=str(e))
