# **TOTEUTUSSUUNNITELMA: Backend V2 (Maksimoitu V1 Uudelleenkäyttö)**

## **VAIHE 0: V1-Infrastruktuurin Haravointi ja Puhdistus (Harvesting)**

**Tavoite:** Luoda backend\_v2 \-runko, johon pelastetaan V1:n raskaat integraatiot, mutta josta tuhotaan kaikki vanhan arkkitehtuurin staattiset ja lineaariset mallit.

**Säilytettävä V1-koodi (Kopioidaan suoraan backend\_v2 kansioon):**

* requirements.txt, Dockerfile, pytest.ini.  
* Koko backend/database/ (Kaikki firestore\_driver.py, tinydb\_driver.py, repository.py ja wrapper.py säilytetään).  
* Koko backend/llm/ (client.py, handler.py, provider.py \- retry-logiikat ja token-laskennat pelastetaan).  
* Koko backend/hooks/ (Kaikki funktiot, esim. linguistics.py, metrics.py, scoring.py pelastetaan).  
* Koko backend/utils/ (Yleiset apufunktiot kuten math\_utils.py ja json\_utils.py).  
* backend/services/web\_fetcher.py (Tämä on elintärkeä uuden RAG / Teoriamaadoituksen kannalta).  
* backend/services/pdf\_generator.py ja backend/templates/ (Runko ja Jinja2 säilytetään).  
* backend/core/security.py, backend/core/rate\_limit.py ja backend/api/auth\_router.py (Autentikaatio säilyy).  
* backend/main.py (FastAPI perusrunko, CORS ja middlewaret).

**Tuhottava V1-koodi (ÄLÄ KOPIOI V2:een):**

* Koko backend/models/domain/, backend/models/dtos/ ja backend/models/view/ (Tämä tuhoaa staattiset luokat kuten judge.py, analyst.py, xai.py).  
* Koko backend/api/transformers/ (BFF/DTO-muuntimia ei enää tarvita SDUI:n takia).  
* Kaikki vanhat API-reitit backend/api/routes/ \-kansiosta (Esim. builder/, config/, execution/ \- korvataan uusilla).  
* Koko backend/agents/ ja backend/tasks/ \-kansiot (Korvataan asynkronisella DAG-moottorilla).  
* Vanha backend/core/engine.py ja backend/core/component.py.

**🤖 Antigravity-prompti 0 (Kopioi IDE:en):**

*"Olemme Vaiheessa 0\. Luo kansio backend\_v2 kopioimalla V1-repositoryn backend-hakemisto, MUTTA tee seuraavat radikaalit siivoukset: 1\) Poista kokonaan kansiot: models/domain/, models/dtos/, models/view/, api/transformers/, agents/, tasks/ ja kaikki kansiot api/routes/ sisältä (säilytä vain api/auth\_router.py ja api/schemas.py jos yleisiä). Poista tiedostot core/engine.py ja core/component.py. 2\) Puhdista llm/-kansion ja hooks/-kansion tiedostot siten, että poistat niistä KAIKKI importit poistettuihin domain-malleihin (käytä funktioiden parametreina toistaiseksi 'dict' tai 'Any'). 3\) Puhdista main.py poistamalla tuhottujen reitittimien importit. Varmista, että karsittu FastAPI-palvelin käynnistyy ilman import-virheitä, tietokantayhteys toimii ja Swagger (/docs) aukeaa tyhjänä. Pidä dokumentti 'ARKKITEHTUURIMÄÄRITTELY: Komponenttipohjainen AI-orkestraattori (Enterprise V2)' jatkuvasti kontekstissasi koko koodauksen ajan."*

## ---

**VAIHE 0.5: Täydellinen Eristys ja SSOT (Data & Runtime Isolation)**

**Tavoite:** Irrottaa V2 täydellisesti V1:n ajonaikaisista riippuvuuksista ja vanhoista tietokantarakenteista (Legacy DB isolation).

**Tarkat Taskit:**

1. **Runtime Isolation:** Ohjaa paikalliset käynnistysskriptit (esim. `run_local.bat`) käynnistämään yksinomaan `uvicorn backend_v2.main:app`. V1-koodeja ei ladata muistiin, mikä takaa itsenäisen toiminnan.
2. **Database & Settings Isolation:** Kytke `backend_v2/settings.py` käyttämään uutta tyhjää tietokantaa. Lokaalisti tämä tarkoittaa `data/db_v2.json` -tiedostoa. Firestoressa otetaan käyttöön kokonaan oma V2 namespace (esim. `v2_` -etuliite kokoelmille tai kokonaan eri GCP-kohde).
3. **Puhdas SSOT (Single Source of Truth):** Luo `backend_v2/seed/seed_data.json`, josta on poistettu kaikki viitteet vanhoihin V1-arkkitehtuurin (Judge, Analyst) staattisiin koodilohkoihin. JSON sisältää vain V2:n sallimia abstrakteja `workflows`, `agents`, `components` ja `universal_matrix` -malleja.
4. **V2-Seederin aktivointi:** Kopioi `backend/seed/run_seed.py` kansioon `backend_v2/seed/` ja konfiguroi sen rekisteri lukemaan puhtaasti vain `backend_v2.models.v2_core` malleja. Testaa ajamalla seaderi, jotta dev-ympäristön V2-kanta populoidaan täysin puhtaalta pöydältä.

