from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
import shutil
import uuid
import os
import json
import logging
from bs4 import BeautifulSoup
import requests as req_lib

from backend.dependencies import DatabaseDep, RegistryDep, get_db_client_dep, get_agent_registry_dep
from backend.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["Tools"])

# --- Endpoints ---

@router.post(
    "/text-extract",
    summary="Extract Text from File",
    response_description="The extracted raw text."
)
async def extract_text_from_file(file: UploadFile = File(...)):
    """
    Extracts text content from an uploaded file (PDF, Docx, etc).
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except: pass

@router.post(
    "/concept-extraction",
    summary="Extract Concepts (Text/File)",
    response_description="List of extracted concepts and relationships."
)
async def extract_concepts_from_file_or_text(
    registry: RegistryDep,
    text: Optional[str] = Body(None),
    file: Optional[UploadFile] = File(None),
    llm_provider: Optional[str] = Body("google")
):
    """
    Extracts domain concepts from either raw text or an uploaded file.
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
                except: pass
    
    if not content:
        raise HTTPException(status_code=400, detail="No text or file provided.")

    try:
        # Resolve config logic
        config = await registry.resolve_model_config('deep')
        
        from backend.llm.provider import LLMFactory
        from backend.services.knowledge_base_service import KnowledgeBaseService
        
        # Using KnowledgeBaseService for extraction as it likely has the logic 'extract_concepts_with_llm'
        # Check previous usage: 'service.extract_concepts_with_llm(final_text, tracker)'
        
        provider = LLMFactory.create_provider(config['provider'], config['model_name'])
        
        kb_service = KnowledgeBaseService(repository=None, llm_provider=provider)
        
        # We need a dummy tracker?
        from backend.services.progress import InMemoryProgressTracker
        tracker = InMemoryProgressTracker()
        
        concepts = await kb_service.extract_concepts_with_llm(content, tracker)
        
        return {"source_length": len(content), "concepts": concepts}
        
    except Exception as e:
        logger.error(f"Concept extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/web-scrape",
    summary="Scrape URL",
    response_description="Extracted text and metadata."
)
async def scrape_url(url: str = Body(..., embed=True)):
    """
    Fetches and parses a public URL.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = req_lib.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return {
            "url": url,
            "title": soup.title.string if soup.title else "",
            "content": text[:50000]
        }
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/citation-lookup",
    summary="Resolve Citations",
    response_description="Resolved context."
)
async def citation_lookup(
    db: DatabaseDep,
    queries: List[str] = Body(..., embed=True)
):
    """
    Uses the Knowledge Base Service to find context for citations.
    """
    try:
        from backend.services.knowledge_base_service import KnowledgeBaseService
        from backend.dependencies import get_async_repository
        from backend.llm.provider import LLMFactory
        
        repo = get_async_repository(db)
        provider = LLMFactory.create_provider("google", "gemini-1.5-flash")
        
        kb_service = KnowledgeBaseService(repo, llm_provider=provider)
        
        results = {}
        for q in queries:
            context = await kb_service.retrieve_context(q)
            results[q] = context
            
        return results

    except Exception as e:
        logger.error(f"Citation lookup failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
