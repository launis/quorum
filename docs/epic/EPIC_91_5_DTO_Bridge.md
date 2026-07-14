# Epic 91.5: The Universal DTO Bridge (Vaihe 1/3)

> [!IMPORTANT]
> Tämä on ensimmäinen osa kolmivaiheisesta arkkitehtuurimigraatiosta (Epic 91.5 -> Epic 92 -> Epic 93). 
> Tämän Epicin ainoa tavoite on luoda uusi datakontrakti (Pydantic DTO), pakottaa nykyinen ohjelmisto käyttämään sitä (Anti-Corruption Layerin kautta) ja varmistaa tietokannan yhteensopivuus. Vasta tämän jälkeen aletaan rakentamaan uutta asynkronista DAG-moottoria (Epic 92) tai käyttöliittymän renderöintiä (Epic 93).

## 1. Yhteenveto ja Tavoite (Objective)

Quorumin järjestelmä kärsii tällä hetkellä epäyhtenäisistä tietorakenteista (Nested Trees, raw Markdown payloadit). Jotta voimme myöhemmin rakentaa deterministisen DAG-moottorin ja aidon Server-Driven UI:n (SDUI), meidän on ensin lukittava **yksi absoluuttinen datamuoto**.

Epic 91.5 luo **Flat Adjacency List** -muotoisen DTO-kannan. Se erottaa dynaamisen suoritustilan (`results`) staattisesta ontologiadatasta (`hydrated_references`), minimoiden payloadin koon, maksimoiden Pydantic V2:n suorituskyvyn ja taaten O(1) SDUI-haut frontendille ilman rekursiivisia laskutoimituksia.

---

## 2. Pydantic V2 DTO -Määrittely (01-python-backend.md Compliance)

Nämä mallit muodostavat uuden, lopullisen sillan Backendin ja Frontendin/PDF-generaattorin välille. Mallit on jäädytetty (`frozen=True`, `strict=True`) ja ne pakottavat referentiaalisen eheyden (Fail-Fast).

> [!IMPORTANT]
> **Tier 3 Mandaatti (SSOT Decomposition):** Tietorakenteesta tulee liian iso yhteen tiedostoon koodattavaksi. Yli 500 rivin God Code -tiedostoja ei sallita. DTO-kanta on jaettava alikansioon `backend_v2/models/dtos/report/`.
> * `enums.py`: (Sijaitsee `backend_v2/models/enums.py`) Kaikki globaalit tilat kuten `ExecutionStatus`.
> * `shared.py`: Yhteiset rakenteet (esim. virheet, `ErrorDetailsDTO`).
> * `atoms.py`: Solmutason rakenteet (esim. AtomResultDTO, HydratedAtomDTO)
> * `metrics.py`: Suorituskykymittarit
> * `root.py`: Vain pääluokka `ReportDataDto`, joka kokoaa muut yhteen.
> 
> **Kehäriippuvuuksien (Circular Dependency) Esto:** DTO-mallit sijaitsevat riippuvuusgraafin ehdottomalla pohjalla (Layer 0). DTO-tiedostot (`backend_v2/models/...`) **eivät saa koskaan importata mitään** järjestelmän ylemmiltä tasoilta, kuten `services` (esim. AliasEngine) tai `api`. Palvelut (Services) saavat importata malleja, mutta mallit eivät koskaan palveluita. Tämä sääntö estää `ImportError: cannot import name` -kaatumiset Pydantic-validaattoreissa.

Alla on koko rakenteen looginen sisältö, joka tulee hajauttaa yllä mainitun säännön mukaisesti:

