# EPIC: Vertex Search Re-Integration & Architecture Alignment (V2)

## 1. Yhteenveto (Summary)
Vertex Search (Google Grounding) ei tällä hetkellä aktivoidu "De-Generator" (V2) -työnkuluissa (esim. Reflection Chain V2), vaikka ympäristömuuttujat (`ENABLE_VERTEX_SEARCH`, `GOOGLE_CLOUD_PROJECT`) ovat kunnossa. Tämä johtuu kahdesta juurisyystä:
1. **Arkkitehtuurikuilu:** Haun koodi (`search.py`) on riippuvainen `step_analyst`-koneen tuottamista hakusanoista, mutta modernit asiantuntijaverkostot (esim. `steprule_falsifier`) eivät työnkuluissa tuota näitä. Hooksien kytkentä ei siksi tuota hakusanoja haettavaksi, ohittaen haun äänettömästi ("Fail-Fast").
2. **Kieliristiriita (Schema Mismatch):** Vanhat dokumentaatiot ja vanhat kehotteet vaativat LLM:ää tuottamaan suomenkieliset JSON-Pydantic-avaimet ("hypoteesit", "hakusana_ehdotus"), kun taas Python-koodin skanneri etsii englanniksi "hypotheses" ja "search_query".

## 2. Tavoitteet (Objectives)
- Palauttaa Vertex Search -faktantarkistus saumattomaksi ja varmatoimiseksi (100% On-Target) osaksi Quorumin V2-työnkulkuja.
- Yhtenäistää JSON/Pydantic-skeemat (suomi vs englanti) siten, että koodi ja LLM-säännöt puhuvat samaa Output Extensions -kieltä.

## 3. Vaiheet (Milestones & Execution Plan)

### Vaihe 1: Pydantic-skeemojen ja Sääntöjen Yhtenäistäminen
- **Kuvaus:** Koodin ja LLM:n välinen kommunikaatio on standardoitava. V2-arkkitehtuurin (De-Generator) mukaisesti kaikessa sisäisessä tietorakenteessa tulee käyttää englanninkielistä "Output Extension" -avainta `search_query` tai `hypotheses`. 
- **Toimenpide:** Varmistetaan `analyst.py` -skeeman Pydantic-avaimet ja korjataan mahdolliset virheelliset `seed_data.json` Prompt-lohkot, jotta kielimalli ohjeistetaan tuottamaan englanninkieliset avaimet suomen sijaan.

### Vaihe 2: Search Hookin (`execute_google_search`) refaktorointi
- **Kuvaus:** Hook eristetään `step_analyst` -kovakoodauksesta.
- **Toimenpide:** Muutetaan `search.py` iteroiduksi. Sen ei tulisi etsiä hakusanoja vain `step_analyst` -nimisestä paikasta, vaan laajemmin `state.inputs` -dataobjektista (eli siitä askeleesta, minkä hook-vaiheessa haku oikeasti ajetaan). Etsitään dynaamisesti mitä tahansa generoitua `search_query`-avainta riippumatta askeleen nimestä (esim. ohjelmoidun Falsifierin tuottama hakusana).

### Vaihe 3: Ajokohtainen Hakuloki (Execution Search Audit)
- **Kuvaus:** Vianetsinnän ja läpinäkyvyyden parantamiseksi jokaisen ajon haut dokumentoidaan pysyvästi kyseisen ajon omaan kansioon käyttäen järjestelmän standardia tallennusrajapintaa.
- **Toimenpide:** `search.py` -hookkia laajennetaan tallentamaan ajokohtainen hakuloki kohdekansioon `executions/<execution_id>/` hyödyntäen standardia tallennusrajapintaa (`backend_v2.services.storage` / `FileDriver`), jotta tallennus toimii myös pilvessä (GCS) lokaalin levyn lisäksi. Lokiin kirjataan tarkasti luodut hakusanat, kaikki Vertex-rajapinnan palauttamat virheet ja varoitukset. Reaaliaikainen ohjelman eteneminen (progress) ja järjestelmätason viestit ohjataan standardin `logging`-protokollan kautta järjestelmälokiin (esim. `backend_debug.log`).

### Vaihe 4: Työnkulkujen Seed-datan Päivitys
- **Kuvaus:** Päivitetään työnkulku (esim. `reflection_chain_v2` / `fused_audit_chain`) siten, että se pakottaa LLM:n oikeasti generoimaan hakusanoja tarvittaessa joko lisäämällä erillinen Fact-Checking -välivaihe tai liittämällä tiettyihin `steprule`-koneisiin oikeat `output_extensions` ("search_query").
- **Toimenpide:** Edelliset muutokset tallennetaan `data/db_v2.json` / `seed_data.json` puitteissa ja luodaan validi V2 tietokantaseed. (Seuraamalla tiukkaa *Configuration Backup Protocol* -käytäntöä).

### Vaihe 5: Laadunvarmistus (QA) 
- **Kuvaus:** Estetään jatkossa hiljaiset virheet ajamalla korjattu Reflection Chain -työnkulku (tai muu valittu V2 työnkulku).
- **Toimenpide:** Todennetaan `backend_debug.log`:sta, että `[SearchHook]`-kutsut menevät läpi Vertex AI:lle (eikä ohitu "No queries" -viestillä). Todennetaan UI:sta, että Tuomari/Falsifier todella näkee löydetyt google-linkit ja käyttää niitä lähdemateriaalina ("Ei hakutuloksia" -tekstin sijaan).

---
*Tämä Epic noudattaa Quorumin V2.33 Zero-Compromise Pledgesiä.*