**🤖 Antigravity-prompti 0.5:**

*"Olemme Vaiheessa 0.5. Tavoitteenamme on katkaista V2:n riippuvuus vanhaan V1-runtimeen ja tietokantaan tekemällä täydellinen eristys. 1) Varmista, että uvicorn käynnistää vain `backend_v2.main:app`. 2) Konfiguroi `backend_v2/settings.py` ohjaamaan tietokantayhteys V2-specifiseen kantaan (esim. `db_v2.json` tai V2 Firestore namespace). 3) Luo puhdas V2-versio `seed_data.json` -tiedostosta kansioon `backend_v2/seed/` ja poista siitä kaikki staattiset V1-koodiviitteet. 4) Refaktoroi V2:n oma `run_seed.py` siementämään tietokanta puhtaalta pöydältä ainoastaan `models.v2_core.py` Pydantic-mallien läpi."*

## ---

**VAIHE 1: Append-Only DB ja Uudet Dynaamiset Mallit**

**Tavoite:** Laajentaa V1:n repository.py tukemaan Append-Only \-versiointia, ja koodata uuden arkkitehtuurin vaatimat puhtaat NoSQL-mallit.

**Tarkat Taskit:**

1. **Append-Only Repository:** Laajenna V1:n database/repository.py tekemällä uusi luokka AppendOnlyRepository. Sen update/put-operaation on pakotettava vanhan dokumentin tilaan is\_latest: False ja luotava uusi dokumentti uudella ID:llä \[slug\]\_v\[versio\].  
2. **I18n ja V2-mallit (models/v2\_core.py):**  
   * Luo I18nText (kentät default\_locale ja translations).  
   * Luo **Universaali Matriisi**, johon sisällytetään V2-arkkitehtuurin uutuudet: type (float/int/string), allow\_decimals (bool), strictness\_level (int 0-100), require\_justification (bool) ja theory\_grounding (dict: source\_url ja citation\_reference).  
   * Luo SystemConfig (malli-taso \-mappaukset) ja DataDictionaryField (UI-vihjeet).  
   * Luo Orkestraatiomallit: Agent (lukitsee fyysiset versiot, sis. pre\_hooks) ja Workflow (sis. dynaamiset syötteet expected\_inputs sekä askeleet steps, joilla on depends\_on ja input\_mappings).

**🤖 Antigravity-prompti 1:**

*"Olemme Vaiheessa 1\. 1\) Laajenna database/repository.py tekemällä AppendOnlyRepository. Sen tulee ylikirjoittaa päivitysmetodi (update) niin, että se käyttää V1:n ajuria asettamaan vanhan dokumentin 'is\_latest: False' \-tilaan ja insertoi kokonaan uuden versionumeroidun dokumentin (esim. \_v2). 2\) Luo models/v2\_core.py. Koodaa Pydantic-mallit: I18nText, UniversalMatrix (huomioi V2 kentät: type, allow\_decimals, strictness\_level, require\_justification, theory\_grounding), SystemConfig, DataDictionaryField, Agent ja Workflow (jossa expected\_inputs, depends\_on ja input\_mappings). 3\) Luo näille uudet CRUD API-reitit api/v2/ \-kansioon. Varmista Pydantic-validaattorilla, että Workflown depends\_on ei salli syklisiä riippuvuuksia."*

## ---

**VAIHE 2: LLM Clientin Vapautus ja Turvallinen Hook-rekisteri**

**Tavoite:** Kytkeä V1:stä pelastetut raskaat koneistot irti staattisista vaatimuksista ja tehdä niistä dynaamisia työkaluja.

**Tarkat Taskit:**

1. **Dynaaminen LLM Client (llm/provider.py & llm/client.py):** V1-koodissa response\_format odotti tiettyä kovakoodattua domain-luokkaa. Muuta metodien signatuuri ottamaan vastaan dynamic\_schema\_model: Type\[BaseModel\]. Syötä tämä lennosta luotu Pydantic-luokka suoraan Structured Outputs \-rajapinnalle (esim. OpenAI/Gemini). Säilytä kaikki V1:n backoff/retry- ja rate-limit-logiikka sellaisenaan.  
2. **Hook-Rekisteri (core/hook\_registry.py):** Rakenna Python-dekoraattori @hook\_registry.register(name="...").  
3. **V1 Hookien refaktorointi (hooks/):** Avaa V1:n hooks/metrics.py, hooks/linguistics.py jne. Muuta ne käsittelemään raakoja dict-objekteja (esim. def calculate(data: dict) \-\> dict) ja rekisteröi ne dekoraattorilla.  
4. Luo API-reitti GET /api/v2/system/hooks käyttöliittymää varten.

