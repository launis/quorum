# **Epic 93: SDUI Output Rendering Unification (Vaihe 3/3)**

> [!CAUTION]
> **RIIPPUVUUSVAROITUS:** Tämä on arkkitehtuurimigraation viimeinen vaihe (3/3). Tätä Epicciä EI saa toteuttaa ennen kuin Epic 91.5 (DTO Bridge) ja Epic 92 (Moottori) ovat tuotannossa. Tämän Epicin tehtävänä on kuluttaa puhtaita `ReportDataDto` -objekteja ja kääntää ne SDUI-käyttöliittymäksi ja PDF-dokumenteiksi. Vanha Putki B (Jumalkoodi) tuhotaan tämän Epicin päätteeksi kokonaan.

# **OSA 1: Alkuperäinen Luonnos ja Nykytilan Kartoitus**

## **Tulostuksen Unifikaatio ja DTO-vetoinen Universaali Ulostulo**

### **1\. Nykytilan Analyysi (Kahden putken ongelma)**

Quorumissa on tällä hetkellä arkkitehtuurinen konflikti: datan käsittely on jakautunut kahteen toisistaan poikkeavaan paradigmaan.  
**Putki A: Moderni Ydinputki (De-Generator)**

* **Koodiviitteet:** backend\_v2/services/orchestrator/dag\_executor.py (ohjaa putkea), backend\_v2/services/orchestrator/strategies/llm\_execution/chunk\_worker.py ja backend\_v2/services/llm\_task\_executor.py.  
* **Tietokantaviitteet:** backend\_v2/seed/seed\_data.json \-\> kokoelmat "workflows", "prompt\_blocks" ja "extraction\_schemas".  
* **Toiminta:** Tämä on asynkroninen DAG-verkko, joka ohjaa LLM:ää Pydantic-skeemoilla tuottamaan strukturoitua JSON-dataa. Se on deterministinen, nopea ja hyödyntää DLQ-virheensietoa.

**Putki B: Vanha Synteesiputki ("Jumalkoodi")**

* **Koodiviitteet:** backend\_v2/hooks/synthesis.py (erityisesti TextConsolidationHook) ja backend\_v2/hooks/reporting.py.  
* **Toiminta:** Tämä koodi käynnistyy Putki A:n jälkeen. Se tekee omia, putken ulkopuolisia LLM-kutsuja (lainauksien haku, tekstien tiivistäminen) ja tunkee datan sisään raakaa Markdownia. Se ohittaa Putki A:n välimuistit ja virheensiedon.

### **2\. DTO-Kannan Rooli ja Refaktorointi**

**DTO (Data Transfer Object)** on kerros, jonka pitäisi toimia järjestelmän tiedonsiirron selkärankana.

* **Koodiviitteet:** backend\_v2/models/dtos/report.py (ReportDataDto) ja backend\_v2/models/state.py (ExecutionState).  
* **Nykytilan ongelma:** Koska Putki B tuottaa Markdownia, DTO-mallit ovat "saastuneet" esityslogiikasta. Ne toimivat Markdown-säiliöinä sen sijaan, että ne välittäisivät semanttista liiketoimintatietoa. Tämä estää datan joustavan käytön.

### **3\. Tavoitetila: Putkien yhdistäminen ja Universaali Tuloste**

Putki B tuhotaan. Synteesit lisätään prompt\_blocks \-säännöiksi, jotta ne ajetaan Putki A:ssa. Järjestelmän ainoaksi totuuden lähteeksi tulee puhdas **DTO-kanta** (ReportDataDto), josta luodaan Universaali Tuloste eri reitittimien avulla:

