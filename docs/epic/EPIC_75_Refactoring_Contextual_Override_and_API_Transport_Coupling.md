# EPIC 75: Refactoring Contextual Override & API Transport Coupling

## 1. Yhteenveto & Tavoite (Executive Summary)

Quorum V2:n arkkitehtuurissa on tunnistettu kaksi merkittävää koodihajua (code smell) ja tyyppiturvallisuuden rikkojaa:
1. **`contextual_override`-mekanismin purkkaviritykset:** `contextual_override` toimii suunniteltuna DLQ-reitittimenä, mutta sen toteutus nojaa kovakoodattuihin sentinel-arvoihin (`"[CONTEXTUAL_OVERRIDE_APPLIED]"`), raakojen sanakirjojen mutatoimiseen kesken suorituksen ja Pydantic-mallien suojauksen ohittamiseen `object.__setattr__`-kikkailulla.
2. **API-reitittimen (`executions.py`) transport-kerroksen kytkentä liiketoimintalogiikkaan:** Reititintaso lukee manuaalisesti raakaa JSON-pyyntöä eagerness-päätöksiin, ohittaa Pydanticin automaattisen FastAPI-validoinnin ja suorittaa pitkäkestoista pollausta (`while True` -silmukalla) suoraan HTTP-reitittimen sisällä Stream-endpointissa.

**Tavoite:** 
* Abstrahoida ja poistaa taikamerkkijonot sekä raa'at sanakirjamutaatiot `contextual_override`-käsittelystä ja palauttaa 100 % tyyppiturvallisuus (Pydantic-pariteetti).
* Eriyttää HTTP/Transport-kerros (`executions.py`) täysin liiketoimintalogiikasta ja tietokannan pollaamisesta siirtämällä eager-uutto ja SSE-tilaohjaus Service-kerrokselle.

---

## 2. Nykyisten ongelmien tarkka kuvaus

### Kohde A: `contextual_override` ja tyyppiturvallisuuden murtuminen

* **Ongelma 1: Magic String**  
  Kovakoodattua sentinel-arvoa `"[CONTEXTUAL_OVERRIDE_APPLIED]"` käytetään merkitsemään tilannetta, jossa fyysistä sitaattia ei ole mutta ohitus sallitaan. Tämä arvo vuotaa aina testeistä ja malleista [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py):n kautta [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py)-kääntäjään asti.
  
* **Ongelma 2: Sanakirjojen mutaatiot**  
  [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py) mutatoi suoraan raakaa JSON-sanakirjaa `resolve_majority_vote`-funktion sisällä ilman tyyppikontrollia. Tämä vaikeuttaa kenttien lisäämistä tai tyyppien tiukentamista myöhemmin.
  
* **Ongelma 3: Pydanticin frozen-lukituksen ohittaminen**  
  Tiedostossa [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py) oleva `BaseTDAExtraction` (ja [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py):ssa `StrippedBaseTDAExtraction`) joutuvat käyttämään `object.__setattr__(self, "exact_quote", None)` kiertääkseen Pydantic-mallin muuttumattomuuden (`frozen=True`) validaation `mode="after"` -vaiheessa.

### Kohde B: HTTP-reitittimen (`executions.py`) transport-kerroksen vuoto

* **Ongelma 1: Raakadataprosessointi ennen validointia**  
  Endpointissa `start_execution` otetaan vastaan `Request`-olio ja luetaan raaka JSON `data = await request.json()`, jotta eager-uutto voidaan käynnistää ehdolla `if "raw_inputs" in data` ennen kuin data validoidaan `ExecutionCreate`-malliksi. Tämä ohittaa FastAPI:n automaattisen riippuvuuden validoinnin.
  
