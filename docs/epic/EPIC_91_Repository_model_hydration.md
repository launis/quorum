# ** EPIC 91: Repository Model Hydration & Type-Safety Hardening**

## ** Tavoite**

Refaktoroida database-kerroksen rajapinnat (`interfaces.py`) ja niiden toteutukset (`repositories/`) tukemaan valmiiksi tyypitettyjen ja validoitujen Pydantic-mallien palauttamista kaikille **ei-polymorfisille entiteeteille** (kuten `User`, `Step`, `PromptBlock` ja `SystemConfig` -rakenteet). 

Tämä poistaa kooditoiston (boilerplate) ja parantaa MyPy-tyyppiturvallisuutta palvelukerroksessa (Service Layer), jossa tällä hetkellä joudutaan manuaalisesti kutsumaan `.model_validate(data, strict=False)` jokaisen repositoriokyselyn jälkeen.

---

## ** ARKKITEHTONINEN VIITEKEHYS JA LAATUPERIAATTEET (Hardening-viitekehys)**

Tämän Epicin toteutuksessa noudatetaan Quorum V2:n tiukkaa laadunvarmistuksen ideologiaa (`hardening.xml`):

1. **Pure Hydration Boundary (Sääntö 10):**
   * Tietokannasta (TinyDB/Firestore) ladattu data hydratoidaan tietokantarajalla käyttäen löysää validointiä: `.model_validate(data, strict=False)`. Tämä sallii tietokannan natiivityyppien (kuten päivämäärämerkkijonojen) automaattisen muunnoksen ilman virheitä.
   * API-rajoilla ja FastAPI-reitittimissä säilytetään tiukka validointi (`strict=True`).

2. **Kaksivaiheinen Repositorio-kuvio (Sääntö 74 hienosäätö):**
   * Sääntö 74 (`polymorphic_parsing_mandate`) vaatii repositoriot palauttamaan raakaa `dict[str, Any]`-dataa polymorfisille kokoelmille.
   * Ei-polymorfisille olioille luodaan repositorioihin ensisijaisiksi metodeiksi tyypitetyt malli-metodit (esim. `get_user_model`), mutta raakadatamenetelmät (esim. `get_user`) säilytetään taustalla raakadata-manipulaatiota varten.

3. **Zero Legacy Instantiations (Sääntö 2):**
   * Kaikki legacy-muotoiset Pydantic V1 -konstruktorikutsut (kuten `MyModel(**data)`) korvataan `.model_validate()` -metodeilla.

4. **Kattava Dokumentaatio ja Tyyppivarmistus (Säännöt 24, 54-58):**
   * Kaikki uudet ja muutetut metodit varustetaan Google-tyylisillä docstringeillä (Args, Returns, Raises).
   * Tyypityksessä käytetään PEP 695 geneerisiä tyyppejä ja moderneja union-operaattoreita (`X | None`).

---

## ** VAIHE 1: Käyttäjähallinnan tyyppiturvallisuus (User Model Hydration)**

**Vastuualue:** Backend (Database & Service)

