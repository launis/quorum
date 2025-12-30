from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Depends
from typing import Any
from backend.dependencies import get_llm_provider_factory, get_db_client_dep, LLMProviderFast
from backend.database.repository import AbstractWorkflowRepository
from backend.agents.coach import CoachAgent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post(
    "/extract-text", 
    summary="Extract Document Text",
    response_description="Extracted text and metadata."
)
async def extract_document_text(
    file: UploadFile = File(..., description="The document to parse (PDF, DOCX, TXT). Max 10MB.")
):
    """
    Parses and extracts plain text from an uploaded document.
    Supports PDF (`.pdf`), Word (`.docx`), and Plain Text (`.txt`).

    Args:
        file (UploadFile): The binary file upload.

    Returns:
        dict: Contains 'filename' and 'text'.

    Raises:
        HTTPException: If the file is too large (>10MB) or format is unsupported.
    """
    try:
        # Read file into memory
        file_bytes = await file.read()
        
        # Check size limit (10MB)
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
        
        filename = file.filename.lower() if file.filename else ""
        text = ""

        # Process using centralized processor
        from backend.services.document_processor import DocumentProcessor
        
        if filename.endswith(".pdf"):
            text = DocumentProcessor.extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            text = DocumentProcessor.extract_text_from_docx(file_bytes)
        elif filename.endswith(".txt"):
            text = DocumentProcessor.extract_text_from_txt(file_bytes)
        else:
             # Fallback: check content type
             if file.content_type == "application/pdf":
                 text = DocumentProcessor.extract_text_from_pdf(file_bytes)
             elif file.content_type == "text/plain":
                 text = DocumentProcessor.extract_text_from_txt(file_bytes)
             else:
                 raise HTTPException(status_code=400, detail="Unsupported file format. Supported: .pdf, .docx, .txt")
        
        return {"filename": file.filename, "text": text}
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/extract-concepts", 
    summary="Extract Concepts (Experimental)",
    response_description="A list of extracted concepts using LLM."
)
async def extract_concepts_from_file_or_text(
    llm_provider: LLMProviderFast,
    file: UploadFile = File(None, description="Optional source file."),
    text: str = Body(None, description="Optional raw source text.")
):
    """
    Uses the configured LLM to semantically extract concepts from input text or file.
    Note: This is an experimental tool endpoint.

    Args:
        file (UploadFile, optional): Binary file source.
        text (str, optional): Text string source.
        llm_provider: Dependency.

    Returns:
        dict: Object containing a list of 'concepts'.

    Raises:
        HTTPException: If no input is provided or extraction fails.
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Must provide either file or text.")
    
    final_text = text or ""
    
    if file:
        try:
            file_bytes = await file.read()
            filename = file.filename.lower()
            from backend.services.document_processor import DocumentProcessor
            
            if filename.endswith(".pdf"):
                final_text = DocumentProcessor.extract_text_from_pdf(file_bytes)
            elif filename.endswith(".docx"):
                final_text = DocumentProcessor.extract_text_from_docx(file_bytes)
            elif filename.endswith(".txt"):
                final_text = DocumentProcessor.extract_text_from_txt(file_bytes)
            else:
                 final_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"File processing error: {e}")

    if not final_text.strip():
        raise HTTPException(status_code=400, detail="No text extracted.")

    # Instantiate functionality on the fly (lightweight)
    from backend.services.knowledge_base_service import KnowledgeBaseService
    from backend.services.progress import InMemoryProgressTracker
    
    # We pass None for repository since extraction logic doesn't use it.
    service = KnowledgeBaseService(repository=None, llm_provider=llm_provider)
    tracker = InMemoryProgressTracker()
    
    try:
        concepts = await service.extract_concepts_with_llm(final_text, tracker)
        return {"concepts": concepts}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/citation-lookup", 
    summary="Lookup Citations",
    response_description="Matches found in the Knowledge Base."
)
async def lookup_citations(
    text: str = Body(..., embed=True, description="The content text to scan for citations."),
    db: Any = Depends(get_db_client_dep)
):
    """
    Scans the provided text for key terms or citations present in the system's Knowledge Base.
    Utilizes the CoachAgent's 2-hop resolution logic.
    """
    if not text:
         return {"citations": []}
         
    try:
        from backend.dependencies import get_async_repository, get_db_client_dep
        # Manually resolving for clarity or change sig
        repo = get_async_repository(db)
        
        # Load KB
        items = await repo.get_knowledge_base_items()
        
        concepts = {}
        references = []
        
        for item in items:
            i_type = item.get('type')
            if i_type == 'concept':
                term = item.get('term')
                defn = item.get('definition')
                if term and defn:
                    concepts[term] = defn
            elif i_type == 'reference':
                ref_obj = {
                    "citation": item.get('definition'),
                    "short_citation": item.get('term'),
                    "doi": item.get('doi_link')
                }
                references.append(ref_obj)
        
        knowledge_base = {
            "concepts": concepts,
            "references": references
        }
        
        # Use CoachAgent static method
        matches = CoachAgent.find_citations(text, knowledge_base)
        
        return {"citations": matches}
        
    except Exception as e:
         logger.error(f"Citation validation failed: {e}")
         raise HTTPException(status_code=500, detail=str(e))
