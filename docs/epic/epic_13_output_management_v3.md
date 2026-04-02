# EPIC 13: Output Management V3 (Tulostuksen Hallinnan Uudistus)

## 1. Yleiskatsaus (Overview)
Tämän Epicin tavoitteena on implementoida tekoälyavusteinen tulostuksen hallinta (Output Management V3) Cognitive Quorum -järjestelmään. Järjestelmä hyödyntää nykyistä Server-Driven UI (SDUI) -arkkitehtuuria. Epicin tavoitteet ovat:
1. Tekoälyavusteinen tekstien muotoilu ja laadun parantaminen (toiston poisto, syntetisointi).
2. Tietolohkojen yhdistäminen ja dynaamisen yhteenvedon generointi puhtaaseen Markdown-muotoon.
3. Tulostusmäärittelyjen (Output Profile) jämäkkä konfigurointiyhteys Admin Studiossa ("Three-Pane" layout).

Lisäksi Epic kattaa PDF-raporttien asynkronisen generoinnin. Päämääränä on tuottaa napakoita ja visuaalisesti hienoja tulosteita laitteesta riippumatta nykyrakenteita kunnioittaen. Tämä on useita iteraatioita kestävä kokonaisuus.

## 2. Pääominaisuudet (Key Features)
1. **Tekstien Syntetisointi Markdowniksi:** Uusi asynkroninen jälkikäsittelyhook (`TextConsolidationHook`), joka ajaa eri osioiden tekstit synteesi-LLM:n läpi jäsennellyksi, tyylikkääksi Markdown-tekstiksi.
2. **SynthesisConfigDTO:** Output Profilen sisään upotettu uusi asetusmalli, johon keskitetään puhtaasti tulostuksen pituusrajoitteet, maskaukset ja formaatit.
3. **Datan Maskaus (PII Redaction):** Asetus (`enable_pii_masking`), joka varmistaa, että tekoäly anonymisoi arkaluonteisen datan (nimet, tunnisteet) jo synteesivaiheessa esimerkiksi sidosryhmäraporteissa.
4. **Sallitut Vientiformaatit & Tyhjät Osiot:** Vipu `allowed_exports` (pdf, docx) ja `omit_empty_sections`, jolla tyhjät arvosteluosiot putoavat kauniisti synteesistä yrittämättä pakottaa "Ei saatavilla"-tekstejä.
5. **Sisäisten prompt-viitteiden suodatus:** LLM:lle annetaan vahva ohje siivota sisäinen jargoni.
6. **Lukijatason ja Äänensävyn Valinta:** Kyky valita tulostukselle tai osiolle lukijataso (esim. asiantuntija, maallikko).
7. **Preamble-Teksti (Johdanto):** Muokattavissa oleva johdantoteksti.
8. **Asynkroninen PDF-generointi:** Olemassa olevien worker-rakenteiden laajennus kestämään rikasta Markdown-lähdekoodia.
9. **Kumulatiivinen Historiayhteenveto:** Asetus (`include_historical_summary`), jolla työnkulku noutaa aiemmat raportit.
10. **Ehdottoman Monikielinen Generointi (I18n):** Preamble-tekstit ja staattiset rakenteet tukevat natiivia i18n-käännöstä. Kieli puretaan ohjelmallisesti `_resolve_i18n_str()` funktiolla ennen kuin se sysätään LLM:lle promptissa.
11. **Laajennuspohjainen (Extension-Driven) MCP-hakujen automatisointi:** Vältetään manuaalisten hakuohjeiden kirjoittamista vapaisiin teksti-prompteihin. Hakujen laukaisu sidotaan dynaamisesti valittuihin Prompt-lohkon ulostulolaajennuksiin (esim. `_coaching` / Käytännön harjoitteet tai `_theory_link` / Teoriatieto). Järjestelmä generoi automaattisesti tasan yhden (1) optimoidun hakukäskyn tekoälylle laajennusteeman pohjalta.
12. **EU Tekoälysäädös Audit Trail (Provenance):** Täysi jäljitettävyys tulostuksessa syntyvälle uudelle tiedolle. Synteesi jättää tietokantaan täsmälleen yhtä vahvan, auditoitavan muistijäljen (käytetty prompti, MCP-lähteet) kuin alkuperäiset työnkulun askeleetkin.

