import os
import sys
import asyncio
import logging
import json

# Force mock DB
os.environ["USE_MOCK_DB"] = "True"
os.environ["MOCK_LLM_MODE"] = "True"

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.engine import WorkflowEngine
from backend.models.state import WorkflowState, InputData
from backend.config import get_db_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_courtroom_2_0():
    print("=== VERIFYING COURTROOM 2.0 IMPLEMENTATION ===")
    
    # 1. Initialize Engine
    db_path = get_db_path()
    engine = WorkflowEngine(db_path)
    print(f"Engine initialized with DB: {db_path}")
    
    # 2. Setup Inputs
    inputs = InputData(
        history_text="Opiskelija: Maapallo on litteä. Opettaja: Ei ole. Opiskelija: Onpas, katso horisonttia.",
        product_text="Tutkielma: Maapallon muoto. Johtopäätös: Litteä on.",
        reflection_text="Opin, että omiin silmiin voi luottaa."
    )
    
    # 3. Create Execution (Sequential Audit Chain)
    # Convert inputs to dict
    raw_inputs = inputs.model_dump()
    
    # Create execution record
    print("Creating execution record...")
    try:
        execution_id = engine.create_execution("sequential_audit_chain", raw_inputs)
        print(f"Execution ID: {execution_id}")
    except Exception as e:
        print(f"ERROR creating execution: {e}")
        return

        return

    # Debug: Check workflow steps
    from tinydb import Query
    Wf = Query()
    wf = engine.workflows_table.search(Wf.id == "sequential_audit_chain")[0]
    print(f"Workflow Steps IDs: {wf['steps']}")
    
    Step = Query()
    all_steps = engine.steps_table.all()
    print(f"Total Steps in DB: {len(all_steps)}")
    found_steps = [s['id'] for s in all_steps if s['id'] in wf['steps']]
    print(f"Found matching steps in DB: {len(found_steps)} / {len(wf['steps'])}")

    # 4. Run Execution
    print("Starting execution...")
    try:
        final_state = await engine.run_execution(execution_id, raw_inputs)
    except Exception as e:
        print(f"CRITICAL FAILURE during execution: {e}")
        if hasattr(e, 'errors'):
            print(f"Validation Errors: {json.dumps(e.errors(), indent=2)}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Verify Outputs
    print("\n=== VERIFICATION RESULTS ===")
    
    # Helper to check step
    def check_step(key, name):
        # Result is a dict, not object
        trace = final_state.get('trace', {})
        if key in trace:
            print(f"[PASS] {name} executed. Output: {list(trace[key].keys())}")
            return True
        else:
            print(f"[FAIL] {name} NOT found in trace.")
            return False

    all_passed = True
    
    # Check Profiler (Step 2.5)
    print(f"Trace keys: {list(final_state.get('trace', {}).keys())}")
    
    # We expect 'step_profiler', 'step_archivist', 'step_coach'
    pass_profiler = check_step('step_profiler', 'Profiler Check')
    pass_archivist = check_step('step_archivist', 'Archivist Check')
    pass_coach = check_step('step_coach', 'Coach Check')
    
    # Check Hooks (via aux_data)
    print("\n=== HOOK VERIFICATION ===")
    aux = final_state.get('aux_data', {})
    
    # Profiler Hook
    if 'profiler_metrics' in aux:
        print(f"[PASS] Profiler Hook (metrics): {aux['profiler_metrics']}")
    else:
        print("[FAIL] Profiler Hook (metrics) missing.")
        all_passed = False

    # Archivist Hook
    if 'archivist_precedents' in aux:
        print(f"[PASS] Archivist Hook (precedents) found. Length: {len(aux['archivist_precedents'])}")
    else:
        print("[FAIL] Archivist Hook (precedents) missing.")
        all_passed = False

    # Coach Hook
    if 'step_coach' in aux:
        coach_data = aux['step_coach']
        print(f"[PASS] Coach Data in Aux: {list(coach_data.keys())}")
    else:
         print("[FAIL] Coach Data output missing from Aux.")
         all_passed = False

    if all_passed and pass_profiler and pass_archivist and pass_coach:
        print("\n\nSUCCESS: Courtroom 2.0 fully verified!")
    else:
        print("\n\nFAILURE: Some verifications failed.")

if __name__ == "__main__":
    asyncio.run(verify_courtroom_2_0())
