"""API Router for Administrative Tasks.

This module provides endpoints for system maintenance, database management,
knowledge base ingestion, and banned phrase configuration.
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Annotated, Any, Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import (
    AuthServiceDep,
    CurrentUserDep,
    DatabaseDep,
    LLMProviderDeep,
    LLMProviderFast,
    RepositoryDep,
    get_async_repository,
)
from backend.exceptions import (
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend.models.auth import UserAdminView, UserCreate, UserRole, UserUpdate
from backend.schemas.admin import QueueStats

# --- Local Imports (SSOT Exceptions First) ---
from backend.schemas.error import APIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# --- Request/Response Models ---

class AdminTaskResponse(BaseModel):
    """Standard response for initiating background admin tasks."""
    status: Literal["started", "starting", "failed"]
    job_id: str
    task: str
    message: str | None = None

class TaskStatusResponse(BaseModel):
    """Response model for task progress."""
    status: str
    stage: str | None = None
    percent: int | float = 0
    error: APIError | None = None  # SSOT: Uses standardized Error Schema

class IngestRequest(BaseModel):
    """Request model for knowledge base ingestion."""
    file_path: Annotated[
        str, Field(description="Path to the source document.", examples=["data/Doc.docx"])
    ] = "data/Holistinen Mestaruus.docx"
    reset_db: Annotated[
        bool, Field(description="Clear DB before ingestion.")
    ] = False

class BannedPhraseRequest(BaseModel):
    """Request model for adding a banned phrase."""
    phrase: Annotated[str, Field(min_length=2, description="The phrase to ban.")]

class BannedPhraseResponse(BaseModel):
    """Response model for banned phrase operations."""
    status: str
    phrase: str

class GenericActionResponse(BaseModel):
    """Response model for generic admin actions."""
    status: str
    uid: str | None = None

class GeneratedPhrasesResponse(BaseModel):
    """Response model for generated banned phrases."""
    status: str
    message: str
    added_phrases: list[str]

class GeneratePhrasesRequest(BaseModel):
    """Request model for generating banned phrases using LLM."""
    language: Annotated[str, Field(description="Target language code (e.g., 'en').")] = "en"

class SelfTestResponse(BaseModel):
    """Response model for system self-test."""
    llm_status: str
    db_status: str
    details: dict[str, Any]

class UpdateRoleRequest(BaseModel):
    """Request model for updating a user's role."""
    role: UserRole


# --- State (InMemory) ---
admin_task_status: dict[str, dict[str, Any]] = {}


# --- Dependencies ---

def require_root(user: CurrentUserDep) -> CurrentUserDep:
    """Dependency to enforce ROOT role access."""
    if user.role != UserRole.ROOT:
        # SSOT: Raise Domain Exception. Global handler logs warning & returns 403.
        raise PermissionDeniedError("Root access required")
    return user

def require_admin_or_root(user: CurrentUserDep) -> CurrentUserDep:
    """Dependency to enforce ADMIN or ROOT role access."""
    if user.role not in [UserRole.ROOT, UserRole.ADMIN]:
        raise PermissionDeniedError("Admin or Root access required")
    return user


# --- Helper Functions ---