## 3. Tekninen Toteutus & Arkkitehtuuri
Toteutus nojaa tiukasti järjestelmän nykyiseen arkkitehtuuristandardiin:
* **SDUI-BFF -paketointi:** Olemassa olevaa `ReportLayoutDTO`-rakennetta käytetään sellaisenaan. BFF-kerros (esim. `sdui.py`) paketoi synteesi-Markdownin suoraan standardiin Server-Driven UI -lohkoon: `{"type": "paragraph", "id": "coach-markdown", "value": {"content": "..."}}`.
* **Numeeristen Graafien Eristys ja Pyöristyskorjaus (Zero-Math UI):** Numeeriset matriisigraafit (1D, 2D ja 3D) säilytetään omina lohkoinaan. **HUOM: Aiempien skaalausongelmien korjaamiseksi kaikkien graafien näytettävät arvot on pakko jatkossa pyöristää aina tasan yhteen desimaaliin.** Näyttö (Frontend) ei laske tätä (Zero-Math sääntö), vaan backendin BFF-kerroksen on huolehdittava pyöristyksestä kohteelle ennen siirtoa. Synteesi-Markdown levitetään tekstillisenä lisäkerroksena näiden viereen.
* **OutputRenderer pääroolissa:** Flutterin `ResultDashboard` piirtää automaattisesti lohkot `OutputRenderer`-komponentilla, joka hyödyntää rikastettua `MarkdownStyleSheet`-tyyliä (luettelot, taulukot).
* **Visuaalinen Pariteetti (UI vs. PDF):** Näyttöruudun (Flutter) ja tuotetun PDF-vientiasiakirjan välillä taataan ehdoton visuaalinen pariteetti.
* **PdfReportService:** Kevennetty `pdf_generator.py` muuntuu Jinja2-moottorilla standardiksi PDF-generoijaksi Markdown-to-HTML lisäyksellä varmistaen yllä mainitun pariteetin.

## 4. Toteutussuunnitelma (Milestones M1-M4)
Tämä Epic toteutetaan seuraavissa puhtaasti eristetyissä virstanpylväissä:

### M1: Pydantic Data Models & Seeding (Storage Level)
* **`backend_v2/models/domain/output_profile.py`**: Yhtenäistetään arkkitehtuuri luomalla tiukka alimalli `SynthesisConfigDTO`, joka upotetaan OutputProfileen (`synthesis: SynthesisConfigDTO | None = None`). Tämä erillinen objekti kantaa ominaisuudet: `length_constraint`, monikielinen `preamble_text` (I18nText), `include_historical_summary`, `enable_pii_masking: bool`, `allowed_exports: list[Literal["pdf", "docx", "raw_json"]]` ja `omit_empty_sections: bool`.
* **`backend_v2/seed/seed_data.json`**: Päivitetään oletusprofiilit (`op_executive_summary`) tällä uudella loogisella, sisäkkäisellä rakenteella.
* **`backend_v2/seed/scripts/patch_epic13.py`**: Luodaan puhdas migraatioskripti tietokannassa olevien data-profiilien päivittämiseen, jotta TinyDB/Firestore täyttää fail-fast `extra="forbid"` vaatimukset.

