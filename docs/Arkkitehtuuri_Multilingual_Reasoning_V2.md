# Arkkitehtuurimäärittely: Monikielinen Logiikkaketju (Multilingual Reasoning) V2

**Tila:** Phase 9 (Hardening & Standardization)
**Viitekehykset:** Flutter (Client), Pydantic / Riverpod (Core), RFC 7807 (Error Handling), ISO 8601 (Temporal)

## 1. Johdanto ja Tavoitteet
Quorum V2 -alustan The Zero-Deploy SDUI -arkkitehtuuri vaatii täysin uudenlaisen lähestymistavan monikielisyyteen (I18n / Lokalisointi). Perinteinen menetelmä, jossa backend joko a) palauttaa koodattuja merkkijonoja UI:lle tai b) yrittää arvailla asiakkaan kielen, on **kielletty** (The No-String Mandate). 

Tavoitteena on irrottaa tekoälyn "kognitiivinen" päättelymekanismi (aina englanniksi laadun maksimoimiseksi) loppukäyttäjän "esitys- ja asiointikielestä" (esim. suomi), kadottamatta järjestelmän vikasietoisuutta tai alkuperäisten syötteiden (lainauksien) nyansseja.

Kaiken tämän taustalla vaikuttaa absoluuttinen 5-kerroksinen (5-Layer) Hybridi-Lokalisointistrategia.

---

## 2. The Holistic Localization Strategy (5 Kerrosta)

Tässä arkkitehtuurissa on tiukka rajanveto sille, mikä järjestelmän osa vastaa mistäkin kielellisestä kokonaisuudesta - tekstistä numeroihin ja aikoihin.

### Kerros 1: Staattinen Käyttöliittymä (Compile-Time l10n)
Flutterin luontaiset `.arb`-tiedostot (esim. `app_fi.arb`, `app_en.arb`) on varattu **ainoastaan** käyttöliittymän kiinteille, staattisille komponenteille.
*   **Käyttökohteet:** Napit ("Tallenna"), navigaatio, vakiovaroitukset, staattiset otsakkeet.
*   **Virheenhallinta (RFC 7807 Dual-Reporting):** Backend ei koskaan käännä virheitä tai yhdistele stringejä (esim. "Syöte puuttuu"). Se viestii poikkeukset Enum-tunnisteilla (esim. `"error_code": "VALIDATION_FAILED"`). Flutterin `AppErrorExt` on UI-reititin, joka yhdistää backendin lähettämän dynaamisen tunnisteen lokaaliin `.arb`-käännökseen ja tarjoaa käyttäjälle yhdistetyn *Actionable Hintin* (virhe + toimintaohje omalla kielellä).

### Kerros 2: SDUI-Tietokanta & Dynaamiset Säännöt (Runtime Payload)
Kun järjestelmään lisätään uusia arviointimatriiseja, kyselyitä tai sääntöjä (PromptBlocks), nämä eivät kuulu `.arb`-tiedostoihin, koska se rikkoisi Zero-Deploy -arkkitehtuurin (vaatisi koodinjulkaisun jokaisen tekstinmuutoksen yhteydessä).
*   **Käyttökohteet:** Tietokannassa asuvat monikieliset matriisiselitykset, skaalat (1-5 pistettä) ja ohjetekstit asiointikielellä.
*   **Toteutus:** Pydantic DTO (esim. PromptBlock) tallentaa rakenteen kantaan mallilla `translations: {"fi": "Syyttäjä...", "en": "Prosecutor..."}`. Backend puskee koko DTO-objektin rajapinnasta läpi. Flutter (tyhmänä moottorina) iteroi oman Riverpod `Locale`-asetuksensa mukaista avainta ja renderöi käyttöliittymän reaaliaikaisesti tällä sisällöllä. Vihje: AI-moottori ei lue näistä koskaan muuta kuin `en` arvon.

### Kerros 3: Kognitiivinen Moottori & English-Only Mandate (The Deep Engine)
Tekoälymalli on asiantuntija-agenttina huomattavasti kyvykkäämpi englanninkielisenä. Koko ydinmoottori tekee tälle ns. "Bilingual Reasoning" -leikkauksen.
*   **The English-Only Mandate:** Admin-käyttäjien asettamat järjestelmätason syötteet (kuten Context Retrievaliin laitettava `ai_description`) ja asiantuntija-agenttien metatiedot on **vaatimuksena kirjoitettava aina englanniksi**, jotta tekoälyn ongelmanratkaisuympäristö pysyy kognitiivisesti maksimaalisella (Fidelity) tasolla.
*   **Hybridiajattelu (Scratchpad + Quotes):** Kun malli analysoi suomenkielistä tekstiä, se pakotetaan ajattelemaan analyysiprosessi (JSON-avaimet ja argumentaatio/scratchpad) **englanniksi**, mutta sen on poimittava käyttäjän alkuperäiset lainaukset täysin koskemattomina alkuperäiskielellä (raaka *Quote*). 