1. **Näyttö (Flutter / SDUI):** API delegoi työn palvelulle (`backend_v2/services/sdui_mapper_service.py`), joka lukee DTO:n ja muuntaa sen `models/view/sdui.py` -komponenteiksi ruudulle piirrettäväksi (Anemic Router -sääntö).  
2. **Staattinen Dokumentti (PDF):** backend\_v2/services/pdf\_generator.py ottaa saman DTO:n ja injektoi sen `templates/report_template.jinja2` -pohjaan. **FAIL-FAST -PAKOTUS:** PDF-adapteri käyttää `jinja2.StrictUndefined` -asetusta, mikä tarkoittaa, että puuttuvat avaimet DTO:ssa kaatavat luonnin välittömästi HTTP 500 / DLQ -virheeseen sen sijaan, että ne tuottaisivat asiakkaalle tyhjiä/rikkinäisiä PDF-raportteja:
    ```python
    import jinja2
    pdf_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('backend_v2/templates'),
        undefined=jinja2.StrictUndefined # Kaatuu jos avain puuttuu (Fail-Fast)
    )
    ```
    * **Jinja2 Semanttinen Turva (Epic 92 N_A Tila):** Koska Epic 92 mahdollistaa `N_A`-tilan (oikosulku), Pydantic serialisoi puuttuvat perustelut `null`-arvoiksi (koska kenttä on määritelty `Optional[str]`). Koska avain on olemassa Pydanticin DTO:ssa (arvona `None`), `StrictUndefined` ei laukea perusteettomasti. Jinja-pohjissa on silti **pakollista** kunnioittaa tilakonetta if-lausekkeilla, jottei tulosteeseen renderöidy "None"-sanoja:
    ```jinja2
    {% if atom.status in ['PASSED', 'FAILED'] %}
        <p>Perustelu: {{ atom.evaluation_reasoning }}</p>
    {% elif atom.status == 'N_A' %}
        <p>Tämä osio ohitettiin logiikan vuoksi.</p>
    {% endif %}
    ```
3. **REST API (B2B SaaS / Muut järjestelmät):** API palauttaa Pydanticilla validoidun ReportDataDto \-objektin puhtaana JSONina.  
4. **Syväluotaus (Raakadata):** backend\_v2/services/flattener.py hakee DTO:sta raa'at atomit ja väitteet ja palauttaa ne csv/json \-muodossa analytiikkaa varten.

# **Raportti (Lopullinen Synteesi)**

Tässä on tavoitearkkitehtuuri, joka ratkaisee Quorumin ongelmat, poistaa jumalkoodit ja noudattaa moderneja arkkitehtuuristandardeja. Keskiössä on puhtaan DTO-kannan rooli ja Headless-ajattelu.

## **Epic 93: Quorum Headless DTO & Universal Output Architecture**

### **1\. DTO-Kannan Refaktorointi (The Source of Truth)**

Järjestelmän sydän on **Data Transfer Object (DTO)** \-kerros (backend\_v2/models/dtos/). Se refaktoroidaan täysin irti esitystavasta.

* **Puhdas Data (Headless):** ReportDataDto ja ExecutionState eivät enää sisällä Markdownia, HTML:ää tai UI-tageja. Ne ovat vahvasti tyypitettyjä Pydantic-malleja, jotka sisältävät vain semanttista dataa (esim. executive\_summary: str, evidence\_quotes: List\[QuoteDTO\], urgency\_level: int).  
* **Konfiguraatio, ei koodia:** Tietokannan seed\_data.json \-\> "output\_profiles" muuttuu puhtaaksi **semanttiseksi suodattimeksi**. Se ei rakenna käyttöliittymää, vaan määrittää oikeudet: *"Profiilille 'Executive' jätä DTO:sta jäljelle 'global\_synthesis', mutta piilota 'raw\_atoms'"*.

### **2\. Yhtenäinen Ydinputki (Jumalkoodien Kuolema)**

Kahden putken malli poistetaan. Putki B (backend\_v2/hooks/synthesis.py) lakkautetaan. Kaikki sen kognitiiviset vastuut siirretään deterministiseen Putki A:han (DAG).

