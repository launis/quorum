# **🚀 EPIC 89: Dynamic Tool Registry & SRP Hardening (V2)**

**Epic ID:** EPIC-89
**Tila:** Ready for Implementation
**Prioriteetti:** P2 (Arkkitehtuurivelka / Laajennettavuus)
**Arkkitehtuuri:** Python 3.14+, FastAPI, Pydantic V2, MCP

## **🎯 Tavoite**
Vapauttaa `mcp_tool_loop.py` kovakoodatusta `Tavily` -riippuvuudesta. Tällä hetkellä Quorumin Agentic-luuppi osaa käyttää työkaluja (Tools), mutta koodi on kytketty (Coupled) suoraan `tavily_search_client.py` -kirjastoon. Tavoitteena on luoda SRP (Single Responsibility Principle) -pohjainen `ToolDispatcher` ja `BaseTool` -rajapinta, jolloin uusia työkaluja (kuten sisäiset tietokantahaut, laskimet tai mock-työkalut) voidaan rekisteröidä järjestelmään pelkällä konfiguraatiolla.

---

## **🔍 Nykytila (As-Built)**
- `mcp_tool_loop.py` sisältää kovakoodatut vakiot: `TAVILY_TOOL_ID = "mcp_tavily_search"`.
- Moduuli tekee suoran importin: `from backend_v2.services.mcp.tavily_search_client import tavily_search`.
- LLM:n työkaluvalinta on "Fake-Dynamic": Työkalut esitellään OpenAI Schema -muodossa, mutta ajo (Execution) on if/else -spagettia (`if TAVILY_TOOL_ID in allowed_tools:`).
- `_execute_tavily_search()` on osa loop-moottoria, eikä erillinen työkaluluokka.

---

## **📐 Ehdotettu Arkkitehtuuri (Phase 9 Yhteensopiva)**

### 1. `BaseTool` (Abstraktio)
Uusi ylätason luokka `backend_v2/models/domain/tools.py` -tiedostoon:
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from backend_v2.models.v2_core import MCPAuditTrace

class BaseTool(ABC):
    @property
    @abstractmethod
    def tool_id(self) -> str: pass

    @property
    @abstractmethod
    def declaration(self) -> dict: pass # OpenAI schema

    @abstractmethod
    async def execute(self, **kwargs) -> MCPAuditTrace:
        """Suorittaa työkalun ja palauttaa aina standardoidun MCPAuditTracen"""
        pass
```

### 2. `ToolDispatcher` (Rekisteri)
Uusi moduuli `backend_v2/services/mcp/dispatcher.py`:
- Pitää sisällään dict-rakenteen rekisteröidyistä työkaluista: `{"mcp_tavily_search": TavilyTool()}`.
- Vastaa oikean työkalun instanssin hakemisesta, kun `mcp_tool_loop.py` pyytää sitä.

### 3. Modulaarinen `TavilyTool`
Siirretään nykyinen logiikka uuteen tiedostoon `backend_v2/services/mcp/tools/tavily.py`:
- Perii `BaseTool` -luokan.
- Vastaa käännöksistä (Translation Service) ja `MCPAuditTrace` -luonnista.

### 4. `mcp_tool_loop.py` Puhdistus
- Poistetaan KAIKKI viittaukset Tavilyyn.
- Kun `allowed_tools` annetaan loopille, se pyytää `ToolDispatcherilta` näiden työkalujen deklaratiot (`dispatcher.get_declarations(allowed_tools)`).
- Jos LLM haluaa käyttää työkalua, loop kutsuu vain `await dispatcher.execute_tool(tool_id, **kwargs)`.

---

## **🛑 Phase 9 - Säännöt & Laatuvaatimukset (Quality Gates)**

1. **Forensinen Jatkuvuus (Epic 88 Integrity):**
   - Työkalun vaihto ei saa rikkoa `MCPAuditTrace` tai `ScorecardAtomDTO` -rakennetta. Työkalun palauttaman datan täytyy pystyä tuottamaan `<external_evidence>` lohko täydellisesti entiseen malliin.

2. **Fail-Fast (DLQ):**
   - Työkalun suoritus ei saa koskaan kaatua äänettömästi (Silent Drop). `AppException` tai ErrorCodes.FETCH_FAILED tulee heittää eteenpäin Pydantic-tason käsittelyyn, kuten aiemmin.

3. **Opaque ID Hardening:**
   - Työkalun palauttamat todisteet tulee injektoida `AliasEngine`:n kautta, jotta käyttöliittymään (Flutter/PDF) päätyy vain turvallisia `docN` pseudonyymejä (esim. `local_id = local_alias_engine.register(real_id)`).

## **✅ Varmistus / Falsifiointisuunnitelma**
- [ ] Backendin testit menevät läpi uudella dispatcherilla: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] Uuden työkalun (esim. MockTool) rekisteröinti onnistuu yhtä koodiriviä muuttamalla.
- [ ] Koko koodikannasta (paitsi `tools/tavily.py`) ei löydy enää sanaa "Tavily".
