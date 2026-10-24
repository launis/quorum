# Ohje: Miten käyttää /tier3-god-code-decomposition -työnkulkua

Tämä dokumentti on ohjenuora sille, miten tekoälyagenttia (Antigravity) ohjeistetaan purkamaan suuria "God Code" -tiedostoja turvallisesti. Tier 3 on nyt **puhdas suunnittelija (God Code Planner)** aivan kuten Tier 1. Se ei kirjoita itse riviäkään koodia, vaan laatii turvallisen, monivaiheisen Strangler Fig -mallin mukaisen suunnitelman ja seurantatiedoston, jota suoritetaan sen jälkeen erillisillä istunnoilla.

Kun käynnistät työnkulun, agentti tulostaa automaattisesti ruudulle ohjeet siitä, mitä se on tekemässä. Varmista aina, että promptistasi löytyvät seuraavat elementit:

## 1. Kohde (Target)
**Tarkka tiedostopolku, jota puretaan.**
Ilman tarkkaa polkua tekoäly saattaa arvailla väärän tiedoston.
*Esimerkki:* `--target="backend_v2/database/repositories/component.py"`

## 2. Älykäs domain-analyysi (Bounded Contexts)
**Mitä asioita tiedostosta halutaan irrottaa.**
Sinun ei tarvitse itse tietää tai luetella domaineita manuaalisesti. Voit antaa tekoälylle vain yhden tiedoston polun ja pyytää sitä *analysoimaan tiedoston* sekä tunnistamaan siitä itsenäiset loogiset kokonaisuudet (Domain-Driven Design). Agentti lukee koodin, tekee kattavan arkkitehtuurikartoituksen ja luo jokaiselle tunnistamalleen domainille oman `phaseX_domain.md` -osasuunnitelman.

## 3. Generoitava Tracker ja Kapulanvaihto (Session Handover)
Koska tekoäly toimii nykyään vain suunnittelijana, se luo aina automaattisesti Markdown-pohjaisen seurantatiedoston (esim. `docs/epic/[tiedostonnimi]_decomposition_tracker.md`). Kun tekoäly ilmoittaa olevansa valmis, se kirjoittaa trackerin loppuun täydellisen `/tier5-resume` -komennon. Tämä komento sisältää parametrit `--achieved`, `--learned` ja `--remaining`, joihin tekoäly on tiivistänyt kaiken oppimansa: mitkä tiedostot puretaan, mitä riippuvuuksia löydettiin, ja mitkä `phaseX_domain.md` -suunnitelmat suoritetaan seuraavaksi. Sinun tarvitsee vain kopioida tämä komento uuteen ikkunaan käynnistääksesi varsinaisen koodauksen (`/tier2-execute` -suorittajalla).

---

### Esimerkki täydellisestä "yhden tiedoston" discovery-promptista:

> `/tier3-god-code-decomposition --target="backend_v2/database/repositories/massive_repo.py". Analysoi tämä God Code -tiedosto huolellisesti ja tunnista siitä itsenäiset loogiset kokonaisuudet (DDD). Toimi God Code Plannerina: laadi jokaiselle tunnistamallesi domainille oma osasuunnitelmansa (purettavaksi siisteihin alihakemistoihin) ja generoi lopuksi docs/epic/massive_repo_decomposition_tracker.md -seurantatiedosto delegointikomennolla.`

---

## 4. Koodikannan Monoliittien Tarkka Suoritusjärjestys (Master Execution Sequence)