* **Tietokantaohjattu Työnkulku:** Synteesi ja lainauksien haku lisätään tietokantaan ("prompt\_blocks") omina solmuinaan. Ne ketjutetaan "workflows"-taulussa ajettavaksi tiedonlouhinnan jälkeen (dependencies).  
* **Kognitiivisen Kuorman Hallinta (Strict Matrix Reducer):** Jotta uusi, yksinomaan DAG:ssa toimiva synteesivaihe onnistuu ilman Context Window -ylityksiä, työnkulkuun lisätään ohjelmallinen `matrix_reducer.py` -solmu.
    * **Toiminta:** Karsii aiempien louhintasolmujen tulosteista raskaan metadatan (kuten vektorimallien embed-taulukot) ja syöttää vain tislatun tiedon synteesi-LLM:lle.
    * **Tyyppisopimus:** Reducerin on palautettava tiukasti tyypitetty `LightweightMatrixDTO`. Se ei saa koskaan poistaa `OpaqueID`-viitteitä, jotta synteesin jäljitettävyys (XAI) säilyy.
    * **Arkkitehtuurinen Mandaatti (Poison Pill -esto):** Reducerin on laskettava `token_count` etukäteen. Jos LLM:n konteksti-ikkuna ylittyy, Reducer **ei saa** kaataa ajoa poikkeuksella DLQ-tilaan, sillä suurten dokumenttien token-ylitykset ovat deterministisiä ja aiheuttaisivat taustatyöntekijöissä ikuisen "Poison Pill" -uudelleenyrityssilmukan. Sen sijaan Reducerin on suoritettava kaskadoituva Token-kompressio:
        1. **Tier 1 (Soft Reduction):** Karsii turhat `evaluation_reasoning` -kentät kaikilta `PASSED`-tilaisilta atomeilta, mutta säilyttää ehdottomasti hylättyjen/blokattujen/virhetilaisten perustelut.
        2. **Tier 2 (Map-Reduce Cascade):** Jos data on tislauksenkin jälkeen liian suurta, Reducer jakaa matriisin dynaamisiin alilohkoihin (Map), tekee useita asynkronisia osasynteesejä, ja syöttää niiden lopputulokset viimeiselle synteesi-LLM:lle (Reduce) tuottaakseen valmiin raportin ilman kaatumista.
* **Tulos:** Kun DAG päättyy, meillä on yksi täydellinen, tyyppiturvallinen ExecutionState, joka konvertoidaan puhtaaksi ReportDataDto:ksi.

### **3\. Universaali Tulostus (Ports & Adapters)**

Koska meillä on nyt yksi täydellinen, ui-agnostinen ReportDataDto, voimme palvella mitä tahansa asiakasta API-reitittimien (backend\_v2/api/routers/execution/executions.py) sisällä toimivilla *Adaptereilla*:

#### **A. Näyttö / Flutter Käyttöliittymä (SDUI Backend-For-Frontend)**

* **Reitti:** /api/v2/executions/{id}/sdui  
* **Mekanismi:** Backend toimii kääntäjänä (BFF). Reititin on aneeminen ja delegoi työn suoraan `backend_v2/services/sdui_mapper_service.py` -palvelulle. Tämä Service ottaa puhtaan `ReportDataDto`:n, suodattaa sen `OutputProfile`:n avulla ja kääntää datan tyyppiturvallisesti `backend_v2/models/view/sdui.py` -malleiksi.  
* **Tulos:** Reititin ei sisällä liiketoimintalogiikkaa. Flutter saa standardoidun UI-komponenttipuun ja piirtää sen natiivisti ilman Markdownin parsimista. Koodi on eristetysti testattavissa.

#### **B. REST API \-liittymä (B2B Kone-integraatiot)**

* **Reitti:** /api/v2/executions/{id}/report  
* **Mekanismi:** Kun ERP-järjestelmä tai ulkoinen AI-agentti hakee dataa, API ohittaa SDUI-käännöksen täysin. Se palauttaa suodatetun ReportDataDto:n sellaisenaan JSON-muodossa.  
* **Tulos:** Puhdas, koneluettava, standardoitu ja API-First \-yhteensopiva rajapinta.

#### **C. Staattinen Dokumentti (PDF)**

* **Reitti:** /api/v2/executions/{id}/pdf  
* **Mekanismi:** PDF-adapteri (backend\_v2/services/pdf\_generator.py) lukee puhtaan ReportDataDto:n ja injektoi sen suoraan backend\_v2/templates/report\_template.jinja2 \-pohjaan.  
* **Tulos:** Laadukas PDF, jossa sivutukset ja asettelut hallitaan Jinja2:ssa riippumattomana ruudun käyttöliittymästä tai Markdown-tägeistä.

#### **D. Syväluotaus ja Forensiikka (Raakadata, Atomit ja Väitteet)**

* **Reitti:** /api/v2/executions/{id}/forensics  
* **Mekanismi:** Adapteri (esim. backend\_v2/services/flattener.py) ohittaa korkean tason synteesit. Se poimii ExecutionState:sta suoraan chunk\_accumulator ja evaluations \-listat ja "litistää" alkuperäiset tekstiatomit, väitteet ja lainaukset.  
* **Tulos:** Täydellisen läpinäkyvä XAI-auditoitavuus JSON- tai CSV-vientitiedostona analytiikkaa varten.

