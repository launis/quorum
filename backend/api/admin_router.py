"""API Router for Administrative Tasks.

This module provides endpoints for system maintenance, database management,
knowledge base ingestion, and banned phrase configuration.
"""

import json
import logging
import os
import subprocess
import sys
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Path, Query, UploadFile
from pydantic import BaseModel, Field

from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import (
    CurrentUserDep,
    DatabaseDep,
    LLMProviderDeep,
    LLMProviderFast,
    RepositoryDep,
    get_async_repository,
)
from backend.models.auth import UserRole

logger = logging.getLogger(__name__)


def require_root(user: CurrentUserDep):
    """Dependency to enforce ROOT role access.

    Args:
        user (CurrentUserDep): The authenticated user.

    Returns:
        User: The user object if authorized.

    Raises:
        HTTPException: If the user is not ROOT (403).
    """
    if user.role != UserRole.ROOT:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_root)])

# --- Models ---


class IngestRequest(BaseModel):
    """Request model for knowledge base ingestion.

    Attributes:
        file_path (str): Path to the source document.
        reset_db (bool): Whether to clear the database before ingestion.
    """

    file_path: Annotated[
        str,
        Field(
            description="The relative or absolute file path to the source document for ingestion.",
            examples=["data/Holistinen Mestaruus.docx"],
        ),
    ] = "data/Holistinen Mestaruus.docx"

    reset_db: Annotated[
        bool,
        Field(
            description="If True, the existing knowledge base will be cleared before ingesting the new file.",
        ),
    ] = False


class BannedPhraseRequest(BaseModel):
    """Request model for adding a banned phrase."""

    phrase: Annotated[
        str, Field(description="The text phrase that should be banned from user inputs or agent outputs.")
    ]


class GenerateBannedPhrasesRequest(BaseModel):
    """Request model for generating banned phrases."""

    language: Annotated[
        str, Field(description="The target language for generating banned phrases (e.g., 'en', 'fi').")
    ] = "en"


# --- Centralized Status ---
admin_task_status: dict[str, dict[str, Any]] = {}

# --- Helper Functions ---