def _start_admin_task(
    background_tasks: BackgroundTasks,
    repo: AbstractWorkflowRepository,
    method_name: str,
    *args
) -> AdminTaskResponse:
    """Helper to start standard admin tasks in background.

    NOTE: Background tasks require explicit exception handling/logging
    as they run outside the request-response middleware cycle.
    """
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Initializing", "percent": 0}

    # Lazy import to prevent circular dependencies
    from backend.services.administration_service import AdministrationService
    from backend.services.progress import InMemoryProgressTracker

    service = AdministrationService(repo)
    method = getattr(service, method_name)

    async def _run_task():
        def tracker_callback(payload):
            admin_task_status[job_id] = payload

        tracker = InMemoryProgressTracker(callback=tracker_callback)
        try:
            # Handle Async vs Sync methods dynamically
            if asyncio.iscoroutinefunction(method):
                res = await method(tracker, *args) if args else await method(tracker)
            else:
                loop = asyncio.get_running_loop()
                res = (
                    await loop.run_in_executor(None, method, tracker, *args)
                    if args
                    else await loop.run_in_executor(None, method, tracker)
                )

            logger.info(f"Admin Task '{method_name}' [Job: {job_id}] completed: {res}")

            # Ensure completion is marked if not failed
            if admin_task_status[job_id].get("status") != "failed":
                admin_task_status[job_id].update({"status": "completed", "percent": 100})

        except Exception as e:
            # CRITICAL: Log stack trace here because global handler won't see this.
            error_code = "TASK_FAILED"
            logger.error(f"{error_code}: Admin Task '{method_name}' [Job: {job_id}] CRASHED: {e}", exc_info=True)

            # Use SSOT APIError schema for status response
            error_model = APIError(
                error_code=error_code,
                message=str(e),
                details={"task": method_name}
            )
            admin_task_status[job_id] = {"status": "failed", "error": error_model.model_dump()}

    background_tasks.add_task(_run_task)
    return AdminTaskResponse(status="started", job_id=job_id, task=method_name)


# --- Endpoints ---

@router.get(
    "/users/roles",
    summary="Get Assignable Roles",
    response_model=list[UserRole],
    dependencies=[Depends(require_admin_or_root)],
)
async def get_assignable_roles(user: CurrentUserDep):
    """Returns the list of roles the currently authenticated user is allowed to assign."""
    if user.role == UserRole.ROOT:
        return [UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.VIEWER]
    if user.role == UserRole.ADMIN:
        return [UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.VIEWER]
    return []


@router.post(
    "/users",
    summary="Create User",
    response_model=UserAdminView,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_root)],
)
async def create_user(
    request: UserCreate,
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    """Creates a new user under the active organization constraints."""
    try:
        return await auth_service.create_user(creator_uid=user.uid, user_data=request)
    except PermissionError as e:
        # Transform Logic Error -> Domain Exception (403)
        error_code = "PERMISSION_DENIED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code) from e
    except ValueError as e:
        # Transform Logic Error -> Domain Exception (400)
        error_code = "INVALID_USER_DATA"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=error_code) from e
    # Generic Exception? Let it bubble! Global Handler logs 500+Trace.


