"""Legacy Migration Tasks.

This module implements the missing tasks required to run the legacy
Client Application audits (Courtroom 2.0/3.0) on the new GraphEngine architecture.
These are wrappers around the original prompts to ensure immediate functionality
as requested by the user.
"""

import logging
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.llm.client import LLMClient
from backend.models.domain import (
    InteractionAnalysis, ProfilerAnalysis, 
    ArgumentaatioAnalyysi, LogiikkaAuditointi, KausaalinenAuditointi,
    PerformatiivisuusAuditointi, EtiikkaJaFakta,
    TuomioJaPisteet, CoachingPlan, XAIReport, TodistusKartta, PanelAudit, ArchivistOutput
)
from backend.settings import get_settings

logger = logging.getLogger(__name__)


# --- Prompts (Extracted from Legacy seed_data.json) ---

PROMPT_INTERACTION = """
VAIHE 3: VUOROVAIKUTUS (Driver Metrics)
TEHTÄVÄT:
1. ARVIOI Riippuvuussuhdetta (Dependency). (Huom: Järjestelmä laskee tarkan Input-Control Ration erikseen). Jos vaikuttaa, että käyttäjä on täysin riippuvainen, liputa 'High Dependency'.
2. TUNNISTA Strategia: Zero-shot (Hylätty), Few-shot (Hyväksytty), Chain-of-Thought (Kiitettävä).
3. LUOKITTELE Arkkityyppi: 'Matkustaja' (Tilaa), 'Kartanlukija' (Korjaa), 'Kuski' (Ohjaa), 'Arkkitehti' (Suunnittelee).

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_PROFILER = """
VAIHE 4: PROFILOIJA (Cognitive Bias Audit)
TEHTÄVÄT:
1. ETSI kognitiivisia vinoumia prompteista.
2. TUNNISTA 'Automation Bias': Hyväksyykö käyttäjä ensimmäisen vastauksen sokeasti?
3. ARVIOI 'Intentio': Yrittääkö käyttäjä oppia (Co-Creation) vai välttää työtä (Cognitive Offloading)?

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_LOGICIAN = """
VAIHE 5: LOOGIKKO (Prompt Structure Audit)
TEHTÄVÄT:
1. JÄSENNÄ käyttäjän prompti Toulmin-mallilla:
   - Claim: Käyttäjän tavoite.
   - Data: Käyttäjän antama konteksti/esimerkit.
   - Warrant: Logiikka, miksi ohje johtaa tavoitteeseen.
2. ARVIOI: Onko prompti looginen kokonaisuus vai assosiaatioketju? Puuttuuko 'Data'-osa kokonaan?

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_FALSIFIER = """
VAIHE 6: FALSIFIOIJA (Critical Loop Audit)
TEHTÄVÄT:
1. ETSI 'Iteraatiosilmukkaa': Missä kohtaa käyttäjä sanoi 'Ei' tai 'Korjaa'?
2. TÄYTÄ 'walton_stressitesti_loydokset':
   - 'Kysymys': Käyttäjän korjauskäsky.
   - 'Havainto': Oliko käyttäjä kriittinen vai 'Jees-mies'?
