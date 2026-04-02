# EPIC 13: Output Management V3 (Tulostuksen Hallinnan Uudistus)

## 1. Yleiskatsaus (Overview)
Tämän Epicin tavoitteena on uudistaa täysin Cognitive Quorum -järjestelmän tulostuksien hallinta (Output Management). Painopisteenä on tekstisisältöjen laadun parantaminen (toiston poisto, syntetisointi), lukijatasojen valintamahdollisuuksien lisääminen sekä Admin Studion käyttöliittymän merkittävä parannus "Three-Pane" tyyppiseen työpöytä-layoutiin. Tämä on useita iteraatioita kestävä kokonaisuus.

## 2. Pääominaisuudet (Key Features)
1. **Tekstien Syntetisointi (Text Consolidation):** Uusi asynkroninen jälkikäsittelyhook (`TextConsolidationHook`), joka ajaa eri osioiden erilliset `justification`-tekstit ja ulostulolaajennukset (coaching, risk_flag, falsification jne.) kevyen synteesi-LLM:n läpi. Tämä yhdistää sisällön yhtenäiseksi ja toistovapaaksi asiantuntijatekstiksi.
2. **Sisäisten prompt-viitteiden suodatus:** Osa syntetisointivaihetta LLM:lle annetaan vahva ohje siivota sisäinen jargoni (esim. promptien muuttujanimet) loppukäyttäjän dokumentista.
3. **Lukijatason Valinta (Reader Understanding Dimension):** Kyky valita tulostukselle tai osiolle lukijataso (esim. Executive, Asiantuntija, Maallikko), joka ohjaa `TextConsolidationHook`:n generoimaa kielellistä ulosantia.
4. **Mukautettava Otsikko (Customizable Header Config):** Admin-käyttäjälle valintakytkimet, jotta raportin alkuun voidaan valita näytettäväksi käyttäjän nimi (display_name), organisaation nimi (org_name) ja sähköposti.
5. **Preamble-Teksti (Johdanto):** Muokattavissa oleva I18nText-johdantoteksti (esim. kuvaamaan tieteellistä pohjaa ja luotettavuutta) ennen varsinaisia moduuleja.
6. **Käyttöliittymäuudistus (Studio UI Redesign):** Admin Studion `OutputProfileCrudView` suunnitellaan kokonaan uudestaan moderniin Master-Detail / Three-Pane-layoutiin, jossa portfoliot/profiilit ovat vasemmalla listana, keskellä on tulostusosiot, ja oikealla aukeaa kunkin osion tarkka hallintapaneeli.

## 3. LLM Arkkitehtuurisäännöt (Model Registry V2 & 01-python-backend.md)
**HUOM: Nämä säännöt sitovat kaikkea tämän Epicin LLM-integraatiotyötä (mm. Synthesis Hookia).**
Kaikki LLM-työkalujen käyttö **TÄYTYY** noudattaa Pydantic V2 / Phase 9 Fail-Fast arkkitehtuuria (`01-python-backend.md` -sääntöjen mukaisesti) sekä `c:\src\quorum\backend_v2\llm\` ympäristön arkkitehtuurinormeja:

*   **Model Registry -pohjaisuus (LLMClient):** Suorat OpenAI tai VertexAI SDK -kutsut tai kovakoodatut instanssit ovat EHDOTTOMASTI KIELLETTY. Kaikki LLM-pyynnöt on ajettava `backend_v2.llm.client` -moduulista löytyvän `LLMClient.from_strategy("strategy_name", repo)`-operaation kautta, joka hakee oikeat reititykset ja rajoittimet tietokannasta ("Zero-Fallback" -sääntö).
*   **Structured Outputs Pydantic V2:** LLM-kutsut eivät saa palauttaa raakatekstiä JSON-parsinnan toivossa. Synteesihookissa on käytettävä LLMClient:n `run_structured_task()` -metodia ja annettava tiukka Pydantic V2 -malli (`response_model`), joka varmistaa ulostulon validiteetin. Regex-ratkaisut on ankarasti kielletty.
*   **Ei-tukkimista FastAPI -säikeessä (Non-Blocking execution):** Raskas LLM-syntetisointi prosessoi pitkiä tokeneita. Suoritukset on EHDOTTOMASTI käännettävä asynkroniseksi poikkeuksetta (ajetaan Arq Workerin kautta) eikä koskaan lukitsemaan FastAPI HTTP -requestia. Yli 500 ms prosessit FastAPI-säikeessä katsotaan arkkitehtuurivirheeksi.
*   **Data Leak Prevention:** Vaikka prompt olisi virheellinen, sisältäen PII-dataa tai LLM kaatuisi, näitä LLM-pyyntöjä / raw-payload dataa EI LOKITETA (ei `logger.error` tai Exceptionin sisään). Lokiin tallennetaan vain matemaattinen virhekoodi ja System ID (Trace ID). 

## 4. Seuraavat Askeleet (Next Steps)
1. **Tier 2 (Database & Data Models):** Luodaan `seed_data.json` tiedostoon ja vastaaviin Backend Pydantic -malleihin Output Profileen tarvittavat kentät (`header_config`, `synthesis_config`, `preamble_text`). Varmennetaan re-seedillä TinyDB:ssä.
2. **Tier 2 (Dart Freezed):** Päivitetään vastaavat client-app koodiston `report_data_dto.dart` rakenteet ja ajetaan Flutterin build_runner.
3. **Tier 2 (Reporting Backend Services):** Suunnitellaan `backend_v2/hooks/reporting.py` -tiedostoon tuki uudelle `TextConsolidationHook`:lle ja ajetaan se osana DAG:ia, jos profiili niin käskee.
4. **Tier 2 (Studio UI Layout Refactor):** Poistetaan nykyinen lomakerakentaja ja luodaan Split/ThreePane layout.
