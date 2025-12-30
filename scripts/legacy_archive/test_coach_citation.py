import asyncio
import sys
import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock State and Models
class ActionItem(BaseModel):
    otsikko: str
    kuvaus: str
    resurssit: Optional[List[str]] = Field(default_factory=list)

class CoachingPlan(BaseModel):
    kehityskohteet_konkreettisesti: List[ActionItem]
    lahdeluettelo: Optional[List[str]] = Field(default_factory=list)

class WorkflowState:
    def __init__(self):
        self.step_coach = CoachingPlan(
            kehityskohteet_konkreettisesti=[
                ActionItem(
                    otsikko="Kognitiivisen tason nosto",
                    kuvaus="Hyödynnä Bloomin taksonomiaa syventääksesi analyysia.",
                    resurssit=[]
                ),
                ActionItem(
                    otsikko="Luotettavuuden parantaminen",
                    kuvaus="Tarkastele BARS-asteikkoa ja sen sovelluksia.",
                    resurssit=["(Smith & Kendall 1963)"] # Pre-existing citation from LLM
                )
            ]
        )
        self.inputs = type("Inputs", (), {"bibliography_context": []})()
        self.aux_data = {}

# Mock Repository (not needed for post_process as it loads from file)

async def run_test():
    # Ensure cwd is correct for loading data/coach_resources.json
    print(f"CWD: {os.getcwd()}")
    
    from backend.agents.coach import CoachAgent
    
    agent = CoachAgent()
    
    # Manually load KB for testing
    kb_path = os.path.join(os.getcwd(), "data", "coach_resources.json")
    with open(kb_path, "r", encoding="utf-8") as f:
        agent.knowledge_base = json.load(f)
    
    # Reload KB manually if needed, but __init__ does it.
    if not agent.knowledge_base:
        print("ERROR: Knowledge Base not loaded!")
        return

    print("Knowledge base loaded.")
    print(f"Concepts: {list(agent.knowledge_base.get('concepts', {}).keys())}")
    
    state = WorkflowState()
    
    print("Enriching plan...")
    agent.enrich_learning_plan(state)
    
    items = state.step_coach.kehityskohteet_konkreettisesti
    
    # Check Item 1: "Bloom"
    # Definition in KB has "(Wiggins 1998)"
    # Expect "Wiggins, Grant. 1998..." in resources
    item1 = items[0]
    print(f"\nItem 1: {item1.otsikko}")
    print(f"Resources: {item1.resurssit}")
    
    found_wiggins = any("Wiggins" in r for r in item1.resurssit)
    if found_wiggins:
        print("SUCCESS: Found Wiggins reference for Bloom.")
    else:
        print("FAILURE: Did not find Wiggins reference for Bloom.")
        
    # Check Item 2: "BARS"
    # Definition in KB has "(Smith & Kendall 1963)"
    # User input already has "(Smith & Kendall 1963)" as text string from LLM?
    # No, LLM usually puts just text. Our test case simulates LLM putting the key.
    # Our logic should APPEND the full ref if not present.
    item2 = items[1]
    print(f"\nItem 2: {item2.otsikko}")
    print(f"Resources: {item2.resurssit}")
    
    # Should contain FULL ref now
    found_smith = any("Smith, Patricia" in r for r in item2.resurssit)
    if found_smith:
        print("SUCCESS: Found full Smith reference.")
    else:
        print("FAILURE: Did not find full Smith reference.")

if __name__ == "__main__":
    asyncio.run(run_test())
