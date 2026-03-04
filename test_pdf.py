import asyncio
import os
import sys

# Setup quorum paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from backend.services.pdf_generator import PdfReportService
from backend.database.firestore_repo import FirestoreRepository

async def generate():
    os.environ["mode"] = "local"
    repo = FirestoreRepository()
    
    # We just need to grab ANY execution to test PDF generation. Let's get executions from local DB
    import json
    with open("data/db.json", "r") as f:
        db_data = json.load(f)
    
    execs = db_data.get("executions", {})
    if not execs:
        print("No executions found.")
        return
        
    ex_id = list(execs.keys())[-1]
    print(f"Generating PDF for execution: {ex_id}")
    
    service = PdfReportService(repo)
    pdf_bytes = await service.generate_execution_pdf(ex_id)
    
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("test_output.pdf saved!")

if __name__ == "__main__":
    asyncio.run(generate())
