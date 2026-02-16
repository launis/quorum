
import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# SUPPRESS LOGS
logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
logging.getLogger("backend").setLevel(logging.ERROR)
logging.getLogger("litellm").setLevel(logging.ERROR)

sys.modules["backend.llm.factory"] = MagicMock()
from backend.llm.factory import LLMFactory

LLMFactory.create_provider.return_value = MagicMock()

from backend.agents.coach import CoachAgent
from backend.agents.logician import LogicianAgent
from backend.agents.panel import PanelAgent


async def debug():
    print("--- COACH ---")
    try:
        agent = CoachAgent(model="gpt-4o-mini", provider="openai")
        await agent.execute(input_data={"history_text": "foo"}, execution_context={})
        print("COACH: No exception raised")
    except Exception as e:
        print(f"COACH: Raised {type(e).__name__}: '{str(e)}'")

    print("--- LOGICIAN ---")
    try:
        agent = LogicianAgent(model="gpt-4o-mini", provider="openai")
        await agent.execute(input_data={}, execution_context={})
        print("LOGICIAN: No exception raised")
    except Exception as e:
        print(f"LOGICIAN: Raised {type(e).__name__}: '{str(e)}'")

    print("--- PANEL ---")
    try:
        agent = PanelAgent(model="gpt-4o-mini", provider="openai")
        await agent.execute(input_data={"history_text": "foo"}, execution_context={})
        print("PANEL: No exception raised")
    except Exception as e:
        print(f"PANEL: Raised {type(e).__name__}: '{str(e)}'")

if __name__ == "__main__":
    asyncio.run(debug())
