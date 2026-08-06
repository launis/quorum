# Ylätason suunnitelma: God Code -tiedostojen refaktorointi (Tier 2 & Tier 3)

Tämä suunnitelma määrittelee, kuinka kolme massiivista "God Code" -tiedostoa (`worker.py`, `v2_core.py` ja `lightweight_matrix.py`) hajautetaan koheesiivisiin alihakemistoihin ja komponentteihin Single Source of Truth (SSOT) ja Domain-Driven Design (DDD) -periaatteiden mukaisesti. Suunnitelma noudattaa Tier 3 (God Code Decomposition) Strangler Fig -mallia ja Tier 2 (Backend Hardening) Pydantic Fail-Fast -sääntöjä.

**Arkkitehtuurillinen linjaus (Yhdenmukaisuus aiemman refaktoroinnin kanssa):**
Kaikki uudet komponentit pakotetaan noudattamaan täsmälleen samoja rakenteellisia sääntöjä kuin aiemmin refaktoroidut hakemistot:
1. **`models/domain/` -yhdenmukaisuus**: Uusien domain-mallien on noudatettava `security.py` kaltaista puhdasta rakennetta (ei palvelulogiikkaa, strict `ConfigDict`, `V2CoreBase` periytyminen, TypeAdapter-validaatio).
2. **`services/sdui/adapters/` -yhdenmukaisuus**: Workerien ja Service-kerroksen hajautuksessa hyödynnetään `SduiAdapterProtocol` ja `AdapterContext` -tyyppistä arkkitehtuuria. Kullekin työntekijälle tai palvelulle määritellään muuttumaton (immutable) Context-DTO ja yhtenäinen Protocol (esim. `WorkerProtocol` yksittäisellä `@staticmethod execute(context: JobContext)` -metodilla).

> [!WARNING]
> **User Review Required: Strangler Fig -Siirtymä**
> `v2_core.py` tiedoston pilkkominen rikkoo satoja import-lausekkeita koko koodikannassa, mikäli alkuperäinen tiedosto poistetaan suoraan. Hyväksytkö lähestymistavan, jossa alkuperäinen `v2_core.py` jätetään toistaiseksi "Hollow Shell" -proxyksi (joka vain importtaa ja eksporttaa uudet mallit `@deprecated` tagilla), jotta järjestelmä pysyy kääntyvänä (compilable) siirtymän ajan?

> [!IMPORTANT]
> **Arkkitehtuurillinen Korjaus: Service Layer Hydration Firewall & Hardcoding**
> `lightweight_matrix.py` rikkoo tällä hetkellä sääntöjä kahdella tavalla:
> 1. Se sisältää raskasta palvelulogiikkaa (`AnchorValidationService`).
> 2. Se on täynnä kovakoodattuja arvoja (kuten Literal `PASS`/`FAIL` ja suomenkielinen `blacklist` "ei löydy").
> Tämä logiikka siirretään pois. DTO ei saa tehdä tietokantahakuja, joten tarvittava lokaalisaatiodata (Lexicon) ladataan Service-kerroksessa ja syötetään DTO:lle `ValidationInfo.context`in kautta.

## Ehdotetut Muutokset

### 1. Kovakoodauksien (Hardcoding) Poistaminen ja Enum-Refaktorointi
Sekä `lightweight_matrix.py` että `v2_core.py` sisältävät kymmeniä `Literal["..."]` -määrityksiä, jotka rikkovat SSOT-periaatetta ja `01-python-backend.md` -sääntöjä. Lisäksi `lightweight_matrix.py` sisältää suomenkielisiä sanoja (esim. "ei löydy"), mikä rikkoo `internal_language_and_epic_ban` -sääntöä.

#### Enumien Keskittäminen (`backend_v2/models/enums.py`)
Luodaan ja keskitetään kaikki seuraavat kovakoodatut Literalit virallisiksi Enum-luokiksi:
- `EvaluationStatus` (PASS, FAIL, CONTESTED, DLQ)
- `AggregationMode` (EXISTS, ALL_MUST_COMPLY)
- `EvaluationTrack` (EXTRACTIVE_SENSOR, COGNITIVE_JUDGEMENT)
- `BoundingBoxScope` (sentence, paragraph, document, ...)
- `PresetView` (1d_metrics, 2d_compare, matrix_summary, ...)
- `ExportFormat` (pdf, docx, raw_json, xlsx)

#### Tietokantapohjainen Kontekstisyöttö (Database Context Injection)
- **Sanastojen (Blacklist) refaktorointi**: `lightweight_matrix.py`:n sisältämä `blacklist` (jossa on sanoja kuten "null", "ei löydy", "ei sovelleta") poistetaan täysin.
- **Toteutus**: Service-kerros (esim. `RAGPreflightService`) lukee tietokannasta sallitut/kielletyt lokaalisaatiosanat (esim. `LexiconConfigPayload`:n kautta). Kun Pydantic DTO (LightweightExtractionAtom) validoidaan, tämä sallittujen ja kiellettyjen sanojen lista syötetään Pydanticille `ValidationInfo.context` -muuttujan kautta (`AtomEvaluationItemDTO.model_validate(data, context={"blacklist": db_blacklist})`). Näin DTO pysyy puhtaana (ei tietokantariippuvuutta), mutta voi validoida datan dynaamisesti tietokannan asetusten perusteella.

---

