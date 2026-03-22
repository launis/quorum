# Epic: Pydantic Syväintegraatio & Ultimate Fail-Fast (Quorum V2.7+)

**Tila:** Analysoitu ehdotus  
**Päivämäärä:** Arkkitehtuurikatselmus Maaliskuu 2026  
**Kohderaportti:** `Arkkitehtuurimäärittely_ AI-orkestraattori V2.md` jatkokehitys  

**Konteksti:** Quorum V2 nojaa vahvasti Pydantic-pohjaiseen "Strict Pydantic / Fail-Fast" -arkkitehtuuriin. Vaikka domain-mallit (esim. DTO:t ja reitittimet) ovat jo tyyppiturvallisia, järjestelmän sisäisessä kognitiivisessa reitityksessä ja validointilogiikassa (Hookit, DAG Executor, LLM JSON-parsinta) on edelleen aukkoja. Näissä kohdissa luotetaan liikaa abstraktioihin kuten `dict[str, Any]` tai standardeihin `@dataclass`-malleihin vauhdin vuoksi.

Tämä Epic dokumentoi kolmiosaisen arkkitehtuuripäivityksen, jonka tavoitteena on poistaa kaikki jäljellä olevat "kognitiiviset sokeat pisteet" tekoälyn ja tietokannan väliltä viemällä Pydanticin validointi aivan suoritusmoottorin ytimeen.

---

## Vaihe 1: Muuttumaton Konteksti-injektio (HookContext Pydantic-mallina)

**Tavoite:** Korvata nykyinen `core/hook_registry.py`:n `@dataclass HookExecutionContext` aidolla Pydantic `BaseModel` -objektilla.  
**Toteutus:** Luodaan Pydantic-malli `HookContext(BaseModel)`, jossa on konfiguroituna `model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)`. Tämä sallii tietokanta-injektion (Repository) vahvan tyypityksen, mutta lukitsee itse datamallin muuttumattomaksi suoritushetkellä (Immutable).

**Kriittinen Analyysi:**
*   **Hyödyt (High Reward):** Tämä on matalalla roikkuva hedelmä. Kun järjestelmä takaa (Fail-Fast instansiointihetkellä), että esimerkiksi ohjeistuksiin injektoitava `repository` ja `execution_id` ovat absoluuttisesti oikeita ja oikean tyyppisiä, yksikään hook ei voi kaatua satunnaiseen tyyppivirheeseen. `frozen=True` takaa rakenteellisesti, ettei rinnakkainen hook pysty vahingossakaan sabotoimaan yhteistä dataväylää ohjelmoijien virheiden takia.
*   **Riskit (Low Risk):** Pienet. Pääasiassa vaatii kaikkien nykyisten hookkien (mm. `scoring.py`, `integrity.py`) funktiosignatuurien manuaalisen tyypityksen päivityksen. Suorituskyky pysyy erinomaisena, sillä mallia instansioidaan melko harvoin (vain askeleiden vaihtuessa).

---

## Vaihe 2: DAG-topologian Ennakoiva Validointi (The Pre-Flight Check)

**Tavoite:** Siirtää vastuu työnkulkujen (DAG) riippuvuusverkon oikeellisuuden tarkistuksesta suoritushetkeltä mallin instansiointihetkelle.  
**Toteutus:** Lisätään `Workflow` Pydantic-malliin `@model_validator(mode='after')`, joka analysoi raskaasti `steps`-taulukkoa:
1. Tekee topologisen lajittelun varmistaen, ettei ole syklistä lenkkiä (Cycle / infinite loop).
2. Validoi, että kaikki lokaalit datareititykset (`$inputs.*` ja `$steps.*`) ohjaavat dataan, joka on joko saatu sisääntulossa (Expected Inputs) tai syntynyt *ennen* nykyistä askelta.

**Kriittinen Analyysi:**
*   **Hyödyt (Massive Impact):** Tällä hetkellä Quorumissa on riski, että konfiguraatiomuutoksissa Admin Studiosta syntyy rikkinäinen reititys, joka kaatuu vasta, kun joku yrittää oikeasti suorittaa workflow'n. Uusi `@model_validator` estää "Bad DAGin" tallentumisen jo `seed_data.json`:n migraatiossa (tai API POST/PUT-hetkellä), pudottaen HTTP 422:n takaisin Admin Studioon. Tämä on Ultimate Fail-Fast -malli config-hallinnassa.
*   **Riskit (Moderate Effort):** Työnkulkujen asymmetriset reititykset (erityisesti fallbackit tai villit dynaamiset avaimet) tekevät staattisesta analysoinnista Pydanticin sisällä raskasta koodia. Jos validaattoriin laitetaan buginen ehto, se katkaisee kyvyn ajaa koko järjestelmää, koska Pydantic on leppymätön.

---

## Vaihe 3: Dynaaminen Runtime Schema Valiadi (Pydantic 'create_model')

**Tavoite:** Pakottaa "Schema-Driven AI:n" tuottamat dynaamiset JSON-vastaukset suoraan Pydantic-malleihin kääntämällä mallit lennosta muistissa.  
**Toteutus:** `DAGExecutor` skannaa askeleen `PromptBlock`-viittaukset (mittaristomatriisit ja säännöt) ja käyttää Pydanticin `create_model('DynamicSchema', **fields)`:iä generoidakseen validointiluokan lennosta. Kun rajapinnan GenAI vastaa abstraktilla JSONilla (`dict[str, Any]`), se pusketaan vastasyntyneen luokan läpi: `ValidatedData(**llm_json)`.

**Kriittinen Analyysi:**
*   **Hyödyt (Total Strictness):** Ratkaisee täydellisesti LLM:n tyyppimuunnosongelmat (coercion), joissa tekoäly vahingossa palauttaa luvun merkkijonona tai unohtaa kentän arvon. Tyyppihallusinaatiot kaatuvat heti kognitiivisen luupin ja tietokannan väliselle turva-aidalle, jättämättä järjestelmän tilaksi kryptisiä virhesanakirjoja. Numeerinen käsittely muuttuu 100% matemaattiseksi faktoihin perustuen.
*   **Riskit (High Complexity):** Suuri prosessointikuorma (CPU-overhead) kun tuhansia luokkia syntyy iteratiivisesti taustatyöntekijän muistissa. Ongelmana on myös "kuoleman kierre": jos avoin/yleisluontoinen kenttä määritellään liian laiskasti ja tekoäly tuottaa listan sanoja yksittäisen stringin sijasta, ohjelma kaatuu suoraan 500 Server Error -tilaan, mikä tuhoaisi asiakkaan luottamuksen järjestelmään nopeasti.

---

## Suositukset Toimenpiteiksi (Roadmap)
Tämä Epic suositellaan toteutettavaksi osana V2-vakautusta vaiheittain alkaen **Vaiheesta 1 (HookContext)**, joka on turvallisin ja parantaa koko tiimin DX:ää (Developer Experience). 

Sen jälkeen siirrytään **Vaiheeseen 2 (DAG Validator)**. Vaihe 3 on arkkitehtuuriltaan kaunis, mutta sen riskitekijät suosittelevat sen implementoinnin aloittamista rajatulla pilottiprojektilla vain tietyissä, erittäin kontrolloiduissa numeerisissa arviointimatriiseissa (esimerkiksi pelkät BARS-pisteytykset), jottei koko moottori haurastu LLM:n rakenteellisten mikromuutosten alla.
