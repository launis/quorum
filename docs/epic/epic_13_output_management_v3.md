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
* **OutputRenderer on pääroolissa:** Flutterin puolella oleva `output_renderer.dart`, joka käyttää `flutter_markdown_plus` -kirjastoa, ottaa suoraan backendin tuottaman synteesi-Markdownin renderöidäkseen sen laadukkaasti ja jäsennellysti ruudulle.
* **Nykyiset DTO:t riittävät pitkälle:** Säilytämme nykyisen `ReportLayoutDTO` -rakenteen sellaisenaan. Lisäämme layout-tyypiksi pelkän "MARKDOWN_BLOCK", joka kantaa tuoreen LLM-synteesitekstin. `sdui.py` ja frontend osaavat näyttää sen ilman uusia kymmentä eri komponenttimallia.
* **PdfReportService pysyy yksinkertaisena:** `pdf_generator.py` hyödyntää jo valmiiksi Jinja2-templateja. Laajennamme PDF:n Jinja-templatea tukemaan jämäkämpää Markdown-to-HTML -muunnosta (esim. Pythonin markdown-kirjastolla) ennen WeasyPrint-renderöintiä.

## 4. Seuraavat Askeleet (Next Steps)
Voimme edetä tekniseen työhön erittäin suoraviivaisesti varjellen olemassa olevia rakenteita:

* **Output Profile -mallin päivitys (Backend):**
  * Lisätään `output_profile.py` -tiedostoon `length_constraint` (pituusrajoite) ja `preamble_text` (johdantoteksti).
* **TextConsolidationHook (LLM Synteesi):**
  * Luodaan uusi synteesihookki, joka ottaa raakadatan ja puskee sen synteesi-LLM:n läpi.
  * Prompti ohjeistaa mallia: *"Kirjoita yhtenäinen Markdown-yhteenveto, pituusrajoite: {length_constraint}, poista sisäinen jargoni."*
  * Ulostulo tallennetaan suoraan Markdown-stringinä "MARKDOWN_BLOCK"-rakenteeseen tietokantaan.
* **Asynkroninen PDF Worker (Tietojenkäsittely):**
  * Siirretään pitkäkestoinen `pdf_generator.py`:n suoritus blokkaamattomaan Arq-workeriin (`worker.py` -> `generate_pdf_task`).
* **Three-Pane UI (Frontend):**
  * Toteutetaan Admin Studioon uusi moderni jaettu työpöytänäkymä (Three-Pane layout).
  * Oikean reunan tulosten katseluruutu hyödyntää olemassa olevaa responsiivista `OutputRenderer`:ia tuotetun Markdown-synteesin esittämiseen. Mitään visuaalisesti rajoittavaa A4-lukitusta tai matematiikkaa ei siihen koodata.
* **Arkkitehtuuridokumentaation Päivitys:**
  * Päivitetään `.agents/rules/04_directory_reference.md` vastaamaan uusia polkuja (koskien Worker/Hook-rakenteita). Huom: `04_directory_reference.md` ainoa tarkoitus on jatkossakin pelkästään lyhyesti selittää mitä tiedostoja on missäkin hakemistossa, se ei sisällä ohjelmointilogiikkaa.

## 5. LLM Arkkitehtuurisäännöt
* **Model Registry -pohjaisuus (LLMClient & Yleiset ajot):** Suorat SDK-kutsut tai erilliset LLM-kääreet ovat kiellettyjä. Käytetään valmista `backend_v2/llm/client.py` -luokkaa ja `LLMClient.from_strategy()` -metodia kaikkialla.
* **Kutsutavat ja roolien esittely (Injektiosuoja):** Kaikki LLM-operaatiot rakennetaan siten, että infrastruktuuri (/system prompt) eristetään kovakoodatuksi vakioksi ohjelmiston tiedoston alkuun, eikä viedä tietokantaan (kuten `translation_hook.py` tekee).
* **DLP ja lokituskielto raakadatalle:** Vaikka LLM-kutsu kaatuisi luodessaan Markdownia, ehdoton lokituskielto asiakkaan raakadatalle (PII) pätee. Palvelimelle kirjataan vain matemaattinen Trace ID ja virhekoodaus.