@router.patch(
    "/users/{user_id}",
    summary="Update User",
    response_model=UserAdminView,
    dependencies=[Depends(require_admin_or_root)],
)
async def update_user(
    user_id: Annotated[str, Path(description="Target User UID")],
    request: UserUpdate,
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    """Updates an existing user profile."""
    try:
        return await auth_service.update_user(initiator_uid=user.uid, target_uid=user_id, updates=request)
    except PermissionError as e:
        error_code = "PERMISSION_DENIED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code) from e
    except ValueError as e:
        # Service maps "not found" to ValueError occasionally; explicit catch preferred
        error_code = "USER_NOT_FOUND"
        logger.error(f"{error_code}: User {user_id} not found: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=error_code) from e
    except RuntimeError as e:
        # Specific Business Logic Check (SSOT Logic)
        if "LAST_ADMIN_PROTECTION" in str(e):
            error_code = "LAST_ADMIN_PROTECTION"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise HTTPException(status_code=409, detail=error_code) from e
        # Unknown Runtime Error -> Bubble
        raise


@router.delete(
    "/users/{user_id}",
    summary="Delete User",
    response_model=GenericActionResponse,
    dependencies=[Depends(require_admin_or_root)],
)
async def delete_user(
    user_id: Annotated[str, Path(description="Target User UID")],
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    """Deletes a user (Enforces Last Admin Protection)."""
    try:
        await auth_service.delete_user(initiator_uid=user.uid, target_uid=user_id)
        return GenericActionResponse(status="deleted", uid=user_id)
    except PermissionError as e:
        error_code = "PERMISSION_DENIED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code) from e
    except ValueError as e:
        if "Last Admin" in str(e):
             error_code = "LAST_ADMIN_PROTECTION"
             logger.error(f"{error_code}: {e}", exc_info=True)
             raise HTTPException(status_code=409, detail=error_code) from e

        error_code = "USER_NOT_FOUND"
        logger.error(f"{error_code}: User {user_id} not found: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=error_code) from e
    except RuntimeError as e:
        if "LAST_ADMIN_PROTECTION" in str(e):
            error_code = "LAST_ADMIN_PROTECTION"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise HTTPException(status_code=409, detail=error_code) from e
        raise


@router.post(
    "/export/seed-data",
    summary="Export Seed Data",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def export_seed_data(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Trigger seed data export task."""
    return _start_admin_task(background_tasks, repo, "export_seed_data")


@router.post(
    "/database/rebuild",
    summary="Rebuild Database",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def rebuild_database(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Trigger database rebuild task."""
    return _start_admin_task(background_tasks, repo, "rebuild_database")


@router.post(
    "/database/reset/mock",
    summary="Reset Mock Database",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def reset_mock_db(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Trigger mock database reset task."""
    return _start_admin_task(background_tasks, repo, "reset_mock_db")


@router.post(
    "/database/reset/prod",
    summary="Reset Production Database",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def reset_prod_db(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Trigger production database reset task."""
    return _start_admin_task(background_tasks, repo, "reset_prod_db")


@router.post(
    "/database/reset/firestore",
    summary="Reset Firestore",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def reset_firestore_db(background_tasks: BackgroundTasks, repo: RepositoryDep):
    """Trigger firestore database reset task."""
    return _start_admin_task(background_tasks, repo, "reset_firestore")


@router.post(
    "/self-test",
    summary="Run System Self-Test",
    response_model=SelfTestResponse,
)
async def run_self_test(db_client: DatabaseDep, llm_provider: LLMProviderFast):
    """Executes a self-test of LLM and Database connectivity."""
    report: dict[str, Any] = {"llm_status": "unknown", "db_status": "unknown", "details": {}}

    # 1. Test LLM (Isolated Try-Except for Resilience)
    try:
        response = await llm_provider.generate("Ping", system_instruction="Reply OK.")
        report["llm_status"] = "ok" if response else "empty_response"
        if response:
            report["details"]["llm_response"] = str(response)[:100]
    except Exception as e:
        # Diagnostic endpoint: report error, don't crash
        report["llm_status"] = "error"
        report["details"]["llm_error"] = str(e)

    # 2. Test DB
    try:
        from backend.settings import get_settings
        settings = get_settings()
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
    response_model=TaskStatusResponse,
)
def get_task_status(job_id: Annotated[str, Path(description="UUID of the background job")]):
    """Retrieves the status of a specific background task."""
    status_data = admin_task_status.get(job_id)
    if not status_data:
        raise ResourceNotFoundError("Job", job_id)
    return status_data


@router.get(
    "/knowledge-base/status/{job_id}",
    summary="Get Ingestion Status (Legacy)",
    deprecated=True,
)
def get_ingestion_status(job_id: Annotated[str, Path(description="UUID of the background job")]):
    """Legacy endpoint redirection."""
    # Legacy wrapper, just delegate
    return get_task_status(job_id)


@router.post(
    "/knowledge-base/ingest",
    summary="Ingest from File (Path)",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def ingest_knowledge_base(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    repo: RepositoryDep,
    llm_provider: LLMProviderFast,
):
    """Triggers ingestion from a local file path."""
    if not os.path.exists(request.file_path):
        raise ResourceNotFoundError("File", request.file_path)

    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Initializing", "percent": 0}

    from backend.services.knowledge_base_service import KnowledgeBaseService
    from backend.services.progress import InMemoryProgressTracker

    service = KnowledgeBaseService(repo, llm_provider=llm_provider)

    async def _run_ingest():
        try:
            with open(request.file_path, "rb") as f:
                content = f.read()
            filename = os.path.basename(request.file_path)

            tracker = InMemoryProgressTracker(callback=lambda p: admin_task_status.update({job_id: p}))
            await service.ingest_from_bytes(
                content, filename, tracker=tracker, job_id=job_id, reset_db=request.reset_db
            )

            # Ensure status is marked completed if service doesn't implicitly do it
            if admin_task_status[job_id].get("status") != "failed":
                 admin_task_status[job_id]["status"] = "completed"

        except Exception as e:
            # Background Task: Must Log
            error_code = "INGESTION_FAILED"
            logger.error(f"{error_code}: Ingestion failed: {e}", exc_info=True)
            error_model = APIError(error_code=error_code, message=str(e))
            admin_task_status[job_id] = {"status": "failed", "error": error_model.model_dump()}

    background_tasks.add_task(_run_ingest)
    return AdminTaskResponse(
        status="started",
        job_id=job_id,
        task="ingest_from_file",
        message=f"Ingesting {request.file_path}",
    )


@router.post(
    "/knowledge-base/upload",
    summary="Upload and Ingest File",
    response_model=AdminTaskResponse,
    dependencies=[Depends(require_root)],
)
async def upload_knowledge_base(
    file: Annotated[UploadFile, File(description="File to ingest.")],
    repo: RepositoryDep,
    llm_provider: LLMProviderFast,
    background_tasks: BackgroundTasks,
    reset_db: Annotated[bool, Query(description="Clear KB first.")] = False,
):
    """Uploads and ingests a file into the knowledge base."""
    job_id = str(uuid.uuid4())
    admin_task_status[job_id] = {"status": "starting", "stage": "Reading Upload", "percent": 0}

    try:
        content = await file.read()
        filename = file.filename or "upload"
    except Exception as e:
        error_code = "UPLOAD_READ_FAILED"
        logger.error(f"{error_code}: Failed to read file: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=error_code) from e

    if repo is None:
        repo = await get_async_repository()

    from backend.services.knowledge_base_service import KnowledgeBaseService
    from backend.services.progress import InMemoryProgressTracker

    service = KnowledgeBaseService(repo, llm_provider=llm_provider)

    async def _run_ingest():
        try:
            tracker = InMemoryProgressTracker(callback=lambda p: admin_task_status.update({job_id: p}))
            await service.ingest_from_bytes(content, filename, tracker=tracker, job_id=job_id, reset_db=reset_db)
            if admin_task_status[job_id].get("status") != "failed":
                 admin_task_status[job_id]["status"] = "completed"
        except Exception as e:
            error_code = "INGESTION_FAILED"
            logger.error(f"{error_code}: Upload ingestion failed: {e}", exc_info=True)
            error_model = APIError(error_code=error_code, message=str(e))
            admin_task_status[job_id] = {"status": "failed", "error": error_model.model_dump()}

    background_tasks.add_task(_run_ingest)
    return AdminTaskResponse(status="started", job_id=job_id, task="upload_ingest", message=f"Ingesting {filename}")


@router.get(
    "/banned-phrases",
    summary="List Banned Phrases",
    response_model=list[dict[str, Any]],
)
async def get_banned_phrases(repo: RepositoryDep):
    """Retrieves all banned phrases from the repository."""
    # Bubble up DB errors
    return await repo.get_banned_phrases()


@router.post(
    "/banned-phrases",
    summary="Add Banned Phrase",
    response_model=BannedPhraseResponse,
)
async def add_banned_phrase(request: BannedPhraseRequest, repo: RepositoryDep):
    """Adds a new phrase to the banned list."""
    if len(request.phrase.strip()) < 2:
         error_code = "PHRASE_VALIDATION_FAILED"
         logger.warning(f"{error_code}: Phrase too short: '{request.phrase}'")
         raise HTTPException(status_code=400, detail=error_code)

    await repo.add_banned_phrase(request.phrase.strip())
    return BannedPhraseResponse(status="added", phrase=request.phrase.strip())


@router.delete(
    "/banned-phrases/{phrase}",
    summary="Remove Banned Phrase",
    response_model=BannedPhraseResponse,
)
async def delete_banned_phrase(
    db: DatabaseDep,
    phrase: Annotated[str, Path(description="Phrase to remove")]
):
    """Removes a phrase from the banned list."""
    # Bubble up DB errors
    from tinydb import Query as TinyQuery
    table = db.table("banned_phrases")
    table.remove(TinyQuery().phrase == phrase)
    return BannedPhraseResponse(status="removed", phrase=phrase)


@router.post(
    "/banned-phrases/generate",
    summary="Generate Banned Phrases",
    response_model=GeneratedPhrasesResponse,
)
async def generate_banned_phrases(
    request: GeneratePhrasesRequest,
    repo: RepositoryDep,
    llm_provider: LLMProviderDeep
):
    """Uses LLM to generate banned phrases."""
    try:
        existing_records = await repo.get_banned_phrases()
        existing = [p["phrase"] for p in existing_records]

        lang_map = {"fi": "Finnish", "en": "English"}
        language_name = lang_map.get(request.language, "English")

        system_prompt = "You are a security expert. Identify adversarial prompts."
        user_prompt = f"Generate 10 NEW banned phrases in {language_name}. Return strictly JSON key 'phrases'."

        response = await llm_provider.generate(user_prompt, system_instruction=system_prompt)
        # Assuming simplified handling
        clean_response = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        candidates = data.get("phrases", [])

        added = []
        for phrase in candidates:
            if phrase not in existing:
                await repo.add_banned_phrase(phrase, language=request.language)
                added.append(phrase)

        return GeneratedPhrasesResponse(
            status="success",
            message=f"Generated {len(candidates)}, Added {len(added)}.",
            added_phrases=added
        )
    except Exception as e:
        # LLM Failure -> Bubble?
        # Typically treated as service unavailable or 500. Bubble.
        # But logging context helps for LLM issues.
        error_code = "PHRASE_GENERATION_FAILED"
        logger.error(f"{error_code}: LLM Phrase generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e


@router.get(
    "/org/{organization_id}/users",
    summary="List Organization Users",
    response_model=list[UserAdminView],
)
async def list_organization_users(
    organization_id: Annotated[str, Path(description="Organization ID")],
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    """Retrieve all users for a specific organization (Admin View)."""
    if user.role != UserRole.ROOT:
        error_code = "AUTH_PERMISSION_DENIED"
        if user.role == UserRole.ADMIN and user.organization_id != organization_id:
            logger.warning(f"{error_code}: Admin {user.uid} attempted to access org {organization_id}")
            raise HTTPException(status_code=403, detail=error_code)
        if user.role not in [UserRole.ROOT, UserRole.ADMIN]:
            logger.warning(f"{error_code}: User {user.uid} with role {user.role} attempted admin access")
            raise HTTPException(status_code=403, detail=error_code)

    return await auth_service.get_users_by_organization(organization_id)


@router.put(
    "/user/{user_id}/role",
    summary="Update User Role",
    response_model=UserAdminView,
)
async def update_user_role(
    user_id: Annotated[str, Path(description="User ID")],
    request: UpdateRoleRequest,
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    """Updates a user's role (Enforces hierarchy)."""
    try:
        return await auth_service.update_user_role(initiator_uid=user.uid, target_uid=user_id, new_role=request.role)
    except (PermissionError, ValueError, RuntimeError) as e:
        msg = str(e)
        if "LAST_ADMIN_PROTECTION" in msg:
             error_code = "LAST_ADMIN_PROTECTION"
             logger.error(f"{error_code}: {e}", exc_info=True)
             raise HTTPException(status_code=409, detail=error_code) from e
        if isinstance(e, ValueError):
            error_code = "USER_NOT_FOUND"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise HTTPException(status_code=404, detail=error_code) from e
        if isinstance(e, PermissionError):
            error_code = "PERMISSION_DENIED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code) from e
        raise


@router.get(
    "/system/queue",
    summary="Get Queue Statistics",
    response_model=QueueStats,
    dependencies=[Depends(require_root)],
)
async def get_queue_stats(request: Request):
    """Retrieves current metrics from the ArQ Redis queue."""
    pool = getattr(request.app.state, "arq_pool", None)
    if not pool:
        return QueueStats(queued_jobs=0, active_jobs=0, dead_jobs=0)

    try:
        queued = await pool.queued_jobs()
        return QueueStats(queued_jobs=len(queued), active_jobs=0, dead_jobs=0)
    except Exception as e:
        # Non-critical, just log warning
        logger.warning(f"Queue stats failed: {e}")
        return QueueStats(queued_jobs=0, active_jobs=0, dead_jobs=0)
