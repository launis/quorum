# Master Protocol: SDUI Purge & Extreme MVC Migration V3
**Status:** REQUIRED REFACTORING FOR NEW CONTEXT WINDOW
**Target:** `c:\src\quorum\`

## PRIMARY DIRECTIVE FOR AI AGENT
Tämä on ehdoton toimeenpanosuunnitelma. Suorita nämä vaiheet järjestyksessä. **Älä kyseenalaista askeleita tai kysy lupaa – käyttäjä on hyväksynyt nämä.** Tavoitteena on poistaa Server-Driven UI (SDUI) kokonaan ja pakottaa järjestelmä Model-View-Controller (MVC) -malliin. Pydantic-mallien `extra="forbid"` on pidettävä voimassa.

---

### STEP 1: Pydantic-mallien Puhdistus & DTO-lisäykset (`backend_v2/models/v2_core.py`)
**Toimenpiteet:**
1. **ETSI JA POISTA:** Poista koodista KAIKKI SDUI-komponentteihin liittyvät Pydantic-luokat. Poista luokat:
   - `BlueprintComponentBase`
   - `HeaderComponent`, `MetadataHeaderComponent`, `EvaluationNotesPanelComponent`, jne.
   - `Gauge1DComponent`, `Matrix2DComponent`, `Scatter3DComponent`
   - `GridRowComponent`, `RenderBlueprint`
   - Kaikki asioihin liittyvät Literal-tyypit ja Unionit (`BlueprintComponentType`, `BlueprintComponentWithoutGridType`).
2. **MUOKKAA Workflow-luokkaa:**
   - Poista `render_blueprints` kenttä kokonaan `Workflow`-luokasta.
   - Lisää `Workflow`-luokkaan uusi kenttä: `output_mapping: dict = Field(default_factory=dict, description="Pre-defined routing rules for axes")`.
3. **LUO DTO-luokat (Lisää nämä tiedoston v2_core.py loppuun):**
```python
class ReportAxisDTO(V2CoreBase):
    name: str = Field(description="Axis name, e.g. Y-Akseli")
    score: float | None = None
    justification: str | None = None

class ReportDataDTO(V2CoreBase):
    workflow_id: str
    preset_view: Literal["1d_metrics", "2d_compare", "3d_complex", "default"]
    axes: list[ReportAxisDTO] = Field(default_factory=list)
    synthesis: str | None = None
```

### STEP 2: Tietokannan (seed_data.json) massiivinen siivous (`backend_v2/seed/seed_data.json`)
**Toimenpiteet:**
1. **Poista SDUI-Koodi:** Etsi `"workflows"`-listan sisältä kohta `render_blueprints`. Poista tuo kokonainen sanakirja täydellisesti jokaiselta työnkululta (kymmeniätuhansia rivejä).
2. **Lisää Output Mapping:** Lisää puhdistetun `workflow`-objektin sisään (esim. `wf_d653...`) manuaalisesti uusi kenttä `"output_mapping": { "preset_view": "3d_complex" }` jotta malli pysyy validina.
3. **Selkeytä Node-ID:t:** Etsi työnkulun `steps`-listasta raskaat solmutunnisteet (esim. `"id": "steprule_ec0bbf02...`) ja muuta ne ihmisen luettaviksi. 
   - *Sääntö:* Alkuosa `steprule_` on pakollinen, sen perässä oltava vain vähintään 8 merkkiä numeroita tai a-z kirjaimia (ei enää toista alaviivaa).
   - *Esimerkki:* Muuta `steprule_ec0bbf...` -> `steprule_xaireporter1`.

### STEP 3: Kontrollerin koodaus (`backend_v2/services/blueprint.py`)
**Toimenpiteet:**
1. Poista tiedostosta vanha SDUI-logiikka (`resolve_component`, `get_block_title`, vanha PDF-rakentaja). Puhdista tiedosto käytännössä kokonaan.
2. Jätä/Rakenna metodi `build_report_dto(execution_id: str) -> ReportDataDTO:`
   - Metodin tehtävä on noutaa ajo tietokannasta ja pelkistää `$results`-kuorma.
   - Koska SDUI-reititin purettiin, luo metodiin "kovakoodattu" apulogiikka, joka etsii `$results`-avaimista arvosanoja ja tekstejä ja pakottaa ne puhtaiksi `ReportAxisDTO` -olioiksi, ja palauttaa yhden siistin `ReportDataDTO` -olion.

### STEP 4: Tulostuksen (Jinja2) kovakoodaus (`backend_v2/templates/report_template.jinja2`)
**Toimenpiteet:**
1. Poista templatesta rekursiivinen makro `{% macro render_comp(comp) %}` sekä kaikki siihen perustuvat dynaamiset luupit.
2. Aseta pohjaksi kova ohjelmointilogiikka, joka olettaa saavansa syötteenä `ReportDataDTO` -olion.
   ```jinja2
   {% if payload.preset_view == '3d_complex' %}
       <!-- Piirrä puhtaalla HTML:llä 3D-matriisin paikat -->
       <!-- Loopit: for axis in payload.axes -->
   {% elif payload.preset_view == '1d_metrics' %}
       <!-- Piirrä 1D-mittaristo -->
   {% endif %}
   ```

### STEP 5: Testigenerointi (`run_all.py` / `test_pdfs.py`)
**Toimenpiteet:**
1. Aja ensin Pydantic-tietokannan vahvistus: `python backend_v2/seed/run_seed.py local`
2. Korjaa mahdolliset "Extra input is forbidden" validaatiovirheet `seed_data.json` tiedostosta armottomasti pudottamalla ylimääräiset kentät pois.
3. Varmista PDF-generoinnin nopeus Pythonilla. Koko reititys on onnistunut, kun PDF syntyy ilman yhtäkään SDUI-komponenttia, pelkän Pydantic-DTO-objektin voimalla.
