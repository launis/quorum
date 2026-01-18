
import asyncio
import logging
from backend.core.registry import TaskRegistry
# Import modules to trigger registration
import backend.tasks.security
import backend.tasks.analysis
from backend.models.domain import TaintedData, TodistusKartta

def test_registry_resolution():
    print("\n--- Testing TaskRegistry Resolution ---")
    
    # Check Guard
    guard_def = TaskRegistry.get("guard")
    assert guard_def is not None, "Guard task not registered!"
    print(f"Guard Handler: {guard_def.handler}")
    print(f"Guard Output: {guard_def.output_schema}")
    
    assert guard_def.output_schema == TaintedData, f"Guard output schema mismatch! Got {guard_def.output_schema}"
    # The handler should be the 'agent_wrapper' local function from registry.py. 
    # Its name might be 'agent_wrapper' or similar depending on python version/scope.
    assert "agent_wrapper" in str(guard_def.handler) or "wrapper" in str(guard_def.handler.__name__), f"Guard handler is not the agent wrapper! Got {guard_def.handler}"
    
    # Check Analyst
    analyst_def = TaskRegistry.get("analyst")
    assert analyst_def is not None, "Analyst task not registered!"
    print(f"Analyst Handler: {analyst_def.handler}")
    print(f"Analyst Output: {analyst_def.output_schema}")
    
    assert analyst_def.output_schema == TodistusKartta, f"Analyst output schema mismatch! Got {analyst_def.output_schema}"
    
    # Check Panel
    # Import panel task to trigger registration
    import backend.tasks.panel
    panel_def = TaskRegistry.get("panel")
    assert panel_def is not None, "Panel task not registered!"
    print(f"Panel Handler: {panel_def.handler}")
    from backend.models.domain import PanelAudit
    assert panel_def.output_schema == PanelAudit, f"Panel output schema mismatch! Got {panel_def.output_schema}"
    assert "agent_wrapper" in str(panel_def.handler) or "wrapper" in str(panel_def.handler.__name__), f"Panel handler is not the agent wrapper! Got {panel_def.handler}"
    
    assert panel_def.output_schema == PanelAudit, f"Panel output schema mismatch! Got {panel_def.output_schema}"
    assert "agent_wrapper" in str(panel_def.handler) or "wrapper" in str(panel_def.handler.__name__), f"Panel handler is not the agent wrapper! Got {panel_def.handler}"
    
    # Check Retrieval
    # Import retrieval task to trigger registration
    import backend.tasks.retrieval
    retrieval_def = TaskRegistry.get("retrieve_context")
    assert retrieval_def is not None, "Retrieval task not registered!"
    print(f"Retrieval Handler: {retrieval_def.handler}")
    from backend.models.domain import ContextData
    assert retrieval_def.output_schema == ContextData, f"Retrieval output schema mismatch! Got {retrieval_def.output_schema}"
    assert "agent_wrapper" in str(retrieval_def.handler) or "wrapper" in str(retrieval_def.handler.__name__), f"Retrieval handler is not the agent wrapper! Got {retrieval_def.handler}"
    
    print("\nSUCCESS: Tasks are correctly registered as Agent Adapters.")

if __name__ == "__main__":
    test_registry_resolution()