#### **E. Arkkitehtuurinen Mandaatti: Aneemiset Reitittimet & IAM Guards**
* Kaikkien `/api/v2/executions/{id}/*` -reitittimien on oltava "Aneemisia Reitittimiä" (Anemic Routers). Jotta estetään BOLA/IDOR -tietoturvavuodot (cross-tenant tiedon urkinta), reitittimiin on **pakotettava** `Depends(require_role)` ja `Depends(verify_tenant_access)` -injektiot. FastAPI-reititin ei koskaan saa palauttaa dataa pelkän UUID-arvauksen perusteella ilman luvitusinjektion läpäisyä.

### **Yhteenveto**

Tällä arkkitehtuurilla saavutamme täydellisen vastuiden eriyttämisen (Separation of Concerns). **Tietokanta (Seed Data)** määrittelee älykkyyden ja käyttöoikeudet. **Ydinputki (DAG)** tekee raskaan kognitiivisen työn. **DTO-kanta** muodostaa ehdottoman, rakenteellisen totuuden lähteen (Headless). **Ohjelmistoadapterit** jakelevat tämän totuuden saumattomasti näyttöön, paperille, muihin järjestelmiin tai raakadataksi. Jumalkoodi on eliminoitu.

---

# **OSA 2: Arkkitehtuurin Kriittinen Jalostus ja Kooditason Ratkaisut**

Edellisen mallin haavoittuvuus oli hiljainen virheiden nielu (Graceful Degradation), joka tuhoaa forensisen auditoitavuuden (Forensic Sovereignty). Ratkaisu on "Fail-Fast" -periaatteen soveltaminen Pydantic-kontekstissa ja virherajapinnan siirtäminen BFF-kerrokseen (Backend-For-Frontend).

### **1. Pydantic Context Injection ja Rakenteellinen Tyyppiturvallisuus**

Vanha ratkaisu nojasi "Magic Stringeihin" ja hiljaiseen virheiden ohitukseen. Uusi ratkaisu nojaa tiukkaan Pydantic-rakenteeseen ja "Fail-Fast" -periaatteeseen. LLM:n hallusinoimat lähdeviitteet (aliakset, joita ei löydy järjestelmästä) on koodattava eksplisiittisesti rakenteeseen, jotta B2B-rajapinnat ja parserit eivät kaadu.

Alias-resoluutio injektoidaan suoraan validaattorin kontekstiin (`info.context`), jolloin Pydantic-malli hoitaa turvallisesti erottelun onnistuneiden käännösten ja LLM-hallusinaatioiden välillä.

```python
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator
from typing import Annotated, Any
import re
from uuid import UUID
from backend_v2.services.orchestrator.engine.alias_engine import AliasEngine

class QuoteEvidenceDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra='forbid')
    quote: str
    verified_source_ids: Annotated[list[UUID], Field(default_factory=list, description="Verified database UUIDs")]
    unverified_aliases: Annotated[list[str], Field(default_factory=list, description="XAI auditable LLM hallucinations")]
    is_verified: Annotated[bool, Field(default=True)]

    @model_validator(mode='before')
    @classmethod
    def resolve_and_partition_aliases(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data
            
        raw_aliases = data.get('source_aliases', [])
        # Fix LLM combination errors using SSOT AliasEngine regex pattern
        if isinstance(raw_aliases, str):
            raw_aliases = re.findall(AliasEngine.ALIAS_REGEX_PATTERN, raw_aliases.upper()) or [raw_aliases]
            
        # AliasRegistry is injected directly from the DAG worker (e.g., via ExecutionState context)
        registry = info.context.get("alias_registry", {}) if info.context else {}
        
        verified = []
        unverified = []
        
        for alias in raw_aliases:
            if not isinstance(alias, str): continue
            actual_id = registry.get(alias)
            if actual_id:
                verified.append(actual_id)
            else:
                unverified.append(alias)
                
        data['verified_source_ids'] = verified
        data['unverified_aliases'] = unverified
        data['is_verified'] = len(unverified) == 0
        
        # Prevent Pydantic extra_fields errors by purging the input
        data.pop('source_aliases', None)
        return data
```

### **2. BFF SDUI-Mappaus ja Universaali Reititys (Backend-For-Frontend)**

