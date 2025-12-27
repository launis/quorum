import json
from datetime import datetime
from backend.database.wrapper import get_db_client
from backend.database.repository import TinyDBRepository

def register_types():
    client = get_db_client()
    db = TinyDBRepository(client)
    
    # Define the standard types requested
    types_list = [
        "prompt", 
        "rule", 
        "mandate", 
        "instruction", 
        "header", 
        "task",  # New requirement
        "bars"   # New requirement
    ]
    
    # Create the configuration component
    type_registry = {
        "id": "SYSTEM_COMPONENT_TYPES",
        "name": "System Component Types Registry",
        "type": "system_config",
        "description": "Registry of valid component types for the UI dropdown.",
        "content": json.dumps(types_list), # Store as JSON string in content
        "registered_at": datetime.now().isoformat()
    }
    
    print(f"Registering types: {types_list}")
    
    # Upsert into components table
    print(f"Registering types: {types_list}")
    
    # Check existence
    existing = db.get_component_by_id("SYSTEM_COMPONENT_TYPES")
    if existing:
        print("Updating existing registry...")
        from tinydb import Query
        Q = Query()
        db.components.remove(Q.id == "SYSTEM_COMPONENT_TYPES")
    
    db.register_component(type_registry)
    print("Success! SYSTEM_COMPONENT_TYPES registered.")

if __name__ == "__main__":
    register_types()
