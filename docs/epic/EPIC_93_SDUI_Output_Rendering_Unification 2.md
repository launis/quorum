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

1. **Näyttö (Flutter / SDUI):** API (backend\_v2/api/routers/output\_profiles.py) lukee DTO:n ja muuntaa sen models/view/sdui.py \-komponenteiksi ruudulle piirrettäväksi.  
2. **Staattinen Dokumentti (PDF):** backend\_v2/services/pdf\_generator.py ottaa saman DTO:n ja renderöi sen templates/report\_template.jinja2 \-pohjan kautta.  
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
* **Reducer-solmu:** Jotta LLM ei tukehtuisi dataan, työnkulkuun lisätään ohjelmallinen matrix\_reducer.py \-solmu. Se poistaa aiempien solmujen JSON-tulosteista raskaan metadatan, ja syöttää vain tislatun ydin-tiedon synteesi-LLM:lle.  
* **Tulos:** Kun DAG päättyy, meillä on yksi täydellinen, tyyppiturvallinen ExecutionState, joka konvertoidaan puhtaaksi ReportDataDto:ksi.

### **3\. Universaali Tulostus (Ports & Adapters)**

Koska meillä on nyt yksi täydellinen, ui-agnostinen ReportDataDto, voimme palvella mitä tahansa asiakasta API-reitittimien (backend\_v2/api/routers/execution/executions.py) sisällä toimivilla *Adaptereilla*:

#### **A. Näyttö / Flutter Käyttöliittymä (SDUI Backend-For-Frontend)**

* **Reitti:** /api/v2/executions/{id}/sdui  
* **Mekanismi:** Backend toimii kääntäjänä (BFF). Kooditason mapperi (esim. sdui\_mapper.py) ottaa puhtaan ReportDataDto:n, suodattaa sen OutputProfile:n avulla ja **koodissa** kääntää datan tyyppiturvallisesti backend\_v2/models/view/sdui.py \-malleiksi (esim. SduiNarrativeCard).  
* **Tulos:** Flutter saa standardoidun UI-komponenttipuun ja piirtää sen natiivisti ilman Markdownin parsimista. Koodi on testattavissa, eikä Pydantic-muutos riko tietokantaa.

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

### **Yhteenveto**

Tällä arkkitehtuurilla saavutamme täydellisen vastuiden eriyttämisen (Separation of Concerns). **Tietokanta (Seed Data)** määrittelee älykkyyden ja käyttöoikeudet. **Ydinputki (DAG)** tekee raskaan kognitiivisen työn. **DTO-kanta** muodostaa ehdottoman, rakenteellisen totuuden lähteen (Headless). **Ohjelmistoadapterit** jakelevat tämän totuuden saumattomasti näyttöön, paperille, muihin järjestelmiin tai raakadataksi. Jumalkoodi on eliminoitu.

---

# **OSA 2: Arkkitehtuurin Kriittinen Jalostus ja Kooditason Ratkaisut**

Edellisen mallin (2-Stage Opaque Schema) haavoittuvuus oli hiljainen virheiden nielu (Graceful Degradation), joka tuhoaa forensisen auditoitavuuden (Forensic Sovereignty). Ratkaisu on "Fail-Fast" -periaatteen soveltaminen Pydantic-kontekstissa ja virherajapinnan siirtäminen BFF-kerrokseen (Backend-For-Frontend) suoraan koodissa.

### **1. Pydantic Context Injection ja Deterministinen Resoluutio**

**Kritiikki (Falsifikaatio):** Erillinen alias-resoluutio `scoring.py`:ssä on altis katkoksille. Jos LLM yhdistää kaksi aliasta ("DOC-1 ja DOC-2"), koodi kaatuu tai kadottaa toisen. Jos validointi ja alias-mäppäys erotetaan, serialisointi hidastuu.
**Ratkaisu (Koodi):** Käytetään Pydanticin `ValidationInfo` -kontekstia yhdistämään validointi ja resoluutio deterministisesti samaan vaiheeseen. Sivuvaikutukset (kuten lokitus) on kielletty validattorissa, joten palautamme eksplisiittisen `OpaqueID.UNVERIFIED` -arvon.

