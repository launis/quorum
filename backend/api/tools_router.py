from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz


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

        # Process directly from memory
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        
        return {"filename": file.filename, "text": text}
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