### M2: TextConsolidationHook & LLM Synthesis (Logic Level)
* **`backend_v2/hooks/synthesis.py` (UUSI)**: Toteutetaan asynkroninen LLM-yhteenveto-hook (`TextConsolidationHook`).
  * **Eri Promptien Yhdistäminen (Deduplication):** Hook ohjeistaa tekoälyä yhdistelemään useista eri työnkulkusolmuista ja erillisistä prompteista peräisin olevat raakatekstit yhdeksi täysin koherentiksi tietovirraksi. Kaikki itsetoisto ja sirpaleisuus poistetaan tylysti.
  * **Output Config -tiedon Fuusio:** Hook lukee Output Profilesta dynaamisesti tulevia lisäyksiä (esim. `preamble_text` tai muokattavia vinkkejä) ja LLM sulauttaa nämä luontevaksi osaksi tekstijatkumoa. Se tekee tämän yhtenäisenä osana tulostetta toistamatta itseään tai rikkomatta kontekstia.
  * **Kohdekieli & I18n Purku:** Kohdekieli on deterministinen ja haetaan ajosta. Hookin TÄYTYY purkaa `OutputProfile`n `I18nText`-kentät (kuten `preamble_text`) lokaaliksi merkkijonoksi olemassa olevalla `_resolve_i18n_str()`-logiikalla ILMAN LLM-arvailua **ennen** niiden injektointia itse LLM:n promptiin.
  * **XAI Alaviitteet ja Structured Output:** Jotta viitteet voidaan varmistaa ohjelmallisesti ja välttää raakatekstin rikkoontuminen, LLM pakotetaan käyttämään Pydantic JSON scheman mukaista Structured Output -formaattia. Muoto on esim: `{"synthesized_markdown": "...", "cited_sources": [...]}`. Tästä muodostuvat inline `[1]` viitteet MCP Toolseihin.
  * **Datan Maskaus & PII:** Hook reitittää datan maskauksen, mikäli `enable_pii_masking` on aktivoitu.
  * **Token-seuranta ja Observability:** Synteesikutsu kääritään `logfire.span`-lohkoon, jotta toistonpoiston tehokkuutta on visuaalisesti helppo auditoida Admin puolella. Kulutetut LLM-tokenit ja kustannukset ohjataan tiukasti `_step_metadata['token_usage']` -objektiin Blueprintin kulutettavaksi.
  * **Automaattinen työkalusääntöjen injektio (PromptCompiler / Tool Loop):** Laajennetaan `PromptCompiler` ja `mcp_tool_loop.py` -logiikkaa reagoimaan aktiivisiin ulostulolaajennuksiin (suffixes).
    * **Dynaaminen Promptaus ja Skaalautuvuus (Multi-Tool):** Koska UI:hin voi jatkossa tulla lukuisia eri MCP-työkaluja (nyt vasta 1, jatkossa useita), injektiota EI lukita kovakoodatusti yhteen työkaluun (kuten `mcp_tavily_search`). Kun havaitaan aktiivinen laajennus (esim. `_theory_link`), järjestelmä lukee kyseisellä askeleella sallitut työkalut listasta (`allowed_mcp_tools`). Tämän jälkeen PromptCompiler generoi dynaamisen lisäohjeen tyyliin: *"Käytä dynaamisia työkaluja [{työkalulista}] tasan yhden (1) kerran etsiäksesi ajantasaista materiaalia. Upota löytämäsi lähteet näihin laajennuskenttiin."*
    * **Kattorajoitin (Max Calls 1):** `mcp_tool_loop.py` -vaiheeseen lisätään älykäs ohitus automaatiohaun alkaessa: tekoälyn oletusarvoinen `MAX_TOOL_CALLS_PER_STEP = 3` ylikirjoitetaan arvoon `1`. Hakusykli on salamannopea, estää "Infinity Loopit" ja säästää API-kustannuksia drastisesti.
* **`backend_v2/api/routers/output_profiles.py`**: Varmistetaan uusien kenttien läpivienti ja suojataan API `response_model=OutputProfileDTO` vuotojen estämiseksi.

### M3: Architecture Connectors (BFF & Worker Offloading)
* **`backend_v2/services/blueprint.py` (BFF)**: Backend-for-Frontend käärijä tunnistaa valmiin synteesi-Markdownin ja paketoi sen suoraan olemassa olevaan, yksinkertaiseen SDUI-lohkoon: `{"type": "paragraph", "id": "coach-markdown", "value": {"content": "..."}}`. Se EI mutatoi puhdasta `ReportLayoutDTO`-perusrakennetta. **KORJAAVA TOIMENPIDE:** Blueprint saa vastuulleen korjata aiemmin toimimattoman skaalauksen, jolloin kaikille graafeille välittyvät luvut pyöristetään pakotetusti aina yhdellä desimaalilla tässä kerroksessa. Kaikki `has_warning` -liput kirjataan metadatasta ylätason `ReportDataDTO.global_score` / métriikka -komponenttiin.
* **`backend_v2/worker.py`**: Laajennetaan `generate_pdf_task()` -työnkulkua tukemaan uutta Markdown-to-HTML -muunnosta asynkronisesti.
* **`backend_v2/services/pdf_generator.py`**: Laajennetaan mallia HTML-kääntämistä varten. **Markdownin tietoturva (XSS Sanitointi)**: Backend ajaa tiukan HTML/Markdown-sanitaation (esim. `bleach`-kirjastolla) generoiduille teksteille juurikin tässä vaiheessa suojellakseen UI:ta ja WeasyPrint-moottoria tekoäly-hallusinaatioiden aiheuttamilta haitallisilta HTML/JS-tageilta.

