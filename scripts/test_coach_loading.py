import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from backend.agents.coach import CoachAgent
from backend.models.state import WorkflowState

class MockRepo:
    def get_knowledge_base_items(self):
        return [
            {"type": "concept", "term": "Concept1", "definition": "Def1"},
            {"type": "reference", "term": "Ref1...", "definition": "Ref1 Full", "doi_link": "doi1"}
        ]

async def run_test():
    repo = MockRepo()
    agent = CoachAgent()
    state = WorkflowState(execution_id="test", inputs={})
    
    print("Running prepare_context...")
    await agent.prepare_context(state, repository=repo)
    
    kb = getattr(agent, "knowledge_base", None)
    
    print("Knowledge Base:", kb)
    
    assert kb is not None
    assert "Concept1" in kb["concepts"]
    assert len(kb["references"]) == 1
    assert kb["references"][0]["citation"] == "Ref1 Full"
    
    print("SUCCESS: CoachAgent loaded KB from DB.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_test())