### Kerros 4: Numeerinen ja Temporaalinen Standardi (Dates, Numbers, Currencies)
Numeroita, päivämääriä, kellonaikoja ja valuuttoja **ei koskaan formatoita merkkijonoiksi (strings) tai lokalisoida (esim. "14. maaliskuuta") backendissä**.
*   **Aika (The Temporal Standard):** Kaikki kellonajat ohjelmassa tallennetaan ja käsitellään backendissä absoluuttisena UTC-aikana. Lokeihin ja kantaan menee tiukasti `datetime.now(timezone.utc)`. API:n yli JSON-formaatissa siirtyy aina laitteistosopiva ISO 8601 -standardi (`"2026-03-14T15:30:00Z"`).
*   **Luvut ja Data (Primitives):** Skemaattinen data (`score`, token-määrä) valuu rajapinnasta läpi primitiivisinä numeroina (esim. `5.0` tai `12450`).
*   **Esittäminen (Flutter ICU / intl):** Vasta kun tieto saapuu sovelluksen ruudulle, Flutter ottaa vastuun konvertoiden datan käyttäjän laitteen paikallisten aika- ja numeroasetusten mukaiseksi. Esim. Dartin `intl`-kirjaston avulla aikavyöhyke konvertoidaan fyysiseksi viisariajaksi ja numerot pilkutetaan `.arb` (ICU) luokitteluilla (`decimalPattern`).

### Kerros 5: The Translation Boundary & Loppusynteesi (Dynamic Data L10n)
Koska ".arb" ei pysty kääntämään reaaliajassa lauseita, joita ei aiemmin ollut olemassa (kuten mallin yllä keksimää uniikkia `scratchpad`-ajattelua), the "Raw Auditor JSON-View" vaatii ratkaisun.
*   **The Translation Hook:** Kun asiantuntija-agentti suorittaa askeleen, deterministinen ohjelmallinen the Translation Boundary Hook (esim. kevyt `gemini-2.5-flash` -malli) laukaistaan väliin. Se lukee asiointikielen (esim. `language="fi"`) API-pyynnöstä, ottaa englanninkielisen hybridijsonin ja **kääntää vain tekstiarvot (values) asiointikielelle muuttamatta ohjelmiston JSON-avaimia (keys).**
*   **Lopullinen Markdown-tuote:** Koko ketjun viimeinen kokoaja-solmu (XAI-raportoija) syntetisoi yllä käännetystä datasta ihmisluettavan, dynaamisen, ja asiakkaalle täydellisellä lokaalilla siivotun raportin (Markdown, `flutter_markdown`).

---

## 3. Toteutuksen Pääkohdat (Vastuunjako)

Tämän mallin saavuttamiseen vaaditaan seuraavat käytännön muutokset V2-monorepossa. Ne on jaettu tiukasti Backendin ja Frontendin kesken "Zero-Deploy SDUI" -sääntöjen mukaisesti.

### Backend (Python / Pydantic V2)
1.  **Sys-Config & Päätelymoottori (`seed_data.json`)**:
    *   Lisätään asiantuntija-agenteille *Bilingual-rajoite* (System Prompt: "Read input in given language, but analyze and reason STRICTLY in English. Quote verbatim").
    *   Lisätään uusi `translation_hook` asianmukaisten Output-agenttien konfiguraatioputkeen.
2.  **Input Ingestion (`input_processing.py`)**:
    *   Pakotetaan injektoimaan AI-ohjeet ja Context Metadata (`ai_description`) puhtaasti englanniksi (*The English-Only Mandate*).
3.  **Käännöskoukun Toteutus (`translation_hook.py`)**:
    *   Rakennetaan uusi The Translation Boundary post-hook (Kevyt LLM, esim. Flash). Se lukee asiakkaalta lähetetyn The Negotiation Contextin `target_language` (esim. "fi"), ja kääntää ainoastaan askeleen JSON:n dynaamiset tekstiarvot asiointikielelle tallentaen avaimet ehjinä.
4.  **Aika- ja Lukustandardit**:
    *   Varmistetaan (Linting/Review), että mikään endpoint ei taita aikaa tai valuuttoja stringeiksi, vaan jättää ne ISO 8601 UTC / Float -muotoon.

### Frontend (Flutter / Riverpod)
Ainoa osa, missä käyttöliittymä reagoi, on kyky olla tyhmä ja kaunis renderöintimoottori, joka käyttää hyväkseen `.arb`-staattisia lokeja ja laitteiston lokaaleja. Aivan kuten nyt.
1.  **Dynaaminen Kielen Välitys (Context Sync)**:
    *   Varmistetaan, että Flutterin API-kerros lähettää Riverpod-tilan mukaisen lokaalin asiointikielen (esim. `target_language: "fi"`) osana HTTP-pyynnön parametreja, jotta Backendin `translation_hook` tietää, mille kielelle JSON käännetään lennosta.
2.  **Temporaalinen Esitys (Intl/ICU)**:
    *   Auditoijan (JSON-näkymän) ja muiden SDUI-komponenttien numeeriset ja temporaaliset tiedot ajetaan lokaalin `intl`-kirjaston läpi. Aika käännytään käyttäjän lokaalille vyöhykkeelle, ja numerot esitetään `.arb`-tiedoston `decimalPattern`-parametrein.
3.  **Virheiden Lokalisointi (RFC 7807)**:
    *   Jatketaan `AppErrorExt`-mallin käyttöä. Jos uusia käännöspisteitä syntyy moottorin virheille (esim. `TRANSLATION_FAILED`), niille varataan selitykset ja *Actionable Hintit* valmiiksi `.arb`-tiedostoihin.
4.  **Käyttöliittymän Konfiguraatio-Ohjeet (The English-Only Mandate)**:
    *   Cognitive Admin Studioon (Frontend V2) on lisättävä selkeät ja ohjaavat apu- / vihjetekstit kaikkiin kenttiin, jotka osallistuvat LLM:n syväohjaamiseen (`ai_description`, asiantuntija-agenttien metadatakentät). Esim. l10n:llä `app_en.arb`: *"MANDATORY: Must be written in English. This is a cognitive prompt, not user data."* Näin pakotetaan *System Native Mandate* -ajattelu suoraan loppukäyttäjälle käyttöliittymätasolla ennen tietokantaan kirjausta.
