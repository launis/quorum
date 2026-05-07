# Epic 49: Output Profile & Dynamic Reporting Enhancements

## Kohde ja Laajuus (Scope & Objectives)
Käyttäjän toiveena on laajentaa ja tarkentaa tulostettavien raporttien metatietoja, otsikoita sekä asettelua. Keskeisimmät tavoitteet ovat:
1. **Identity Metadata**: Mahdollistaa päivämäärän (paikallista aikaa muodossa `vvvv kk pv hh:mm`), organisaation ja käyttäjänimen dynaaminen valinta tulostusprofiilista. Konteksti poistetaan kokonaan tai piilotetaan oletuksena.
2. **Mukautettava Selite (Custom Preface)**: Tulostusnäytöltä annettava rich text -selite, joka renderöidään PDF-raportin alkuun.
3. **Dynaamiset Otsikot ja Sarakkeet**: Raportin otsikot (esim. "YHTEENVETO / MATRIX SUMMARY") ja matriisitaulukon näytettävät sarakkeet tehdään dynaamisesti valittaviksi Admin Studiossa.
4. **Terminologian ja Kuvausten Päivitys**: Järjestelmän matriisien ja arviointien otsikoiden muuttaminen käyttäjäystävällisiksi sekä selitteiden lisääminen näkyviin arviointitaulukkoon (esim. `seed_data.json` ja `.arb` tiedostot). Monikielisyys (I18nText) varmistetaan kaikkialla periaatteella **English First**.
5. **PDF ja UI Pariteetti**: "Zero-Math" UI:n ja PDF:n yhdenmukaistaminen uusien dynaamisten termien ja sarakkeiden osalta.

## Arkkitehtuuriset Rajoitteet (Architectural Constraints)
*   **Fail-Fast Pydantic V2**: Jos uusia kenttiä lisätään (esim. `user_name`, `custom_preface`, `visible_columns`), niiden tulee olla tiukasti tyypitettyjä DTO-kerroksessa.
*   **No-String Mandate & English First**: Kaikki Frontend-UI:n uudet tekstit on vietävä `.arb` käännöstiedostoihin (ensin `en`, sitten `fi`). Backendin dynaamiset arvot asuvat `seed_data.json` Single-Source-of-Truth -tiedostossa, ja jokaisessa `I18nText` -objektissa on oltava englanti ensimmäisenä oletuskielenä.
*   **Zero-Math UI**: Ajan konversio lokaaliksi ajaksi tulee joko hoitaa Frontendissä tai Backendissä deterministisesti. Koska palvelin toimii UTC-ajassa, luotettavin tapa on antaa Frontendin lähettää haluttu paikallisen ajan aikaleima merkkijonona (esim. `local_time_str`) tulostuspyynnön mukana.

---

## Vaihe 1: Domain & Backend Pydantic (Identity Metadata & Preface)
**Tiedostot:**
- `backend_v2/models/dtos/output_profile.py`
- `backend_v2/models/v2_core.py`
- `backend_v2/api/routers/render.py`

**Tehtävät:**
1. Päivitä `OutputProfileCreateDTO`, `OutputProfileUpdateDTO` ja `EmbeddedOutputProfile` sallimaan kenttä `"user"` `visible_metadata` -listassa, ja muuta oletuslistaksi `["date", "organization", "user"]`.
2. Lisää `OutputLayoutBlock` -malliin uusi ominaisuus: `visible_columns: list[str] = Field(default_factory=lambda: ["label", "score", "distribution"])`, jotta PDF:n ja UI:n matriisitaulukon sarakkeet voidaan valita dynaamisesti.
3. Lisää `ReportDataDTO` -luokkaan kentät:
   - `user_name: str | None = None`
   - `local_time_str: str | None = None` (jotta vältämme UTC-Jinja2 -aikaongelmat)
   - `custom_preface_md: str | None = None`
4. Päivitä `ExecutionService` / `/executions/{id}/render` endpoint vastaanottamaan uudet valinnaiset query-parametrit (esim. `?custom_preface_md=...&local_time_str=...`), jotka ruiskutetaan suoraan `ReportDataDTO`:hon PDF-renderöintiä varten.

## Vaihe 2: Frontend UI - Tulostusikkuna ja Output Profile CRUD
**Tiedostot:**
- `client_app_v2/lib/features/studio/views/output_profile_crud_view.dart`
- `client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart`
- `client_app_v2/lib/features/executions/views/execution_render_view.dart`

