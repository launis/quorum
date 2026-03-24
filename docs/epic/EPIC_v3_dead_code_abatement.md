# EPIC: V3 Kuolleen Koodin Siivous & Referenssin Täydennys (Dead Code Abatement)

**STATUS:** Draft / Planning Phase  
**TIER:** Tier 1 (Epic Planner)
**CONTEXT:** Quorum V3 Architecture (Python Backend V2 + Flutter Client V2)

## 📌 1. Objective
Tavoitteena on tunnistaa ja tuhota säälimättä kaikki V1/V2 jäänteet ja turhat ohjelmatodistukset sekä backendistä että frontendistä. Rinnalla päivitetään aukottomasti `docs/reference.md` -dokumentti jäljelle jäävillä elävillä ohjelmilla.

NO CODE SHALL BE DELETED WITHOUT EXPLICIT USER APPROVAL. Zero-Trust -metodologia: automaattiset työkalut tuottavat false-positiivisia (esim. FastAPI Pydantic-reitit), joten jokainen poistoehdokas (Kill List) on varmennettava manuaalisesti.

## 🔍 2. Kolmivaiheinen Varmennusprotokolla (The 3-Way Verification)
Jokainen epäilty tiedosto käy läpi vähintään kolme toisistaan riippumatonta testiä ennen poistotuomiota:
1. **Staattinen Analyysi (Pintatason skannaus):** Pyydetään työkaluja (kuten Pythonin `vulture`, `pip-extra-reqs` tai Dartin `flutter analyze`) etsimään kuolleita koodipolkuja ja orpoja riippuvuuksia suoraan koodirakenteesta (AST).
2. **Käsityö-Grep (Syvyysskannaus):** Etsitään tiedoston, luokan tai funktion nimellä (`grep_search`) suoria tai epäsuoria viittauksia (esim. dynaamisia injektioita) koko koodikannasta.
3. **Dynaaminen / Arkkitehtuurin todistus (Looginen skannaus):** Voidaanko tiedoston sisältämä ohjelma ajaa yhä asynkronisessa V3-moottorissa? Jos se koodi operoi vanhoilla SDUI-renderöijillä, LangChain Wrappereilla tai haamukentillä, tiedosto on kuollut.

## 🚨 3. Banned Patterns (Kielletyt Toimintamallit)
- **Blind Faith in Vulture:** Automatisoitu työkalu (vulture) ei ymmärrä Pydantic-validaattoreita tai FastAPI:n reitityksiä. Älä koskaan poista koodia sokeasti sen ehdotuksesta.
- **Rogue Formatting:** Älä yhdistä koodin uudelleenmuotoilua (refactoring) ja poistamista (deletion) samaan askeleeseen. Poisto-commitien on oltava eristettyjä (`git revert` turvaamiseksi).
- **Modifying Seed/DB:** DB-tiedostot ja `seed_data.json` on rajattu koodinpoiston ulkopuolelle. Ne noudattavat omia elinkaarisääntöjään.

## 🏗️ 4. Menetelmä / Milestones (Hakemistokohtaiset etapit)

Projekti suoritetaan turvallisesti hakemistokohtaisissa (directory-by-directory) etapeissa. Automaattiset työkalut ajetaan kutakin kansiota vasten, luodaan The Kill List, varmistetaan se 3-Way metodilla, poistetaan kuolleet levyltä ja kirjoitetaan selviytyneet `reference.md` -tiedostoon oppaiksi.

### Milestone 1: Backend - Models, Schemas & Utils (`backend_v2/models/`, `backend_v2/utils/`)
- Ajetaan testit (Pip dependency jäänteet, Vulture, Pydantic V2 sääntövertailu).
- Varmistetaan, että ainoastaan V3 Event Sourcing ja Fail-Fast -mallit selviytyvät.
- **Dokumentointi:** Eloonjääneet kirjataan selityksineen `docs/reference.md` "Backend Data Models" -osioon.

### Milestone 2: Backend - Services, LLM & Engine (`backend_v2/services/`, `backend_v2/engine/`, `backend_v2/llm/`)
- Metsästetään säälimättä kaikki riippuvuudet LangChainiin, vanhoihin Vertex API -wrapppereihin tai V2 RAG Search -virityksiin. 
- Analysoidaan Hookit (`backend_v2/hooks/`, `backend_v2/engine/`) ja karsitaan kaikki mikä korvattiin uudistetulla LLM-reitittimellä.
- **Dokumentointi:** Täydennetään rekisteri moottorin palveluiden osalta (esim. LiteLLM-reititin, BlueprintTransformer).

### Milestone 3: Backend - Routers & Database (`backend_v2/routers/`, `backend_v2/database/`)
- Analysoidaan API-rajapinnat ja tietokantayhteydet. Poistetaan kaikki koodi, joka tukee vanhoja Endpointeja (esim. SDUI polut).
- **Dokumentointi:** Kirjataan `reference.md` dokumenttiin V3-rajapinnat ja tapahtumalokin tietokantatasot.

### Milestone 4: Frontend - Core & UI-Jäänteet (`client_app_v2/lib/`)
- Ajetaan `flutter analyze` ja `dart_code_metrics:metrics check-unused-files lib`.
- Poistetaan julmasti kaikki SDUI:hin (Server Driven UI) viittaava valmis koodi, custom-reititinhelvetit ja kovat matriisi-renderöijät jotka korvattiin litteällä Flat MVC -Riverpod arkkitehtuurilla.
- Skannataan `.arb` käännöstiedostot orvoista teksteistä.
- **Dokumentointi:** Dokumentoidaan säilyvät frontend-palvelut, views ja Riverpod statet rekisteriin.

### Milestone 5: Loppusiivous ja Synkronointi
- Viimeinen auditointi. Ristiinvertailu, että `reference.md` on täydellinen kartta 100% elävästä koodista ilman varjoja menneisyydestä.
- Käännetään ja koestetaan (API Test & Flutter Build), että koko järjestelmä nousee jaloilleen V1/V2 -veloista vapaana.
