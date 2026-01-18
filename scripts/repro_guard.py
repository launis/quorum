
import asyncio
import json
import logging
import os
import sys
from typing import Any

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append("c:/src/quorum")

# Imports after path setup
from backend.agents.guard import GuardAgent
from backend.settings import Settings
from backend.models.state import WorkflowState

# Mock needed components to run agent in isolation
# We need to simulate the GraphEngine's resolution of prompts.

DB_PATH = "c:/src/quorum/data/db.json"
TARGET_EXEC_ID = "ff5f84fb-ed55-4648-9c63-fbfa404dd96e"

def load_db_data():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_execution_inputs(db_data, exec_id):
    # Find execution in "executions" or similar if they are stored there.
    # The user found execution in db.json earlier.
    # db.json structure: {"workflows": ..., "executions": ...}
    executions = db_data.get("executions", {})
    target = executions.get(exec_id)
    if not target:
        raise ValueError(f"Execution {exec_id} not found in db.json")
    
    # Global inputs are usually in target["inputs"]
    return target.get("inputs", {})

def resolve_prompts_from_db(db_data, step_id="step_guard"):
    # We need to manually reconstruct the full system prompt from seed/db components
    # just like graph engine does. 
    # Or, we can just run the agent and let it do it?
    # GuardAgent.execute takes `config`. The config usually contains `llm_prompts` LIST of IDs.
    # The BaseAgent helper `_construct_system_instruction` takes this list and looks them up.
    # But BaseAgent usually fetches prompt components from a Repository.
    # We don't have the full app context here easily. 
    
    # SHORTCUT: We can Construct the prompt manually using the mapped IDs in the workflow definition
    # and the components in db.json["components"].
    
    workflows = db_data.get("workflows", {})
    # Find workflow used in execution.
    # We assume "sequential_audit_chain" from context.
    wf = workflows.get("1") # "1" is sequential_audit_chain ID usually? No, ID is string.
    # Actually keys in db["workflows"] are "1", "2"... 
    # Let's find one with id "sequential_audit_chain"
    
    target_wf = None
    for k, v in workflows.items():
        if v.get("id") == "sequential_audit_chain":
            target_wf = v
            break
            
    if not target_wf:
        raise ValueError("Workflow sequential_audit_chain not found")
        
    # Find step_guard config
    step_config = None
    for step in target_wf.get("steps", []):
        if step.get("id") == "step_guard":
            step_config = step.get("config", {})
            break
            
    if not step_config:
        raise ValueError("step_guard config not found")
        
    prompt_ids = step_config.get("llm_prompts", [])
    
    # Resolve these IDs from db["components"]
    components = db_data.get("components", {})
    
    resolved_texts = []
    
    # Iterate prompts and find content
    for pid in prompt_ids:
        # components structure is dict of id->component? Or list?
        # In the files view earlier: "components": {"1": {...}, "2": {...}}
        # But grep showed "components": [{"id":...}] in seed_data?
        # View of DB showed: "components": {"1": {"content": "...", "id": "HEADER_MANDATES"}}
        
        found = False
        for k, comp in components.items():
            if comp.get("id") == pid:
                resolved_texts.append(comp.get("content"))
                found = True
                break
        if not found:
            logger.warning(f"Prompt component {pid} not found in DB")
            
    full_prompt = "\n\n".join(resolved_texts)
    return full_prompt

async def run_guard():
    print(f"Loading data from {DB_PATH}...")
    db_data = load_db_data()
    
    print(f"Extracting inputs for {TARGET_EXEC_ID}...")
    try:
        inputs = extract_execution_inputs(db_data, TARGET_EXEC_ID)
    except ValueError as e:
        print(f"Error: {e}")
        # Fallback for testing if exec missing
        print("Using dummy inputs for testing conditional prompt...")
        inputs = {
            "history_text": "Tämä on testiteksti ilman mitään henkilötietoja. Vain yleistä keskustelua.",
            "product_text": "Tuote on valmis.",
            "reflection_text": "Reflektio."
        }
    
    print("Resolving system prompt from DB...")
    system_prompt = resolve_prompts_from_db(db_data)
    
    print("\n--- RESOLVED PROMPT SNIPPET (CHECKING FOR FIX) ---")
    if "TARKISTA:" in system_prompt:
        print("SUCCESS: Found 'TARKISTA:' in prompt.")
    else:
        print("FAILURE: 'TARKISTA:' not found in prompt!")
        
    # Instantiate Agent
    # We need to manually inject the prompt because we aren't using the full engine/repo stack
    # that usually resolves it. BaseAgent doesn't take raw prompt in constructor.
    # But `execute` takes `config`. 
    # However, BaseAgent logic looks up prompt IDs in `config['llm_prompts']`.
    # Since we don't have the Repo wired up in this script, that lookup would fail or need mocking.
    
    # EASIER: Subclass GuardAgent in script to override `_construct_system_instruction` 
    # or just Mock the method.
    
    agent = GuardAgent(model="vertex_ai/gemini-2.5-flash") # Use fast model as configured
    
    # Monkey patch _construct_system_instruction to return our resolved prompt
    # async def _construct_system_instruction(self, config: dict[str, Any]) -> str:
    async def mock_construct(config):
        return system_prompt
        
    agent._construct_system_instruction = mock_construct
    
    print("Executing GuardAgent...")
    
    print("Executing GuardAgent...")
    
    print(f"DEBUG: Input keys: {list(inputs.keys())}")
    
    from backend.models.state import InputData
    
    # Wrap inputs in InputData then WorkflowState
    try:
        # Construct InputData
        input_data = InputData(**inputs)
        
        workflow_state = WorkflowState(
            execution_id=TARGET_EXEC_ID,
            inputs=input_data,
            current_step_name="step_guard"
        )
    except Exception as e:
        print(f"Failed to construct WorkflowState: {e}")
        return

    try:
        # Pass WorkflowState object 
        result = await agent.execute(state=workflow_state)
        
        print("\n--- EXECUTION RESULT ---")
        # BaseAgent.execute returns WorkflowState, not AgentResult wrapper
        guard_output = result.step_guard
        print(guard_output) 
        
        data_content = guard_output.safe_data if guard_output else "NO OUTPUT"
        # If model returns object, pydantic to dict
        if hasattr(data_content, "model_dump"):
            print(data_content.model_dump())
        else:
             print(data_content)

        # Check for Hallucination
        res_str = str(guard_output)
        if "12345" in res_str or "Asiakasnumero" in res_str:
            print("\n[FAIL] HALLUCINATION DETECTED: Found 'Asiakasnumero' or '12345'")
        else:
            print("\n[PASS] NO HALLUCINATION DETECTED.")
            
    except Exception as e:
        print(f"Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_guard())