### 2. `backend_v2/models/v2_core.py` (Domain Mallien Hajautus)
Tämä 1700-rivinen tiedosto rikotaan erillisiin domain-kohtaisiin tiedostoihin `backend_v2/models/domain/` ja `backend_v2/models/core/` alle. **Sääntö:** Kuten `security.py`, kaikki uudet tiedostot ovat puhtaita DTO-skeemoja, joiden `ConfigDict(frozen=True, strict=True, extra="forbid")` on pakotettu, eikä niihin lisätä ulkoisia riippuvuuksia tai kovakoodattuja Literaleja.

#### [NEW] `backend_v2/models/domain/i18n.py`
- Siirretään `I18nText`.

#### [NEW] `backend_v2/models/domain/prompt_blocks.py`
- Siirretään `PromptBlock`, `MatrixScale`, `MatrixRow`, `MatrixClaim`, `TDAAssertion`, `TheoryGrounding`, `AcceptanceCriterion`, `AntiPattern`.

#### [NEW] `backend_v2/models/domain/llm_config.py`
- Siirretään LLM- ja MCP-rekisterit: `ModelProfile`, `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `AllowedMCPTool`, `MCPAuditTrace`.

#### [NEW] `backend_v2/models/domain/workflow_steps.py`
- Siirretään DAG-määritykset: `Step`, `StepRule`.

#### [NEW] `backend_v2/models/domain/lexicons.py`
- Siirretään sanastot: `LexiconConfigPayload`, `SystemConfigPerformativeLexicons`, `LexiconSuggestionListDTO`.

#### [MODIFY] `backend_v2/models/v2_core.py`
- Poistetaan yllä mainitut luokat ja lisätään niihin importit uusista tiedostoista (Strangler Fig Proxy).

---

### 3. `backend_v2/models/dtos/lightweight_matrix.py` (DTO:iden Puhdistus)
Tämä 700-rivinen DTO-tiedosto sisältää liikaa liiketoimintalogiikkaa ja validointia. Se jaetaan puhtaampiin datansiirto-objekteihin ja logiikka siirretään pois (kuten tehtiin domain-refaktoroinnissa).

#### [NEW] `backend_v2/models/dtos/atom_evaluation.py`
- Siirretään `AtomEvaluationItemDTO`, `LightweightExtractionAtom`, `ReducedAtomDTO` ja `MatrixEvaluationItemDTO`.

#### [MODIFY] `backend_v2/models/dtos/lightweight_matrix.py`
- Jätetään tähän vain varsinainen `LightweightMatrixOutput` ja siihen liittyvät apuluokat (esim. `LevelStatsDTO`, `XAILogDto`).
- **Logiikan Poisto**: Poistetaan `AnchorValidationService`-riippuvuudet ja MCP-sorsatekstien sumea täsmäytys (`_enforce_null_hypothesis_before` -validaattorista). Tämä validointi tullaan jatkossa syöttämään puhtaana DTO:lle jo Service-kerroksessa. Kaikki kovakoodatut Literalit vaihdetaan Enum-kutsuiksi.

---

### 4. `backend_v2/worker.py` (Arq Background Tasks)
Worker-tiedosto hoitaa tällä hetkellä liikaa. Se refaktoroidaan noudattamaan samaa muotoa kuin `sdui/adapters/` -hakemisto: Määritellään muuttumaton Context-olio ja Protocol, jonka taakse eri työt piilotetaan.

#### [NEW] `backend_v2/services/execution/protocols/worker_protocol.py`
- Luodaan `WorkerProtocol` ja `JobContext` (vrt. `SduiAdapterProtocol` ja `AdapterContext`). Kaikki työt käyttävät tätä rajapintaa tietojen välittämiseen ilman kymmeniä irtonaisia muuttujia.

#### [NEW] `backend_v2/workers/execution_worker.py`
- Siirretään `execute_workflow_job` -logiikan reititys noudattaen `WorkerProtocol`ia.

#### [NEW] `backend_v2/workers/render_worker.py`
- Siirretään `generate_pdf_job` ja `render_profile_job` omiin dedikoituihin renderöinti-workereihinsa.

#### [NEW] `backend_v2/services/execution/workflow_metrics_service.py`
- Irrotetaan `worker.py`:n valtava `execute_workflow_job` -metodin sisällä tapahtuva `execution_trace`:n läpikäynti omaan palveluunsa (Service). Myös tämä palvelu voi noudattaa standardoitua protokollaa.

#### [MODIFY] `backend_v2/worker.py`
- Muutetaan tiedosto pelkäksi Arq-konfiguraatioksi ja funktioiden rekisteröintipisteeksi, joka kutsuu `workers/`-hakemiston alityöntekijöitä.

## Verification Plan

### Testien ja Kattavuuden Varmistus (Phase 0)
- Ennen koodin purkamista suoritetaan `uv run pytest backend_v2/` ja varmistetaan, että yksikkötestien kattavuus on vähintään 75% näille tiedostoille. (Jos ei, luodaan Golden Master -testit as-is).

### Purkamisen Jälkeinen Auditointi
- Ajetaan globaali laadunvarmistus: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- Varmistetaan, että `v2_core.py` -proxy mahdollistaa edelleen FastAPI:n ja testien onnistuneen suorituksen ilman Circular Import -ongelmia.
- Varmistetaan, että Enum-refaktorointi on tehty oikein e2e-testeissä (FastAPI-reitit ymmärtävät Enumit).
- Varmistetaan, että DTO-malleista poistettu AnchorValidation-logiikka ei riko olemassa olevia sumean haun testejä (ne pitää kytkeä oikeaan Serviceen).
