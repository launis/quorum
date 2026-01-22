import asyncio
from backend.core.registry import TaskRegistry
from backend.agents.base import BaseAgent
from pydantic import BaseModel

class DummyAgent(BaseAgent):
    async def execute(self, *args, **kwargs):
        print("AGENT EXECUTE REACHED")
        return {}

async def run():
    print("STARTING DEBUG RUN")
    TaskRegistry.register_agent(["debug_task"], DummyAgent, dict)
    handler = TaskRegistry.get("debug_task").handler
    print(f"HANDLER: {handler}")
    
    class Input(BaseModel):
        x: int = 1
        
    try:
        await handler(Input(x=1), execution_config={"test": "config"})
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(run())
