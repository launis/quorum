import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from backend_v2.database.factory import get_repository
from backend_v2.settings import get_settings
from backend_v2.models.state import StateProjector
from backend_v2.core.hook_registry import HookDependencies, HookState
import backend_v2.hooks.synthesis  # Varmistetaan että hook rekisteröityy

async def main():
    print("Haetaan tietokanta ja ajo...")
    repo = await get_repository(get_settings())
    execution_id = "exe_72097b1a21a64fb0b5915c1e55698536"
    profile_id = "prf_7cc661da3f9f405c"
    
    execution = await repo.get_execution(execution_id)
    if not execution:
        print(f"Execution {execution_id} ei löytynyt!")
        return
        
    projector = StateProjector()
    for evt in execution.execution_trace:
        projector.apply_delta(evt)
    final_inputs = projector.snapshot
    
    print("\n=== LÄHTÖTILANNE (StateProjector Snapshotin avaimet ja sisällön koko) ===")
    for k, v in final_inputs.items():
        val_str = str(v)
        val_preview = val_str[:100].replace('\n', ' ') + "..." if len(val_str) > 100 else val_str
        print(f" - [{k}]: data_type={type(v).__name__}, string_length={len(val_str)}")
        
    print(f"\n--- Ajetaan text_consolidation_hook profiilille {profile_id} ---")
    metadata = getattr(execution, "metadata", {}) or {}
    if isinstance(metadata, dict):
        metadata["target_profile_id"] = profile_id

    state = HookState(
        execution_id=execution_id, 
        workflow_id=execution.workflow_id, 
        inputs=final_inputs, 
        metadata=metadata
    )
    deps = HookDependencies(repository=repo)
    
    from backend_v2.core.hook_registry import hook_registry
    try:
        hook_res = await hook_registry.execute("text_consolidation_hook", state, deps)
        if hook_res.success:
            print("\n=== LOPPUTULOS (Syntetisoitu Markdown) ===")
            print(hook_res.state_delta.get("synthesized_markdown", ""))
        else:
            print("\n=== HOOK EPÄONNISTUI ===")
    except Exception as e:
        print("\n=== HOOK KAATUI ===")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