### M4: Flutter Client Display (Desktop-First UI Layer)
* **`client_app_v2/lib/shared/widgets/output_renderer.dart`**: Toteutetaan `MarkdownStyleSheet` tyylien rikastaminen (luettelot/list, data taulukot/table, lainaukset/blockquote), jotta LLM:n rikas Markdown tuottuu pikselilleen oikein.
* **`client_app_v2/lib/features/execution/views/widgets/result_dashboard.dart`**: Varmistetaan olemassa olevan automaattisen `_buildWarningBanner`in häiriötön esilletuonti, mikäli backend lähettää viestiin Graceful Degradation `metrics.has_warning == true` lipun. Lisäksi varmistetaan, että tekstin sisälle syntyvät inline-viitteet (`[1]`) yhdistyvät loogisesti alalaidan aiempaan `_buildReferencesSection` XAI-lähdeluetteloon.
* **(TBA) Profiilien Hallinta Adminissa**: Toteutetaan olemassa olevien vapaiden näyttökomponenttien sisään Preamble_textien ja pituusasetusten (Three-Pane tyyppinen) modifikaationäyttö, johon navigoidaan puhtaasti Stripe Opaque ID -tyylillä (`blk_...`).

## 5. LLM Arkkitehtuurisäännöt
* **Model Registry -pohjaisuus (LLMClient & Yleiset ajot):** Suorat SDK-kutsut tai erilliset LLM-kääreet ovat kiellettyjä. Käytetään valmista `backend_v2/llm/client.py` -luokkaa ja `LLMClient.from_strategy()` -metodia kaikkialla.
* **Pre-prompt ja Roolien eristely (Injektiosuoja):** Kaikki LLM-operaatiot rakennetaan siten, että infrastruktuuri (/system prompt) eristetään kovakoodatuksi vakioksi ohjelmiston tiedoston alkuun, eikä viedä tietokantaan (kuten `translation_hook.py` tekee).
* **DLP ja lokituskielto raakadatalle:** Vaikka LLM-kutsu kaatuisi luodessaan Markdownia, ehdoton lokituskielto asiakkaan raakadatalle (PII) pätee. Palvelimelle kirjataan vain matemaattinen Trace ID ja virhekoodaus.
* **Virhesietoisuus (Graceful Degradation):** Mikäli synteesi-LLM kaatuu ulkopuoliseen API-virheeseen, työnkulku ei saa keskeytyä kokonaan. Backend palauttaa tällöin raportin raakadatan perusmuodossaan, asettaa metatietoihin `has_warning: true` -lipun varoitusviesteineen, ja antaa frontendin valmiin `_buildWarningBanner`-logiikan hoitaa virheviestintä käyttäjälle pehmeästi.
* **Deterministinen Työkalujen Käyttö (Tool Forcing via UI Extensions):** Admin-käyttäjän ei koskaan tule joutua ohjelmoimaan hakuohjeita käsin prompt-lohkoihin saadakseen ulkaisia linkkejä. Työkalujen käyttö ja LLM:n kontekstin rikastaminen määräytyvät deterministisesti sen mukaan, mitkä ulostulolaajennuksen ruksit (checkboxit) on kytketty päälle kyseisessä askeleessa. Tämä pitää liiketoimintalogiikan puhtaasti käyttöliittymän konfiguraation varassa.
* **EU AI Act Yhteensopivuus & Audit Trail (Jäljitettävyys):** Koska `TextConsolidationHook` voi tuottaa järjestelmään ulkoisten MCP-hakujen myötä täysin *uutta tietoa*, tämän tuloste-synteesin on pakko jättää kantaan fyysinen, muuttumaton jälki. Samalla tavalla kuin Workflow-askeleet tallentavat ajonaikaiset havainnot, myös synteesivaiheen on tallennettava (esim. `execution` tason metatietoihin) oma versionsa: käytetty injektoitu prompti, MCP-työkalujen raakapalautteet sekä lopullinen LLM-vastaus. Tämä takaa 100% "Provenance" (läpinäkyvyyden) säädösten edellyttämällä tavalla täysin audit-kelpoisesti jokaisen PDF-dokumentin kohdalla.
