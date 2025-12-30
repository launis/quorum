import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.executor import Executor
from dotenv import load_dotenv

load_dotenv()

def test_executor():
    executor = Executor()
    
    # Mock context for STEP_8_JUDGE matching HypothesisArgument schema
    context = {
        "hypothesis_argument": "Test hypothesis argument based on evidence.",
        "toulmin_structure": {"claim": "Test Claim", "data": "Test Data"},
        "citations": [{"source": "Test Source", "explanation": "Test Explanation"}]
    }
    
    try:
        print("Testing STEP_8_JUDGE with Gemini...")
        # Let's try passing the new model name explicitly to verify the handler works with it.
        result = executor.execute_step("STEP_8_JUDGE", context, model_override="models/gemini-2.5-pro")
        print("Execution successful!")
        print("Result:", result)
        
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    test_executor()
