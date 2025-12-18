import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from backend.dependencies import (
        get_db_client_dep, 
        get_repository_dep, 
        get_agent_registry_dep, 
        get_prompt_builder_dep,
        get_storage_service_dep,
        get_document_service_dep
    )
    from backend.core.engine import WorkflowEngine
    from backend.config import DB_PATH

    print("Resolving dependencies...")
    db_client = get_db_client_dep()
    repository = get_repository_dep(db_client)
    registry = get_agent_registry_dep(repository) # Repository is dependency
    prompt_builder = get_prompt_builder_dep(repository, registry)
    storage_service = get_storage_service_dep()
    document_service = get_document_service_dep(storage_service)
    
    print("Instantiating Engine...")
    engine = WorkflowEngine(
        db_path=DB_PATH,
        repository=repository,
        registry=registry,
        prompt_builder=prompt_builder,
        storage_client=storage_service,
        document_service=document_service
    )
    print("Engine instantiated successfully.")
    print(f"Document Service: {engine.document_service}")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