```python
from pydantic import BaseModel, ValidationInfo, field_validator
from typing import List, Union
import re

class QuoteEvidenceDTO(BaseModel):
    quote: str
    source_alias: List[str] # Pakotetaan aina listaksi

    @field_validator('source_alias', mode='before')
    def extract_aliases(cls, v):
        # Korjaa LLM:n yhdistelmävirheet (esim. "DOC-1, DOC-2")
        if isinstance(v, str):
            found = re.findall(r'DOC-\d+', v)
            return found if found else ["OpaqueID.UNVERIFIED"]
        return v

    @field_validator('source_alias')
    def resolve_aliases(cls, v: List[str], info: ValidationInfo):
        # AliasRegistry injektoidaan suoraan DAG-workerista
        registry = info.context.get("alias_registry", {}) if info.context else {}
        resolved = []
        for alias in v:
            actual_id = registry.get(alias)
            # Hiljaisen degradation sijaan liputetaan virhe rakenteellisesti
            resolved.append(actual_id if actual_id else "OpaqueID.UNVERIFIED")
        return resolved
```

### **2. BFF SDUI-Mappaus ja Virherajapinnan Inversio (RFC 7807)**

**Kritiikki (Falsifikaatio):** Jos BFF (esim. `sdui_mapper.py`) generoi jokaiselle `source_alias` -arvolle oman SDUI-kortin, UI duplikoi saman lainauksen (Huono UX). UI:n ei pidä kaatua, mutta datan menetystä ei sallita. Validator-metodeihin koodattu Dual-Reporting tuottaisi myös sivuvaikutuksia data-malleihin.
**Ratkaisu (Koodi):** Yhdistetään lainauksen lähteet SDUI-kortin `sources` -listaan `sdui_mapper.py`:ssa. Jos mukana on `OpaqueID.UNVERIFIED`, muutetaan kortin tyyppi `SduiWarningCard` -komponentiksi, joka säilyttää datan mutta varoittaa loppukäyttäjää hallusinaatiosta. Samalla BFF tekee Dual-Reporting lokituksen (ainoassa oikeassa paikassa sivuvaikutuksille).

```python
def map_evidence_to_sdui(q: QuoteEvidenceDTO) -> SduiComponent:
    source_names = []
    has_unverified = False
    
    for source_id in q.source_alias:
         if source_id == "OpaqueID.UNVERIFIED":
             has_unverified = True
             # Dual-Reporting tapahtuu tässä adapterikerroksessa, ei data-mallissa
             logger.error(f"Hallusinoitu alias havaittu: {q.quote}") 
         else:
             # Snapshot-nimen haku (simuloitu)
             source_names.append(get_snapshot_name(source_id))
    
    if has_unverified:
         # Pusketaan virheraja Flutterille asti. "Tyhmä" UI vain piirtää.
         return SduiWarningCard(
             text=q.quote, 
             sources=source_names, 
             error="Varmentamaton lähde (AI Hallusinaatio)"
         )
         
    return SduiQuoteCard(text=q.quote, sources=source_names)
```

**Johtopäätös:** Tämä malli poistaa alias-resoluution erillisen vaiheen. Se estää LLM:n syntaksivirheet deterministisellä Regex-esikäsittelyllä, kieltää validattoreiden sivuvaikutukset, ja pakottaa hallusinaatiot datavirtaan (`OpaqueID.UNVERIFIED`), jonka SDUI-BFF-kerros lopulta nappaa turvallisesti käyttöliittymään. Jumalkoodi ja Regex-hakkerointi on virallisesti korvattu tyyppiturvallisella putkella.

---