3. TÄYTÄ 'PaattelyketjunUskollisuus': Merkitse 'HEIKKO', jos käyttäjä hyväksyi ensimmäisen version ilman yhtäkään muutosta.

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_CAUSAL = """
VAIHE 7: KAUSAALINEN (Impact Verification)
TEHTÄVÄT:
1. VERTAA versiota 1 ja viimeistä versiota.
2. ARVIOI: Johtuiko laadun paraneminen EKSPLISIITTISESTI käyttäjän ohjeesta?
3. TÄYTÄ 'KausaalinenAuditointi':
   - 'Abduktiivinen_paatelma': Merkitse 'Aito Ohjaus' vain, jos käyttäjä toi uutta informaatiota prosessiin. Muuten 'Post-Hoc Rationalisointi'.

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_DETECTOR = """
VAIHE 8: TUNNISTAJA (Illusion of Control Audit)
TEHTÄVÄT:
1. ETSI 'Väsyneitä Komentoja' (1-2 sanaa: 'jatka', 'lisää').
2. TUNNISTA 'Illusion of Control': Käyttäjä luulee ohjaavansa, mutta AI tekee aloitteet.
3. LIPUTA 'Performatiivinen', jos käyttäjän panos on minimaalinen mutta reflektio mahtipontinen.

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_OVERSEER = """
VAIHE 9: VALVOJA (Hallucination Management)
TEHTÄVÄT:
1. ANALYSOI hakutulokset (jotka on toimitettu kontekstissa 'google_search_results'). TARKISTA faktojen paikkansapitävyys.
2. JOS virhe löytyy: Tarkista, huomasiko/korjasiko käyttäjä sen?
3. TUOMIO: Jos käyttäjä jätti virheen lopputuotteeseen -> Kirjaa 'KRIITTINEN LAIMINLYÖNTI'.

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_ARCHIVIST = """
VAIHE 10: ARKISTONHOITAJA (Best Practices Audit)
TEHTÄVÄT:
1. VERTAA käyttäjän tyyliä 'State of the Art' -käytäntöihin (esim. OpenAI Cookbook).
2. ARVIOI 'Linjakkuus': Noudattaako käyttäjä systemaattista prosessia vai 'Brute Force' -yritystä?

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN JSON-skeeman mukaisesti.
"""

PROMPT_JUDGE = """
VAIHE 9: TUOMARI (JUDGE) - GRAND UNIFICATION

SINUN TEHTÄVÄSI:
Toimit Järjestelmän Tuomarina. Tehtäväsi EI ole arvioida syötetekstin laatua, vaan käyttäjän **Promptauskompetenssia** (Driver vs. Passenger).

