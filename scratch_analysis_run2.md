# Ongoing Run Analysis (Run 2)

## Status
- **10:52:** Ajo on käynnistynyt! (Execution ID: `exe_928e1f063c494f0785cbb6b7ddbed3d6`)
- Syötteet (`product_text.md` ja `chat_log.md`) on purettu ja ensimmäinen `ChatParserLLM` Vertex AI -caching on käynnissä.

## Exceptions & Interesting Events
- **10:54:11:** `[SecurityHook] PII detected and redacted. Threat count: 3` -> Deterministinen turvakoukku toimii täsmälleen kuten ensimmäisessä ajossa.
- **10:55:36:** `Lexical Verifier used Fuzzy Fallback for 'Sääntelypaine...'. Score 99.3% >= threshold 80.0%` -> AnchorValidationService pelasti rikkoutuneen tekstiankkurin kaatumasta. Determinismitoimii!
- **10:57:12:** Toinen `Fuzzy Fallback` pelastus ('CSRD-direktiivin ja EU-taksonomian kaltaiset säädö...', 99.2%)!
- **10:58:27:** Kolmas `Fuzzy Fallback` pelastus ('**Sääntelypaine:** CSRD-direktiivin ja<br>EU-takso...', 99.3%)! Markdown-artifakteja poimittu nätisti talteen.
- **10:59:57:** `LLM Schema Validation Failed.` -> **11:00:50** `Self-Healing successful.` Pydantic-korjausluuppi pelasti rikkoutuneen JSON-rakenteen lennosta!
- **11:01:20 & 11:01:26:** `RateLimitError: Resource exhausted (429)`. Vertex AI kapasiteetti ylittyi! Mutta järjestelmän `dynamic exponential backoff` otti kopin, odotti, ja lopulta **11:02:20** saatiin `200 OK` ja prosessi jatkui ilman kaatumista. Täydellinen joustavuus.
- **11:02:50 - 11:05:12:** Kolme uutta `LLM Schema Validation Failed` osumaa putkeen! Pydantic-korjausluuppi hoitaa nämä kaikki vuorotellen `Self-Healing successful`. Järjestelmä on todella kovilla, mutta ei anna periksi!
- **11:07:36:** Jälleen `RateLimitError: Resource exhausted (429)`. Exponential Backoff iski kiinni ja ajoi sen onnistuneesti läpi kello **11:08:15** ilman käyttäjälle näkyvää kaatumista.
- **11:08:46 - 11:09:36: MÄÄRITELMÄLLINEN ONNISTUMINEN!** Malli hallusinoi täysin väärän ankkurin ('Talousjärjestelmän vakauteen...'). Lexical Verifier laski, että RapidFuzz on vain 78.6%, mikä jäi alle tiukan 80.0% rajan. Uudelleenyritys johti tilaan `Stuck Loop Detected in Logical Validation`. Kuten olimme Epicissä suunnitelleet, ohjelmisto hylkäsi väärän datan ja injektoi `Null Object Fallbackin` ilman yhtäkään kaatumista! Ajo jatkuu.
- **11:15:48:** AJO VALMIS! `PDF generated successfully and path saved`. Taustajärjestelmä selvisi kaikista haasteista.
- **11:15:49:** Uusi virhe UI-puolella: Flutter kaatuu Riverpod-virheeseen. `CheckedFromJsonException: Could not create SduiParagraphBlock. There is a problem with "citations". type 'int' is not a subtype of type 'String' in type cast`.

## Epic Tracking: System 2 Reliability Fixes
*(Seurataan samojen ominaisuuksien suoriutumista tässä ajossa)*
