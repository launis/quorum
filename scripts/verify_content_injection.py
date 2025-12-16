
import sys
import os
import asyncio

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.coach import CoachAgent
from backend.models.state import WorkflowState

def test_coach_content_injection():
    print("\n--- Testing CoachAgent Content Injection ---")
    agent = CoachAgent()
    state = WorkflowState(
        execution_id="test",
        step_id="step_coach",
        inputs={},
        history=[],
        context_data={},
        aux_data={}
    )
    
    # Mock concepts from DB
    mock_concepts = [
        {"term": "Holistinen Mestaruus", "definition": "A state of complete mastery."},
        {"term": "Concept B", "definition": "Another important concept."}
    ]
    
    # Simulate execute logic passing preloaded concepts
    # We test the _build_prompt method which does the string construction
    prompt = agent._build_prompt(state, preloaded_concepts=mock_concepts)
    
    # Check if headers and definitions are present
    if "#### Holistinen Mestaruus" in prompt:
         print("PASS: Header 'Holistinen Mestaruus' found.")
    else:
         print("FAIL: Header 'Holistinen Mestaruus' missing.")
         
    if "A state of complete mastery." in prompt:
         print("PASS: Definition content found.")
    else:
         print("FAIL: Definition content missing.")

    if "### REFERENCE MATERIAL" in prompt:
        print("PASS: 'REFERENCE MATERIAL' section header found.")
    else:
        print("FAIL: 'REFERENCE MATERIAL' section header missing.")

if __name__ == "__main__":
    try:
        test_coach_content_injection()
    except Exception as e:
        import traceback
        traceback.print_exc()

