
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.chat_log_parser import ChatLogParser
from backend.services.document_service import DocumentService

DB_PATH = "data/db.json"
SOURCE_DIR = r"c:\src\quorum\data\files\1e205b2c-c907-45a1-a5e5-3fa4cc10952f"

MAPPING = {
    "keskusteluhistoria SITRA.pdf": "history_text",
    "lopputuote sitra.pdf": "product_text",
    "Reflektiodokumentti sitra.pdf": "reflection_text"
}

def inject_history():
    print(f"--- Patches DB from {SOURCE_DIR} ---")
    
    # 1. Load DB
    if not os.path.exists(DB_PATH):
        print("DB not found.")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    if not executions:
        print("No executions found.")
        return

    # Find latest
    # Assuming IDs are time-sortable or we just trust insertion order if dict performs that way
    # Or explicitly sort by created_at if available
    
    # Sort by ID (UUID isn't time sortable, but let's assume last inserted is at end of dict in modern Py)
    latest_id = list(executions.keys())[-1]
    execution = executions[latest_id]
    
    print(f"Targeting Latest Execution: {latest_id}")
    print(f"Current Inputs: {list(execution.get('inputs', {}).keys())}")
    
    # 2. Read Files
    new_inputs = execution.get("inputs", {})
    
    for filename, input_key in MAPPING.items():
        filepath = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"File missing: {filename}")
            continue
            
        print(f"Processing {filename} -> {input_key} ...")
        
        with open(filepath, "rb") as f:
            content = f.read()
            
        text = ""
        try:
            if filename.lower().endswith(".pdf"):
                text = DocumentService._extract_text_from_pdf(content)
            else:
                text = content.decode("utf-8")
        except Exception as e:
            print(f"Failed to extract {filename}: {e}")
            continue
            
        # Parse if history
        if input_key == "history_text":
            text = ChatLogParser.parse(text)
            
        print(f"Extracted {len(text)} chars.")
        new_inputs[input_key] = text
        
    # 3. Save
    execution["inputs"] = new_inputs
    # Also update 'status' to 'pending' to retry? 
    # Or just leave as is if the user just wants the input populated for VIEWING?
    # Usually if inputs are missing, the Agents have already run on empty input.
    # To re-run, we should probably set status to 'pending' and clear results?
    # BUT user said "LUE ... JA KÄSITTELE".
    # If I just update inputs, result won't change.
    
    # Let's ASK user afterwards. For now, inject inputs so they ARE processed "separately" (by me).
    # Actually, if I update inputs, the user can verify they are there.
    # To re-run, they might need to clone.
    
    data["executions"][latest_id] = execution
    
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print("Database updated successfully.")
    print("You may need to restart the backend or client to see changes.")

if __name__ == "__main__":
    inject_history()
