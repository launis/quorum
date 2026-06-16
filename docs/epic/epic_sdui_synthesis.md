# Epic: Synthesis SDUI (Server-Driven UI)

## 1. Tavoite
Täydellinen Server-Driven UI (SDUI) raporttien synteeseille. Korvataan vapaamuotoinen `synthesized_markdown` -teksti strukturoidulla komponenttilistalla (`list[UIBlockDTO]`), jotta käyttöliittymän (Flutter ja PDF) renderöinti on täysin determinististä, eikä raskaita ja virhealttiita Markdown-jäsentimiä tarvita.

## 2. Arkkitehtuurisäännöt ja Rajoitteet (Constraints)

Seuraavia sääntöjä on noudatettava ehdottomasti koko epicin toteutuksen ajan:

> [!IMPORTANT]
> **Hardening Rule #30 (`tripartite_rendering_boundary`)**
> **Hardening Rule #37 (`pydantic_namespace_collisions`)**: Kaikki Pydantic-skeemat vain `models/` -hakemistoon.
> **Hardening Rule #29 (`high_fidelity_prompting`)** & **#51 (`hybrid_prompting_mandate`)**
> **Hardening Rule #2 (`strict_pydantic_v2_rust`)** & **#8 (`duck_typing_token_shield_exception`)**
> **Hardening Rule #20 (`the_self_healing_ban`)**: Kieltää Regex-pohjaisen paikkailun, mutta sallii Structured Retry -mallin.
> **Hardening Rule #44 (`cross_language_enum_parity`)**: Flutterin ja Pythonin Enumien on oltava synkassa.
> **Agent Rule (`strict_physical_anchoring_mandate`)**: Kieltää fuzzy-matchingin. Lähdeviittaukset on löydyttävä fyysisesti `str.find()`-haulla.

1. **Flat Architecture:** Rekursiiviset komponentit ovat ehdottomasti kiellettyjä. Yksikään blokkityyppi ei saa sisältää toista `list[UIBlockDTO]` -kenttää. Kaikki blokit ovat terminaalisia primitiivejä samassa tasalistassa.
2. **Zero-Trust Validation:** Kaikkien Pydantic-mallien (blokkien) on käytettävä asetusta `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")`.
3. **Rakenteelliset viittaukset (Citations):** Lähdeviittaukset on käsiteltävä blokkitason strukturoituna datana (`citations: list[int]`), ei tekstin sisäisinä inline-merkintöinä (esim. `[1]`). Frontend ei saa käyttää Regex-parsintaa.

## 3. Toteutusvaiheet (Implementation Plan)

### Vaihe 1: Backend Pydantic SDUI -mallit ja Vertex AI "Fat Object" Pattern
**Tiedosto:** `backend_v2/models/dtos/sdui_components.py` (ja mallien päivitykset)
- **Olemassa olevan infrastruktuurin hyödyntäminen (`sdui.py`):** Koodikannassa on jo valmiina `SduiBlockBase` (joka perii `V2CoreBase`:n) sekä polymorfinen `AnySduiBlock` -diskriminaattori.
  1. **Perintä:** Uusien blokkien (`ParagraphBlock`, `BulletListBlock`, `AlertBlock`) on **ehdottomasti perittävä** suoraan `SduiBlockBase`-luokka. Näin varmistetaan, että ne jakavat saman perusrakenteen ja Pydantic-konfiguraatiot, ja sisältävät automaattisesti pakollisen `block_type`-kentän.
  2. **Unionin Laajennus:** Olemassa olevaa O(1)-diskriminaattoria (`AnySduiBlock`) laajennetaan sisällyttämällä siihen uudet blokit: `AnySduiBlock = Annotated[HeroInsightBlock | ParagraphBlock | BulletListBlock | AlertBlock, Field(discriminator="block_type")]` (Rule 96).
  3. **Käyttö:** DTO-rakenteissa synteesin lopputulos määritellään puhtaasti muotoon `content_blocks: list[AnySduiBlock]`. Uutta irrallista `UIBlockDTO` -tyyppiä ei saa luoda.
