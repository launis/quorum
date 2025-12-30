
import sys
import os
import json
import base64
from pathlib import Path

# Add backend to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.wrapper import get_db_client
from backend.services.document_processor import DocumentProcessor
from tinydb import Query

# SETUP
DB_PATH = "backend/database/db_mock.json" # Adjust if your path differs in config
FILES_ROOT = "backend/files/executions"

def migrate_blobs():
    print(f"Starting Migration on {DB_PATH}...")
    
    db = get_db_client()
    executions_table = db.table('executions')
    
    all_executions = executions_table.all()
    count = 0
    bloated_count = 0
    
    for exc in all_executions:
        execution_id = exc.get('execution_id')
        inputs = exc.get('inputs', {})
        modified = False
        
        # Check inputs for Base64 blobs
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("[BASE64:PDF]"):
                bloated_count += 1
                try:
                    print(f" -> Found Blob in Execution {execution_id}, Field: {key}")
                    
                    # 1. Prepare Directory
                    archive_dir = Path(FILES_ROOT) / execution_id
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 2. Decode
                    b64_data = value.replace("[BASE64:PDF]", "")
                    file_bytes = base64.b64decode(b64_data)
                    
                    # 3. Save to Disk
                    file_path = archive_dir / f"{key}.pdf"
                    with open(file_path, "wb") as f:
                        f.write(file_bytes)
                    print(f"    Saved to {file_path}")
                    
                    # 4. Extract Text
                    text = DocumentProcessor.extract_text_from_pdf(file_bytes)
                    print(f"    Extracted {len(text)} chars")
                    
                    # 5. Update Input in Memory
                    inputs[key] = text
                    modified = True
                    
                except Exception as e:
                    print(f"    ERROR processing blob: {e}")
        
        # 6. Update DB Record if changed
        if modified:
            # We update the WHOLE inputs object
            Execution = Query()
            executions_table.update({'inputs': inputs}, Execution.execution_id == execution_id)
            count += 1
            
    print(f"Migration Complete.")
    print(f"Found {bloated_count} blobs.")
    print(f"Updated {count} execution records.")

if __name__ == "__main__":
    migrate_blobs()
