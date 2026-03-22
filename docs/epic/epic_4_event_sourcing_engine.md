# Epic 4: Event Sourcing DAG Engine (Zero-Copy State)

## Arkkitehtuurillinen Tavoite (Visio)
Nykyinen V2.5-tason `DAGExecutor` moottori suorittaa rinnakkaisia verkkosolmuja ja kytkee niiden tuloksia takaisin globaaliin tilaan hyödyntäen typettömiä Python-sanakirjoja (`shared_state_data: dict`). Tämä ratkaisu vaatii suorituskykyä syövää lennosta tapahtuvaa tila-sekoittamista (`deep_merge_dicts`) ja rekursiivisia tyhjiökopioita (`copy.deepcopy()`), jotta asynkroniset rinnakkaiset LLM-ajot eivät vahingossa ylikirjoita ristiin toistensa tuloksia oudoilla avainkonflikteilla.

Tämän Epicin tavoitteena on saattaa loppuun Quorumin V3-tason moottoripäivitys siirtymällä täysimittaisesti `backend_v2/models/state.py` -tiedostossa jo määriteltyyn, mutta irti kytkettyyn Pydantic-pohjaiseen **Event Sourcing -malliin** (Append-Only loki).

## Konkreettiset Hyödyt
1. **O(1) Append-Only Tilahistoria:** Poistetaan raskaat deepcopyt, koska historia on vain jäädytetty (`frozen=True`) lista `TraceEvent` -Pydantic -muuttujia. Ajo liittää lokiin lisää rivejä (`state.add_event(...)`), eikä mitään aikaisempaa koskaan editoida historiassa taaksepäin.
2. **`deep_merge_dicts` -funktion tuhoaminen:** Koska objektit ovat muuttumattomia ja lokaaleja, moottorin ei tarvitse koskaan liimata avaimia toisiinsa matemaattisesti (mikä on hidasta ja altista bugeille JSON-taulukoissa). Rinnakkaisajoista tulee absoluuttisen lankaturvallista (thread-safe).
3. **100% Pydantic Tyyppiturvallisuus:** Spagetti-sanakirjojen globaali siirtyminen historiaan koko moottorin sisuskaluista asti. Askel kerrallaan koko Quorum V2 tiukkenee entisestään.

## Suoritustavoitteet (Milestones)

### Milestone 1: Tyypitettyjen Tilojen Sidonta (Orchestrator Setup)
- Kartoitetaan `dag_executor.py` ja etsitään kaikki nykyiset `deep_merge_dicts`-operaatiot sekä `shared_state_data` -viittaukset.
- Alustetaan DAG-ajojen elinkaari luomaan uusi `WorkflowState` -objekti aivan ajon alussa sen sijaan, että se luottaisi oletus `dict`-kääröön.

### Milestone 2: Askelten (Step Nodet) Output-Refaktorointi
- Muutetaan `engine_nodes.py` ja solmujen `execute`-metodit niin, että ne palauttavat tyhmän sanakirjan sijasta tiukkoja `TraceEvent` -objekteja (esim. `event_type="output"` tai `event_type="reasoning"`).
- Päivitetään askeleiden rinnakkaisajojen iterointisilmukka (`asyncio.gather` tai vastaava Worker-patteri) kokoamaan listaksi uusia `TraceEventtejä`, jotka ruiskutetaan suoraan moottorin puhtaaseen lokilistaan lennosta.

### Milestone 3: Datan Kulutus ja Pre/Post -Koukut (Input Harvesting)
- Refaktoroidaan Pre- ja Post-Koukku -järjestelmä lukemaan syötteitä (Inputs) Pydanticin dynaamisista viittauksista (`state.get_context()`) eikä vanhasta `dict.get()` -spagetista.
- Päivitetään tiedon lukija "katselevaksi", sillä koukuilla (kuten `ValidationHook`) ei ole missään nimessä oikeutta muuttaa järjestelmän asynkronista lokia suoraan omilla päätöksillään ohi Append-säännön.

### Milestone 4: Regressio ja V3 Moottorin Testaus
- Suoritetaan DAG-testipenkki esimerkiksi rinnakkaisella Epic 3 -tyylin tekoälyväittelyllä. 
- Varmistetaan, että asiantuntija-analyysin matriisit ja loppuraportit muodostuvat JSON-formaattina täysin identtisiksi verrattuna aikaisempaan sekavaan merge-tekniikkaan. Kun Output vastaa byte-for-byte vanhaa tulostetta, tiedämme moottoripäivityksen onnistuneen.