- **Toteutettavat Uudet Blokkimallit (`sdui.py`):**
  - `ParagraphBlock(SduiBlockBase)` (`block_type: Literal["paragraph"]`, `text: str`, `citations: list[int]`)
  - `BulletListBlock(SduiBlockBase)` (`block_type: Literal["bullet_list"]`, `items: list[BulletListItem]`)
  - `AlertBlock(SduiBlockBase)` (`block_type: Literal["alert_box"]`, `severity: Literal["info", "warning"]`, `text: str`, `citations: list[int]`)
- **Konversio ja DLQ-kaatumisen Esto (Viimeinen Turvaverkko):** Jos malli ei korjaa virhettään maksimi-retryjen jälkeenkään, backend parseroi palautuneen listan tiukaksi `list[AnySduiBlock]` -rakenteeksi iteroimalla blokit yksitellen `try-except` -lohkossa. Jos blokki yhä hajoaa validointiin (esim. puuttuva kenttä), se pudotetaan hiljaisesti (Drop) tai korvataan `AppErrorBoundary` -varoitusblokilla (Graceful Degradation). Tämä pelastaa loppusynteesin DLQ-kaatumiselta.

### Vaihe 2: Synteesipromptien päivitys ja Migraatiostrategia
**Tiedostot:** `synthesis.py` ja kaikki `synthesized_markdown` -kentän kuluttajat
- **Migraatiostrategia (Rip-and-Replace):** `synthesized_markdown` -kenttä on erittäin laajasti käytössä (DTO, state_delta, blueprint, testit). Koska vanhoja ajoja ei tarvitse tukea, kenttä **poistetaan kokonaan** ja korvataan kerralla `content_blocks`:lla. Taaksepäin yhteensopivuutta ei rakenneta. Kaikki yli 15 kuluttajaa on päivitettävä samassa epicissä, jotta lokaalit auditoinnit (backend_audit_loop.py) menevät läpi.
- Päivitä LLM-kutsu palauttamaan uuden Pydantic-skeeman mukainen rakenne (Structured Outputs).
- **Hybrid Prompting & Context Caching (Rule 29, 51, 52):** Synteesin prompt on kirjoitettava Hybrid Prompting -topologialla (XML/Markdown). Kaikki dynaaminen data injektoidaan `<execution_parameters>` -tagiin, ja core-ohjeet pysyvät 100 % staattisena Context Caching -yhteensopivuuden varmistamiseksi. Nykyinen `synthesis.py` noudattaa jo tätä rakennetta — se on säilytettävä.
- Lisää system_promptiin tiukka ja selkeä XML-ohje (`<rule>`-elementti), joka ohjaa synteesiä:
  - Luettele sallitut `block_type`-arvot (exhaustively).
  - Kiellä rekursio, sisäkkäiset blokit ja Markdown-syntaksin käyttö tekstikentissä.
  - Ohjeista asettamaan lähdeviittaukset `citations`-kenttään (1-indeksoituna) tekstin sisään kirjoittamisen sijaan.

### Vaihe 3: PDF-moottorin päivitys
**Tiedostot:** `pdf_generator.py`, `report_template.jinja2`
- Poista synteesiin kohdistuva `markdown`-filtteri (`| md | safe`) PDF-templatesta.
- Päivitä template iteroimaan `content_blocks`-listaa ja renderöimään HTML-elementit (`<p>`, `<ul>`, `<div class="alert">`) blokkityypin mukaisesti. Lähdeviittaukset renderöidään suoraan `citations`-listasta.