**Tehtävät:**
1. Lisää Admin Studioon (`OutputProfileCrudView`) CheckboxListTile uudelle Identity Metadata -kentälle: `Käyttäjä (user)`.
2. Lisää Layout Editoriin (`layout_editor_card.dart`) mahdollisuus valita näytettävät sarakkeet (`visible_columns`).
3. Luo loppukäyttäjän renderöintinäkymään (tulostusnäyttöön) dialogi, jossa käyttäjä voi syöttää "Selitteen" (Rich text / Markdown) ennen PDF-generoinnin käynnistämistä.
4. Välitä tämä teksti API-kutsussa backendille. Generoi myös `local_time_str` Dartissa muotoon `yyyy kk pv hh:mm` ja lähetä pyynnön mukana.

## Vaihe 3: Tietokannan (SSOT) Terminologian Päivitys (English First)
**Tiedostot:**
- `backend_v2/seed/seed_data.json`

**Tehtävät:**
1. Muuta matriisien ja PromptBlockien `label` ja `description` -kentät annettujen vaatimusten mukaisiksi, varmistaen "English First" I18nText-rakenteissa. Esimerkiksi:
   - "Turvallisuus- ja Etiikkasuodatin" -> `label`: `{"en": "Responsibility", "fi": "Vastuullisuus"}`, `description`: `{"en": "Ensures...", "fi": "Varmistaa, ettei tekoälyä käytetä tavalla, joka tuottaa perusteetonta tai riskialtista tietoa."}`
   - (Tee sama kaikille annetuille avaimille: Harkintakyky, Oman tiedon rajat, Päättelyn rehellisyys jne.)
2. Muuta Output Profile -mallien otsikot I18nText-muodossa:
   - "Globaali johdon yhteenveto" -> `{"en": "AI Utilization Summary", "fi": "Yhteenveto tekoälyn hyödyntämisestä"}`
3. Varmista, että nämä on muutettu sekä `prompt_blocks` arrayn että `workflows` -> `output_profiles` sisällä olevista rakenteista.
4. Päivitä profiilien `layouts`-blokkeihin dynaaminen otsikko `title`, korvaten kovakoodatun "YHTEENVETO / MATRIX SUMMARY" dynaamisella `{"en": "DETAILED SCORING MATRIX", "fi": "ARVIOINNIN YKSITYISKOHTAINEN PISTEYTYS"}`.

## Vaihe 4: PDF & SDUI Renderöintipohjien Päivitys (Jinja2 & Arb)
**Tiedostot:**
- `backend_v2/templates/report_template.jinja2`
- `client_app_v2/lib/l10n/app_fi.arb` & `app_en.arb`

**Tehtävät:**
1. Poista PDF-pohjasta kovakoodatut kentät "YHTEENVETO / MATRIX SUMMARY" ja ota käyttöön layout-blokin dynaaminen `title`.
2. Etsi kovakoodattu "Logiikkamatriisi" ja ota I18nText tai Arb-käännös dynaamisesti käyttöön ("Osaamisen osa-alueet").
3. Varmista, että PDF ja Flutter UI renderöivät vain ne taulukkosarakkeet, jotka on määritetty layoutin `visible_columns` -listassa.
4. Päivitä Jinja2-templaten `Kannen metatiedot` (Identity Metadata) osio:
   - Poista/piilota `Konteksti` renderöinti.
   - Ota käyttöön `dto.user_name`, jos `user` on `visible_metadata` listassa.
   - Vaihda aiempi UTC `dto.created_at` renderöitymään suoraan `dto.local_time_str` arvosta.
5. Renderöi `custom_preface_md` (selite) raportin alkuun tyylikkäässä Rich Text (HTML) laatikossa/osiossa.
6. Varmista, että matriisien `description` tulostetaan PDF:n taulukossa tai matriisiotsikoiden yhteydessä käyttäjän toivomalla tavalla.

## Suoritusohje
Kun hyväksyt tämän suunnitelman, voimme siirtyä vaiheeseen 1 käyttämällä `/tier2-execute` komentoa. Suoritan vaiheet tarkan atomisesti pyytäen sinulta aina hyväksynnän ja git commitin välissä.