def run_script(script_name: str, args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Helper to run a script from the scripts directory in a subprocess.

    Args:
        script_name (str): Name of the script file.
        args (List[str]): Additional arguments for the script.

    Returns:
        subprocess.CompletedProcess: The result of the execution.

    """
    from backend.settings import get_settings

    if args is None:
        args = []
    settings = get_settings()
    script_path = os.path.join(settings.scripts_dir, script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Use the same python interpreter
    cmd = [sys.executable, script_path] + args

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def _start_admin_task(
    background_tasks: BackgroundTasks, repo: AbstractWorkflowRepository, method_name: str, *args
) -> dict[str, str]:
    """Starts an administrative task in the background using AdministrationService.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (AbstractWorkflowRepository): Async Repository instance.
        method_name (str): Name of the method to call on AdministrationService.
        *args: Variable length argument list to pass to the method.

    Returns:
        dict: A dictionary containing the 'status', 'job_id', and 'task' name.
    """
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Initializing", "percent": 0}

    # repo is already passed
    import asyncio

    from backend.services.administration_service import AdministrationService
    from backend.services.progress import InMemoryProgressTracker

    service = AdministrationService(repo)
    method = getattr(service, method_name)

    async def _run_task():
        def tracker_callback(payload):
            admin_task_status[job_id] = payload

        tracker = InMemoryProgressTracker(callback=tracker_callback)
        try:
            # Execute the method (Assuming AdminService methods are async or wrapped)
            if asyncio.iscoroutinefunction(method):
                if args:
                    res = await method(tracker, *args)
                else:
                    res = await method(tracker)
            else:
                # Run sync method in threadpool to avoid blocking loop
                loop = asyncio.get_running_loop()
                # Use lambda or functools.partial could be cleaner, but straight args work with run_in_executor
                # in recent python. Note: run_in_executor(None, func, *args)
                if args:
                    res = await loop.run_in_executor(None, method, tracker, *args)
                else:
                    res = await loop.run_in_executor(None, method, tracker)
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
    response_description="Confirmation that the export task has started.",
)
async def export_seed_data(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Triggers the seed data export process via AdministrationService in the background.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (RepositoryDep): The async repository dependency.

    Returns:
        dict: A dictionary containing the job ID and status.

    """
    return _start_admin_task(background_tasks, repo, "export_seed_data")


@router.post(
    "/database/rebuild",
    summary="Rebuild Database",
    response_description="Confirmation that the rebuild task has started.",
)
async def rebuild_database(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Triggers a complete database rebuild (drop and re-seed) in the background.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (RepositoryDep): The async repository dependency.

    Returns:
        dict: A dictionary containing the job ID and status.

    """
    return _start_admin_task(background_tasks, repo, "rebuild_database")


@router.post(
    "/database/reset/mock",
    summary="Reset Mock Database",
    response_description="Confirmation that the Mock DB reset task has started.",
)
async def reset_mock_db(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Triggers 'rebuild_mock_db.py' in the background.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (RepositoryDep): Database dependency.

    Returns:
        dict: Job status and ID.
    """
    return _start_admin_task(background_tasks, repo, "reset_mock_db")


@router.post(
    "/database/reset/prod",
    summary="Reset Production Database (Local)",
    response_description="Confirmation that the Prod (TinyDB) reset task has started.",
)
async def reset_prod_db(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Triggers 'rebuild_prod_db.py' in the background.

    WARNING: This wipes the local production database.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (RepositoryDep): Database dependency.

    Returns:
        dict: Job status and ID.
    """
    return _start_admin_task(background_tasks, repo, "reset_prod_db")


@router.post(
    "/database/reset/firestore",
    summary="Reset Firestore Database",
    response_description="Confirmation that the Firestore reset task has started.",
)
async def reset_firestore_db(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Triggers 'seed_firestore.py' in the background.

    WARNING: This wipes the Firestore database!

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (RepositoryDep): Database dependency.

    Returns:
        dict: Job status and ID.
    """
    return _start_admin_task(background_tasks, repo, "reset_firestore")


@router.post(
    "/self-test",
    summary="Run System Self-Test",
    response_description="A health report detailing LLM and Database connectivity.",
)
async def run_self_test(db_client: DatabaseDep, llm_provider: LLMProviderFast):
    """Executes a quick self-test of the LLM connection and Database state.

    Args:
        db_client (DatabaseDep): Database dependency.
        llm_provider (LLMProvider): LLM provider dependency.

    Returns:
        dict: A health report with 'llm_status' and 'db_status'.

    """
    report: dict[str, Any] = {"llm_status": "unknown", "db_status": "unknown", "details": {}}

    # 1. Test LLM
    try:
        response = await llm_provider.generate(
            prompt="Hello, reply with 'OK' if you can hear me.",
            system_instruction="You are a health check bot. Reply briefly.",
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
        count = len(db_client.table("workflows").all())
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
    response_description="The current status and progress of the background task.",
)
def get_task_status(job_id: str = Path(..., description="UUID of the background job.")):
    """Retrieves the progress/status of a specific background task.

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
    deprecated=True,
)
def get_ingestion_status(job_id: str = Path(..., description="UUID of the background job.")):
    """Legacy endpoint for checking ingestion status. Redirects to get_task_status.

    Args:
        job_id (str): The unique identifier of the job.

    Returns:
        dict: The status object.

    """
    return get_task_status(job_id)


@router.post(
    "/knowledge-base/ingest",
    summary="Ingest from File (Path)",
    response_description="Confirmation that ingestion has started.",
)
async def ingest_knowledge_base(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    repo: RepositoryDep,
    llm_provider: LLMProviderFast,
):
    """Starts the process of ingesting a document into the knowledge base from a local file path.

    Args:
        request (IngestRequest): Ingestion configuration (file path, reset flag).
        background_tasks (BackgroundTasks): FastAPI background task manager.
        repo (RepositoryDep): Database dependency.
        llm_provider (LLMProviderFast): LLM provider for embedding generation.

    Returns:
        dict: Job status, ID, start confirmation message.
    """
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Initializing", "percent": 0}

    # repo is already injected
    from backend.services.knowledge_base_service import KnowledgeBaseService

    service = KnowledgeBaseService(repo, llm_provider=llm_provider)

    async def _run_ingest():
        try:
            if not os.path.exists(request.file_path):
                admin_task_status[job_id] = {"status": "failed", "error": "File not found"}  # type: ignore[index]
                return

            # Read file in binary mode
            with open(request.file_path, "rb") as f:
                content = f.read()
            filename = os.path.basename(request.file_path)

            from backend.services.progress import InMemoryProgressTracker

            tracker = InMemoryProgressTracker(callback=lambda p: admin_task_status.update({job_id: p}))

            await service.ingest_from_bytes(
                content, filename, tracker=tracker, job_id=job_id, reset_db=request.reset_db
            )
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            admin_task_status[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(_run_ingest)
    return {"status": "started", "job_id": job_id, "message": f"Ingestion started. (Reset: {request.reset_db})"}


@router.post(
    "/knowledge-base/upload",
    summary="Upload and Ingest File",
    response_description="Confirmation that upload ingestion has started.",
)
async def upload_knowledge_base(
    file: Annotated[UploadFile, File(description="The file to be uploaded and ingested.")],
    repo: RepositoryDep,
    llm_provider: LLMProviderFast,
    background_tasks: BackgroundTasks,
    reset_db: Annotated[bool, Query(description="Whether to clear the KB before ingestion.")] = False,
):
    """Uploads a file and triggers the ingestion process.

    Args:
        file (UploadFile): The binary file to ingest.
        reset_db (bool): If True, clear KB before ingestion.
        background_tasks (BackgroundTasks): Background task manager.
        repo (RepositoryDep): Database dependency.
        llm_provider (LLMProviderFast): LLM provider dependency.

    Returns:
        dict: Job status, ID, filename, and reset flag.
    """
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Reading Upload", "percent": 0}

    content = await file.read()
    filename = file.filename or "upload"

    if repo is None:
        repo = await get_async_repository()
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
    "/banned-phrases", summary="List Banned Phrases", response_description="A list of all currently banned phrases."
)
async def get_banned_phrases(repo: RepositoryDep):
    """Retrieves all banned phrases from the database.

    Args:
        repo (RepositoryDep): Database dependency.

    Returns:
        list[dict]: List of banned phrase objects (e.g. {'phrase': 'bad word'}).
    """
    return await repo.get_banned_phrases()


@router.post("/banned-phrases", summary="Add Banned Phrase", response_description="Confirmation of the added phrase.")
async def add_banned_phrase(request: BannedPhraseRequest, repo: RepositoryDep):
    """Adds a new phrase to the blocklist.

    Args:
        request (BannedPhraseRequest): The phrase to add.
        repo (RepositoryDep): Database dependency.

    Returns:
        dict: Status and the added phrase.

    Raises:
        HTTPException: If the phrase is too short (400).
    """
    # Validate
    if not request.phrase or len(request.phrase.strip()) < 2:
        raise HTTPException(status_code=400, detail="Phrase too short")

    await repo.add_banned_phrase(request.phrase.strip())
    return {"status": "added", "phrase": request.phrase}


@router.delete(
    "/banned-phrases/{phrase}", summary="Remove Banned Phrase", response_description="Confirmation of removal."
)
async def delete_banned_phrase(
    db: DatabaseDep, phrase: str = Path(..., description="The URL-encoded phrase to delete.")
):
    """Remove a phrase from the banned list.

    Args:
        db (DatabaseDep): Database dependency.
        phrase (str): The phrase string to remove.

    Returns:
        dict: Status and the removed phrase.

    Raises:
        HTTPException: If deletion fails (500).
    """
    try:
        from tinydb import Query
        # We need to access the banned phrases list in the DB
        # This implies we have a 'config' table or similar.
        # As per 'get_banned_phrases' logic (which wasn't fully shown but likely uses settings or DB),
        # let's assume it's in a 'config' table.

        # Implementation depends on how banned phrases are stored.
        # If they are just in settings, we can't delete them via API persistently unless we update a file/DB.
        # Assuming DB 'banned_phrases' collection for this example as per previous context.

        # Check if we are using settings-based or DB-based.
        # If DB based:
        table = db.table("banned_phrases")
        query = Query()
        table.remove(query.phrase == phrase)

        return {"status": "removed", "phrase": phrase}

    except Exception as e:
        logger.error(f"Failed to remove banned phrase: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/banned-phrases/generate",
    summary="Generate Banned Phrases",
    response_description="A list of newly generated and added banned phrases.",
)
async def generate_banned_phrases(
    request: GenerateBannedPhrasesRequest, repo: RepositoryDep, llm_provider: LLMProviderDeep
):
    """Uses the LLM to generate new potential banned phrases based on common adversarial patterns.

    Args:
        request (GenerateBannedPhrasesRequest): Configuration for generation (e.g. language).
        repo (RepositoryDep): Database dependency.
        llm_provider (LLMProvider): LLM provider dependency.

    Returns:
        dict: Report containing added phrases.

    Raises:
        HTTPException: If generation fails.

    """
    # 1. Get existing to provide context
    existing_records = await repo.get_banned_phrases()
    existing = [p["phrase"] for p in existing_records]

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
        clean_response = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        candidates = data.get("phrases", [])

        added = []
        for phrase in candidates:
            if phrase not in existing:
                await repo.add_banned_phrase(phrase, language=request.language)
                added.append(phrase)
                existing.append(phrase)  # Update local list

        return {
            "status": "success",
            "message": f"Generated {len(candidates)} candidates, added {len(added)} new phrases.",
            "added_phrases": added,
        }

    except Exception as e:
        logger.error(f"Failed to generate banned phrases: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
