import sys
import os
import json

# Add project root to path (one level up)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.engine.orchestrator import Orchestrator
from src.database.initialization import initialize_database
import src.components.hooks # Register hooks

def verify_optimized():
    print("Verifying Optimized Workflow (KVOORUMI_OPTIMIZED)...")
    
    # Initialize DB
    initialize_database()
    
    initial_inputs = {
        "prompt_text": "Optimized Test Prompt",
        "history_text": "Optimized Test History",
        "product_text": "Optimized Test Product",
        "reflection_text": "Optimized Test Reflection"
    }
    
    try:
        orchestrator = Orchestrator()
        # Run the optimized workflow
        result = orchestrator.run_workflow("KVOORUMI_OPTIMIZED", initial_inputs)
        
        print("   Success! Workflow executed.")
        print("   Final Verdict:", result.get('final_verdict'))
        if 'citations' in result:
            print("   Citations:", result['citations'])
        print("   XAI Report:", result.get('xai_report')[:50] + "...")
        if "VASTUUVAPAUSLAUSEKE" in result.get('xai_report', ''):
            print("   Disclaimer found in report.")
        else:
            print("   WARNING: Disclaimer NOT found in report.")
        
    except Exception as e:
        print(f"   Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_optimized()
