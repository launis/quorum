import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB, Query

from processor import PDFProcessor

app = FastAPI(
    title="Cognitive Quorum API",
    description="Backend for Cognitive Quorum application.",
    version="0.1.0"
)

# Database setup
db = TinyDB('/app/data/db.json')
assessments_table = db.table('assessments')

# Ensure upload directory exists
UPLOAD_DIR = "/app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AssessmentData(BaseModel):
    """
    Model representing the extracted text data from assessment files.

    Attributes:
        prompt_text (str): Text extracted from the prompt PDF.
        history_text (str): Text extracted from the history PDF.
        product_text (str): Text extracted from the product PDF.
        reflection_text (str): Text extracted from the reflection PDF.
    """
    prompt_text: str
    history_text: str
    product_text: str
    reflection_text: str

class AssessmentResponse(BaseModel):
    """
    Response model for assessment creation.

    Attributes:
        status (str): The status of the upload operation (e.g., "success").
        message (str): A descriptive message about the operation result.
        files_received (List[str]): List of filenames that were successfully uploaded.
        data (AssessmentData): The extracted text data from the files.
    """
    status: str
    message: str
    files_received: List[str]
    data: AssessmentData

@app.post("/upload", response_model=AssessmentResponse)
async def upload_files(
    prompt_file: UploadFile = File(...),
    history_file: UploadFile = File(...),
    product_file: UploadFile = File(...),
    reflection_file: UploadFile = File(...)
):
    """
    Uploads the necessary files for assessment.

    Args:
        prompt_file (UploadFile): The main assessment prompt (PDF).
        history_file (UploadFile): The conversation history (PDF).
        product_file (UploadFile): The final product (PDF).
        reflection_file (UploadFile): The reflection document (PDF).

    Returns:
        AssessmentResponse: Status of the upload including list of saved files.

    Raises:
        HTTPException: If file upload fails for any reason (500 error).
    """
    files = [prompt_file, history_file, product_file, reflection_file]
    saved_filenames = []
    extracted_texts = {}

    try:
        # 1. Save files
        for file in files:
            file_location = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
            saved_filenames.append(file.filename)
            
            # 2. Extract text immediately
            try:
                text = PDFProcessor.extract_text_from_pdf(file_location)
                # Map filename/parameter to specific key (simplified logic for now)
                # We assume the order of files matches the function args: prompt, history, product, reflection
                if file == prompt_file:
                    extracted_texts["prompt_text"] = text
                elif file == history_file:
                    extracted_texts["history_text"] = text
                elif file == product_file:
                    extracted_texts["product_text"] = text
                elif file == reflection_file:
                    extracted_texts["reflection_text"] = text
            except Exception as e:
                print(f"Error extracting text from {file.filename}: {e}")
                # For now, fail hard if extraction fails, or we could set empty string
                raise HTTPException(status_code=400, detail=f"Failed to extract text from {file.filename}")

        # 3. Validate with Pydantic
        assessment_data = AssessmentData(**extracted_texts)

        # 4. Log to DB with extracted data
        assessments_table.insert({
            "status": "uploaded",
            "files": saved_filenames,
            "data": assessment_data.dict()
        })

        return {
            "status": "success",
            "message": "Files uploaded and processed successfully",
            "files_received": saved_filenames,
            "data": assessment_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/health")
def health_check():
    """
    Simple health check endpoint.

    Returns:
        dict: A dictionary containing the status of the API.
    """
    return {"status": "ok"}

# --- Hello World Feature ---

class Greeting(BaseModel):
    """
    Model representing a greeting message.

    Attributes:
        message (str): The greeting message content.
    """
    message: str

greetings_table = db.table('greetings')

@app.post("/greet", response_model=Greeting)
async def create_greeting(greeting: Greeting):
    """
    Saves a greeting to the database.

    Args:
        greeting (Greeting): The greeting object to be saved.

    Returns:
        Greeting: The saved greeting object.
    """
    greetings_table.insert({"message": greeting.message})
    return greeting

@app.get("/greet", response_model=Greeting)
async def get_last_greeting():
    """
    Retrieves the last greeting from the database.

    Returns:
        dict: A dictionary containing the message of the last greeting, or a default message if none exist.
    """
    all_greetings = greetings_table.all()
    if not all_greetings:
        return {"message": "No greetings yet."}
    return {"message": all_greetings[-1]["message"]}
