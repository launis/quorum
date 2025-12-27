# Tekninen Arkkitehtuuri ja Analyysi (V2.0 Refactor)

Tämä dokumentti kuvaa Cognitive Quorum v2.0 -järjestelmän teknisen arkkitehtuurin ja analysoi sen ydinominaisuuksia joulukuun 2025 refaktoroinnin jälkeen.

---

## 1. Ydinarkkitehtuuri: Modulaarinen Monoliitti

Järjestelmä on rakennettu moderneilla Python-standardeilla, korostaen staattista tyypitystä ja selkeää rajapintojen erottelua.

### Backend (FastAPI)
- **Framework:** FastAPI
- **Validointi:** Pydantic v2 (Strict Mode) hyödyntäen `typing.Annotated`.
- **Dokumentaatio:** 100% Google-style docstrings ja automaattisesti generoitu OpenAPI / Swagger.
- **Rakenne:** Modulaariset reitittimet (`routers`) erotettuna ydinlogiikasta (`engine`, `services`).

### Frontend (Streamlit)
- **Rooli:** Kevyt käyttöliittymäkerros, joka visualisoi backendin tilan.
- **Kommunikaatio:** REST API -kutsut backendin state-endpointteihin.

### Tietokanta (TinyDB Abstraction)
- **Toteutus:** Tiedostopohjainen JSON-tietokanta (TinyDB) kääritään abstraktiokerroksella (`backend/database/wrapper.py`).
- **Hyödyt:** Täysin siirrettävä (portable), ei vaadi erillistä tietokantapalvelinta asennuksessa.
- **Seed Data:** Järjestelmän konfiguraatio ladataan `seed_data.json` -tiedostosta, mikä mahdollistaa "Infrastructure as Data" -mallin.

---

## 2. Agenttiarkkitehtuuri (Cognitive Assembly Line)

Agentit eivät ole itsenäisiä "mustia laatikoita", vaan ne toimivat osana determinististä liukuhihnaa (Workflow Pipeline).

| Agentti | Rooli | Vastuualue |
| :--- | :--- | :--- |
| **GuardAgent** | Portinvartija | Tietoturva, PII-suojaus (Presidio-hook), syötteen sanitointi. |
| **AnalystAgent** | Analyytikko | Datan esikäsittely ja strukturointi. |
| **InteractionAnalyst** | Vuorovaikutus | Analysoi käyttäjän ja AI:n välistä dynamiikkaa. |
| **ProfilerAgent** | Profiloija | Tunnistaa käyttäjän intention ja kognitiiviset vinoumat. |
| **LogicianAgent** | Loogikko | Rakentaa loogiset argumenttirakenteet (Toulmin). |
| **FalsifierAgent** | Falsifioija | Yrittää kumota hypoteesit ja testaa päättelyn kestävyyden. |
| **CausalAgent** | Kausaalisuus | Analysoi syy-seuraussuhteet (DoWhy-hook). |
| **DetectorAgent** | Detektori | Tunnistaa performatiivisuuden ja teeskentelyn. |
| **OverseerAgent** | Valvoja | Faktantarkistus ja eettinen valvonta. |
| **PanelAgent** | Paneeli | "Fan-out" -agentti, joka simuloi usean asiantuntijan paneelia (optimointi). |
| **ArchivistAgent** | Arkistonhoitaja | Analysoi prosessin ja vertaa sitä aiempiin tapauksiin. |
| **JudgeAgent** | Tuomari | Antaa lopputuomion (Verdicts) ja pisteyttää suorituksen. |
| **CoachAgent** | Valmentaja | Tarjoaa kehitysehdotuksia ja pedagogista palautetta. |
| **XAIReporter** | Raportoija | Tuottaa selitettävän (XAI) loppuraportin. |

---

## 3. High-Fidelity Sync Loop

Järjestelmä ylläpitää tilaa (`WorkflowState`) keskitetysti.

1.  **Engine** lataa tilan kannasta.
2.  **Runner** ajaa yhden askeleen (Agentin).
3.  **Agentti** kutsuu LLM Provideria (`backend/llm/provider.py`).
4.  **LLM** palauttaa strukturoidun JSON-vastauksen (Pydantic Schema).
5.  **Agentti** päivittää tilan (`state.step_X`).
6.  **Engine** tallentaa tilan kantaan.

Tämä takaa, että jos prosessi kaatuu, se voidaan jatkaa tismalleen samasta kohdasta (State Persistence).

---

## 4. Kehittyneet Ominaisuudet (Hooks)

Agentit hyödyntävät deterministisiä "koukkuja" (Hooks) tehtäviin, jotka vaativat tarkkuutta yli LLM:n kykyjen.

*   **RAG (Retrieval-Augmented Generation):** Semanttinen haku dokumenteista (`backend/services/knowledge_base_service.py`).
*   **Causal Inference (DoWhy):** Tilastollinen kausaalianalyysi (`backend/hooks/causal.py`).
*   **PII Protection (Presidio):** Henkilötietojen tunnistus ja maskaus (`backend/hooks/security.py`).
*   **Google Search:** Reaaliaikainen tiedonhaku (`backend/hooks/search.py`).

---

## 5. Dokumentaatio ja Laadunvarmistus

Refaktoroinnin (Dec 2025) myötä koodikanta noudattaa tiukkoja standardeja:

*   **Täydellinen tyypitys:** Kaikki funktiot ja metodit käyttävät Type Hintingia.
*   **Annotated Pydantic:** Tietomallit käyttävät `Annotated[Type, Field(...)]` -syntaksia.
*   **Google-Style Docstrings:** Jokainen moduuli, luokka ja funktio on dokumentoitu standardin mukaisesti.
*   **Englanninkielinen koodi:** Kaikki kommentit ja sisäinen dokumentaatio on englanniksi (käyttäjälle näkyvä sisältö suomeksi/englanniksi).

```mermaid
graph TD
    User[Käyttäjä] --> FE[Frontend (Streamlit)]
    
    subgraph "Backend (FastAPI)"
        FE -- REST API --> API[Routers]
        API --> Engine[Workflow Engine]
        
        Engine -- "Load State" --> DB[(TinyDB JSON)]
        Engine -- "Execute Step" --> Runner[Pipeline Runner]
        
        subgraph "Agent Execution"
            Runner --> Agent[Base Agent]
            Agent --> Prompt[Prompt Builder]
            Agent --> LLM[LLM Provider (Gemini)]
            
            Agent -- "Invoke Hook" --> Hooks[Deterministic Hooks]
            Hooks --> PII[Security/PII]
            Hooks --> RAG[Knowledge Base]
            Hooks --> Stats[Causal/Metrics]
        end
        
        Agent -- "Update State" --> Engine
    end
    
    Engine -- "Save Result" --> DB
```