```python
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated, Self

# File: backend_v2/models/enums.py (strict_configuration_segregation)
class ExecutionStatus(str, Enum):
    """
    Str-Enum is mandatory for OpenAPI/Swagger generation,
    ensuring Flutter receives type-safe classes instead of Literal strings.
    """
    PASSED = "PASSED"
    FAILED = "FAILED"
    N_A = "N_A"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"  # DAG macro-orchestration requires runtime states
    QUEUED = "QUEUED"

    @property
    def l10n_key(self) -> str:
        """strict_enum_l10n_mapping: Guarantees Flutter .arb compatibility"""
        return f"status_{self.name.lower()}"

class SDUIComponentType(str, Enum):
    """no_raw_string_enum_mappings: Prevents Magic String crashes in Flutter."""
    BOOLEAN_CARD = "boolean_card"
    EXTRACTED_VALUE_CARD = "extracted_value_card"
    ERROR_CARD = "error_card"
    N_A_CARD = "n_a_card"
    
    @property
    def l10n_key(self) -> str:
        return f"sdui_{self.name.lower()}"

class ErrorDetailsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    error_code: Annotated[str, Field(description="Standardized error code, e.g., LLM_TIMEOUT")]
    message: Annotated[str, Field(description="Technical error message or stack trace")]

class HydratedAtomDTO(BaseModel):
    """
    Static ontology data. Perfectly cacheable.
    Must not contain any dynamic execution-related data.
    """
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    sdui_component: Annotated[SDUIComponentType, Field(description="Server-Driven UI hint for frontend. Ensures frontend performs no reasoning logic.")]
    resolved_claim: Annotated[str, Field(description="Cleaned claim in human language")]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote from the document (static forensic evidence)")]

class ExtractedValueDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    value: str | float | int | bool
    unit: Annotated[str | None, Field(default=None, description="Unit of measurement, e.g., 'tCO2e' or 'EUR'")]

class AtomResultDTO(BaseModel):
    """
    Dynamic execution data (DAG node).
    """
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    tda_id: Annotated[str, Field(description="Opaque ID pointing to the hydrated_references dictionary key")]
    status: ExecutionStatus
    extracted_data: Annotated[ExtractedValueDTO | None, Field(default=None, description="Quantitative or isolated result")]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote from the document")]
    contextual_override: Annotated[bool, Field(default=False, description="Allows cognitive override without a verbatim quote")]
    evaluation_reasoning: Annotated[str | None, Field(default=None, description="Strictly AI cognitive reasoning, no infra errors")]
    error_details: Annotated[ErrorDetailsDTO | None, Field(default=None, description="Populated only if status is SYSTEM_ERROR")]
    
    depends_on_tda_ids: Annotated[list[str], Field(default_factory=list, description="DAG adjacency list")]
    short_circuit_reason_tda_ids: Annotated[list[str], Field(default_factory=list)]

    @model_validator(mode='before')
    @classmethod
    def validate_cognitive_vs_system_state(cls, data: Any) -> Any:
        """Fail-Fast & Graceful Healing: Prevents hallucinations and incomplete data before freeze."""
        if isinstance(data, dict):
            # Null-Hypothesis Override (blind_extraction_null_hypothesis)
            if data.get('contextual_override') is True and data.get('source_quote') is not None:
                # Healing: Jos LLM hallusinoi lainauksen, pyyhitään se turvallisesti mode='before'
                data['source_quote'] = None
                
            status = data.get('status')
            if status in ("PASSED", "FAILED", ExecutionStatus.PASSED, ExecutionStatus.FAILED):
                if not data.get('evaluation_reasoning'):
                    raise ValueError(f"Reasoning is mandatory for cognitive status {status}")
                if not data.get('contextual_override') and not data.get('source_quote'):
                    raise ValueError("source_quote is mandatory unless contextual_override is True")
                    
            if status in ("SYSTEM_ERROR", ExecutionStatus.SYSTEM_ERROR) and not data.get('error_details'):
                raise ValueError("Error details are mandatory when status is SYSTEM_ERROR")
        return data

class ExecutionMetricsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    total_atoms: int
    evaluated: int
    short_circuited_na: int
    duration_ms: Annotated[int, Field(default=0, description="Execution duration in milliseconds for observability")]

class GlobalSynthesisDTO(BaseModel):
    """
    Data structure for high-level synthesized reports.
    """
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    executive_summary: Annotated[str | None, Field(default=None, description="High-level synthesized summary")]
    urgency_level: Annotated[int | None, Field(default=None)]

class ReportDataDto(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    execution_id: str
    workflow_id: Annotated[str, Field(description="For UI correlation")]
    global_metrics: ExecutionMetricsDTO
    global_synthesis: Annotated[GlobalSynthesisDTO | None, Field(
        default=None, 
        description="Stores the final synthesized output of the document."
    )]
    results: Annotated[list[AtomResultDTO], Field(
        description="SDUI-RULE: Backend must return this list strictly topologically sorted. Frontend does not compute the DAG."
    )]
    hydrated_references: Annotated[dict[str, HydratedAtomDTO], Field(
        description="O(1) Dictionary: tda_id -> Static text."
    )]

    @model_validator(mode='after')
    def enforce_referential_integrity(self) -> Self:
        """
        FAIL-FAST ARCHITECTURE INVARIANT:
        Ensures that every tda_id present in the results list and dependencies
        actually exists in the hydrated_references dictionary.
        """
        ref_keys = set(self.hydrated_references.keys())
        
        # Declarative Set Logic (declarative_set_logic_mandate)
        used_ids = {res.tda_id for res in self.results}
        dep_ids = {dep for res in self.results for dep in res.depends_on_tda_ids}
        sc_ids = {sc for res in self.results for sc in res.short_circuit_reason_tda_ids}
        
        all_referenced_ids = used_ids | dep_ids | sc_ids
        missing_keys = all_referenced_ids - ref_keys
        
        if missing_keys:
            raise ValueError(f"Referential Integrity Error: Missing keys in hydrated_references: {missing_keys}")
            
        return self
```

