# **TAVOITEDOKUMENTTI: Askelten Eriyttäminen ja Uudelleenkäytettävyys (TaskBlueprint / SystemStep)**

## **1. Ongelman Kuvaus**

V2-arkkitehtuurin alkuperäisessä "De-Generator"-suunnitelmassa tehtiin kriittinen havaintovirhe tietokantamallinnuksessa: Työnkulun askeleet (`StepRule`) mallinnettiin elämään yksinomaan `Workflow`-objektin sisällä (upotettuina `steps`-listaan).

V1:ssä (kuten `seed_data.json` osoittaa) askeleet (esim. `step_guard`) olivat erillisiä, itsenäisiä entiteettejä, joita pystyi kytkemään *useisiin eri työnkulkuihin*. Askel sisälsi massiivisen määrän ohjeistusta (`llm_prompts`) ja deterministisiä esiprosessoreita (`pre_hooks`).

Jos jatkaisimme aiemmalla V2-mallilla, joutuisimme *kopioimaan* saman "Guard"-askeleen matriisiluettelot ja ohjeet manuaalisesti jokaiseen uuteen työnkulkuun. Tämä johtaisi ylläpitokelvottomaan hajautumiseen ja "Single Source of Truth" -periaatteen rikkoutumiseen ohjeistuksessa.

Lisäksi huomattiin, että V1:stä ei oltu migroimassa kaikkea ohjeistusta V2:een, koska V2 keskittyi aluksi vain "mitattaviin arviointeihin" (UniversalMatrix), hyläten pitkät säännöt ja LLM-mandaatit.

## **2. Tavoite ja Ratkaisu**

Tavoitteena on palauttaa askeleille modulaarisuus ja varmistaa **100 % V1-ohjeistuksen säilyminen** migraatiossa. 

Saavutamme tämän tekemällä kolme arkkitehtuuritason korjausta:

### **A. Uusi Tietokantamalli: `TaskBlueprint` (tai `SystemTask`)**
Irrotamme askeleen kognitiivisen ytimen työnkulusta. Luodaan uusi kokoelma `task_blueprints`, joka vastaa V1:n `steps`-kokoelmaa. Se kokoaa yhteen toisiinsa liittyvät ohjepalikat ja hookit.

Esimerkki uudesta rakenteesta (`v2_core.py`):
```python
class TaskBlueprint(BaseModel):
    id: str
    slug: str
    name: I18nText
    description: I18nText
    prompt_blocks: list[str]  # Lista slug-viittauksia (matrices/instructions)
    pre_hooks: list[str]      # Esim. "sanitize_text"
    model_strategy: str | None # Esim. "fast"
```

### **B. Workflown Ohentaminen Reitittimeksi**
`Workflow.steps` ei sisällä enää prompt-viittauksia tai LLM-strategioita. Se vain *reitittää* TaskBlueprintejä DAG-verkossa.

Esimerkki ohennetusta rakenteesta:
```python
class StepRule(BaseModel):
    id: str                  # Graafin solmun ID
    task_blueprint: str      # Viittaus TaskBlueprintin slugiin (esim. "task_guard")
    depends_on: list[str]    # Edeltävät askeleet
    input_mappings: dict     # Datan reititys (esim. "$inputs.history")
```

### **C. Täydellinen Instruction-Migraatio**
Kaikki V1:n `llm_prompts`-taulun tekstit (myös ne, jotka eivät tuota JSON-sarakkeita) pitää migroida V2:n tietokantaan. Ne tallennetaan `matrices` (PromptBlocks) -kokoelmaan siten, että niiden `type` on erikseen `MatrixDataType.INSTRUCTION`.

Näin järjestelmä tunnistaa, että kyseinen matriisi on pelkkää System Promptin sisällysluetteloa, eikä odota tekoälyn palauttavan siihen omaa dimension-arvoaan.

Älä käytä UUID:tunnisteita linkkina vaan slug

## **3. Suoritusaskeleet (Toimenpiteet)**

1. **Päivitä `v2_core.py` (Backend)**
   * Lisää uusi Pydantic-malli `TaskBlueprint`.
   * Puhdista `StepRule`-malli poistamalla `matrix_ids` ja `model_strategy`, korvaa ne `task_blueprint` -viittauksella.
2. **Laajenna `migrate_v1_to_v2.py` (Migraatioskripti)**
   * Skriptin on pelastettava *kaikki* V1-komponentit V2 `matrices` -kokoelmaan asettaen pelkille teksteille `type="instruction"`.
   * Skriptin on luotava V1:n `stepit` erillisiksi `TaskBlueprint` -dokumenteiksi V2-siemendataan (`seed_data.json`).
3. **Päivitä Työnkulkumoottori (`DAGExecutor` ja `PromptCompiler`)**
   * Työnkulkumoottorin on suorituksen aikana luettava työnkulusta `task_blueprint`-slug, haettava tuo blueprint tietokannasta ja annettava sen `prompt_blocks` kääntäjälle työstettäväksi.
4. **Päivitä UI (Admin Studio)**
   * Poista "Step" rakennuspalikoista Prompt Blocks -valinnat. Luo uusi CRUD-näkymä "Task Blueprints", jossa asiantuntijat rakentavat näitä ohjenippuja erillään työnkuluista.
   
Tämän muutoksen myötä voimme käyttää "Guard"- tai "Analyst"-taskeja sadoissa eri työnkuluissa vapaasti dynaamisina noodeina menettämättä tippaakaan V1:n raskaasta LLM-ohjeistuksesta.
