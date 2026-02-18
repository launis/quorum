import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import APIRouter, BackgroundTasks, UploadFile, status

from backend.dependencies import KnowledgeBaseServiceDep
from backend.exceptions import AppException, ErrorCodes
from backend.models.dtos.config import (
    KnowledgeIngestResponse,
    KnowledgeJobStatusResponse,
    KnowledgeResetResponse,
)
from backend.models.dtos.knowledge import KnowledgeStatusResponse

router = APIRouter()

# Global In-Memory Job Store for MVP (Replace with Redis/DB in V3)
ingestion_jobs: dict[str, dict[str, Any]] = {}


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED, response_model=KnowledgeIngestResponse)
async def ingest_knowledge_base(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    service: KnowledgeBaseServiceDep,
    language: str = "auto",
    model_strategy: str | None = None,
) -> KnowledgeIngestResponse:
    """Starts an asynchronous knowledge base ingestion job.

    This endpoint accepts a file upload (DOCX or MD), initiates an asynchronous
    processing task, and returns a job ID for polling status.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager.
        file (UploadFile): The file to ingest (docx, md).
        service (KnowledgeBaseServiceDep): The knowledge base service dependency.
        language (str): Language code of the document (e.g. 'en', 'fi', 'auto').
                      Defaults to "auto".

    Returns:
        KnowledgeIngestResponse: A generic response containing the 'job_id'.

    """
    try:
        job_id = str(uuid.uuid4())

        # Initialize Job State
        ingestion_jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "stage": "Aloitetaan",
            "result": None,
            "error": None
        }

        # Task Wrapper for Progress Tracking
        async def process_task():
            # Adapter to bridge Service callbacks to our Job Store
            class SimpleTracker:
                def start(self, meta):
                    pass

                def update(self, stage, percent):
                    if job_id in ingestion_jobs:
                        ingestion_jobs[job_id].update({"progress": percent, "stage": stage})

                def complete(self, result):
                    if job_id in ingestion_jobs:
                        ingestion_jobs[job_id].update({
                            "status": "completed",
                            "result": result,
                            "progress": 100,
                            "stage": "Valmis"
                        })

                def fail(self, error):
                    # Extract error code if available, otherwise unknown
                    error_code = ErrorCodes.UNKNOWN_ERROR.value
                    if isinstance(error, AppException):
                        error_code = error.error_code

                    if job_id in ingestion_jobs:
                        ingestion_jobs[job_id].update({
                            "status": "failed",
                            "error": str(error),
                            "error_code": error_code,
                            "stage": "Virhe"
                        })

            try:
                content = await file.read()
                # The service expects (content_bytes, filename, tracker, job_id)
                await service.ingest_from_bytes(
                    content,
                    file.filename or "unknown_file",
                    SimpleTracker(),
                    job_id=job_id,
                    language=language,
                    model_strategy=model_strategy
                )
            except Exception as e:
                # Catch-all for safety. Only update if not already reported as failed by the service/tracker.
                error_code = ErrorCodes.KNOWLEDGE_INGESTION_FAILED
                logger.error(f"[KnowledgeIngestion] {error_code.value}: Background task failed: {e}", exc_info=True)

                if job_id in ingestion_jobs and ingestion_jobs[job_id].get("status") != "failed":
                    ingestion_jobs[job_id].update({
                        "status": "failed",
                        "error": str(e),
                        "error_code": error_code.value,
                        "stage": "Järjestelmävirhe"
                    })

        background_tasks.add_task(process_task)
        return KnowledgeIngestResponse(job_id=job_id)

    except Exception as e:
        error_code = ErrorCodes.KNOWLEDGE_INGESTION_FAILED
        logger.error(f"[KnowledgeConfig] {error_code.value}: Failed to initiate ingestion: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to initiate ingestion: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.get("/ingest/{job_id}", status_code=status.HTTP_200_OK, response_model=KnowledgeJobStatusResponse)
async def get_ingestion_status(job_id: str) -> KnowledgeJobStatusResponse:
    """Polls the status of an ingestion job.

    Args:
        job_id (str): The unique identifier of the ingestion job.

    Returns:
        KnowledgeJobStatusResponse: The current state of the job (status, progress, stage, result, error).

    Raises:
        AppException: If the job_id is not found (404 JOB_NOT_FOUND).
    """
    try:
        job = ingestion_jobs.get(job_id)
        if not job:
            raise AppException(
                message=f"Ingestion job '{job_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.JOB_NOT_FOUND}
            )
        # Inject ID for frontend consistency
        return KnowledgeJobStatusResponse(job_id=job_id, **job)
    except Exception as e:
        if isinstance(e, AppException):
             raise e
        
        error_code = ErrorCodes.KNOWLEDGE_INGESTION_FAILED
        logger.error(f"[KnowledgeConfig] {error_code.value}: Failed to get job status: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to get job status: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.delete("/reset", status_code=status.HTTP_200_OK, response_model=KnowledgeResetResponse)
async def reset_knowledge_base(
    service: KnowledgeBaseServiceDep,
) -> KnowledgeResetResponse:
    """Resets the Knowledge Base by deleting all items.

    Args:
        service (KnowledgeBaseServiceDep): The knowledge base service dependency.

    Returns:
        KnowledgeResetResponse: Success message.
    """
    try:
        await service.repository.clear_knowledge_base()
        return KnowledgeResetResponse(message="Knowledge Base reset successfully.")
    except Exception as e:
        error_code = ErrorCodes.KNOWLEDGE_RESET_FAILED
        logger.error(f"[KnowledgeConfig] {error_code.value}: Failed to reset Knowledge Base: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to reset Knowledge Base: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.get("/status", status_code=status.HTTP_200_OK, response_model=KnowledgeStatusResponse)
async def get_knowledge_status(
    service: KnowledgeBaseServiceDep,
) -> KnowledgeStatusResponse:
    """Checks the status of the Knowledge Base.

    Returns:
        KnowledgeStatusResponse: Contains a boolean indicating if documents exist,
                                 and counts of documents and precedents.
    """
    try:
        # 1. Check Precedents (Completed Executions)
        # We access the repository directly via the service
        repo = service.repository
        
        # In V3 (SQL/Vector), use count() query. 
        # For TinyDB, we just check length of all/search.
        all_execs = await repo.get_all_executions()
        precedent_count = len([x for x in all_execs if x.status == "completed"])

        # 2. Check Knowledge Base Documents
        # MVP: Fetch all items and count. 
        # In V3 (Vector DB), replace with count() method.
        kb_items = await repo.get_knowledge_base_items()
        document_count = len(kb_items)
        
        return KnowledgeStatusResponse(
            has_documents=(precedent_count > 0 or document_count > 0),
            document_count=document_count,
            precedent_count=precedent_count
        )

    except Exception as e:
        error_code = ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED
        logger.error(f"[KnowledgeConfig] {error_code.value}: Failed to check status: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to check knowledge status: {e}",
            status_code=500,
            details={"error_code": error_code}
        ) from e