**🤖 Antigravity-prompti 2:**

*"Olemme Vaiheessa 2\. 1\) Avaa V1:stä säilytetyt llm/provider.py, llm/handler.py ja llm/client.py. Muuta LLM-generointimetodit ottamaan vastaan 'dynamic\_schema\_model: Type\[BaseModel\]' staattisten luokkien sijaan. Välitä tämä dynaaminen Pydantic-malli suoraan LLM:n Structured Outputs \-parametriin. Säilytä V1:n olemassa oleva retry- ja ratelimit-logiikka koskemattomana. 2\) Luo core/hook\_registry.py ja toteuta dynaaminen koodinrekisteröintidekoraattori. 3\) Käy läpi hooks/-kansion analytiikkafunktiot. Pakota ne käyttämään puhtaita dict-objekteja ja rekisteröi ne dekoraattorilla. 4\) Tee reitti GET /api/v2/system/hooks, joka palauttaa rekisteröidyt nimet listana."*

## ---

**VAIHE 3: Aivot – I18n Prompt Compiler, Kireys ja Teoriamaadoitus**

**Tavoite:** Rakentaa V2:n monimutkaisin komponentti, joka muuttaa ontot tietokantamallit lennosta LLM-valmiiksi asynkronisiksi komennoiksi.

**Tarkat Taskit (services/orchestrator/prompt\_compiler.py):**

1. **I18n Fallback:** Funktio, joka purkaa I18nText-objektit (ohjeet, ankkurit) target\_locale-kielelle tai default\_localeen.  
2. **RAG / Web Fetcher:** Jos matriisissa on theory\_grounding.source\_url, käyttää V1:n services/web\_fetcher.py hakemaan teksti asynkronisesti. Injektoi se \<theory\_context\> \-tageilla System Promptiin.  
3. **Kireyden Kalibrointi:** Muuttaa kriteerin strictness\_level (0-100) semanttiseksi tekstiohjeeksi (esim. "0 \= Absolute Leniency, assign max score", "100 \= Absolute Strictness, penalize all flaws").  
4. **Dynaaminen Pydantic:** Käyttää Pythonin pydantic.create\_model. Jos kriteerillä on require\_justification: True, luo arvo-kentän lisäksi lennosta tekstikentät {slug}\_justification ja {slug}\_citation. Injektoi field descriptioniin ohje: *"Perustele arvo yksityiskohtaisesti \<theory\_context\> \-lähteeseen tukeutuen."*  
5. **Datan Reititys (XML):** Lukee askeleen input\_mappings ja käärii datan roolia vastaaviin XML-tageihin (esim. \<target\_conversation\>). Liittää loppuun kielipakon CRITICAL MANDATE.

**🤖 Antigravity-prompti 3:**

*"Olemme Vaiheessa 3\. Luo services/orchestrator/prompt\_compiler.py. Rakenna kääntäjäluokka, joka: 1\) Toteuttaa I18n Fallback \-logiikan tekstien purkuun target\_locale-parametrilla. 2\) Lukee matriisit: jos theory\_grounding.source\_url on määritelty, hae se V1:n web\_fetcher.py:llä asynkronisesti ja injektoi teksti \<theory\_context\> \-tageihin. 3\) Muuntaa strictness\_levelin (0-100) matemaattiseksi System Prompt \-mandaatiksi kireydestä/armollisuudesta. 4\) Käärii askeleen input\_mappings-syötteet semanttisiin XML-tageihin tietoturvan vuoksi. 5\) Luo lennosta pydantic.create\_model() \-avulla dynaamisen skeeman. Jos require\_justification=True, generoi varsinaisen arvon lisäksi lennosta '{slug}\_justification' ja '{slug}\_citation' \-kentät ja ohjeista tekoälyä tukeutumaan haettuun lähteeseen. 6\) Lisää lopuksi CRITICAL MANDATE kohdekielen pakotuksesta."*

## ---

**VAIHE 4: Asynkroninen DAG Executor & Jäädytys**

**Tavoite:** Korvata vanha lineaarinen core/engine.py modernilla asynkronisella graafipohjaisella suoritusmoottorilla.

**Tarkat Taskit (services/orchestrator/dag\_executor.py):**

