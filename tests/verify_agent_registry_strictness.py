
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import logging
from backend.core.registry import TaskRegistry
from backend.agents.analyst import AnalystAgent, AnalystInput
from backend.agents.logician import LogicianAgent, LogicianInput
from backend.agents.critics import LogicalFalsifierAgent, FalsifierInput
from backend.agents.critics import FactualOverseerAgent, OverseerInput
from backend.agents.critics import CausalAnalystAgent, CausalInput
from backend.agents.critics import PerformativityDetectorAgent, PerformativityInput
from backend.agents.panel import PanelAgent, PanelInput

# Mock Registration trigger
# Agents are usually registered via decorator or explicit call in `backend.agents.__init__` or `backend.bootstrap`?
# Let's inspect `backend/agents/__init__.py` to see how they are registered.
# If they use @register_agent decorator, they might be registered on import.
# But `TaskRegistry.register_agent` is checks `cls.agents_map`.

async def verify_registry():
    print("Verifying TaskRegistry strictness...")
    
    # Manually register for testing if not auto-registered
    # Usually `backend.bootstrap` handles this.
    # Let's simulate what `bootstrap` does or just call register_agent manually for test.
    
    # 1. Analyst
    TaskRegistry.register_agent(["step_analyst"], AnalystAgent, AnalystAgent.OUTPUT_SCHEMA)
    analyst_task = TaskRegistry.get("step_analyst")
    if analyst_task.input_schema == AnalystInput:
        print("✅ AnalystAgent registered with AnalystInput")
    else:
        print(f"❌ AnalystAgent registered with {analyst_task.input_schema}")

    # 2. Logician
    TaskRegistry.register_agent(["step_logician"], LogicianAgent, LogicianAgent.OUTPUT_SCHEMA)
    logician_task = TaskRegistry.get("step_logician")
    if logician_task.input_schema == LogicianInput:
        print("✅ LogicianAgent registered with LogicianInput")
    else:
        print(f"❌ LogicianAgent registered with {logician_task.input_schema}")

    # 3. Falsifier
    TaskRegistry.register_agent(["step_falsifier"], LogicalFalsifierAgent, LogicalFalsifierAgent.OUTPUT_SCHEMA)
    falsifier_task = TaskRegistry.get("step_falsifier")
    if falsifier_task.input_schema == FalsifierInput:
        print("✅ LogicalFalsifierAgent registered with FalsifierInput")
    else:
        print(f"❌ LogicalFalsifierAgent registered with {falsifier_task.input_schema}")

    # 4. Overseer (FactualOverseerAgent)
    TaskRegistry.register_agent(["step_overseer"], FactualOverseerAgent, FactualOverseerAgent.OUTPUT_SCHEMA)
    overseer_task = TaskRegistry.get("step_overseer")
    if overseer_task.input_schema == OverseerInput:
        print("✅ FactualOverseerAgent registered with OverseerInput")
    else:
        print(f"❌ FactualOverseerAgent registered with {overseer_task.input_schema}")

    # 5. Causal
    TaskRegistry.register_agent(["step_causal"], CausalAnalystAgent, CausalAnalystAgent.OUTPUT_SCHEMA)
    causal_task = TaskRegistry.get("step_causal")
    if causal_task.input_schema == CausalInput:
        print("✅ CausalAnalystAgent registered with CausalInput")
    else:
        print(f"❌ CausalAnalystAgent registered with {causal_task.input_schema}")

    # 6. Detector (PerformativityDetectorAgent)
    TaskRegistry.register_agent(["step_detector"], PerformativityDetectorAgent, PerformativityDetectorAgent.OUTPUT_SCHEMA)
    detector_task = TaskRegistry.get("step_detector")
    if detector_task.input_schema == PerformativityInput:
        print("✅ PerformativityDetectorAgent registered with PerformativityInput")
    else:
        print(f"❌ PerformativityDetectorAgent registered with {detector_task.input_schema}")

    # 7. Panel (PanelAgent)
    TaskRegistry.register_agent(["step_panel"], PanelAgent, PanelAgent.OUTPUT_SCHEMA)
    panel_task = TaskRegistry.get("step_panel")
    if panel_task.input_schema == PanelInput:
        print("✅ PanelAgent registered with PanelInput")
    else:
        print(f"❌ PanelAgent registered with {panel_task.input_schema}")


if __name__ == "__main__":
    asyncio.run(verify_registry())
