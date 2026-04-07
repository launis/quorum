# 07: Infrastruktuuri ja Lokitus (Observability)

Järjestelmä operoi asynkronisen Python FastAPI -arkkitehtuurin, raskaiden Arq / Redis -taustatyöntekijöiden ja Docker-konttien päällä. Koska taiteellisen asiantuntijajärjestelmän debuggaus on perinteisesti tuskaista ("miksi tekoäly tuotti huonon tuloksen?"), Cognitive Quorum panostaa massiivisesti "Forensic Sovereignty" -tyyliseen jäljitettävyyteen.

## 1. Lokitus (The ContextFilter Mandate)

Lokitus (`backend_v2/logging_config.py`) ei ole vain tekstivirtaa, vaan arkkitehtuurisesti kytketty The Zero-Compromise Ppledgen "Fail-Fast" periaatteisiin.

1. **Kontekstisidonnaisuus (`ContextFilter`):** Jokainen taustaprosessiin (Worker) tai reitittimeen (API) syntyvä lokirivi, oli se sitten tietokantavirhe tai LLM-integraation varoitus, ohjataan `ContextFilter`:n läpi. Tämä injektoi lokiriville *aina* aktiivisen `execution_id`:n (tai oletuksena `request_id`). Tämän ansiosta massiivisesta serverin lokitiedostosta (`backend_debug.log`) pystytään greppaamaan sekunneissa kaikki yhtä tiettyä työnkulkua koskettavat 100 eri I/O -kutsua The Event Sourcing -ketjussa.
2. **Dual-Reporting (RFC 7807):** Järjestelmän on ehdottomasti estetty nielemästä virheitä lennossa. Kun koodi kaatuu odottamattomaan poikkeukseen, sitä ei "hoideta pois", vaan se työnnetään ensin rakenteellisena `logger.error` viestinä talteen (mukaanlukien täysi Stack Trace ja virhekoodi), ja uudelleenheitetään asiakkaalle puhtaana Pydantic-validoituna `AppException` (RFC 7807 Problem Details) rakenteena vian selvittämiseksi.

## 2. Pydantic Logfire & LLM Observability

Tekoälyn toimintakyky ei saa ikinä olla Musta Laatikko. Järjestelmä on integroitu suoraan Pydanticin viralliseen Logfire-pilveen (`logfire.configure`).
* Kaikki HTTP-pyynnöt ja tekoälyintegraatiot (`litellm.success_callback = ["logfire"]`) säteilytetään suoraan kojelautaan pilveen vianjäljitystä varten.
* Tämä paljastaa tarkasti kauan mallilla (esim. Gemini Pro) meni generoida tietty Pydantic Structured Output, paljonko se maksoi (Token usage), ja kaatuiko kysely mahdollisesti rikkinäiseen Pydantic-skeeman luontiin (`schema_builder.py`).

## 3. Infrastruktuuri ja Ympäristöt

Quorum pohjaa kontitettuun "Infrastructure as Code" -toimintamalliin. Siksi järjestelmällä ei ole erillistä paikallisista eroja koskevaa ydinlogiikkaa. 

```mermaid
flowchart LR
    subgraph Infastructure ["Docker / Paikallinen Infra"]
        UI["Client App V2 (Flutter 3)"]
        API["FastAPI V2 (Portteri)"]
        Redis[("Redis (Arq)")]
        Worker["Python Worker (Arq)"]
    end

    subgraph Observability ["Observability / Lokitus"]
        Context["ContextFilter (execution_id)"]
        LogFile[("backend_debug.log")]
        LogfireCloud(("Pydantic Logfire Cloud"))
    end

    UI -->|"HTTP Request"| API
    API --> Redis
    Redis -->|"Asynkroninen ajo"| Worker

    API -->|"Dual-Reporting RFC 7807"| Context
    Worker -->|"Dual-Reporting RFC 7807"| Context
    Context --> LogFile

    API -.->|"HTTP Traces & Exceptions"| LogfireCloud
    Worker -.->|"LLM Token Traces & Pydantic Validations"| LogfireCloud
```
* **Worker Queue (Arq + Redis):** Kuten aiemmin mainittu, työnkulut eivät koskaan elä NginX tai Uvicorn pääprosessin sisällä. Kun asiakas laukaisee evaluaation, FastAPI -päärajapinta tallentaa Pydantic-mallit tietokantaan, lähettää tiedon sadasosasekunneissa Arq-palvelimelle (Redis), joka aloittaa raskaiden tekoälymallien asynkronisen ohjaamisen eristetyssä Worker-säikeessä.
* **Paikallinen Ajo:** Kehittäjät hyödyntävät käynnistysrutiineja kuten `run_local.bat` ja taustamallistoa `docker-compose.yml`, nostaen paikallisen Redis-ilmentymän sekunneissa kehityskäyttöön varmistaen täydellisen pilvipariteetin.
