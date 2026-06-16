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

1. **Flat Architecture:** Rekursiiviset komponentit ovat ehdottomasti kiellettyjä. Yksikään blokkityyppi ei saa sisältää toista `list[UIBlockDTO]` -kenttää. Kaikki blokit ovat terminaalisia primitiivejä samassa tasalistassa.
2. **Zero-Trust Validation:** Kaikkien Pydantic-mallien (blokkien) on käytettävä asetusta `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")`.
3. **Rakenteelliset viittaukset (Citations):** Lähdeviittaukset on käsiteltävä blokkitason strukturoituna datana (`citations: list[int]`), ei tekstin sisäisinä inline-merkintöinä (esim. `[1]`). Frontend ei saa käyttää Regex-parsintaa.

## 3. Toteutusvaiheet (Implementation Plan)

### Vaihe 1: Backend Pydantic SDUI -mallit ja Vertex AI "Fat Object" Pattern
**Tiedosto:** `backend_v2/models/dtos/sdui_components.py` (ja mallien päivitykset)
- Luo uusi tiedosto polymorfisille UI-komponenteille.
- **Kriittinen Rajoite (Vertex AI 400 Bad Request):** Google Vertex AI Structured Outputs ei tue JSON Scheman `anyOf` tai `oneOf` -rakenteita. Jos LLM:lle lähetetään Pydanticin Discriminated Union suoraan, API kaatuu 400-virheeseen.
- **Toteutus (LLM-rajapinta & Structured Retry):** LLM-promptille ja Vertex AI:lle luodaan litteä "Fat Object" -malli (esim. `UIBlockPromptDTO`), jossa kentät ovat valinnaisia (`Optional`). **Kriittinen lisäys:** Fat Objectiin on lisättävä Python-tason `@model_validator(mode="after")`. Jos LLM asettaa esim. `block_type="bullet_list"`, mutta unohtaa valinnaisen `items`-kentän, validaattorin on nostettava hallittu `ValueError`. Tämä laukaisee LLM-clientin (esim. Instructor/Marvin) automaattisen **Structured Retry** -luupin, joka syöttää virheilmoituksen tekoälylle ja käskee korjaamaan JSON-rakenteen lennosta (Self-Healing).
- **Toteutus (Sisäiset Mallit):** Sisäisessä arkkitehtuurissa ja tietokantamalleissa pidetään tiukat polymorfiset blokit:
  - `ParagraphBlock` (`block_type: Literal["paragraph"]`, `text: str`, `citations: list[int]`)
  - `BulletListBlock` (`block_type: Literal["bullet_list"]`, `items: list[BulletListItem]`)
  - `AlertBlock` (`block_type: Literal["alert_box"]`, `severity: Literal["info", "warning"]`, `text: str`, `citations: list[int]`)
- Luo sisäinen O(1) union-tyyppi (Rule 96): `UIBlockDTO = Annotated[ParagraphBlock | BulletListBlock | AlertBlock, Field(discriminator="block_type")]`.
- **Konversio ja DLQ-kaatumisen Esto (Viimeinen Turvaverkko):** Jos malli ei korjaa virhettään maksimi-retryjen jälkeenkään, backend parseroi palautuneen listan tiukaksi `list[UIBlockDTO]` -rakenteeksi iteroimalla blokit yksitellen `try-except` -lohkossa. Jos blokki yhä hajoaa validointiin (esim. puuttuva kenttä), se pudotetaan hiljaisesti (Drop) tai korvataan `AppErrorBoundary` -varoitusblokilla (Graceful Degradation). Tämä pelastaa loppusynteesin DLQ-kaatumiselta.

### Vaihe 2: Synteesipromptien päivitys
**Tiedostot:** `synthesis.py`
- Päivitä LLM-kutsu palauttamaan uuden Pydantic-skeeman mukainen rakenne (Structured Outputs).
- Lisää system_promptiin tiukka ja selkeä XML-ohje (`<rule>`-elementti), joka ohjaa synteesiä:
  - Luettele sallitut `block_type`-arvot (exhaustively).
  - Kiellä rekursio, sisäkkäiset blokit ja Markdown-syntaksin käyttö tekstikentissä.
  - Ohjeista asettamaan lähdeviittaukset `citations`-kenttään (1-indeksoituna) tekstin sisään kirjoittamisen sijaan.

