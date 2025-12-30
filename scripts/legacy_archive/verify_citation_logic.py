
import sys
import os
import asyncio

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.knowledge_base_parser import KnowledgeBaseParser
from backend.agents.coach import CoachAgent
from backend.models.state import WorkflowState  # Assuming this exists and is importable

def test_parser_extraction():
    print("\n--- Testing KnowledgeBaseParser.extract_short_citation ---")
    cases = [
        ("Acemoglu, Daron & Restrepo, Pascual. 2018: The race...", "Acemoglu & Restrepo 2018"),
        ("Smith, John. 2020. Title.", "Smith 2020"),
        ("AERA, APA & NCME. 2014: Standards...", "AERA, APA & NCME 2014"),
        ("Anderson, L. W. & Krathwohl, D. R. (toim.) 2001. Title.", "Anderson & Krathwohl 2001"),
        ("Junk text without date.", None)
    ]
    
    for input_str, expected in cases:
        result = KnowledgeBaseParser.extract_short_citation(input_str)
        status = "PASS" if result == expected else f"FAIL (Expected '{expected}', got '{result}')"
        print(f"Input: {input_str[:30]}... -> {result} [{status}]")

def test_coach_prompt():
    print("\n--- Testing CoachAgent Prompt Injection ---")
    agent = CoachAgent()
    # Mock state
    state = WorkflowState(
        execution_id="test",
        step_id="step_coach",
        inputs={},
        history=[],
        context_data={},
        aux_data={}
    )
    
    # Mock preloaded citations
    citations = ["Acemoglu & Restrepo 2018", "Smith 2020"]
    
    # Call _build_prompt (internal method)
    prompt = agent._build_prompt(state, preloaded_citations=citations)
    
    if "VALID CITATION KEYS (STRICT)" in prompt:
        print("PASS: 'VALID CITATION KEYS (STRICT)' found in prompt.")
    else:
        print("FAIL: 'VALID CITATION KEYS (STRICT)' NOT found in prompt.")
        
    if "Acemoglu & Restrepo 2018" in prompt:
         print("PASS: Citation keys found in prompt.")
    else:
         print("FAIL: Citation keys NOT found in prompt.")

if __name__ == "__main__":
    test_parser_extraction()
    try:
        test_coach_prompt()
    except Exception as e:
        print(f"Coach Prompt Test Error: {e}")
        # Might fail if dependencies like TinyDB or models are tricky to init in script, but CoachAgent init is simple.