### Vaihe 4: Flutter-clientin refaktorointi & Enum Parity Automaatio
**Tiedostot:** Dart DTO -mallit, `enums.dart`, käyttöliittymän renderöintikomponentit, `test_enum_parity.py`
- **Täydellinen Enum Parity -tarkistus (Rule 44):** Tällä hetkellä `test_enum_parity.py` sisältää vain kovakoodattuja testejä. Tässä Epicissä testilogiikka laajennetaan tekemään **täydellinen ja automaattinen tarkistus** ainakin SDUI-blokkien osalta. Testin on dynaamisesti luettava backendin `sdui.py` -tiedostosta kaikki sallitut `block_type` Literal-arvot ja varmistettava ristiin, että jokainen niistä on määritelty Flutterin `enums.dart` -tiedostossa oikeilla `@JsonEnum()` -arvoilla. 
- Päivitä Flutterin Dart DTO:t vastaamaan backendin uutta `content_blocks` -listarakennetta.
- Korvaa olemassa oleva vapaamuotoinen `MarkdownWidget` uudella `SDUIBlockRenderer` -komponentilla.
- Renderöi natiivit Flutter-widgetit (`Text`, `Column`, `Container`) kunkin blokin tyypin mukaisesti. Lähdeviittaukset renderöidään esimerkiksi natiiveina badgeina kappaleen perässä.
- Legacy Markdown -tukea **ei** tarvitse implementoida taaksepäin yhteensopivuuden vuoksi.

### Vaihe 5: Spatiaalinen Ankkurointi (Track A)
**Tiedostot:** `anchor_validation_service.py` / `chunk_worker.py`
- SDUI-blokkeihin tuodut lainaukset (`exact_quote`) voivat erota välimerkeiltään tai asettelultaan alkuperäisestä tekstistä johtuen formaattimuunnoksesta.
- **Kriittinen Rajoite (Spatiaalinen Ankkurointi):** `hardening.xml` Rule 20 kieltää lennosta tapahtuvan Regex-paikkailun ja Agent Rule `strict_physical_anchoring_mandate` kieltää ehdottomasti `fuzz.partial_ratio` tai muun sumean haun käytön.
- **Toteutus (Deterministinen O(N) Normalisointi):** Koodikannassa on jo `AnchorValidationService.normalize_text_with_mapping()`, joka kuorii kaiken ei-alfanumeerisen tekstin ja säilyttää tarkan indeksikartan.
  - LLM:n palauttama `exact_quote` ajetaan tämän normalisoinnin läpi.
  - Alkuperäinen `source_text` ajetaan saman normalisoinnin läpi.
  - Tehdään puhdas, deterministinen `str.find()` normalisoituun tekstiin. Indeksikartan avulla saadaan alkuperäisen, muistissa fyysisesti koskemattoman lähdetekstin indeksit käyttöliittymän (Flutter/PDF) highlight-toiminnallisuutta varten. Regex-hakuja tai joustavia välimerkkikuvioita ei tarvitse eikä saa lisätä.

## 4. Riippuvuudet
- **✅ Ratkaistu:** "Structured Prompting" -epicin `const -> enum` -kääntäjä (`client.py` tai vastaava) on jo onnistuneesti implementoitu (`strip_unsupported_constraints`). Yhtäkään estettä Epicin aloittamiselle ei ole.

## 5. Menestyskriteerit (Definition of Done)
- [x] Backend tuottaa synteesit litteänä `content_blocks` -listana vapaamuotoisen Markdownin sijaan.
- [x] Pydantic-malleissa on käytössä `extra="forbid"` sekä unionin O(1)-diskriminaattori (`block_type`).
- [x] Yksikään blokkityyppi ei ole rekursiivinen (Flat Architecture -mandaatti toteutuu).
- [x] Lähdeviittaukset ovat `citations`-listoissa; regex-parsintaa ei enää tarvita tekstistä.
- [x] LLM-promptissa on eksplisiittinen `<rule>` sallituista komponenteista.
- [x] Flutter piirtää synteesin ilman Markdown-kirjastoa pelkillä natiiviwidgeteillä.
- [x] PDF-generaattori rakentaa rakenteen suoraan blokkien pohjalta ilman Markdown-filtteriä.
