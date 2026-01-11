"""API Router for Utility Tools.

This module provides endpoints for file processing (text extraction),
web scraping, and concept extraction.
"""

import logging
import os
import shutil
import uuid
from typing import Annotated

import requests as req_lib
from bs4 import BeautifulSoup
from fastapi import APIRouter, Body, File, HTTPException, UploadFile

from backend.dependencies import DatabaseDep, RegistryDep
from backend.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["Tools"])

# --- Endpoints ---


@router.post("/text-extract", summary="Extract Text from File", response_description="The extracted raw text.")
async def extract_text_from_file(file: Annotated[UploadFile, File(...)]):
    """Extracts text content from an uploaded file (PDF, Docx, etc).

    Args:
        file (UploadFile): The binary file to process.

    Returns:
        dict: Filename and extracted text.

    Raises:
        HTTPException: If extraction fails (500).
    """
    temp_path = f"temp_{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc_service = DocumentService()
        # Ensure extract_text is async or run in threadpool if sync?
        # DocumentService.extract_text is likely sync.
        text = doc_service.extract_text(temp_path)
        return {"filename": file.filename, "text": text}

    except Exception as e:
        logger.error(f"Text extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@router.post(
    "/concept-extraction",
    summary="Extract Concepts (Text/File)",
    response_description="List of extracted concepts and relationships.",
)
async def extract_concepts_from_file_or_text(
    registry: RegistryDep,
    text: Annotated[str | None, Body()] = None,
    file: Annotated[UploadFile | None, File()] = None,
    llm_provider: Annotated[str | None, Body()] = "google",
):
    """Extracts domain concepts from either raw text or an uploaded file.

    Args:
        registry (RegistryDep): Registry for LLM config.
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
            doc_service = DocumentService()
            content = doc_service.extract_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    if not content:
        raise HTTPException(status_code=400, detail="No text or file provided.")

    try:
        # Resolve config logic
        config = await registry.resolve_model_config("deep")

        from backend.llm.provider import LLMFactory
        from backend.services.knowledge_base_service import KnowledgeBaseService

        # Using KnowledgeBaseService for extraction as it likely has the logic 'extract_concepts_with_llm'
        # Check previous usage: 'service.extract_concepts_with_llm(final_text, tracker)'

        provider = LLMFactory.create_provider(config["provider"], config["model_name"])

        kb_service = KnowledgeBaseService(repository=None, llm_provider=provider)

        # We need a dummy tracker?
        from backend.services.progress import InMemoryProgressTracker

        tracker = InMemoryProgressTracker()

        concepts = await kb_service.extract_concepts_with_llm(content, tracker)

        return {"source_length": len(content), "concepts": concepts}

    except Exception as e:
        logger.error(f"Concept extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/web-scrape", summary="Scrape URL", response_description="Extracted text and metadata.")
async def scrape_url(url: Annotated[str, Body(..., embed=True)]):
    """Fetches and parses a public URL.

    Args:
        url (str): The URL to scrape.

    Returns:
        dict: Title, content, and metadata.

    Raises:
        HTTPException: If connection fails (400).
    """
    try:
        # SSRF Protection
        _validate_url_safety(url)

        headers = {"User-Agent": "Mozilla/5.0"}
        response = req_lib.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Size Limit Enforcement (5MB)
        if len(response.content) > 5 * 1024 * 1024:
            raise ValueError("Response too large (exceeds 5MB limit).")

        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return {"url": url, "title": soup.title.string if soup.title else "", "content": text[:50000]}
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


def _validate_url_safety(url: str):
    """Validates URL to prevent SSRF and unsafe usage.

    Checks:
    1. Scheme is http/https.
    2. Hostname is not private/local (localhost, 127.0.0.1, 10.x, 192.168.x, 172.16.x).
    """
    import ipaddress
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL scheme. Only http/https allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: no hostname.")

    # Check for direct loopback/private usage
    if hostname.lower() in ("localhost", "0.0.0.0"):
        raise ValueError("Access to local network resources is forbidden.")

    try:
        # Resolve to IP to check against private ranges
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)

        if ip.is_loopback or ip.is_private or ip.is_reserved:
            raise ValueError(f"Access to private IP {ip_str} is forbidden.")
    except Exception as e:
        # If we can't resolve, it might be an internal name or invalid. Block to be safe?
        # Or if it's a ValueError from above, re-raise.
        if isinstance(e, ValueError):
            raise e
        # If DNS resolution fails, we probably can't scrape it anyway, but let req_lib handle connection error
        # unless we want to be strict.
        pass


@router.post("/citation-lookup", summary="Resolve Citations", response_description="Resolved context.")
async def citation_lookup(
    db: DatabaseDep, registry: RegistryDep, queries: Annotated[list[str], Body(..., embed=True)]
):
    """Uses the Knowledge Base Service to find context for citations.

    Args:
        db (DatabaseDep): Database dependency.
        registry (RegistryDep): Registry dependency.
        queries (list[str]): List of citation keys or queries.

    Returns:
        dict: Map of query to resolved context.
    """
    try:
        from backend.dependencies import get_async_repository
        from backend.llm.provider import LLMFactory
        from backend.services.knowledge_base_service import KnowledgeBaseService

        # Strict Resolution: Use 'smart' strategy for citation analysis
        config = await registry.resolve_model_config("smart")

        repo = get_async_repository(db)
        provider = LLMFactory.create_provider("google", config["model_name"])

        kb_service = KnowledgeBaseService(repo, llm_provider=provider)

        results = {}
        for q in queries:
            context = await kb_service.retrieve_context(q)
            results[q] = context

        return results

    except Exception as e:
        logger.error(f"Citation lookup failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