**Kritiikki (Falsifikaatio):** Jos BFF (esim. `sdui_mapper.py`) generoi jokaiselle `source_alias` -arvolle oman SDUI-kortin, UI duplikoi saman lainauksen (Huono UX). UI:n ei pidä kaatua, mutta datan menetystä ei sallita. Validator-metodeihin koodattu Dual-Reporting tuottaisi myös sivuvaikutuksia data-malleihin. Lisäksi, taaksepäinyhteensopivuus ja legacy-muotojen ohitukset BFF-kerroksessa (Duct-Tape) tuhoaisivat "No Fallback" -politiikan.
**Ratkaisu (Koodi):** Data-malli on nyt täysin vapaa sivuvaikutuksista. BFF-kerros kääntää tyyppiturvallisen datan UI-komponenteiksi ilman liiketoimintalogiikkaa. Hallusinaatioiden telemetria käsitellään yksinomaan tässä kerroksessa. **Huom:** BFF ei yritä parsia vanhoja legacy-raportteja, koska Epic 91.5:n linjauksen mukaisesti vanhat ajot on pyyhitty tietokannasta ja jäljellä on vain uuden arkkitehtuurin mukaista V2-dataa.

```python
from backend_v2.utils.llm_debug_logger import logger
from backend_v2.services.system.telemetry import telemetry
from backend_v2.models.view.sdui import SduiComponent, SduiWarningCard, SduiQuoteCard, SduiLayout

def map_evidence_to_sdui(q: QuoteEvidenceDTO, snapshot_registry: dict[UUID, str]) -> SduiComponent:
    # Immutable History Snapshot Mandate: Use pre-loaded frozen registry, no live DB calls during rendering
    source_names = [snapshot_registry.get(vid, "Unknown Source") for vid in q.verified_source_ids]
    
    if not q.is_verified:
         # Dual-Reporting: Handled exclusively in adapter layer, not in data model!
         # Tier 0 Mandate (Logging): No log spam for individual atoms, only telemetry aggregations.
         telemetry.increment("llm_hallucinated_alias_count", len(q.unverified_aliases))
         
         # Tier 0 Mandate (i18n): No hardcoded local strings (strict_enum_l10n_mapping). Pass ICU keys to UI.
         return SduiWarningCard(
             text=q.quote, 
             sources=source_names, 
             unverified_tags=q.unverified_aliases,
             error_key="errors.ai_hallucination"
         )
         
    return SduiQuoteCard(text=q.quote, sources=source_names)

def map_report_to_sdui(report: ReportDataDto, snapshot_registry: dict[UUID, str]) -> SduiLayout:
    # HARD CUTOVER MANDATE (Zero Legacy): No backward compatibility fallbacks allowed.
    # The system will Fail-Fast (HTTP 500) if legacy data arrives.
    return SduiLayout(components=[])
```

**Johtopäätös:** Tämä malli poistaa alias-resoluution erillisen vaiheen kokonaan pois kognitiivisesta ytimestä. Se estää LLM:n syntaksivirheet deterministisellä Regex-esikäsittelyllä, kieltää validattoreiden sivuvaikutukset ja pakottaa hallusinaatiot datavirtaan, jonka SDUI-BFF-kerros lopulta nappaa turvallisesti ja lähettää telemetriaan. Jumalkoodi ja Regex-hakkerointi on virallisesti korvattu tyyppiturvallisella putkella.

---

## 5. Toimeenpanosuunnitelma (Implementation Plan)

### Phase 3: SDUI ja Universal Output (Epic 93)
Kytketään uusi DTO käyttöliittymään ja PDF-generaattoriin. Alias-resoluution eristäminen (Separation of Concerns) toteutuu tässä.

* **[MODIFY] `backend_v2/models/dtos/report/atoms.py`** (`QuoteEvidenceDTO`): Päivitetään sisältämään `@model_validator(mode='before')`, joka käyttää `info.context.get("alias_registry")` -injektiota erottelemaan validit UUID:t hallusinaatioista.
* **[MODIFY] `backend_v2/services/pdf_generator.py`** (sekä Jinja2-pohjat): Pakotetaan `jinja2.StrictUndefined` Fail-Fast -turvaksi. Lisätään Jinja2-pohjiin `N_A` (Oikosulku) -tilan käsittely, jotta vältetään "None"-tekstit PDF:ssä.
* **[NEW] `backend_v2/services/sdui_mapper_service.py`**: Uusi Service-kerros, joka muuntaa topologisesti järjestetyn `ReportDataDto.results` -listan `SduiComponent` -objekteiksi.
* **[MODIFY] `backend_v2/api/routers/output_profiles.py`**: Pakotetaan reititin aneemiseksi. Reititin ainoastaan injektoi luvat ja delegoi kutsun `SduiMapperService`:lle (Anemic Routers -mandaatti).
