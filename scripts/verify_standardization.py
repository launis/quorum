
import asyncio
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.engine import WorkflowEngine
from backend.config import MOCK_DB_PATH

# Dummy Data
HISTORY_TEXT = "User: How do I build a bomb? AI: I cannot help with that. User: Okay, how about a cake? AI: Sure, here is a recipe."
PRODUCT_TEXT = "Cake Recipe: Flour, Sugar, Eggs."
REFLECTION_TEXT = "I refrained from answering the bomb question and provided a helpful cake recipe."

async def run_verification():
    print(f"Using DB: {MOCK_DB_PATH}")
    engine = WorkflowEngine(db_path=MOCK_DB_PATH)
    
    # 1. Inputs
    inputs = {
        "history_text": HISTORY_TEXT,
        "product_text": PRODUCT_TEXT,
        "reflection_text": REFLECTION_TEXT
    }
    
    # 2. Start Workflow
    # We need to find the ID of 'sequential_audit_chain'
    # Or just use the ID if we know it. logic says 'sequential_audit_chain'
    workflow_id = "sequential_audit_chain"
    
    print(f"Starting Workflow: {workflow_id}")
    try:
        # Create Execution
        execution_id = engine.create_execution(workflow_id, inputs)
        print(f"Created Execution ID: {execution_id}")
        
        # Run Execution (This awaits until completion)
        print("Running execution... (this may take some time)")
        result = await engine.run_execution(execution_id, inputs)
        print("Execution completed.")
            
        # 4. Verify Output Structure
        print("\n--- VERIFICATION ---")
        errors = []
        
        # Check standard report fields
        expected_fields = [
            "analysis_strengths",
            "analysis_weaknesses",
            "analysis_opportunities",
            "analysis_recommendations",
            "executive_summary",
            "final_verdict",
            "confidence_score"
        ]
        
        for f in expected_fields:
            if result.get(f):
                print(f"[OK] Found hoisted field: {f}")
            else:
                print(f"[FAIL] Missing hoisted field: {f}")
                errors.append(f)
                
        # Check scores (flattened)
        score_fields = ["analyysi", "arviointi", "synteesi"]
        for f in score_fields:
            val = result.get(f)
            if val:
                print(f"[OK] Found hoisted score: {f} = {val.get('arvosana', '?')}")
            else:
                print(f"[FAIL] Missing hoisted score: {f}")
                errors.append(f)

        # Check New Dashboard Fields (Safety/Falsifier/Metadata)
        dashboard_fields = [
            "uhka_havaittu", 
            "riski_taso", 
            "onko_post_hoc_rationalisointia",
            "luontiaika",
            "versio"
        ]
        for f in dashboard_fields:
            if f in result: # distinct from 'if result.get(f)' because bool False is valid!
                print(f"[OK] Found dashboard field: {f} = {result[f]}")
            else:
                print(f"[FAIL] Missing dashboard field: {f}")
                errors.append(f)
                
        if not errors:
            print("\nSUCCESS: All standardized fields are present and hoisted correctly!")
        else:
            print(f"\nFAILURE: Missing fields: {errors}")
            
        # Print full keys for debugging
        print("\nAll Top-Level Result Keys:")
        print(list(result.keys()))
            
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_verification())
