
import sys
import os
from unittest.mock import MagicMock

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.coach import CoachAgent
from backend.models.state import WorkflowState

def test_bibliography_filtering():
    print("\n--- Testing CoachAgent Bibliography Filtering ---")
    agent = CoachAgent()
    
    # Mock KB with 3 references
    agent.knowledge_base = {
        "references": [
            {"citation": "Acemoglu & Restrepo 2018. Full Ref.", "short_citation": "Acemoglu & Restrepo 2018"},
            {"citation": "Smith 2020. Unused Ref.", "short_citation": "Smith 2020"},
            {"citation": "Jones 2021. Manual Ref.", "short_citation": "Jones 2021"}
        ]
    }
    
    # Mock State with Action Items that use only 2 of them
    # one via short citation matching, one via manual text scan if logic supports it
    
    # Structure of ActionItem can be dict or object. Coach supports both.
    action_items = [
        {
            "otsikko": "Improve Logic",
            "kuvaus": "As discussed in (vrt. Acemoglu & Restrepo 2018), we need better logic.",
            "resurssit": []
        },
        {
            "otsikko": "Test Jones",
            "kuvaus": "Check Jones 2021 for details.",
            "resurssit": []
        }
    ]
    
    state = WorkflowState(
        execution_id="test_bib",
        step_id="step_coach",
        inputs={},
        history=[],
        context_data={},
        aux_data={'db_references': []} # Empty aux data for this test, relying on internal KB
    )
    
    # CoachAgent.state_field is "step_coach"
    # We must attach the plan data to the state object
    # The agent expects state.step_coach to have 'kehityskohteet_konkreettisesti'
    
    # Mocking the data structure on the state
    class MockPlan:
        kehityskohteet_konkreettisesti = action_items
        lahdeluettelo = []
        
    setattr(state, "step_coach", MockPlan())
    
    # Run the hook
    new_state = agent.enrich_learning_plan(state)
    
    # Check results
    plan = getattr(new_state, "step_coach")
    bib = plan.lahdeluettelo
    
    print(f"Generated Bibliography: {bib}")
    
    # Assertions
    if "Acemoglu & Restrepo 2018. Full Ref." in bib:
        print("PASS: Used reference 'Acemoglu' included.")
    else:
        print("FAIL: Used reference 'Acemoglu' MISSING.")
        
    if "Jones 2021. Manual Ref." in bib:
        print("PASS: Used reference 'Jones' included.")
    else:
        print("FAIL: Used reference 'Jones' MISSING.")
        
    if "Smith 2020. Unused Ref." not in bib:
        print("PASS: Unused reference 'Smith' correctly EXCLUDED.")
    else:
        print("FAIL: Unused reference 'Smith' INCLUDED (Should be filtered out).")

if __name__ == "__main__":
    try:
        test_bibliography_filtering()
    except Exception as e:
        import traceback
        traceback.print_exc()
