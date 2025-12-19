from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Depends
from backend.dependencies import get_llm_provider, get_repository_dep
from backend.database.repository import AbstractWorkflowRepository
from backend.agents.coach import CoachAgent
import logging

logger = logging.getLogger(__name__)



router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post("/extract-text")
async def extract_document_text(file: UploadFile = File(...)):
    """
    Extracts text from an uploaded document (PDF, DOCX, TXT).
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

@router.post("/extract-concepts")
async def extract_concepts_from_file_or_text(
    file: UploadFile = File(None),
    text: str = Body(None),
    llm_provider = Depends(get_llm_provider)
):
    """
    Experimental Endpoint: Extracts concepts from text using LLM.
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

@router.post("/citation-lookup")
async def lookup_citations(
    text: str = Body(..., embed=True),
    repo: AbstractWorkflowRepository = Depends(get_repository_dep)
):
    """
    Scans text for citations/concepts present in the Knowledge Base.
    Uses CoachAgent's static find_citations logic.
    """
    if not text:
         return {"citations": []}
         
    try:
        # Load KB (Replicating CoachAgent.prepare_context logic)
        items = repo.get_knowledge_base_items()
        
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