Tämä osio määrittelee koko koodikannan (368 tuotantotiedoston) monoliittien, **EPIC 159:n (Dynamic MCP)** ja **EPIC 151:n (PostgreSQL-migraatio)** tarkan suoritusjärjestyksen. Yksityiskohtainen arkkitehtuurianalyysi löytyy dokumentista [docs/koodikannan_purku_ja_migraatiojarjestys.md](file:///c:/src/quorum/docs/koodikannan_purku_ja_migraatiojarjestys.md).

### 4.1 Suoritustilanne (Mitä on jo tehty)

Ennen seuraavien vaiheiden aloittamista koodikannasta on jo **purettu neljä lehtimonoliittia ja viides on valmistumassa**:

| Kohde (Alkuperäinen tiedosto) | Alkuperäinen LOC | Nykytila koodikannassa | Uusi modulaarinen arkkitehtuuri |
| :--- | :--- | :--- | :--- |
| `backend_v2/services/orchestrator/anchor_validation_service.py` | 855 LOC | **SUORITETTU & POISTETTU** | Purettu pakettiin `backend_v2/services/orchestrator/anchor_validation/` |
| `backend_v2/services/export_service.py` | 1 123 LOC | **SUORITETTU & POISTETTU** | Purettu pakettiin `backend_v2/services/export/` |
| `backend_v2/services/matrix_domain_parser.py` | 732 LOC | **SUORITETTU & POISTETTU** | Purettu pakettiin `backend_v2/services/matrix_parser/` |
| `backend_v2/services/ingress/pdf_chat_extractor.py` | 682 LOC | **SUORITETTU & POISTETTU** | Purettu pakettiin `backend_v2/services/ingress/pdf_extractor/` |
| `backend_v2/services/report_service.py` | 749 LOC | **VAIHE 4 AJOSSA** | Purettu pakettiin `backend_v2/services/report/` (`report_service_decomposition_tracker.md`) |

---

### 4.2 Jäljellä Olevien Kohteiden Tarkka Suoritusjärjestys (Aallot 1–4)

```
[AALTO 1: Valmistumassa] ──> report_service (Phase 4 cutover)
         │
         ▼
[AALTO 2: Työkalut]      ──> EPIC 159 (Dynamic MCP, generic_mcp_client, schema_factory, url_validator)
         │
         ▼
[AALTO 3: LLM-infra]     ──> strategies/llm.py (931 LOC) & llm/provider.py (1 580 LOC)
         │
         ▼
[AALTO 4: Ydin & DB]     ──> EPIC 151 (PostgreSQL 18 Clean Slate) & dag_executor.py (1 640 LOC)
```

#### AALTO 1: Raportoinnin Viimeistely (Parhaillaan käynnissä)
- **Kohde**: `backend_v2/services/report_service.py`
- **Seuranta**: `docs/epic/report_service_decomposition_tracker.md`
- **Toimenpide**: Odotetaan käynnissä olevan Phase 4 -vaiheen valmistumista (atominen cutover pakettifasadiin `report/__init__.py` ja vanhan tiedoston poisto).

#### AALTO 2: Dynaaminen MCP ja Työkalukerroksen Modernisointi (EPIC 159)
- **Kohde**: `docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md` (Audit: `docs/epic/EPIC_159_audit_report.md` on **HARDENED & VERIFIED**)
- **Miksi nyt**: 
  - Poistaa vanhat työkalut (`tavily.py`, `wikipedia.py`, `models/domain/tools.py`), stabiloi MCP-skeemat ja tuo dynaamisen `GenericMCPClient`:in.
  - **Kriittinen sääntö**: TÄMÄ ON AJETTAVA ENNEN `strategies/llm.py`:n tai `provider.py`:n purkua, jotta valmis ja auditoitu eepos ei desynkronoidu.
- **Suorituskomento**:
  ```powershell
  # 1. Luodaan suoritustrackeri valmiille auditoidulle eepokselle
  /tier1-tracker-generator docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md

  # 2. Ajetaan autonomisesti monivaiheinen toteutus (vaiheet 1-4)
  uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_159_tracker.md
  ```

#### AALTO 3: LLM-Infrastruktuurin Monoliittien Purkaminen (Klusteri B)
- **Miksi vasta tässä**: Koska EPIC 159 on poistanut staattiset työkalut ja stabiloinut `ToolDispatcher`:in ja `GenericMCPClient`:in rajapinnat.

1. **Kohde 3.1: `backend_v2/services/orchestrator/strategies/llm.py` (931 LOC)**
   - **Komento**:
     ```powershell
     /tier3-god-code-decomposition --target="backend_v2/services/orchestrator/strategies/llm.py"
     ```
   - **Syntyvät moduulit**: `prompt_assembler.py`, `tool_coordinator.py`, `output_validator.py`, `__init__.py`.
   - **Ajo**: `uv run python scripts/auto_phase_runner.py --tracker docs/epic/llm_strategy_decomposition_tracker.md`

2. **Kohde 3.2: `backend_v2/llm/provider.py` (1 580 LOC) & `backend_v2/llm/handler.py` (911 LOC)**
   - **Komento**:
     ```powershell
     /tier3-god-code-decomposition --target="backend_v2/llm/provider.py"
     ```
   - **Syntyvät moduulit**: `semaphore_pool.py`, `cost_calculator.py`, `error_classifier.py`, `execution_engine.py`.
   - **Ajo**: `uv run python scripts/auto_phase_runner.py --tracker docs/epic/provider_decomposition_tracker.md`

#### AALTO 4: PostgreSQL 18 Clean Slate Migration & `dag_executor.py` (EPIC 151 + Klusteri C)
- **Kohde 4.1: EPIC 151 (PostgreSQL 18 Clean Slate Migration)**:
  - Dokumentti: `docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md`
  - Korvaa `TinyDBDriver`:n ja `data/db_v2.json`:n `asyncpg`-yhteysaltaalla ja PostgreSQL 18:lla. Kaikki DTO- ja domain-mallit ovat jo 100 % puhtaita, joten tietokanta luodaan suoraan lopulliseen malliin.
- **Kohde 4.2: `backend_v2/services/orchestrator/dag_executor.py` (1 640 LOC, suurin funktio 1 118 LOC)**:
  - **Miksi vasta tässä**: `dag_executor.py`:n suurin monimutkaisuus johtuu TinyDB-tiedostolukituksesta (`_update_lock`) ja monen megatavun `execution_trace`-blobin jatkuvasta levykirjoituksesta.
  - Kun PostgreSQL on käytössä, `dag_executor.py` pilkotaan **suoraan append-only `trace_events` -tapahtumavirtaan**:
    - `wave_scheduler.py` (Kahnin aaltosuoritus TaskGroupissa)
    - `state_machine.py` (`trace_events` append-only tilasiirtymät)
    - `cancellation_manager.py` (TaskGroup-peruutukset ja DLQ-kirjaukset)
    - `telemetry_broadcaster.py` (SSE/WebSocket-päivitykset)
  - **Komento**:
    ```powershell
    /tier3-god-code-decomposition --target="backend_v2/services/orchestrator/dag_executor.py"
    ```

