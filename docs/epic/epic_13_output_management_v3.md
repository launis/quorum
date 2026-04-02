# EPIC 13: Output Management V3 (Tulostuksen Hallinnan Uudistus)

## 1. Yleiskatsaus (Overview)
Tämän Epicin tavoitteena on uudistaa täysin Cognitive Quorum -järjestelmän tulostuksien hallinta (Output Management). Painopisteenä on tekstisisältöjen laadun parantaminen (toiston poisto, syntetisointi), lukijatasojen valintamahdollisuuksien lisääminen sekä Admin Studion käyttöliittymän merkittävä parannus "Three-Pane" tyyppiseen työpöytä-layoutiin. Lisäksi Epic kattaa PDF-raporttien asynkronisen generoinnin ja tallennuksen, joka on kytketty dynaamisesti työnkulkujen (Workflow) oletusasetuksiin. Päämääränä on tuottaa napakoita ja visuaalisesti 100 % konsekventteja tulosteita laitteesta riippumatta. Tämä on useita iteraatioita kestävä kokonaisuus.

## 2. Pääominaisuudet (Key Features)
1. **Tekstien Syntetisointi (Text Consolidation):** Uusi asynkroninen jälkikäsittelyhook (`TextConsolidationHook`), joka ajaa eri osioiden erilliset `justification`-tekstit ja ulostulolaajennukset (coaching, risk_flag, falsification jne.) kevyen synteesi-LLM:n läpi. Tämä yhdistää sisällön yhtenäiseksi ja toistovapaaksi asiantuntijatekstiksi.
2. **Pituuden Totaalihallinta (Verbosity / Length Constraint):** Mahdollisuus asettaa absoluuttinen pituusrajoite (esim. "One-Pager", "Executive Summary") `synthesis_config`-malliin. Tämä välitetään suoraan alas `prompt_compiler.py`-moduuliin tiukkana rajoittimena, jotta LLM pakotetaan poistamaan korulauseet ja jaarittelut.
3. **Sisäisten prompt-viitteiden suodatus:** Osa syntetisointivaihetta LLM:lle annetaan vahva ohje siivota sisäinen jargoni (esim. promptien muuttujanimet) loppukäyttäjän dokumentista.
4. **Lukijatason Valinta (Reader Understanding Dimension):** Kyky valita tulostukselle tai osiolle lukijataso (esim. Executive, Asiantuntija, Maallikko), joka ohjaa kielellistä sävyä (Tone).
5. **Mukautettava Otsikko (Customizable Header Config):** Admin-käyttäjälle valintakytkimet, jotta raportin alkuun voidaan valita näytettäväksi käyttäjän nimi, organisaation nimi ja sähköposti.
6. **Preamble-Teksti (Johdanto):** Muokattavissa oleva I18nText-johdantoteksti (esim. tieteellinen pohjaus) ennen varsinaisia moduuleja.
7. **Asynkroninen PDF-generointi (Cancellable Worker):** PDF-renderöinti siirretään blokkaavasta säikeestä asynkroniseksi Arq Worker -tehtäväksi (`generate_pdf_task`). Prosessi on keskeytettävä (`asyncio.CancelledError`), mikä pelastaa API-säikeet I/O jähmettymiseltä.
8. **Työnkulkukohtainen oletustuloste (Workflow Default Profile):** Automaattinen PDF-generointi kytketään Työnkulun oletusprofiiliin (`default_output_profile_id`). Vain tässä profiilissa PDF renderöidään automaattisesti tallennustilan ja prosessorin säästämiseksi.
9. **Reaaliaikainen UI-palaute (SSE & Status):** Generoinnin tila ja "Keskeytä"-toiminto tuodaan suoraan käyttöliittymään Server-Sent Events (SSE) -arkkitehtuurilla.
10. **Kumulatiivinen Historiayhteenveto (Cumulative Historical Summary):** Asetus (`include_historical_summary: true`), jolla työnkulku noutaa automaattisesti entiteetin aiemmat raportit / historiadatan. Asynkroninen LLM-hook yhdistää nämä uuden datan kanssa ja luo tulosteen alkuun kokoavan, dynaamisesti elävän yhteenvedon ajan yli.
11. **Ehdottoman Monikielinen Generointi (I18n & Translation Parity):** Kaikki tulosteessa nojaa absoluuttiseen kielivalintaan. Staattiset rakenteet ja Preamble-tekstit käsitellään backendin `I18nText`-objekteina (tukien mm. FI, EN, SV). Itse analyysin tuottavalle LLM-moottorille (`synthesis_config.output_language`) annetaan työnkulun lopussa ehdoton käsky generoida ulostulolohkot halutulla kielellä. Näin työnkulun lopputuloksena voidaan renderöidä asiantuntijatekstit suoraan eri kielivaihtoehdoilla vain Output Profile -kytkintä vaihtamalla.

