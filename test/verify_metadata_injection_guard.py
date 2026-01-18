
import asyncio
import logging
from datetime import datetime
from backend.agents.guard import GuardAgent
from backend.models.state import WorkflowState
from backend.models.domain import TaintedData, TaintedDataContent, SecurityCheck, Metadata

# Mock Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MetaDataTest")

async def test_guard_metadata_injection():
    print("\n--- Testing GuardAgent Metadata Injection ---")
    
    # 1. Setup
    from backend.models.state import InputData
    
    input_data = InputData(
        history_text="Test History",
        product_text="Test Product",
        reflection_text="Test Reflection"
    )
    
    agent = GuardAgent()
    state = WorkflowState(execution_id="test-exec", inputs=input_data)
    
    # 2. Create Minimal TaintedData Input (Simulating LLM Output)
    # Note: We provide a valid Metadata object, but with dummy values that SHOULD be overwritten.
    llm_output = TaintedData(
        data=TaintedDataContent(),
        security_check=SecurityCheck(
            uhka_havaittu=False,
            adversariaalinen_simulaatio_tulos="Simulated",
            riski_taso="MATALA"
        ),
        metadata=Metadata(
            luontiaika="2000-01-01T00:00:00", # OLD TIME
            agentti="FakeAgent",             # WRONG NAME
            vaihe=99                         # WRONG STEP
        ),
        metodologinen_loki="Log",
        edellisen_vaiheen_validointi="Valid",
        semanttinen_tarkistussumma="fake_hash"
    )
    
    print(f"Original Time: {llm_output.metadata.luontiaika}")
    print(f"Original Agent: {llm_output.metadata.agentti}")

    # 3. Call _update_state (which calls _apply_python_authority)
    # We pass the Pydantic model directly (Modern Path)
    await agent._update_state(state, llm_output, output_key="step_guard")
    
    # 4. Verify Result in State
    result = state.step_guard
    
    if not result:
        print("FAILURE: State not updated.")
        return

    print(f"Result Time: {result.metadata.luontiaika}")
    print(f"Result Agent: {result.metadata.agentti}")
    
    # Assertions
    assert result.metadata.luontiaika != "2000-01-01T00:00:00", "Timestamp was NOT updated!"
    assert result.metadata.agentti == "GuardAgent", f"Agent name was NOT updated! Got: {result.metadata.agentti}"
    assert result.semanttinen_tarkistussumma != "fake_hash", "Checksum was NOT updated!"
    
    print("SUCCESS: Metadata was correctly injected.")

if __name__ == "__main__":
    asyncio.run(test_guard_metadata_injection())