1. **Topological Sort:** Ratkaisee Workflown depends\_on \-kytkökset suoritusjärjestykseksi.  
2. **Async Rinnakkaisuus:** Ajaa riippumattomat askeleet Pythonin asyncio.gather() \-komennolla rinnakkain.  
3. **Suoritussykli (Per askel):**  
   * Hae ja pura reititetty data ($inputs ja $steps).  
   * Aja pre\_hooks.  
   * Kutsu Prompt Compileria (VAIHE 3).  
   * **Tallenna täydellinen frozen\_context** (käännetyt promptit, noudettu teoria, luotu JSON Schema, UI-vihjeet) kantaan executions-dokumenttiin *ennen* LLM-kutsua.  
   * Kutsu V1 LLM-clientia (VAIHE 2).  
   * Aja post\_hooks ja tallenna results.

**🤖 Antigravity-prompti 4:**

*"Olemme Vaiheessa 4\. Luo services/orchestrator/dag\_executor.py ja luo FastAPI reitti POST /api/v2/executions/run. Executorin tulee ratkaista Workflown depends\_on \-riippuvuudet Topological Sortilla ja suorittaa vapaat askeleet rinnakkain asyncio.gather() \-avulla. Reititä data askeleille input\_mappings-määritysten perusteella joko $inputs tai $steps \-lähteistä. Askeleen sykli: 1\) Aja hook\_registryn pre\_hook funktiot. 2\) Käännä prompt ja skeema Prompt Compilerilla. 3\) Tallenna koko käännetty paketti (sis. teoriatiedot ja i18n-ohjeet) 'frozen\_context' \-objektina executions-kokoelmaan. 4\) Tee LLM-kutsu lennosta luodulla dynaamisella skeemalla. 5\) Tallenna LLM:n palauttama JSON results-kenttään."*

## ---

**VAIHE 5: Viivästetty Esityseristys (Omni-Channel PDF & Flat File)**

**Tavoite:** Eriyttää tulostus ja pelastaa V1:n staattinen PDF-moottori muuttamalla se dynaamiseksi Block Builderiksi.

**Tarkat Taskit:**

1. **SDUI API:** Luo GET /api/v2/workflows/{id}/ui\_schema (Palauttaa expected\_inputs frontendin dynaamista lomaketta varten).  
2. **V1 PDF Generatorin uudelleensyntymä (services/pdf\_generator.py):**  
   * *Säilytä:* V1:n raskas WeasyPrint/ReportLab konfiguraatio, CSS-tyylit ja alatunnisteet.  
   * *Muuta:* Tuhoa V1:n Jinja2-templatesta (templates/report\_template.jinja2) kaikki staattiset domain-viittaukset (kuten {{ report.bloom\_score }}).  
   * Rakenna templateen dynaaminen silmukka: {% for key, hint in frozen\_context.ui\_hints\_snapshot.items() %}. Jos results-datasta löytyy avaimet {key}\_justification ja {key}\_citation, renderöi ne tyylikkääksi lähdeperustelulaatikoksi PDF-arvon alle (XAI-raportointi).  
3. **Flat File Flattener (services/flattener.py):**  
   * Luo logiikka, joka purkaa asynkronisen DAG-verkon syvän results-JSON-puun yhdeksi litteäksi dictiksi. Vakioi sarakkeiden nimet: \[step\_id\]\_\[slug\] (esim. step\_judge\_bloom\_score\_citation).  
4. Luo renderöintireitti GET /api/v2/executions/{id}/render?format=(pdf|flat).

**🤖 Antigravity-prompti 5:**

*"Olemme Vaiheessa 5, esityskerroksessa. 1\) Luo API GET /api/v2/workflows/{id}/ui\_schema dynaamisen lomakkeen rakennusta varten. 2\) Refaktoroi V1-koodista säilytetty services/pdf\_generator.py ja templates/report\_template.jinja2. Säilytä PDF-kirjaston asetukset (fontit, layout), mutta tee templatesta täysin dynaaminen Block Builder. Se iteroi 'frozen\_context.ui\_hints\_snapshot' läpi ja renderöi palikat 'results'-datan perusteella. Varmista, että se etsii dynaamisesti \_justification ja \_citation \-kentät ja tulostaa ne nätisti arvon perään (XAI). 3\) Luo services/flattener.py, joka litistää DAGin tuottaman sisäkkäisen results-JSONin yhdeksi tasalevyiseksi tietoriviksi analytiikkaa varten yhdistämällä askeleen ID:n ja kentän nimen. 4\) Tee GET /api/v2/executions/{id}/render \-reitti, joka palauttaa datan format=pdf tai format=flat parametrien mukaan."*

---

Näillä viidellä tarkasti rajatulla askeleella ja promptilla Antigravity IDE osaa säilyttää V1:n arvokkaimmat tekniset integraatiot, purkaa kaiken kankean liiketoimintalogiikan, ja rakentaa tilalle arkkitehtuurimäärittelyn mukaisen skaalautuvan V2-orkestraattorin.