## 3. Visuaalinen Pariteetti ja Falsifikaation Suojelu (Zero-Math UX)
Quorumin V2 arkkitehtuuridokumenttien (04 & 06) ohjeistusten mukaisesti tulosteiden tuottamisessa nojataan tiukkaan "Backend-For-Frontend" arkkitehtuuriin. Vapaamuotoisesta Markdown-renderöinnistä luovutaan seuraavilla menetelmillä:

* **Server-Driven UI (SDUI) Lohkot Markdownin sijaan:** 100 % visuaalisen laite-paperi-pariteetin takaamiseksi LLM pakotetaan Pydantic V2:n avustuksella palauttamaan tiukkojen visuaalisten lohkojen muodostamaa taulukkoa (esim. `HeroInsightBlock`, `DataGridBlock`, `ParagraphBlock`). Sekä Flutter UI (ReportLayoutDTO) että PDF-moottori renderöivät nämä lohkot pikselilleen samalla asettelulla.
* **A4 Print-First UX (Käyttöliittymä):** Admin Studion tulevassa "Three-Pane" -arkkitehtuurissa Oikean laidan raporttinäkymää (Detail Canvas) ei voi venyttää vapaasti. Se lukitaan oletuksena tarkkaan **A4-mittasuhteeseen ("Paperi-widget")**, jotta näytölle piirtyvä raportti heijastaa välittömästi (WYSIWYG) tulevaa PDF-tiedostoa.
* **Screen Mode -Vapautus (Käyttöliittymä):** A4-lukituksen rinnalle toteutetaan Flutter-koodissa "Screen Mode" -vaihtopainike. Koska valtaosa lukukerroista on digitaalisia, käyttäjä voi halutessaan vapauttaa lukituksen täyden leveyden responsiiviseen tilaan paremman luettavuuden takaamiseksi.
* **Dynaaminen QA & Itsekorjaus-Luuppi (LLM-as-a-Judge):** LLM-synteeseissä tapahtuva faktojen ja riskien madaltuminen (PR-jargonisointi) estetään Dynaamisella Post-Hookilla (esim. kytkemällä se `integrity.py` -putkeen). Erillinen, nopea arviointimalli (Kriitikko) lukee alkuperäisen datan ja synteesin läpi. Jos vahvoja numeerisia riskejä tai terävyyttä puuttuu, hook laukaisee `Pydantic ValidationErrorin`. Tällöin asynkroninen Arq-Worker tekee syötteestä automaattisen ITSEKORJAUS-yrityksen pyytämällä Generaattoria "Palauttamaan puuttuvat riskit".

