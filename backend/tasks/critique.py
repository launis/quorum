"""Panel Task (Critique).

Functional task for 'Panel' role.
Performs multi-perspective critique (Logic, Ethics, Causal, Performativity).
"""

import logging
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.llm.client import LLMClient
from backend.models.domain import TodistusKartta, PanelAudit
from backend.services.agent_registry import AgentRegistry
from backend.dependencies import get_async_repository

logger = logging.getLogger(__name__)


# --- Prompts ---

SYSTEM_PROMPT = """
Olet Kognitiivinen Paneeli (Cognitive Panel). Tehtäväsi on suorittaa moniulotteinen auditointi annetulle "Todistuskartalle" (analyysille).
Toimit samanaikaisesti useassa roolissa: Logikko, Eetikko, Kausaalisuustutkija ja Performatiivisuustarkkailija.

TEHTÄVÄT:
1. Logiikka (Logician): Auditoi argumentaation pätevyys (Toulmin, Walton).
2. Falsifiointi (Falsifier): Etsi aukkoja päättelyketjussa. Valheellinen logiikka?
3. Kausaalisuus (Causal): Onko syy-seuraussuhteet päteviä vai post-hoc rationalisointia?
4. Performatiivisuus (Detector): Onko teksti aitoa pohdintaa vai tekoäly-jargonia/teatteria?
5. Etiikka & Faktat (Overseer): Onko eettisiä riskejä tai fak virheitä?

SYÖTE:
Saat JSON-muotoisen Todistuskartan (sisältää hypoteesit ja todisteet).

TULOSTE:
Tuota validi JSON, joka vastaa `PanelAudit` -skeemaa. Konsolidoi kaikki näkökulmat yhteen rakenteeseen.
"""

# --- Handler ---


class PanelInput(BaseModel):
    """Input wrapper for Panel task."""
    todistus_kartta: TodistusKartta


@TaskRegistry.register_task(
    name="panel",
    input_schema=PanelInput, # Wrapped input
    output_schema=PanelAudit,
    description="Multi-perspective critique of the analysis."
)
async def panel_task(input_data: PanelInput) -> PanelAudit:
    """
    Executes the Panel LLM task.
    """
    llm_client = LLMClient()
    
    # Serialize input to JSON for the prompt
    input_json = input_data.todistus_kartta.model_dump_json(indent=2)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analysoi tämä Todistuskartta:\n{input_json}"}
    ]
    
    # Resolve Model (Zero-Fallback)
    # MUST match key in AgentRegistry (which uses class name 'PanelAgent')
    model_name = await _resolve_model_name("PanelAgent")

    result = await llm_client.run_structured_task(
        messages=messages,
        response_model=PanelAudit,
        model=model_name
    )
    
    return result


async def _resolve_model_name(agent_name: str) -> str:
    """Helper to resolve model name from AgentRegistry (Zero-Fallback)."""
    repo = await get_async_repository()
    registry = AgentRegistry(repo)
    await registry.discover_and_register_agents()
    
    config = registry.get_agent_config(agent_name)
    if not config or not config.model:
        raise ValueError(f"Could not resolve model for '{agent_name}' from DB (Zero-Fallback).")
        
    return config.model


# --- Class-Based Critic Registration ---

from backend.agents.critics import (
    LogicalFalsifierAgent,
    FactualOverseerAgent,
    CausalAnalystAgent,
    PerformativityDetectorAgent
)
from backend.models.domain import (
    LogiikkaAuditointi,
    EtiikkaJaFakta,
    KausaalinenAuditointi,
    PerformatiivisuusAuditointi
)

TaskRegistry.register_agent(
    task_keys=["falsifier"],
    agent_cls=LogicalFalsifierAgent,
    output_model=LogiikkaAuditointi
)

TaskRegistry.register_agent(
    task_keys=["overseer"],
    agent_cls=FactualOverseerAgent,
    output_model=EtiikkaJaFakta
)

TaskRegistry.register_agent(
    task_keys=["causal"],
    agent_cls=CausalAnalystAgent,
    output_model=KausaalinenAuditointi
)

TaskRegistry.register_agent(
    task_keys=["detector"],
    agent_cls=PerformativityDetectorAgent,
    output_model=PerformatiivisuusAuditointi
)




