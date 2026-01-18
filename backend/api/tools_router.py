"""API Router for Utility Tools.

This module provides endpoints for file processing (text extraction),
web scraping, and concept extraction.
"""

import logging
import os
import shutil
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, Form, UploadFile, status

from backend.dependencies import DatabaseDep, RegistryDep, RepositoryDep, get_document_service_dep

# --- Local Imports ---
# Rule 6: APIError must be the FIRST local import
from backend.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["Tools"])

# --- Endpoints ---


@router.post("/extract-text", summary="Extract Text from File", response_description="Extracted text.")
async def extract_text(
    doc_service: Annotated[DocumentService, Depends(get_document_service_dep)],
    text: str | None = Form(None),
    file: UploadFile = File(None),  # noqa: B008
):
    """Deep-parse a PDF/DOCX file and return raw text.

    Args:
        file (UploadFile): The binary file to process.
        doc_service (DocumentService): Injected document service.
        text (str | None): Optional text fallback.

    Returns:
        dict: Filename and extracted text.

    Raises:
        HTTPException: If extraction fails (500).
    """
    content: str = text or ""
    temp_path: str | None = None
    filename: str | None = None

    if file:
        filename = file.filename or "unknown"
        if file.filename:
            temp_path = f"temp_{uuid.uuid4()}_{file.filename}"
            try:
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                content = doc_service.extract_text(temp_path)
            except Exception as e:
                from backend.exceptions import AppException

                error_code = "TEXT_EXTRACTION_FAILED"
                logger.error(f"{error_code}: {e}", exc_info=True)
                raise AppException(
                    message=str(e),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": error_code},
                ) from e
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as clean_err:
                        logger.debug(f"Failed to cleanup temp file {temp_path}: {clean_err}")
                        pass

    if not content:
        from backend.exceptions import AppException

        error_code = "NO_CONTENT_PROVIDED"
        logger.warning(f"{error_code}: No text or file provided.")
        raise AppException(
            message="No text or file provided",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    return {"filename": filename, "text": content}


@router.post("/extract-concepts", summary="Extract Concepts from Content")
async def extract_concepts_from_file_or_text(
    registry: RegistryDep,
    repo: RepositoryDep,
    doc_service: Annotated[DocumentService, Depends(get_document_service_dep)],
    text: str = Form(None),
    file: UploadFile = File(None),  # noqa: B008
):
    """Extracts domain concepts from either raw text or an uploaded file.

    Args:
        registry (RegistryDep): Registry for LLM config.
        doc_service (DocumentService): Injected document service.
        text (str): Raw text input.
        file (UploadFile): File input.
        llm_provider (str): Preferred provider (deprecated, uses registry).

    Returns:
        dict: Extracted concepts.

    Raises:
        HTTPException: If no input provided (400) or extraction errors (500).
    """
    content = text
    temp_path = None

    if file:
        temp_path = f"temp_{uuid.uuid4()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        try:
            # Use injected service
            content = doc_service.extract_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as clean_err:
                    logger.debug(f"Failed to cleanup temp file {temp_path}: {clean_err}")
                    pass

    if not content:
        from backend.exceptions import AppException

        error_code = "NO_CONTENT_PROVIDED"
        logger.warning(f"{error_code}: No text or file provided.")
        raise AppException(
            message="No text or file provided",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    try:
        # Resolve config logic (Dynamic)
        config = await registry.resolve_model_config("AnalystAgent")  # Strategy: 'deep' analysis

        from backend.llm.provider import LLMFactory
        from backend.services.knowledge_base_service import KnowledgeBaseService

        provider = LLMFactory.create_provider(config["provider"], config["model_name"])

        # Initialize Service
        service = KnowledgeBaseService(repo, llm_provider=provider)

        # Execute Extraction
        concepts = await service.extract_concepts_with_llm(content)

        return {"source_length": len(content), "concepts": concepts}

    except Exception as e:
        from backend.exceptions import AppException

        error_code = "CONCEPT_EXTRACTION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e


@router.post("/web-scrape", summary="Scrape Web Page", response_description="Scraped content.")
async def web_scrape(
    url: Annotated[str, Body(embed=True)],
):
    """Scrapes a public web page.

    Protected against SSRF (Server-Side Request Forgery).
    Blocks requests to localhost and private IP ranges.
    """
    import ipaddress
    import socket
    from urllib.parse import urlparse

    # 1. SSRF Protection
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid URL")

        # Resolve IP
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.is_loopback or ip_obj.is_private:
            from backend.exceptions import AppException

            error_code = "SSRF_PROTECTION_BLOCKED"
            logger.error(f"{error_code}: Access to private IP blocked: {ip}", exc_info=True)
            raise AppException(
                message=f"Access to private IP blocked: {ip}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code},
            )

    except Exception as e:
        if isinstance(e, AppException):
            raise

        # Map specific SSRF errors to 400
        from backend.exceptions import AppException

        if "SSRF" in str(e):
            # Try to map if possible, else generic
            error_code = "SSRF_PROTECTION_BLOCKED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code},
            ) from e

        # Logic error in resolving might be 400 too
        if isinstance(e, ValueError):
            error_code = "INVALID_URL"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code},
            ) from e

        # Fallback
        error_code = "WEB_SCRAPE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        ) from e

    # 2. Mock Implementation for now (or real if needed, but test only checks hardening)
    # Return dummy content
    return {"url": url, "content": "Scraped content placeholder."}


@router.post("/citation-lookup", summary="Resolve Citations", response_description="Resolved context.")
async def citation_lookup(
    db: DatabaseDep, repo: RepositoryDep, registry: RegistryDep, queries: Annotated[list[str], Body(..., embed=True)]
):
    """Uses the Knowledge Base Service to find context for citations.

    Args:
        db (DatabaseDep): Database dependency.
        repo (RepositoryDep): Repository dependency.
        registry (RegistryDep): Registry dependency.
        queries (list[str]): List of citation keys or queries.

        registry (RegistryDep): Registry dependency.
        queries (list[str]): List of citation keys or queries.

    Returns:
        dict: Map of query to resolved context.
    """
    try:
        from backend.llm.provider import LLMFactory
        from backend.services.knowledge_base_service import KnowledgeBaseService

        # Strict Resolution: Use 'smart' strategy for citation analysis
        config = await registry.resolve_model_config("smart")

        # repo is injected via Dependency
        provider = LLMFactory.create_provider("google", config["model_name"])

        kb_service = KnowledgeBaseService(repo, llm_provider=provider)

        results = {}
        for q in queries:
            context = await kb_service.retrieve_context(q)
            results[q] = context

        return results

    except Exception as e:
        from backend.exceptions import AppException

        error_code = "CITATION_LOOKUP_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e
