
import asyncio
import os
import sys

# Ensure backend matches path
sys.path.append(os.getcwd())

from backend.settings import get_settings
from backend.agents.panel import PanelAgent
from backend.services.agent_registry import AgentRegistry
from backend.dependencies import get_async_repository
from backend.llm.provider import MockProvider, LiteLLMProvider

async def main():
    print("--- DIAGNOSTIC START ---")
    settings = get_settings()
    print(f"Settings.use_mock_llm: {settings.use_mock_llm} (Type: {type(settings.use_mock_llm)})")
    
    # Check Registry
    try:
        repo = await get_async_repository()
        registry = AgentRegistry(repo)
        
        print("\n--- REGISTRY RESOLUTION ---")
        model_name = await registry.resolve_model_name("PanelAgent")
        print(f"Resolved Model Name: '{model_name}'")
        
        try:
            model_config = await registry.resolve_model_config("PanelAgent")
            print(f"Resolved Model Config: {model_config}")
        except Exception as e:
            print(f"Note: resolve_model_config failed (might be private/missing): {e}")

    except Exception as e:
        print(f"Repository/Registry Setup Failed: {e}")
        model_name = "ERROR"

    print("\n--- AGENT INSTANTIATION ---")
    agent = PanelAgent()
    print(f"Initial Agent Model: {agent.model}")
    print(f"Initial Agent Provider Type: {agent.provider_type}")
    print(f"Initial Agent LLMProvider: {type(agent.llm_provider)}")
    
    if model_name != "ERROR":
        print(f"\nCalling set_model('{model_name}')...")
        agent.set_model(model_name)
        print(f"Updated Agent Model: {agent.model}")
        print(f"Updated Agent Provider Type: {agent.provider_type}")
        print(f"Updated Agent LLMProvider: {type(agent.llm_provider)}")
        
        if isinstance(agent.llm_provider, MockProvider):
            print("ALERT: Provider IS MockProvider!")
        elif isinstance(agent.llm_provider, LiteLLMProvider):
             print(f"Provider is LiteLLMProvider. Model: {agent.llm_provider.model_name}")

    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    asyncio.run(main())