---

## 3. Pakotettu Migraatio ja No Fallback -politiikka (Hard Cutover)

Järjestelmä on siirrettävä käyttämään tätä uutta DTO:ta välittömästi kokonaisuudessaan.

> [!CAUTION]
> **Tier 3 Mandaatti (Hard Cutover / No Proxies):** Strangler Fig -malli (vanhan koodin tilapäinen ylläpito adapterien ja `@deprecated`-proxyjen avulla) on hylätty, koska se jättää koodikantaan vaarallisen "ikuisen teknisen velan" (Hollow Shells). Epic-sarja (91.5, 92, 93) toteutetaan puhtaana "Big Bang" -tyylisenä Hard Cutoverina.
> 
> * **Ei Adaptereita:** Mitään `legacy_dto_mapper.py` -kääntäjiä vanhan ja uuden välille ei rakenneta.
> * **Delete, don't Deprecate:** Vanha moottorikoodi ja rakenteet poistetaan (Delete) koodikannasta suoraan, eikä niitä jätetä kummittelemaan proxy-metodeina.
> * **Hyväksytty Katkos:** Koodikanta on arkkitehtuurisesti rikki Epicien 91.5 ja 92 implementoinnin ajan. Järjestelmä palautuu täyteen toimintakuntoon vasta Epicin 93 valmistuessa, jolloin se on 100% puhdas, ilman pisaraakaan legacy-koodia.

### Käyttöliittymä (SDUI) ja PDF
Flutter refaktoroidaan lukemaan dataa olettaen, että Backend on hoitanut topologisen lajittelun. Flutter purkaa UI-komponentit lukemalla `results`-listaa ja hakemalla tekstit O(1)-operaatioina `hydrated_references`-sanakirjasta käyttäen `sdui_component`-vihjettä. Kaikki puiden rekursiivinen parsiminen (Nested Traversing) poistetaan UI-koodista.

> [!CAUTION]
> **Main Thread Jank -esto (`main_thread_jank_isolate`):** Massiivisen (jopa tuhansia atomeja sisältävän) DTO-JSON-payloadin synkroninen purkaminen Flutterin pääsäikeessä jäädyttäisi käyttöliittymän (Frame Drop). Payloadin JSON-parsiminen (`jsonDecode`) ja instanssien muuntaminen on **pakotettu** suoritettavaksi taustasäikeessä käyttäen Dartin `await Isolate.run()` -komentoa. Pääsäie vastaa vain renderöinnistä.

### Tietokannan Historiadatan Käsittely (Atomic Transition)
Koska vanhat DTO-mallit poistetaan, olemassa oleva kanta-data hajoaisi noudettaessa.
* **Vanhat ajo-objektit (Execution runs):** Nämä voidaan poistaa / nollata (Wipe). Tuotantotietokannassa historiallisia ajoja ei yritetä parsia uusiksi graafeiksi.
* **Tulostusmäärittelyt (Definitions / Prompt Blocks):** Näille on tehtävä datamigraatioskripti. Määrittelyt siirretään kerralla tukemaan uutta mallia.

> [!IMPORTANT]
> **Tier 3 Mandaatti (Phase 0: Coverage Bootstrap & Zero Behavioral Change):**
> Vaikka tuotannon historialliset ajot voidaan nollata, **testien dataa (fixtures/mocks) ei saa koskaan sokeasti tuhota**. Jos testidata poistetaan, järjestelmän testikattavuus romahtaa ja uuden moottorin rakentaminen on sokeaa leikkausta.
> 
> Ennen yhdenkään Epic 92:n moottoritiedoston refaktorointia on suoritettava **Characterization Tests (Golden Master)**:
> 1. Olemassa olevien testien testidata ja fixturet on **konvertoitava uuteen DTO-muotoon**.
> 2. Testit on saatava vihreiksi uutta DTO-rakennetta vasten, jotta voidaan matemaattisesti taata *Zero Behavioral Change* (uusi moottori ei vahingossa muuta liiketoimintasääntöjä).
> 3. Auditoidessa on aggressiivisesti puhdistettava orvot fixturet (Orphaned Fixture Cleanup), jotka eivät enää palvele uutta arkkitehtuuria, jotta 100% testikattavuusvaatimus säilyy aitona.