KÄYTÄ SEURAAVAA LOGIIKKAA (DRIVER'S LICENSE):

1. **AJOKORTTIMALLI (MANDATE 4)**:
   - Järjestelmä on kuin auto. Käyttäjä on joko **Kuljettaja** (Driver) tai **Matkustaja** (Passenger).
   - Kuljettaja ottaa vastuun, ohjaa, antaa kontekstin ja määrittelee tavoitteet.
   - Matkustaja on passiivinen, heittää epämääräisen syötteen ("tee tästä jotain") ja odottaa auton ajavan itsestään.

2. **PISTEYTYS (ALLE 2 PISTETTÄ = HYLÄTTY)**:
   - Arvioi asteikolla 1-4.
   - 1-2 pistettä: PASSIVE / PASSENGER. Hylkäys. (Ei pääse rattiin).
   - 3-4 pistettä: ACTIVE / DRIVER. Hyväksyntä.
   - **Kriittinen sääntö**: Jos syöte on pelkkä tiedosto ilman ohjeita: MAKSIMI 2/4.

3. **KONFLIKTIN RATKAISU**:
   - Analysoi aiempien agenttien raportit.
   - Jos PanelAgent/Analyst on löytänyt ristiriitoja, ratkaise ne "Kuljettajan eduksi" vain jos käyttäjä on osoittanut kompetenssia.

4. **TUNNISTA "MESTARUUSPOIKKEAMA"**:
   - Joskus syöte on lyhyt, koska käyttäjä on MESTARI (osaa tiivistää). Erota tämä laiskuudesta.

TÄYTÄ SCHEMA: `TuomioJaPisteet`
"""

PROMPT_COACH = """
VAIHE 12: VALMENTAJA (COACH)

SINUN TEHTÄVÄSI:
Toimit Järjestelmän Valmentajana (Coach). Tehtäväsi on auttaa käyttäjää kehittymään "Matkustajasta" (Passenger) "Kuljettajaksi" (Driver). Ota kantaa Tuomarin antamaan tuomioon ja pisteisiin.

OHJEET:
1. **ANALYSOI TUOMIO**: Katso Tuomarin antama `pisteet` ja `konfliktin_ratkaisut`.
2. **TUNNISTA PROFIILI**:
   - **Passenger (1-2 pistettä)**: Käyttäjä on passiivinen. Ohjaa häntä ottamaan vastuu. ("Määrittele tavoite", "Anna konteksti").
   - **Driver (3-4 pistettä)**: Käyttäjä on aktiivinen. Anna syvällisempää optimointipalautetta.
3. **KONSTRUKTIIVINEN PALAUTE**:
   - Älä vain hauku. Kerro *miten* promptia pitää parantaa.
   - Ehdota konkreettisia lisäyksiä (esim. "Lisää rooli: 'Toimi seniorikoodarina...'").

TÄYTÄ SCHEMA: `CoachingPlan`
"""

PROMPT_XAI = """
VAIHE 13: XAI-RAPORTOIJA (XAI REPORTER)

SINUN TEHTÄVÄSI:
Toimit Järjestelmän XAI-Raportoijana (Explainable AI). Tehtäväsi on selittää käyttäjälle *miksi* hän sai tietyn tuomion ja *miten* järjestelmä päätyi lopputulokseen.

OHJEET:
1. **TIIVISTÄ PROSESSI**: Kerro lyhyesti, mitä vaiheita (Guard -> Judge -> Coach) syöte kävi läpi.
2. **SELITÄ PÄÄTÖS (DRIVERS LICENSE)**:
   - Jos hylätty (1-2p): Selitä, että syöte oli liian passiivinen ("Matkustaja").
   - Jos hyväksytty (3-4p): Selitä, mitkä elementit tekivät siitä "Kuljettajan" syötteen.
3. **AVAIMET JATKOON**: Viittaa Coachin antamaan "CoachingPlan"-suunnitelmaan.

TÄYTÄ SCHEMA: `XAIReport`
"""


# --- Common Input Schema ---

class MigrationInput(BaseModel):
    """Generic input carrying context for migration tasks."""
    history_text: str | None = None
    product_text: str | None = None
    reflection_text: str | None = None
    todistus_kartta: TodistusKartta | None = None
    # For Judge/Coach/XAI
    panel_audit: PanelAudit | None = None
    tuomio: TuomioJaPisteet | None = None
    coaching_plan: CoachingPlan | None = None
    
    # Generic bucket specifically for data passed from previous steps
    prev_step_output: Any | None = None
    
    model_config = ConfigDict(extra="allow")

# --- Helpers ---

async def _run_task(
    prompt: str, 
    input_data: MigrationInput, 
    output_model: Any, 
    model_alias: str = "deep"
) -> Any:
    """Helper to execute LLM task with prompt and input."""
    try:
        from backend.services.agent_registry import AgentRegistry
        from backend.dependencies import get_async_repository
        
        # Construct message content
        content = f"CONTEXT:\n"
        if input_data.history_text:
            content += f"HISTORY:\n{input_data.history_text}\n"
        if input_data.product_text:
            content += f"PRODUCT:\n{input_data.product_text}\n"
        
        if input_data.todistus_kartta:
            content += f"EVIDENCE MAP:\n{input_data.todistus_kartta.model_dump_json()}\n"
            
        if input_data.panel_audit:
             content += f"PANEL AUDIT:\n{input_data.panel_audit.model_dump_json()}\n"
             
        if input_data.tuomio:
             content += f"VERDICT:\n{input_data.tuomio.model_dump_json()}\n"
             
        if input_data.coaching_plan:
             content += f"COACHING:\n{input_data.coaching_plan.model_dump_json()}\n"

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]

        # Resolve Model
        repo = await get_async_repository()
        registry = AgentRegistry(repo)
        await registry.discover_and_register_agents()
        config = await registry.resolve_model_config(model_alias)
        model_name = config.get("model_name")
        
        if not model_name:
             raise ValueError(f"Model config for '{model_alias}' resolved but missing 'model_name'. Check DB.")

        llm = LLMClient()
        return await llm.run_structured_task(
            messages=messages,
            response_model=output_model,
            model=model_name
        )
    except Exception as e:
        logger.error(f"Migration Task Failed: {e}")
        # In migration mode, we might want to return None or raise?
        # GraphEngine catches exceptions.
        raise

# --- Task Registrations ---

@TaskRegistry.register_task(name="interaction", input_schema=MigrationInput, output_schema=InteractionAnalysis)
async def interaction_task(input_data: MigrationInput) -> InteractionAnalysis:
    return await _run_task(PROMPT_INTERACTION, input_data, InteractionAnalysis)

@TaskRegistry.register_task(name="profiler", input_schema=MigrationInput, output_schema=ProfilerAnalysis)
async def profiler_task(input_data: MigrationInput) -> ProfilerAnalysis:
    return await _run_task(PROMPT_PROFILER, input_data, ProfilerAnalysis)

@TaskRegistry.register_task(name="logician", input_schema=MigrationInput, output_schema=ArgumentaatioAnalyysi)
async def logician_task(input_data: MigrationInput) -> ArgumentaatioAnalyysi:
    return await _run_task(PROMPT_LOGICIAN, input_data, ArgumentaatioAnalyysi)

@TaskRegistry.register_task(name="falsifier", input_schema=MigrationInput, output_schema=LogiikkaAuditointi)
async def falsifier_task(input_data: MigrationInput) -> LogiikkaAuditointi:
    return await _run_task(PROMPT_FALSIFIER, input_data, LogiikkaAuditointi)

@TaskRegistry.register_task(name="causal", input_schema=MigrationInput, output_schema=KausaalinenAuditointi)
async def causal_task(input_data: MigrationInput) -> KausaalinenAuditointi:
    return await _run_task(PROMPT_CAUSAL, input_data, KausaalinenAuditointi)

@TaskRegistry.register_task(name="detector", input_schema=MigrationInput, output_schema=PerformatiivisuusAuditointi)
async def detector_task(input_data: MigrationInput) -> PerformatiivisuusAuditointi:
    return await _run_task(PROMPT_DETECTOR, input_data, PerformatiivisuusAuditointi)

@TaskRegistry.register_task(name="overseer", input_schema=MigrationInput, output_schema=EtiikkaJaFakta)
async def overseer_task(input_data: MigrationInput) -> EtiikkaJaFakta:
    return await _run_task(PROMPT_OVERSEER, input_data, EtiikkaJaFakta)

# Archivist output schema is simple dict or CaseLawContext if defined
# Step 8a output schema is 'CaseLawContext' in 8a, but 'ArchivistAgent' might output something else.
# Checking seed_data: id="archivist_agent", output_schema: "BestPractices"?
# No explicit schema listed in seed_data visible lines.
# I will use a dummy dict or search domain.py for 'Archivist' schema.
# domain.py had 'CaseLawContext' under Step 8a. Let's assume that's it or use generic dict.
# I'll use a generic dict or basic schema to be safe if 'CaseLawContext' is too specific.
# Archivist output schema is now in domain.py

@TaskRegistry.register_task(name="archivist", input_schema=MigrationInput, output_schema=ArchivistOutput)
async def archivist_task(input_data: MigrationInput) -> ArchivistOutput:
    return await _run_task(PROMPT_ARCHIVIST, input_data, ArchivistOutput)

@TaskRegistry.register_task(name="judge", input_schema=MigrationInput, output_schema=TuomioJaPisteet)
async def judge_task(input_data: MigrationInput) -> TuomioJaPisteet:
    return await _run_task(PROMPT_JUDGE, input_data, TuomioJaPisteet)

@TaskRegistry.register_task(name="coach", input_schema=MigrationInput, output_schema=CoachingPlan)
async def coach_task(input_data: MigrationInput) -> CoachingPlan:
    return await _run_task(PROMPT_COACH, input_data, CoachingPlan)

@TaskRegistry.register_task(name="xai", input_schema=MigrationInput, output_schema=XAIReport)
async def xai_task(input_data: MigrationInput) -> XAIReport:
    return await _run_task(PROMPT_XAI, input_data, XAIReport, model_alias="fast")
