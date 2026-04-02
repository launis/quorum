# EPIC 13: Output Management V3 (Tulostuksen Hallinnan Uudistus)

## 1. Yleiskatsaus (Overview)
Tämän Epicin tavoitteena on uudistaa täysin Cognitive Quorum -järjestelmän tulostuksien hallinta (Output Management). **Ydinteesi on pitää olemassa oleva koodi monelta osin täysin nykyisen kaltaisena**, ja tuoda järjestelmään ainoastaan:
1. Tekoälyavusteinen tekstien muotoilu ja laadun parantaminen (toiston poisto, syntetisointi).
2. Olemassa olevien lohkojen yhdistäminen ja dynaamisen yhteenvedon tekeminen tekoälyllä, suoraan laadukkaaseen Markdown-muotoon.
3. **Aivan erityisesti tulostusmäärittelyjen (Output Profile / Asetukset) käyttöliittymän (UI) ja UX:n merkittävä parantaminen** Admin Studiossa ("Three-Pane" layoutin myötä).

Lisäksi Epic kattaa PDF-raporttien asynkronisen generoinnin. Päämääränä on tuottaa napakoita ja visuaalisesti hienoja tulosteita laitteesta riippumatta nykyrakenteita kunnioittaen. Tämä on useita iteraatioita kestävä kokonaisuus.

## 2. Pääominaisuudet (Key Features)
1. **Tekstien Syntetisointi Markdowniksi:** Uusi asynkroninen jälkikäsittelyhook (`TextConsolidationHook`), joka ajaa eri osioiden erilliset tekstit synteesi-LLM:n läpi jäsennellyksi, tyylikkääksi ja toistovapaaksi Markdown-tekstiksi.
2. **Pituuden Totaalihallinta (Verbosity Constraint):** Mahdollisuus asettaa absoluuttinen pituusrajoite (esim. "One-Pager", "Executive Summary") `synthesis_config`-malliin, mikä pakotetaan työnkulun lopulliseen tekstiin.
3. **Sisäisten prompt-viitteiden suodatus:** LLM:lle annetaan vahva ohje siivota sisäinen jargoni (esim. promptien tekniset muuttujanimet) loppukäyttäjän synteesistä.
4. **Lukijatason ja Äänensävyn Valinta:** Kyky valita tulostukselle tai osiolle lukijataso (esim. asiantuntija, maallikko), joka ohjaa kielellistä sävyä.
5. **Mukautettava Otsikko (Customizable Header Config):** Admin-käyttäjälle valintakytkimet raportin alun esitettäviin muuttujiin (nimet, organisaatiot).
6. **Preamble-Teksti (Johdanto):** Muokattavissa oleva johdantoteksti (esim. tieteellinen pohjustus) ennen varsinaisia datamoduuleja.
7. **Asynkroninen PDF-generointi:** PDF-renderöinti siirretään API-säikeestä asynkroniseksi Arq Worker -tehtäväksi (`generate_pdf_task`), jotta FastAPI pysyy nopeana.
8. **Kumulatiivinen Historiayhteenveto:** Asetus (`include_historical_summary`), jolla työnkulku noutaa aiemmat raportit ja luo tulosteen alkuun kokoavan, dynaamisen yhteenvedon ajan yli.
9. **Ehdottoman Monikielinen Generointi (I18n):** Preamble-tekstit ja staattiset rakenteet tukevat natiivia i18n-käännöstä. Lisäksi syntetisoiva LLM pakotetaan tuottamaan Markdown halutulla loppukielellä Output Profilen ohjaamana.

## 3. Tekninen Toteutus & Olemassa olevan koodin hyödyntäminen
Hybridi-mallimme varmistaa, ettei ohjelmallista Backend-For-Frontend uudelleenkirjoitusta vaadita:
* **Nykyiset DTO:t ja SDUI riittävät sellaisenaan:** Emme muuta tiukasti tyypitettyä `ReportLayoutDTO`-rakennetta emmekä luo uutta `MARKDOWN_BLOCK`-tyyppiä. Sen sijaan BFF-kerros (esim. `sdui.py`) paketoi synteesi-Markdownin olemassa olevaan Server-Driven UI -lohkoon: `{"type": "paragraph", "id": "coach-markdown", "value": {"content": "..."}}`.
* **OutputRenderer on pääroolissa:** Flutterin `ResultDashboard` osaa jo automaattisesti piirtää kyseisen lohkon `OutputRenderer`:illä. Rikastamme ainoastaan Flutter-puolen `MarkdownStyleSheet`-tyylit tukemaan luetteloita (list), lihavointeja, ja taulukoita (table).
* **PdfReportService pysyy yksinkertaisena:** `pdf_generator.py` hyödyntää jo valmiiksi Jinja2-templateja. Laajennamme PDF:n Jinja-templatea tukemaan jämäkämpää Markdown-to-HTML -muunnosta.

## 4. Toteutussuunnitelma (Milestones M1-M4)
Tämä Epic toteutetaan seuraavissa puhtaasti eristetyissä virstanpylväissä:

### M1: Pydantic Data Models & Seeding (Storage Level)
* **`backend_v2/models/domain/output_profile.py`**: Lisätään tulostusprofiiliin tiukat parametrit: `length_constraint` (Esim. "Executive Summary"), joustava sanakirja `preamble_text` (I18nText - ehdoton monikielisyystuki) ja `include_historical_summary`.
* **`backend_v2/seed/seed_data.json`**: Päivitetään ydintiedon oletusprofiilit (`op_executive_summary`) näillä uusilla ominaisuuksilla valmiiksi Pydantic-validointia varten.
* **`backend_v2/seed/scripts/patch_epic13.py`**: Luodaan puhdas migraatioskripti vanhojen testidata-profiilien päivittämiseen, jotta TinyDB/Firestore ei kaadu fail-fast `extra="forbid"` sääntöön.