### Vaihe 3: PDF-moottorin päivitys
**Tiedostot:** `pdf_generator.py`, `report_template.jinja2`
- Poista synteesiin kohdistuva `markdown`-filtteri (`| md | safe`) PDF-templatesta.
- Päivitä template iteroimaan `content_blocks`-listaa ja renderöimään HTML-elementit (`<p>`, `<ul>`, `<div class="alert">`) blokkityypin mukaisesti. Lähdeviittaukset renderöidään suoraan `citations`-listasta.

### Vaihe 4: Flutter-clientin refaktorointi
**Tiedostot:** Dart DTO -mallit, käyttöliittymän renderöintikomponentit
- Päivitä Flutterin Dart DTO:t vastaamaan backendin uutta `content_blocks` -listarakennetta.
- Korvaa olemassa oleva vapaamuotoinen `MarkdownWidget` uudella `SDUIBlockRenderer` -komponentilla.
- Renderöi natiivit Flutter-widgetit (`Text`, `Column`, `Container`) kunkin blokin tyypin mukaisesti. Lähdeviittaukset renderöidään esimerkiksi natiiveina badgeina kappaleen perässä.
- Legacy Markdown -tukea **ei** tarvitse implementoida taaksepäin yhteensopivuuden vuoksi.

### Vaihe 5: Formaattiagnostinen Validaatio ja Spatiaalinen Ankkurointi (Track A)
**Tiedostot:** `chunk_worker.py` (tai missä `evaluate_extraction` sijaitsee)
- Kun syötteet muuttuvat SDUI-blokeiksi vapaan Markdownin sijaan, LLM saattaa poimia lainauksia, joissa välimerkit tai asettelu poikkeavat alkuperäisestä Markdown-rakenteesta (esim. taulukkojen solut).
- **Kriittinen Rajoite (Spatiaalinen Ankkurointi):** Lähdetekstiä **EI SAA** mutatoida (esim. `strip()` tai poistaa välimerkkejä fyysisesti muistista), koska se tuhoaa alkuperäiset indeksit. Frontend (Flutter/PDF) tarvitsee tarkat `start_index` ja `end_index` osoittaakseen koskemattomaan raakatekstiin korostuksia (highlight) varten. Stripatun tekstin indeksit aiheuttaisivat UI:n kaatumisen tai väärien sanojen korostumisen.
- **Toteutus ja ReDoS/Injektio-suojaus:** Muunna LLM:n palauttama `exact_quote` sallivaksi säännölliseksi lausekkeeksi (Regex) seuraavasti: 
  1. Jaa `exact_quote` erillisiksi sanoiksi. 
  2. Suojaa (escape) jokainen sana erikseen (`re.escape(word)`), jotta tekstin sisältämät erikoismerkit (esim. `(`, `?`, `+`) eivät riko Regex-moottoria ja kaada Worker-prosessia. 
  3. Yhdistä sanat joustavalla, mutta **rajatulla** välimerkkikuviolla, esim. `[\s\W]{1,50}`. Älä koskaan käytä rajoittamatonta tähtioperaattoria (`*`) pitkissä teksteissä välttääksesi katastrofaalisen perääntymisen (ReDoS - jumitukset). 
  4. Aja rakennettu turvallinen Regex alkuperäistä, *koskematonta* `source_text` -merkkijonoa vasten käyttäen `re.finditer()`. Näin mätsäys kestää formaattivaihtelut ja erikoismerkit turvallisesti, ja palauttaa oikeat indeksit.

## 4. Riippuvuudet
- **Blocker:** "Structured Prompting" -epicin `const -> enum` -kääntäjä (`client.py` tai vastaava) on oltava implementoituna. Google Vertex AI ei tue Pydanticin `Literal`-tyypin generoimaa JSON Schemaa lennossa ilman tätä käännöstä.

## 5. Menestyskriteerit (Definition of Done)
- [ ] Backend tuottaa synteesit litteänä `content_blocks` -listana vapaamuotoisen Markdownin sijaan.
- [ ] Pydantic-malleissa on käytössä `extra="forbid"` sekä unionin O(1)-diskriminaattori (`block_type`).
- [ ] Yksikään blokkityyppi ei ole rekursiivinen (Flat Architecture -mandaatti toteutuu).
- [ ] Lähdeviittaukset ovat `citations`-listoissa; regex-parsintaa ei enää tarvita tekstistä.
- [ ] LLM-promptissa on eksplisiittinen `<rule>` sallituista komponenteista.
- [ ] Flutter piirtää synteesin ilman Markdown-kirjastoa pelkillä natiiviwidgeteillä.
- [ ] PDF-generaattori rakentaa rakenteen suoraan blokkien pohjalta ilman Markdown-filtteriä.
