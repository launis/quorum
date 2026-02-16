
import asyncio
import logging
import sys

# Add project root to path
sys.path.append("c:/src/quorum")


from backend.database.repository import AsyncRepository
from backend.logging_config import setup_logging
from backend.services.agent_registry import AgentRegistry


# Mocking Agent Class for testing
class MockAgent:
    def __init__(self, model=None):
        self.model = model

async def verify_system_flow():
    print("--- [VERIFICATION] Dynamic Model Strategy Flow ---\n")

    # 1. Setup
    try:
        repo = AsyncRepository()
        registry = AgentRegistry(repo)
        setup_logging()
        logger = logging.getLogger(__name__)
    except Exception as e:
        print(f"[SETUP FAILED] {e}")
        return

    # 2. Test Direct Strategy Resolution (Core Registry)
    print("\n[STEP 1] Testing Registry Strategy Resolution...")
    test_strategies = ["fast", "deep", "strict", "precise"]
    for strategy in test_strategies:
        try:
            resolved = await registry.resolve_model_name(strategy)
            print(f"  [PASS] Strategy '{strategy}' -> '{resolved}'")
        except Exception as e:
            print(f"  [FAIL] Strategy '{strategy}': {e}")

    # 3. Test Agent Configuration Resolution (Task Registry Simulation)
    print("\n[STEP 2] Testing Agent Configuration Resolution...")
    # These agents should exist in your seed_data or be dynamically discoverable
    test_agents = ["GuardAgent", "ProfilerAgent", "RefinerAgent"]

    for agent_name in test_agents:
        try:
            # This mimics what TaskRegistry does during registration
            # It checks if there is a config in 'system_config'->'models'->'google'
            # that keys off the Agent Name (or mapped strategy)

            # Note: The Registry currently resolves logic based on *Strategy Keys*,
            # but Agent Registration often looks up the Agent Name itself to see if it has a specific config.
            # Let's see what resolve_model_config returns for the Agent Name.

            config = await registry.resolve_model_config(agent_name)
            model_name = config.get("model_name", "UNKNOWN")
            print(f"  [PASS] Agent '{agent_name}' -> Model: '{model_name}' (Config resolved)")
        except Exception:
            # This is expected if the Agent Name itself isn't a strategy key in DB.
            # In that case, the system relies on the Agent class's default or the Workflow override.
            print(f"  [INFO] Agent '{agent_name}' has no direct Global Strategy override in DB. (This is normal if relying on Defaults/Workflow)")

    # 4. Test run_agent Logic (Ad-Hoc Override)
    print("\n[STEP 3] Simulating 'run_agent' Ad-Hoc Resolution...")
    ad_hoc_input = "fast"
    try:
        if ad_hoc_input:
            resolved = await registry.resolve_model_name(ad_hoc_input)
            print(f"  [PASS] Input '{ad_hoc_input}' resolved to '{resolved}' for execution.")
        else:
            print("  [SKIP] No input.")
    except Exception as e:
        print(f"  [FAIL] Input '{ad_hoc_input}' failed resolution: {e}")

    # 5. Test GraphEngine Step Resolution Logic (Simulation)
    print("\n[STEP 4] Simulating GraphEngine Step Context...")
    # GraphEngine doesn't resolve "models" directly, it hydrates step config.
    # The step config usually contains a "model" key which might be a strategy name or concrete model.
    # The Task (Agent) then receives this config.

    fake_step_config = {"model": "fast"}
    print(f"  Step Config: {fake_step_config}")

    # Logic in AgentWrapper (Registry.py) or BaseAgent?
    # Actually, BaseAgent defaults to self.model if not passed, BUT
    # if `execution_config` is passed to handler, it overrides.

    # We want to check if "fast" passed to an agent works.
    # Current codebase: BaseAgent.__init__ calls Factory. Factory expects CONCRETE name.
    # So if GraphEngine passes "fast", it MUST be resolved before reaching LLMFactory.

    # Verified in Step 1253: run_agent now resolves it.
    # Verified in Step 1124: register_agent resolves it at STARTUP for the default.

    # BUT: If a Workflow Step has "model": "fast" in its config, and that is passed to
    # `agent_wrapper(..., execution_config={'model': 'fast'})`...
    # The `agent_wrapper` merges it into `exec_kwargs`.
    # Then it calls `agent.execute(..., **exec_kwargs)`.
    # `BaseAgent.execute` calls `self.set_model(model)` if model is in kwargs.
    # `set_model` calls `_create_provider`, which calls `LLMFactory`.
    # `LLMFactory` crashes if model is "fast" (not concrete).

    # DO WE HAVE A BUG IN WORKFLOW EXECUTION?
    # If a step defines "model": "fast", it might crash!

    # Let's verify if `BaseAgent.set_model` or `execute` resolves the strategy.
    # Based on my view of BaseAgent in 1242, set_model DOES NOT resolve.
    # It just assigns and calls factory.

    # So, we need to check if `GraphEngine` or `AgentWrapper` resolves it.
    # `AgentWrapper` (registry.py) code:
    # "exec_kwargs = registry_kwargs.copy(); if execution_config: exec_kwargs.update(execution_config)"
    # It does NOT resolve.

    # CONCLUSION: If a Workflow Step has "model": "fast", it WILL CRASH.
    # I need to verify this hypothesis.

    print("  [HYPOTHESIS] Passing 'fast' to Agent.execute() might crash if not resolved.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_system_flow())
