import asyncio

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.core.registry import TaskRegistry


class DummyAgent(BaseAgent):
    async def execute(self, *args, **kwargs):
        print("AGENT EXECUTE REACHED")
        return {}


async def run():
    print("STARTING DEBUG RUN")
    
    class DummyOutput(BaseModel):
        pass

    TaskRegistry.register_agent(["debug_task"], DummyAgent, DummyOutput)
    task_def = TaskRegistry.get("debug_task")
    assert task_def is not None
    handler = task_def.handler
    print(f"HANDLER: {handler}")

    class Input(BaseModel):
        x: int = 1

    try:
        await handler(Input(x=1), execution_config={"test": "config"})
    except Exception as e:
        print(f"EXCEPTION: {e}")


if __name__ == "__main__":
    asyncio.run(run())
