# Kognitiivinen Quorum V2 - Uuden Vaiheen Alku

Tervetuloa uuteen kontekstiikkunaan. Tämä on Quorum V2 -projektin seuraavan vaiheen aloitustiedosto. 

**Lue tämä dokumentti ja sen viittaamat arkkitehtuuridokumentit huolella ymmärtääksesi projektin nykytilan. Älä kuitenkaan aloita vielä mitään ohjelmointia tai tee muutoksia järjestelmään ennen kuin annan erillisen luvan.**

## Nykytila (Phase 9/10 - V2.5)

Olemme saaneet valmiiksi massiivisen uudelleenkirjoituksen (V2), joka muutti järjestelmän kovakoodatuista agenteista tietokantaohjatuksi, dynaamiseksi arkkitehtuuriksi. 
Tärkeimmät saavutukset:
1. **Single Source of Truth (SSOT):** `data/seed_data.json` on koko järjestelmän totuuden lähde. Se sisältää `system_config` (Model Registry), `prompt_blocks` (Matriisit ja Ohjeet), `steps` ja `workflows`.
2. **Strict Pydantic V2:** Backend (`backend_v2`) on rakennettu tiukan Pydantic V2 -skeeman päälle ilman ORM:ää tai varsinaista tietokantaskeemaa. Data validoidaan ankarasti ja tallennetaan `db_v2.json` (tai Firestoreen, kts. `run_local.bat` ja `USE_MOCK_DB`).
3. **SDUI & Flutter:** Frontend (`client_app_v2`) on "tyhmä" Riverpod-pohjainen renderöijä, joka piirtää UI:n dynaamisesti tietokannasta tulevien `ui_hints` ja Pydantic-mallien perusteella (De-Generator Mandate). Monikielisyys (I18n) hoidetaan automaattisella fallback-logiikalla.
4. **Node DAG & Semantic Routing:** Työnkulkujen suoritus perustuu dynaamiseen suunnattuun syklittömään verkkoon (DAG). Syötteet reititetään muuttujilla (`$inputs.chat_log`, `$steps.node_1`).
5. **Fail-Fast:** Järjestelmä kaatuu tarkoituksella (HTTP 422 tai poikkeus), jos data riitelee Pydantic-mallin kanssa tai jos suhteellisia avaimia puuttuu.

## Seuraavat tavoitteet
1. **Dynaamiset Syötteet Frontendissä:** Korjasimme hiljattain bugin, ja nyt `seed_data.json` (esim. työnkulku `workflow_courtroom_20_full_audit`) vaatii oikein kolme erillistä tiedostoa (`history_text`, `product_text`, `reflection_text`). Seuraavaksi nämä on toteutettava käyttöliittymään (tiedostojen tai tekstin syöttö dynaamisesti).
2. **Dashboard API-reitit:** Tarvitsemme todennäköisesti uusia API-reittejä Dashboardia / `orchestration/new` varten, jotta työnkulkuja voidaan aidosti käynnistää.
3. **Suoritusmoottorin Viimeistely:** Varmistetaan, että uusi DAG Executor pystyy ottamaan nämä tiedostot vastaan ja ajamaan PromptBlockit läpi onnistuneesti käyttäen tiukkoja Pydantic-validaatioita.

## Ohjeistus
1. Olet asetetussa roolissasi. Lue tämä tiedosto.
2. Varmista, että ymmärrät uuden kansiorakenteen (`backend_v2/` ja `client_app_v2/`).
3. Selaa tarvittaessa läpi päivitetyt referenssidokumentit (Backendin Pydantic-luokat ovat ainoa totuus):
   - `docs/Arkkitehtuurimäärittely_ AI-orkestraattori V2.md`
   - `docs/architecture.md`
   - `docs/api_models.md`
   - `docs/data_management.md`
   - `docs/reference.md`

**Vahvista, että olet lukenut ja sisäistänyt tämän uuden suunnan, mutta pysähdy siihen. Älä aloita koodaamista, älä muokkaa tiedostoja, äläkä suorita testejä ennen kuin käyttäjä antaa seuraavan varsinaisen toimeksiannon.**