* **Ongelma 2: SSE Polling reitittimessä**  
  [stream_execution_status](file:///c:/src/quorum/backend_v2/api/routers/execution/executions.py#L68) sisältää `while True:`-silmukan, joka tekee kyselyitä tietokantaan (`await execution_service.get_execution(...)`) kahden sekunnin välein. Tämä sitoo transport-kerroksen suoraan tietokannan kyselylogiikkaan ja estää puhtaan arkkitehtuurierottelun.

---

## 3. Ehdotetut arkkitehtuurimuutokset

### Osa 1: Tyypitetty ja sentinel-vapaa `contextual_override`

1. **Sentinel-arvon eristäminen LLM-rajapintaan:**  
   Pidetään `"[CONTEXTUAL_OVERRIDE_APPLIED]"` vain LLM-kehotteiden rajapinnassa (PromptCompiler) ja parsitaan/käännetään se välittömästi `None`-tilaksi LLM:n vastausrajapinnassa ennen ydinmallien validointia.
2. **Tyypityksen palauttaminen äänestykseen:**  
   Muutetaan `resolve_majority_vote` käyttämään tyypitettyjä väliaikaismalleja tai Pydanticin `.model_copy(update=...)` -metodia raakojen sanakirjojen mutatoinnin sijaan.
3. **Pydantic-validaation korjaus:**  
   Päivitetään `BaseTDAExtraction` siten, ettei sen tarvitse ohittaa muuttumattomuuslukitusta `object.__setattr__`:illa. Tämä saavutetaan siirtämällä korjauslogiikka `mode="before"`-validaattoriin, joka suodattaa raa'an datan ennen mallin luontia ja lukitusta.

### Osa 2: API-kerroksen puhdistus (`executions.py`)

1. **Reitittimen parametrisointi:**  
   Refaktoroidaan `start_execution` ottamaan vastaan suoraan `ExecutionCreate` -tyypitetty olio. Siirretään eager-uuton käynnistys (`doc_service.process_raw_inputs`) `ExecutionService.start_execution` -metodin sisään, jolloin ohjainkerros säilyy puhtaana siirtoväylänä (Transport).
2. **Streaming-generaattorin siirto palvelukerrokseen:**  
   Siirretään SSE-tilaohjauksen silmukkamoduuli ja generaattori pois reitittimestä `ExecutionService`:en. Reititin ainoastaan kutsuu palvelun metodia (esim. `await execution_service.stream_status(execution_id, initiator=current_user)`) ja palauttaa sen palauttaman generaattorin `StreamingResponse`-oliossa.

---

## 4. Toteutuksen Vaiheet

### Vaihe 1: `executions.py` refaktorointi (API/Transport-decoupling)
* Muutetaan `start_execution` ottamaan suoraan FastAPI:n valvoma `payload: ExecutionCreate`.
* Siirretään eager-uuton käynnistys (`process_raw_inputs`) `ExecutionService.start_execution` -metodin alkuun.
* Siirretään `event_generator`-logiikka `ExecutionService`-luokkaan, jotta reititin saa vain valmiin asynkronisen generaattorin.

### Vaihe 2: `contextual_override` tyyppiturvallisuuden hardening
* Muutetaan `BaseTDAExtraction`-mallin validaatiota siten, että `exact_quote` korjataan `mode="before"`-validaattorissa, jotta vältetään `object.__setattr__`-kikkailut `mode="after"`-vaiheessa.
* Päivitetään majority vote -äänestys toimimaan tyypillisesti Pydantic-mallien kautta tai suorittamalla mutaatiot ennen mallin validointivaihetta.

### Vaihe 3: Testien verifiointi
* Ajetaan backendin yksikkötestit ja integraatiotestit (`uv run pytest`) varmistamaan, ettei mikään nykyisistä toiminnoista rikkoonnu refaktoroinnin seurauksena.

---

## 5. Onnistumisen Kriteerit

* [ ] API-reititin [executions.py](file:///c:/src/quorum/backend_v2/api/routers/execution/executions.py) ei sisällä yhtään manuaalista `request.json()` -hakua tai `while True` -silmukkaa.
* [ ] Eager-uutto käynnistyy palvelukerroksen sisällä Pydantic-validoinnin jälkeen.
* [ ] [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)-tiedostossa ei käytetä `object.__setattr__` -metodia Pydantic-mallien väkivaltaiseen mutatoimiseen.
* [ ] Kaikki yksikkö- ja integraatiotestit menevät läpi onnistuneesti (`uv run pytest`).

---

## 6. Riskit ja Varotoimet

* **Vertex AI / LLM -skeemayhteensopivuus:** Jos poistamme `"[CONTEXTUAL_OVERRIDE_APPLIED]"` sentinel-arvon LLM-kehotteista, LLM saattaa alkaa hallusinoida tai palauttaa tyhjiä sitaatteja silloin kun ei pitäisi.  
  *Varotoimi:* Pidetään sentinel-arvo LLM-tason rajapinnassa (PromptCompiler), mutta poistetaan se ydinmalleista ja korvataan se heti kääntäjä-/parseritasolla tyhjällä (`None`) arvolla ennen mallin validointia.
