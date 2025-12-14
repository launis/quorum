from fastapi import APIRouter, UploadFile, File, HTTPException



router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Extracts text from an uploaded PDF file.
    """
    try:
        # Read file into memory
        file_bytes = await file.read()
        
        # Check size limit (10MB)
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

        # Process directly from memory (using centralized processor)
        from backend.services.document_processor import DocumentProcessor
        text = DocumentProcessor.extract_text_from_pdf(file_bytes)
        
        return {"filename": file.filename, "text": text}
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