---

## 4. Havaitut Uhat ja Arkkitehtuurilliset Korjaukset

Tämä DTO-silta torjuu seuraavat järjestelmätason uhat ennen Epic 92/93 aloittamista:

* **Orvot viittaukset ja referentiaalisen eheyden romahdus (Fail-Fast):** Uusi DTO-malli voisi teoriassa luottaa implisiittisesti siihen, että `tda_id`-viittaukset täsmäävät `hydrated_references` -sanakirjan avaimiin. Järjestelmäarkkitehtuurimme kuitenkin kieltää implisiittisen luottamuksen. **Korjaus:** Estetty lisäämällä `@model_validator(mode='after')` -validaattori `ReportDataDto`:hon, joka varmistaa joukko-opilla, että yksikään atomi tai riippuvuus ei viittaa olemattomaan ID:hen. Tämä estää Frontendin Null-Pointer -kaatumiset välittömästi backendissä.
* **SDUI-pariteetin turvaaminen (Frontend Logic Ban):** Jos Backend lähettää litteän listan, Frontend ei saa vastata DAG-puun topologisesta järjestämisestä. **Korjaus:** Backendin on palautettava `results`-lista valmiiksi topologisesti järjestettynä. Lisättiin `sdui_component` -tyyppivihje (sidottu `SDUIComponentType` -enumiin). Frontendin ei tule koskaan "päätellä", miten tieto esitetään, vaan sen on sokeasti toteltava backendin ohjeita.
* **OpenAPI- ja LLM-sopimusten löyhyys:** Ratkaistu koodigeneraatiota tukevalla `ExecutionStatus(str, Enum)` -luokalla, sekä kognitiivisen tilan validaattorilla (`validate_cognitive_vs_system_state`), joka tekee perusteluista pakollisia onnistuessa.
* **Anti-Corruption Layer ja Kanta-migraatio (Duct-Tape Riski):** Täsmennettiin tilapäisen adapterin ehtoja: se ei saa koskaan niellä virheitä (esim. `try/except pass` -fallbackeilla), vaan sen on kaaduttava deterministisesti (HTTP 500), jos vanha moottori tuottaa rikkonaista tai yhteensopimatonta dataa. Lisäksi vaaditaan tietokantojen migraatio tai tyhjennys, koska vanhojen DTO-mallien poistaminen koodikannasta hajoittaa väistämättä olemassa olevien dokumenttien deserialisoinnin.
* **Pydantic V2 Enum Strict Casing & Raw Database Updates (No-String Mandate Strictness):** Pydantic V2:n `StrEnum` on erittäin tiukka kirjainkoon suhteen (esim. `ExecutionStatus.RUNNING` eikä `"running"`). Jos tietokantaa (kuten TinyDB) päivitetään suoraan raw-sanakirjoilla ohittaen Pydantic-validaatio (esim. `{"status": "running"}`), kirjoitus onnistuu, mutta sitä seuraava luku (`model_validate`) kaatuu `ValidationError`-virheeseen. **Arkkitehtuurisääntö:** Kovakoodattujen status-merkkijonojen käyttö koodikannassa on ehdottomasti kielletty. Tietokantapäivityksissä on aina käytettävä enumin `.value` -attribuuttia (esim. `ExecutionStatus.RUNNING.value`) silloin kun päivitetään dict-muodossa.
* **DAG Macro-Orchestration Status -synkronisaatio (Magic Strings -kielto):** Aiempi tapa käyttää vapaita merkkijonoja (kuten `"completed"`, `"finished"`, `"done"`) aiheutti synkronointiongelmia backendin, tietokannan ja käyttöliittymän (Frontend) välillä, ja romutti OpenAPI/Swagger-rajapintakuvauksen luotettavuuden. `ExecutionStatus` toimii nyt järjestelmän Single Source of Truth -luokkana, jonka on tuettava reaaliaikaisia tilasiirtymiä (RUNNING, QUEUED) ja tiukasti määriteltyjä lopputiloja. **Arkkitehtuurisääntö:** Vanha, epätarkka `COMPLETED`-tila on poistettu (deprecated). Ohjelmistoarkkitehtuurissa kaatunut ajo (FAILED) on myös "valmis", joten pelkkä "completed" on liian moniselitteinen. Tästä lähtien päättynyt tila ilmaistaan aina yksiselitteisesti joko `PASSED` (onnistui) tai `FAILED` (kaatui). Pydanticin Fail-Fast -validointi (`strict=True`) estää automaattisesti näiden sääntöjen rikkomisen.

