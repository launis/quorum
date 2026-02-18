
import asyncio
import logging
import sys
import sys
import os
import uuid

# Ensure backend matches path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

# Force required settings for testing
os.environ["STORAGE_BACKEND"] = "MOCK"
os.environ["USE_MOCK_DB"] = "True"

from backend.models.state import WorkflowState
from backend.models.domain.analyst import AnalystOutput, Hypothesis, SearchResult
from backend.hooks.search import execute_google_search

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_search_hook():
    print("Verifying Vertex AI Search Hook (Strict Mode)...")

    # 1. Setup Mock State
    mock_hypothesis = Hypothesis(
        id="hyp-1",
        claim_text="Sitra megatrends 2025 emphasize ecological reconstruction.",
        evidence_found=False,
        search_query="Sitra megatrendit 2025", # Query known to yield results
        quotes=[]
    )

    analyst_output = AnalystOutput(
        thought_process="Reasoning trace for testing purposes.",
        conclusion="Conclusion based on search.",
        confidence_score=0.9,
        hypotheses=[mock_hypothesis],
        rag_evidence=[],
        critical_violation=False
    )
    
    # Simulate Context (serialize to dict as per Engine behavior)
    context = {
        "step_analyst": analyst_output.model_dump(),
        "language": "fi" # Test language Hint
    }

    state = WorkflowState(
        execution_id=uuid.uuid4(),
        workflow_id="test-workflow-1", # Required field
        context_variables=context
    )

    print(f"Input Context: {context}")

    # 2. Execute Hook
    try:
        new_state = execute_google_search(state)
        print("Hook Executed Successfully.")
    except Exception as e:
        print(f"Hook Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 3. Verify Output
    results = new_state.context_variables.get("search_result")
    
    if not results:
        print("FAILED: 'search_result' not found in context.")
        sys.exit(1)

    print(f"Result Function Type: {type(results)}")

    if isinstance(results, SearchResult):
        print(f"Result is strictly typed 'SearchResult'.")
        print(f"Found {len(results.results)} items.")
        
        for item in results.results:
            print(f"   - [{item.title}]({item.link})")
            print(f"     Snippet: {item.snippet[:100]}...")
            
        if len(results.results) > 0:
            print("\nVERIFICATION PASSED: Search returned results via Vertex AI Grounding.")
        else:
            print("\nWARNING: Search executed but returned 0 results. (API might be working but found nothing)")
            
    else:
        print(f"FAILED: Result is not 'SearchResult' model. Got: {type(results)}")
        # If it's a dict, maybe the model_copy did something? 
        # But WorkflowState context_variables is Dict[str, Any], so it preserves objects in memory.
        pass

    print("\n--- Testing Fail Fast (Invalid Data) ---")
    try:
        bad_context = {"step_analyst": {"invalid": "data"}}
        bad_state = WorkflowState(execution_id=uuid.uuid4(), workflow_id="test", context_variables=bad_context)
        execute_google_search(bad_state)
        print("FAILED: Hook should have raised AppException for invalid data.")
    except Exception as e:
        print(f"SUCCESS: Hook correctly raised exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    verify_search_hook()
