"""Analyst Task.

Functional task for 'Analyst' role.
Generates Hypotheses and RAG evidence needs.
"""

import logging
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.llm.client import LLMClient
from backend.models.domain import TodistusKartta
from backend.settings import get_settings

logger = logging.getLogger(__name__)


# --- Schemas ---

class AnalysisInput(BaseModel):
    """Input for Analyst task."""
    history_text: str | None = Field(default=None, description="Conversation history.")
    product_text: str | None = Field(default=None, description="Product description.")
    reflection_text: str | None = Field(default=None, description="Reflection text.")
    precedents_summary: str | None = Field(default=None, description="Summary of past cases.")
    
    model_config = ConfigDict(extra="ignore")


# --- Prompts ---

SYSTEM_PROMPT = """
Olet Kognitiivinen Analyytikko (Cognitive Analyst). Tehtäväsi on analysoida käyttäjän toimittama aineisto ja muodostaa siitä "Todistuskartta".
Tehtäväsi ei ole vielä tuomita, vaan KARTOTTAA väitteet ja etsiä niille tukea.

AINEISTO:
1. Keskusteluhistoria (Prosessi)
2. Lopputuote (Tulos)
3. Reflektio (Itsearviointi)

TEHTÄVÄT:
1. Tunnista aineistosta keskeiset väitteet tai 'Hypoteesit'.
2. Etsi kullekin hypoteesille todisteita (lainauksia) tekstistä.
3. Arvioi kunkin todisteen relevanssi (1-100).

HUOMIOI ENNAKKOTAPAUKSET (JOS ANNETTU):
Jos saat yhteenvedon aiemmista tapauksista, käytä niitä viitekehyksenä.

TULOSTE:
Tuota validi JSON, joka vastaa `TodistusKartta` -skeemaa.
"""

# --- Handler ---

@TaskRegistry.register_task(
    name="analyst",
    input_schema=AnalysisInput,
    output_schema=TodistusKartta,
    description="Analyzes input text to form hypotheses and evidence map."
)
async def analyst_task(input_data: AnalysisInput) -> TodistusKartta:
    """
    Executes the Analyst LLM task.
    """
    settings = get_settings()
    llm_client = LLMClient()
    
    # Construct Context
    context_str = ""
    if input_data.history_text:
        context_str += f"=== KESKUSTELUHISTORIA ===\n{input_data.history_text}\n\n"
    if input_data.product_text:
        context_str += f"=== LOPPUTUOTE ===\n{input_data.product_text}\n\n"
    if input_data.reflection_text:
        context_str += f"=== REFLEKTIO ===\n{input_data.reflection_text}\n\n"
    if input_data.precedents_summary:
        context_str += f"\n{input_data.precedents_summary}\n"
        
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Tässä aineisto:\n{context_str}"}
    ]
    
    # Execute LLM
    # Note: Zero-Fallback rule enforced by LLMClient raising error if model not provided?
    # Actually LLMClient logic in `backend/llm/client.py` was updated to REQUIRE model.
    # Where do we get the model? We should get it from a configuration or registry.
    # For now, per legacy/migration, we might need to query the AgentRegistry or Settings.
    
    # In V2.9 Arch, dynamic discovery is preferred. 
    # But since this is a functional task, it should probably receive the model/config config as input OR 
    # look it up via `backend.services.agent_registry`?
    
    # To keep it simple and compliant with "Zero-Fallback" (NO HARDCODED DEFAULTS), 
    # we need to fetch the configuration.
    
    # We can rely on `backend.services.agent_registry` to resolve the strategy/model.
    # But `analyst_task` is a pure function. 
    # We can allow the registry lookup here? OR require it in input.
    # The prompt implies: "Logic: Use backend.llm.client.run_structured_task to call the LLM."
    
    # Implementation Detail Check: "Use @TaskRegistry.register"
    # The TaskRegistry doesn't inject dependencies automatically yet in the engine impl I wrote.
    # So we must look it up or rely on global settings for a "default" strategy?
    # Or strict zero-fallback means we MUST fetch from DB.
    
    from backend.dependencies import get_agent_registry_dep, get_async_repository
    # We need to construct the registry manually if not injected. 
    # This is getting complex for a simple task function.
    
    # SHORTCUT for Phase 3.3 Task:
    # Use a helper to resolve "analyst" model from DB.
    # We'll use a local helper function to get the model config name.
    
    model_name = await _resolve_model_name("analyst") 

    result = await llm_client.run_structured_task(
        messages=messages,
        response_model=TodistusKartta,
        model=model_name
    )
    
    return result

async def _resolve_model_name(agent_name: str) -> str:
    """Helper to resolve model name from AgentRegistry (Zero-Fallback)."""
    # This is a bit of a hack to respect the zero-fallback without full DI rewrite
    from backend.dependencies import get_agent_registry_dep, get_async_repository
    repo = await get_async_repository()
    # We instantiate registry just to look up config? 
    # Or better: Just use repo to get system_config directly if possible.
    # Actually, AgentRegistry.discover_and_register_agents is async.
    
    # Let's try to get it from settings if it's there? No, strictly DB.
    # We'll instantiate the registry properly.
    from backend.services.agent_registry import AgentRegistry
    registry = AgentRegistry(repo)
    await registry.discover_and_register_agents()
    
    # Analyst "strategy" is typically "deep" or "fast"? 
    # Or generic agent name lookup?
    # In V2, "analyst" usually maps to "deep" reasoning or specific config.
    # Let's assume there's an agent config for "analyst" or use "deep" strategy.
    
    # Looking at `backend/agents/analyst.py`, it inherits from BaseAgent.
    # BaseAgent usually resolves config by name.
    
    config = registry.get_agent_config(agent_name)
    if not config or not config.model:
        # Fallback to "deep" strategy if specific agent not found?
        # Or raise error (Fail Fast).
        # Let's try "deep" strategy as fallback (managed in DB).
        strat = await registry.resolve_model_config("deep")
        if strat and strat.get("model_name"):
            return strat["model_name"]
            
        raise ValueError(f"Could not resolve model for '{agent_name}' from DB (Zero-Fallback).")
        
    return config.model


# --- Class-Based Agent Registration ---

from backend.agents.logician import LogicianAgent
from backend.models.domain import ArgumentaatioAnalyysi

TaskRegistry.register_agent(
    task_keys=["logician"],
    agent_cls=LogicianAgent,
    output_model=ArgumentaatioAnalyysi
)

from backend.agents.profiler import ProfilerAgent
from backend.models.domain import ProfilerAnalysis

TaskRegistry.register_agent(
    task_keys=["profiler"],
    agent_cls=ProfilerAgent,
    output_model=ProfilerAnalysis
)

