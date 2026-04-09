# Epic: Frontend Fail-Fast Network & Retry Policy
**Status**: Backlog  
**Domain**: Client Application (Flutter) / API Networking  
**Priority**: High (System Resilience Requirement)  
**Tunniste**: `mini-epic-failfast`

## 1. Yhteenveto / Executive Summary
Tämän "Mini-Epicin" tavoitteena on estää "Domino-efekti", joka havaittiin, kun Backendin (esim. `HighlightBoxDisplay` tyhjän datan injektio) sisäinen prosessi iski Pydantic Validointiin (HTTP 500), mikä puolestaan jumiutti Frontendin asynkronisen long-polling-silmukan ikuiseen uudelleenyritämisen (Retry) sykliin. 

Tulevan päivityksen tarkoitus on varustaa Frontend luotettavalla **Fail-Fast** -säännöstöllä. Jos sovellus kohtaa HTTP 500 (Internal Server Error) virheen, käyttöliittymän verkkokutsusilmukan tai Dio-asiakkaan on pakko pysäyttää toimintonsa ja ohjata virhe heti Error Boundarylle sen sijaan, että se tukkii backendin lokit toistuvilla kyselyillä.

## 2. Nykytila ja Ongelmat (The Root Cause Cascade)
* **API Route (`/render`) Logiikka**: Asynkronisten operaatioiden aikana reitti palauttaa `202 Accepted`, mitä Riverpod FutureProvider pollasi onnistuneesti ohjelmoidusti.
* **Backend Triggeri**: Tekninen hallucinaatio puski läpi rikkinäistä mallidataa (esim. `[]` kääntyi muotoon `""`), mikä räjäytti Pydanticin V2 tiukan `ValidationErrorin`. Backend vastasi odotetusti ja oikein `HTTP 500 Internal Server Error` Fail-Fast protokollan mukaisesti.
* **Frontendin Kuolemansilmukka**: Frontendin verkkomoduuli (Dio retry evaluator tai erillinen ReportControllerin pollaussilmukka) tulkitsi 500-virheen joko transienttina liikennekatkoksena (Internet connection drop) tai väliaikaisena kieltäytymisenä (Rate Limit/Gateway timeout), ja alkoi moukaroida rajapintaa automaattisesti eksponentiaalisella toistolla.
* **Seuraus**: Yli 6000 rivin logispämmi backendissä (kaataa ohjelmiston samaan paikkaan aina uudelleen) ja turhaa akunkulutusta client-päässä.

## 3. Tavoitteet / Acceptance Criteria
Epic on valmis kun seuraavat vaatimukset täyttyvät The "De-Generator" -arkkitehtuurin mukaisesti:

- [ ] **Dio Oletus Interceptor**: Dion globaali (tai retry) interceptor on rajattu hyväksymään uudelleenyritämisen MIKÄLI statuskoodi on vain laitteistoon tai verkostoon rinnastettava (esim. `502, 503, 504` tai Timeout). Kohdatessa statuskoodin `500`, se hylkää Retry-silmukan ehdottomasti.
- [ ] **Render-Rajapinnan Paikallinen Pollaus**: `ReportController` (Riverpod) varmistaa pollaussilmukassa (kun vastauksena on ollu `202 accepted`), että `try/catch` heittää 500-tasoiset DioExceptionit ulos silmukasta heti katkaisten suorituksen (ei `Future.delayed` pakoja).
- [ ] **UI:n Välitön Rikko (Red Screen Avoidance)**: Kun verkkokutsu pysähtyy `500`:seen, UI kääntää komponentin `error`-tilaan nätisti (esim. kustomoitu AppException Widget Error Boundaryssä), estäen tyhjien tai punaisten näyttöjen syntymisen.
- [ ] **Integraatiossa Varmennettu**: Manuaalinen testaus tehty injektoimalla Backendistä tarkoituksenmukaisesti `raise RuntimeError("Test")` rajapinnasta ja tarkistettu, ettei logiin generoidu toistettuja yrityksiä clientistä.

## 4. Tekniset Vaihtoehdot & Linjaukset
*(Valittava toteutusvaiheessa)*

1. **Keskitetysti Dion Interceptorilla:** (Suositus) Muokataan suoraan mahdollista `RetryInterceptor` luokkaa palauttamaan `false` välittömästi `HTTP 500`, `400` ja `403` statuskoodeissa.
2. **Paikallisesti ReportControllerissa:** Modifioidaan nimenomaista `/execution/render` futurea, the long-poller, joka aiheutti varsinaisen ruuhkan. Katkaistaan loop heittämällä erioikeudellinen `AppException`.
3. **Backend-Tuoksuinen RFC 7807 Filter**: Dion Exception Handler lukee automaattisesti Payloadista RFC 7807 standardimukaisen `error_code: INTERNAL_SERVER_ERROR` JSON avaimen ja asettaa Retryt kielletyiksi.

## 5. Riippuvuudet
* Koskee tiedostoja: Flutterin `ExecutionClient` ja `ReportController`, lisäksi `Dio` instanssin konfiguraatiot (`api_client.dart` / `api_client_provider.dart`).
* Ei vaadi muutoksia Backendiin, sillä Pydantic suoriutuu jo RFC 7807 protokollasta suvereenisti varjellen rajapintojen turmeltumisen sisäisesti.