---

## 5. Toimeenpanosuunnitelma (Implementation Plan)

> [!IMPORTANT]
> **Phase A (Foundation Cleanup)** on pääosin valmis. Alla oleva tilannekatsaus päivitetty 2026-07-14.

### Phase A: Foundation Cleanup (Status)

| Tehtävä | Kuvaus | Status |
|---|---|---|
| **A1** | Live Models siirto pois legacy-tiedostoista (`PromptContextDTO` → `prompt_context.py`) | ✅ Valmis |
| **A2** | Aidosti orpojen legacy-tiedostojen poisto (`context.py`, `matrix.py`, `scoring.py`, `specialists.py`, `synthesis.py`, `validation.py`) | ✅ Valmis |
| **A3** | `ReportDataDto` → `v2_core.ReportDataDTO` migraatio (tuotantokoodi: `execution.py`, `executions.py` router, `sdui_mapper_service.py`) | ✅ Valmis |
| **A3+** | Testien korjaus, `MatrixReducer` refaktorointi, legacy `dtos/report/` -hakemiston ja `result_projector.py` lopullinen tuhoaminen | ☐ Toteutetaan seuraavaksi (ks. `implementation_plan.md`) |
| **A4** | MatrixReducer Contradiction → `reduce_matrix(ExecutionRecord)` | ☐ Katettu A3+ -planimme sivuvaikutuksena |
| **A5** | Puuttuvat DTO-asetukset: `AUTO_RESOLVE_POLICY` ja `MINIMUM_COMPLETENESS_THRESHOLD` → `settings.py` | ☐ Itsenäinen `/tier3-feature-refactor` -sessio |
| **A6** | Golden Master Fixture Cleanup | ✅ De facto valmis: fixture-tiedostot deletoidaan A3+ -planissa, koska koko vanha DTO-malli tuhoutuu |

### Phase B: Backend Features (Odottaa Phase A:n valmistumista)

| Tehtävä | Kuvaus | Status |
|---|---|---|
| **B1** | SDUI Mapper Service täydentäminen | ☐ |
| **B2** | PDF Generator `StrictUndefined` Enforcement | ☐ |
| **B3** | Golden Master E2E Test (uusi, v2_core-pohjainen) | ☐ |
| **B4** | Excel Export Modernization | ☐ |
| **B5** | N/A Manual Override API | ☐ |

### Phase C: Frontend Synchronization (Odottaa Phase B:n valmistumista)

| Tehtävä | Kuvaus | Status |
|---|---|---|
| **C1** | Riverpod Cache Invalidation | ☐ |
| **C2** | Sunset Legacy Frontend Models & Views | ☐ |
| **C3** | XAI Evidence Cards | ☐ |
| **C4** | Main Thread Jank Prevention (`Isolate.run()`) | ☐ |

---

## 6. Definition of Done (DoD)

### Phase A DoD (Foundation Cleanup)
* ✅ `v2_core.ReportDataDTO` on koodattu ja toimii tuotannossa SSOT:na.
* ✅ API (`executions.py` router) palauttaa yksinomaan `v2_core.ReportDataDTO` -objekteja.
* ☐ Vanha `backend_v2/models/dtos/report/` -hakemisto on tuhottu koodikannasta.
* ☐ `result_projector.py` (EnrichedResultProjector, V3ResultProjector) on tuhottu.
* ☐ Kaikki testit käyttävät uutta `v2_core.ReportDataDTO` -mallia.
* ☐ `settings.py` sisältää `AUTO_RESOLVE_POLICY` ja `MINIMUM_COMPLETENESS_THRESHOLD`.

### Phase B DoD (Backend Features)
* ☐ `SduiMapperService` tuottaa täydellisen `ReportView` -komponenttipuun.
* ☐ PDF Generator käyttää `StrictUndefined` -moottoria.
* ☐ Golden Master E2E -testi todistaa koko putken: `ExecutionRecord → ReportDataDTO → ReportView`.

### Phase C DoD (Frontend Synchronization)
* ☐ Flutter käyttää Riverpod O(1) -välimuistia ja Freezed-malleja.
* ☐ Legacy frontend-mallit on tuhottu.
* ☐ XAI Evidence Cards renderöidään SDUI-komponentteina.
* ☐ `Isolate.run()` estää Main Thread Jank -ongelman.