### M2: TextConsolidationHook & LLM Synthesis (Logic Level)
* **`backend_v2/hooks/synthesis.py` (UUSI)**: Toteutetaan asynkroninen LLM-yhteenveto-hook (`TextConsolidationHook`).
  * **Eri Promptien Yhdistäminen (Deduplication):** Hook ohjeistaa tekoälyä yhdistelemään useista eri työnkulkusolmuista ja erillisistä prompteista peräisin olevat raakatekstit yhdeksi täysin koherentiksi tietovirraksi. Kaikki itsetoisto ja sirpaleisuus poistetaan tylysti.
  * **Output Config -tiedon Fuusio:** Hook lukee Output Profilesta dynaamisesti tulevia lisäyksiä (esim. `preamble_text` tai muokattavia vinkkejä) ja LLM sulauttaa nämä luontevaksi osaksi tekstijatkumoa. Se tekee tämän yhtenäisenä osana tulostetta toistamatta itseään tai rikkomatta kontekstia.
  * **Kohdekieli:** Syntetisoitava kieli on deterministinen ja se noudetaan suoraan ajon metadatasta: `execution.metadata.get("target_locale")`.
  * **XAI Alaviitteet:** Pakotetaan tekoäly tuottamaan tekstiin tarkat `[1]` viitteet MCP Toolsien tarjoamista lähdekohdista.
  * **Token-seuranta:** Kulutetut LLM-tokenit ja prosessoinnin kustannukset kohdistetaan tiukasti `_step_metadata['token_usage']` -objektiin, josta myöhempi Blueprint rutiini perii ne koko raportin yhteiskustannuksiin automaattisesti.
* **`backend_v2/api/routers/output_profiles.py`**: Varmistetaan uusien kenttien läpivienti ja suojataan API `response_model=OutputProfileDTO` vuotojen estämiseksi.

### M3: Architecture Connectors (BFF & Worker Offloading)
* **`backend_v2/services/blueprint.py` (BFF)**: Backend-for-Frontend käärijä tunnistaa valmiin synteesi-Markdownin ja paketoi sen suoraan olemassa olevaan, yksinkertaiseen SDUI-lohkoon: `{"type": "paragraph", "id": "coach-markdown", "value": {"content": "..."}}`. Se EI mutatoi puhdasta `ReportLayoutDTO`-perusrakennetta. Kaikki `has_warning` -liput kirjataan metadatasta ylätason `ReportDataDTO.global_score` / métriikka -komponenttiin.
* **`backend_v2/worker.py`**: Luodaan `generate_pdf_task()`. Arq ottaa PDF-renderöinnin vastuun asynkronisena FastAPI:n nopeuttamiseksi tallentaen datan Blob Storageen.
* **`backend_v2/services/pdf_generator.py`**: Laajennetaan mallia tukemaan jämäkkää puhtaan Markdownin HTML-kääntämistä ennen tulosteen viemistä WeasyPrintin ajettavaksi.

### M4: Flutter Client Display (Desktop-First UI Layer)
* **`client_app_v2/lib/shared/widgets/output_renderer.dart`**: Toteutetaan `MarkdownStyleSheet` tyylien rikastaminen (luettelot/list, data taulukot/table, lainaukset/blockquote), jotta LLM:n rikas Markdown tuottuu pikselilleen oikein.
* **`client_app_v2/lib/features/execution/views/widgets/result_dashboard.dart`**: Varmistetaan olemassa olevan automaattisen `_buildWarningBanner`in häiriötön esilletuonti, mikäli backend lähettää viestiin Graceful Degradation `metrics.has_warning == true` lipun. Lisäksi varmistetaan, että tekstin sisälle syntyvät inline-viitteet (`[1]`) yhdistyvät loogisesti alalaidan aiempaan `_buildReferencesSection` XAI-lähdeluetteloon.
* **(TBA) Profiilien Hallinta Adminissa**: Toteutetaan olemassa olevien vapaiden näyttökomponenttien sisään Preamble_textien ja pituusasetusten (Three-Pane tyyppinen) modifikaationäyttö, johon navigoidaan puhtaasti Stripe Opaque ID -tyylillä (`blk_...`).

## 5. LLM Arkkitehtuurisäännöt
* **Model Registry -pohjaisuus (LLMClient & Yleiset ajot):** Suorat SDK-kutsut tai erilliset LLM-kääreet ovat kiellettyjä. Käytetään valmista `backend_v2/llm/client.py` -luokkaa ja `LLMClient.from_strategy()` -metodia kaikkialla.
* **Pre-prompt ja Roolien eristely (Injektiosuoja):** Kaikki LLM-operaatiot rakennetaan siten, että infrastruktuuri (/system prompt) eristetään kovakoodatuksi vakioksi ohjelmiston tiedoston alkuun, eikä viedä tietokantaan (kuten `translation_hook.py` tekee).
* **DLP ja lokituskielto raakadatalle:** Vaikka LLM-kutsu kaatuisi luodessaan Markdownia, ehdoton lokituskielto asiakkaan raakadatalle (PII) pätee. Palvelimelle kirjataan vain matemaattinen Trace ID ja virhekoodaus.
* **Virhesietoisuus (Graceful Degradation):** Mikäli synteesi-LLM kaatuu ulkopuoliseen API-virheeseen, työnkulku ei saa keskeytyä kokonaan. Backend palauttaa tällöin raportin raakadatan perusmuodossaan, asettaa metatietoihin `has_warning: true` -lipun varoitusviesteineen, ja antaa frontendin valmiin `_buildWarningBanner`-logiikan hoitaa virheviestintä käyttäjälle pehmeästi.