* **Task 1.1: Päivitä Rajapinnat ja Repositorio**
  * **Tiedostot:** 
    * [interfaces.py](file:///c:/src/quorum/backend_v2/database/interfaces.py) (lisää metodit `IIdentityRepository` -rajapintaan)
    * [repositories/identity.py](file:///c:/src/quorum/backend_v2/database/repositories/identity.py) (toteuta metodit)
  * **Toteutus:**
    * Lisää metodi `async def get_user_model(self, user_id: str) -> User | None`
    * Lisää metodi `async def get_user_by_email_model(self, email: str) -> User | None`
    * Käytä toteutuksessa `.model_validate(data, strict=False)` raakadatasta.
* **Task 1.2: Refaktoroi AuthService**
  * **Tiedosto:** [services/auth.py](file:///c:/src/quorum/backend_v2/services/auth.py)
  * **Muutos:** Korvaa manuaaliset `User.model_validate(data, strict=False)` kutsut käyttämällä suoraan repositorion uusia `get_user_model` ja `get_user_by_email_model` -metodeja.

---

## ** VAIHE 2: Työvaiheiden tyyppiturvallisuus (Step Model Hydration)**

**Vastuualue:** Backend (Database & Service)

* **Task 2.1: Päivitä Rajapinnat ja Repositorio**
  * **Tiedostot:** 
    * [interfaces.py](file:///c:/src/quorum/backend_v2/database/interfaces.py) (`IWorkflowRepository`)
    * [repositories/workflow.py](file:///c:/src/quorum/backend_v2/database/repositories/workflow.py) (`WorkflowRepositoryImpl`)
  * **Toteutus:**
    * Lisää metodi `async def get_step_model(self, step_id: str) -> Step | None`
* **Task 2.2: Refaktoroi Studio ja Orkestraattori**
  * **Tiedostot:** 
    * [services/studio.py](file:///c:/src/quorum/backend_v2/services/studio.py)
    * [services/orchestrator/dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)
  * **Muutos:** Korvaa manuaaliset `Step.model_validate(data)` -kutsut repositorion `get_step_model`-kutsuilla.

---

## ** VAIHE 3: Prompt-lohkojen tyyppiturvallisuus (PromptBlock Hydration)**

**Vastuualue:** Backend (Database & Service)

* **Task 3.1: Päivitä Rajapinnat ja Repositorio**
  * **Tiedostot:** 
    * [interfaces.py](file:///c:/src/quorum/backend_v2/database/interfaces.py) (`IComponentRepository`)
    * [repositories/component.py](file:///c:/src/quorum/backend_v2/database/repositories/component.py) (`ComponentRepositoryImpl`)
  * **Toteutus:**
    * Lisää metodi `async def get_prompt_block_model(self, block_id: str) -> PromptBlock | None`
    * Lisää metodi `async def get_prompt_block_by_slug_model(self, slug: str) -> PromptBlock | None`
* **Task 3.2: Refaktoroi Studio-palvelu**
  * **Tiedosto:** [services/studio.py](file:///c:/src/quorum/backend_v2/services/studio.py)
  * **Muutos:** Päivitä kaikki PromptBlock CRUD-operaatiot hyödyntämään uusia repositoriometodeja, poistaen toistuvat `.model_validate()` -kutsut.

---

## ** VAIHE 4: Järjestelmäasetusten tyyppiturvallisuus (SystemConfig Hydration)**

**Vastuualue:** Backend (Database & Service)

* **Task 4.1: Päivitä Rajapinnat ja Repositorio**
  * **Tiedostot:** 
    * [interfaces.py](file:///c:/src/quorum/backend_v2/database/interfaces.py) (`ISystemRepository`)
    * [repositories/system.py](file:///c:/src/quorum/backend_v2/database/repositories/system.py) (`SystemRepositoryImpl`)
  * **Toteutus:**
    * Lisää metodi `async def get_model_registry_model(self) -> SystemConfigModelRegistry | None`
    * Lisää metodi `async def get_mcp_gateways_model(self) -> SystemConfigMCPGateways | None`
    * Lisää metodi `async def get_system_config_model(self, config_id: str) -> SystemConfig | None` (tai vastaava tyypitys)
* **Task 4.2: Refaktoroi Studio-palvelun konfigurointireitit**
  * **Tiedosto:** [services/studio.py](file:///c:/src/quorum/backend_v2/services/studio.py)
  * **Muutos:** Korvaa system_config -tyyppien manuaalinen validointi (kuten `SystemConfigModelRegistry.model_validate`) suorilla repositoriokutsuilla.

---

## ** VAIHE 5: Legacy-korjaukset ja siivous**

**Vastuualue:** Backend (Refactoring & Verification)

* **Task 5.1: Korvaa Workflow-legacy-alustus (Sääntö 2)**
  * **Tiedosto:** [repositories/workflow.py](file:///c:/src/quorum/backend_v2/database/repositories/workflow.py)
  * **Muutos:** Korvaa rivillä 67 oleva `return Workflow(**data)` konstruktorikutsu standardilla `return Workflow.model_validate(data, strict=False)` -metodilla.
* **Task 5.2: Automaattinen auditointi ja testit**
  * Suorita kattavat laadunvarmistusajot varmistamaan, ettei mikään tyyppimuunnos rikkoutunut:
    * `uv run python scripts/backend_audit_loop.py backend_v2 --test`
    * `uv run pytest backend_v2/tests/unit/test_seed_schema_alignment.py`

---

## ** Hyväksymiskriteerit (Definition of Done)**

1. Uudet malli-metodit (`get_user_model`, `get_step_model`, `get_prompt_block_model`, jne.) on määritelty `interfaces.py` -tiedostossa ja toteutettu vastaavissa repository-luokissa.
2. `AuthService`, `StudioService` ja `dag_executor.py` on siivottu manuaalisesta Pydantic-validoinnista näiden olioiden osalta.
3. Legacy-tyylinen `Workflow(**data)` on poistettu kokonaan koodikannasta ja korvattu `.model_validate()` -kutsulla.
4. Kaikki backend-yksikkö- ja integraatiotestit menevät vihreänä läpi.
5. Muutokset läpäisevät `backend_audit_loop.py` -tarkastuksen (docstringit ja tyypitykset kunnossa).
