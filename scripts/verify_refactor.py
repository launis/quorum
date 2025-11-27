import sys
import os
import json

# Add project root to path (one level up)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.engine.orchestrator import Orchestrator
from src.database.initialization import initialize_database
import src.components.hooks # Register hooks

def verify_refactor():
    print("Verifying Refactored Structure (Direct Integration)...")
    
    # Initialize DB
    initialize_database()
    
    initial_inputs = {
        "prompt_text": "Refactor Test Prompt",
        "history_text": "Refactor Test History",
        "product_text": "Refactor Test Product",
        "reflection_text": "Refactor Test Reflection"
    }
    
    try:
        orchestrator = Orchestrator()
        result = orchestrator.run_workflow("KVOORUMI_PHASED_A", initial_inputs)
        
        print("   Success! Workflow executed.")
        print("   Final Verdict:", result.get('final_verdict'))
        print("   XAI Report:", result.get('xai_report')[:50] + "...")
        
    except Exception as e:
        print(f"   Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_refactor()
