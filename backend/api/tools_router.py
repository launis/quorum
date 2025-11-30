from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.processor import PDFProcessor
import os
import shutil
import tempfile

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Extracts text from an uploaded PDF file.
    """
    try:
        # Create a temporary file to save the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            # Process the PDF
            processor = PDFProcessor()
            text = processor.extract_text_from_pdf(tmp_path)
            return {"filename": file.filename, "text": text}
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
