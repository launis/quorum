import sys
import os
sys.path.append(os.getcwd())
from backend.services.agent_registry import AgentRegistry
from backend.database.wrapper import get_db_client
from backend.database.repository import TinyDBRepository
from backend.agents.profiler import ProfilerAgent
from backend.settings import get_settings

print("--- DIAGNOSTIC START ---")
try:
    # 1. DB
    settings = get_settings()
    print(f"DB Path: {settings.start_db_path}") 
    
    db = get_db_client()
    repo = TinyDBRepository(db)
    registry = AgentRegistry(repo)
    
    # 2. Strategies
    fast = registry.resolve_model_name("fast")
    print(f"Fast Strategy Model: {fast}")
    
    # 3. Check Registry Loading
    registry.discover_and_register_agents()
    reg_agent = registry.get_agent("ProfilerAgent")
    print(f"Registered Profiler Model: {reg_agent.model}")
    
    # 3.6 Check Display Key
    if reg_agent.model == fast:
        print("DISPLAY LOGIC: Match (Fast)")
    else:
        print(f"DISPLAY LOGIC: Mismatch ({reg_agent.model} != {fast})")
    
    # 4. Schema
    print("Checking Schema Generation...")
    schema = reg_agent.get_response_schema()
    if schema:
        if hasattr(schema, 'model_json_schema'):
            js = schema.model_json_schema()
            print("Schema generated (V2). Properties:", list(js.get('properties', {}).keys()))
        elif hasattr(schema, 'schema'):
            js = schema.schema()
            print("Schema generated (V1).")
        else:
            print("SCHEMA FAILED: No conversion method found.")
    else:
        print("SCHEMA FAILED: get_response_schema returned None")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("--- DIAGNOSTIC END ---")