## 4. LLM Arkkitehtuurisäännöt (Model Registry V2 & 01-python-backend.md)
* **Model Registry -pohjaisuus (LLMClient & Yleiset ajot):** Suorat SDK-kutsut tai omat erilliset tulostuksen LLM-kääreet ovat EHDOTTOMASTI KIELLETTY. Epic 13:n tulostus- ja syntetisointioperaatiot käyttävät tismalleen samaa keskitettyä ja olemassa olevaa yleistä arkkitehtuuria (`backend_v2/llm/client.py` ja `LLMClient.from_strategy()`) kuin itse päätyönkulkujen orkestrointikin.
* **Structured Outputs Pydantic V2:** Synteesihookissa on käytettävä LLMClient:n `run_structured_task()` -metodia luomaan SDUI Block Array (`response_model`). Regex-ratkaisut kielletty.
* **Ei-tukkimista FastAPI -säikeessä:** Yli 500 ms prosessit FastAPI-säikeessä katsotaan virheeksi. Myös uudelleenyritys-/korjausluuppien on tapahduttava omassa Arq Workerissaan. Pitkissä asynkronisissa (PDF) töissä on pakko hyödyntää "SSE-Heartbeat" -sykepulssia, jotta Cloud Load Balancerit eivät katkaise UI-yhteyttä hiljaisuuden takia.
* **Luuppien Katkaisu (Max Retries):** Itsekorjausluupissa on EHDOTON katto (esim. `max_retries = 2`). Järjestelmä ei saa jäädä ikiluuppiin polttamaan API-kustannuksia, jos QA-"Kriitikko" ja "Generaattori" joutuvat umpikujaan.
* **Data Leak Prevention (DLP):** Vaikka prompt olisi virheellinen, sisältäen PII-dataa tai LLM kaatuisi evaluoinnissa, EHDOTON lokituskielto raaka-datalle. Lokitetaan vain matemaattinen virhekoodi + Trace ID. Automaatiotestit varmentavat tämän säännön (Fail-Fast).
* **Two-Tier Prompting (Käskyjen Hallinta):** Synteesin tyyliohjeet (`tone_instruction`, `audience_description`) ovat dynaamisesti muokattavissa Admin Studion Output Profile -näkymästä tietokannassa. Tällä eristetään riskialtis JSON-SDUI rakennesääntö, joka säilyy absoluuttisesti suojattuna ja kovakoodattuna backendin `prompt_compiler.py` -kerroksessa.
* **Conflict Handler (Admin-virheiden eristys):** Jos Admin syöttää `tone_instruction` -kenttään ohjeita, jotka yrittävät rikkoa JSON-skeeman (esim. "kirjoita tämä HTML-taulukkona"), Pydantic-validaatio kaatuu, eikä järjestelmä mene sekaisin. Virhe napataan sulavasti ja pusketaan suoraan "AppErrorBoundaryyn" käyttäjän nähtäville.
* **System/User Role Segregation (Injektiosuojaus ja Välimuisti):** Kaikki tulostukseen ja sisäiseen parsintaan liittyvät uudet LLM-operaatiot TULEE rakentaa äsken testatun ja todennetun arkkitehtuurin mukaisesti: infrastruktuuritason ohje Eristetään kovakoodatuksi vakioksi (esim. `_SYSTEM_INSTRUCTION`) ohjelmatiedoston alkuun EIKÄ sitä viedä tietokantaan. Kutsut LLM:lle EROTETAAN EHDOTTOMASTI `{"role": "system"}` ja `{"role": "user"}` laatikkoihin. Tämä eliminoi Prompt Injektiot ja mahdollistaa Anthropic Caching -nopeushyödyt (esimerkkinä päivitetty `translation_hook.py`).

## 5. Seuraavat Askeleet (Next Steps)

*   **Tier 2 (Database, Pydantic & SDUI Models):**
    *   Luodaan backendin SDUI-pohjaiset Block-mallit (esim. `ReportBlock` polyformisemi, `HeroBlock`, `TableBlock`).
    *   Päivitetään `OutputProfile`-malliin pituussäädin `length_constraint`, sekä `preamble_text`.
    *   Päivitetään `ReportDataDto` hyödyntämään uusia SDUI-lohkoja Markdown-stringin sijaan.
    *   Päivitetään `seed_data.json` vastaamaan uutta Master DTO -mallia.

*   **Tier 2 (Dart Freezed & UI Layout Sync):**
    *   Päivitetään `report_data_dto.dart` rakenteet ja ajetaan `build_runner`.
    *   Toteutetaan Admin Studion "Three-Pane" Split Screen -layout sisältäen oikean laidan lukitun **A4 Paper Canvas** -widgetin.
    *   Lisätään UI:hin asynkroninen PDF:n latausindikaattori (SSE) ja "Keskeytä"-painike.

*   **Tier 2 (Workers & Hooks):**
    *   Suunnitellaan asynkroninen `TextConsolidationHook` ja Dynaaminen QA-Evaluaatio (Kriitikko) Post-Hook rekisteriin. Kytketään automaattinen itsekorjausluuppi (Max 2 retries Pydantic-virheestä) osaksi Worker-työtä.
    *   Luodaan `worker.py` -tiedostoon `generate_pdf_task` (async Cancel -käsittely ja uuden SDUI HTML/CSS block parserin hyödyntäminen WeasyPrintin yli).
    *   Luodaan ei-blokkaava (FastAPI) endpoint `/executions/{id}/generate-pdf`.
