from fastapi import APIRouter, UploadFile, File, HTTPException



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
