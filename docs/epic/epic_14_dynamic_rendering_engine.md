# EPIC 14: Dynamic Rendering Engine & Separation of Concerns (Dynaaminen Tulostusmoottori)

## 1. Yleiskatsaus (Overview)
Tämän Epicin tavoitteena on rakenteellisesti erottaa toisistaan tiedon kerääminen (DAG Execution Engine) ja sen visuaalinen sekä kielellinen paketointi (Rendering Engine). Nykyinen malli ajaa LLM-synteesin suoraan työkalujen ja datan keruun yhteydessä (HookRegistryssä), mikä on token-taloudellisesti raskasta ja estää eri profiilien dynaamisen vertailun.

Tavoitteena on luoda täysin uusi **Dynaaminen Tulostusmoottori**, jossa raskaat, kielelliset LLM-synteesit generoidaan asynkronisesti "Tulostus-Workerin" toimesta vain silloin kun käyttäjä oikeasti pyytää tiettyä näkymää. 

## 2. Pääominaisuudet (Key Features)
1. **Tiedon eriyttäminen (Separation of Concerns):** DAG-moottori keskittyy jatkossa puhtaasti raakadatan hankintaan, matematiikkaan ja arviointiin tuottaen luotettavan `execution_trace` (Event Sourcing) tallenteen. Tekstien kielellinen paketointi siirtyy kokonaan Tulostus-Workerin erilliseksi asynkroniseksi prosessiksi.
2. **Profiilikohtainen Välimuisti (Per-Profile Synthesis Cache):** Yhden globaalin `synthesized_markdown` kentän sijaan ExecutionRecord päivitetään tukemaan profiilikohtaisesti välimuistitettuja tekstipaketteja (esim. `profile_syntheses: dict[str, RenderedSynthesisCache]`), estäen eri rapotointiprofiileja ylikirjoittamasta toistensa tekstejä.
3. **On-Demand Synteesien Generointi & SSE:** Mikäli UI pyytää (GET `/render?profile_id=X`) profiilia, jota ei ole vielä generoitu, Backend käynnistää uuden Tulostus-Workerin ajon ja palauttaa UI:lle indikoinnin odotusajasta.
4. **Synteesien DTO-pariteetti (Globaali & Osiokohtainen):** Globaali johdantoteksti (`synthesized_markdown`) sekä osiokohtaiset tekstit (`section_syntheses` → `ReportLayoutDTO.synthesis_md`) mapataan aidosti läpi koko arkkitehtuurin aina `BlueprintTransformer`:ista Frontendin Dart-malleihin. Tämä korjaa bugin, jossa LLM:n jo valmiiksi generoimat osiokohtaiset synteesit katoavat bittiavaruuteen ennen näytölle piirtymistä.
5. **Raportin Headerien Korjaus:** Riippumatta valituista asetuksista, `visible_metadata` -valinnat Output Profilessa eivät tällä hetkellä vaikuta UI:n tai PDF:n Header-asetteluun. Ohjelmisto pakotetaan kunnioittamaan näitä asetuksia Headerin dynaamisessa koontivaiheessa.
6. **Pisteiden Vakauttaminen (Semantic Self-Healing):** `prompt_compiler.py`:n asettamaa ankaraa `step_1_evidence_quote` -validointia pehmennetään. Nykyinen ehto pakottaa mallin alentamaan pisteitään päästäkseen Pydantic-validoinnista läpi ("or lower the score immediately"), jos sanasta sanaan menevä lainaus ei onnistu. Tämä oikoreitti poistetaan ja tilalle sallitaan vahva semanttinen perustelu.

## 3. Tekninen Toteutus & Arkkitehtuuri
* **Arkkitehtuurin Puhdistus:** `text_consolidation_hook` irrotetaan `worker.py`n orkestraattorista (DAG-lohkosta). Pää-Worker ohjeistetaan jatkossa vain päättämään työnsä kutsumalla `enqueue_job("render_profile_job", default_profile_id)`, aivan kuten se kutsui ennestään PDF-generoinnin.
* **Backend-for-Frontend (BFF) Päivitykset:** Pydantic (`backend_v2/models/v2_core.py`) ja Freezed (`client_app_v2/.../report_data_dto.dart`) -mallit päivitetään peilaamaan tarkasti toisiaan, lisäten puuttuvat kentät globaalille synteesille (`synthesized_markdown`). Etsitään ja pakotetaan BlueprintTransformer injektoimaan tämä arvo.
* **State Management (UI):** Flutter Riverpod korjataan kuuntelemaan `is_synthesis_pending` -tilaa, jolloin ohjelmisto voi renderöidä nätisti Shimmer/Loading-laatikon niihin osioihin, joihin tekstiä vasta generoidaan LLM:n toimesta. PDF ladataan taustalla samaan tapaan vasta kun synteesi on valmis.

## 4. Toteutussuunnitelma (Milestones M1-M4)

### M1: V2.9 Scoring Stabilization (Pydantic Retry Fix)
* Poistetaan `prompt_compiler.py`:n dynaamisesta `make_validator`-säännöstä haitallinen neuvo ("or lower the score immediately"), jolla malli on voinut ohittaa validoinnin pistettään laskemalla.
* Päivitetään `step_1_evidence_quote` Field-määritystä siten, että se sallii tarkan lainauksen lisäksi semanttisen perustelun (joustavoitetaan verbatim-vaatimusta sotkuisten PDF-tekstien vuoksi).

### M2: DTO Full-Stack Mapping & UI Headers
* Päivitetään `ReportDataDTO` ja `ReportLayoutDTO` (Pydantic ja Freezed) vastaamaan toisiaan siten, että `synthesized_markdown` ja osiokohtaiset `synthesis_md` -tekstit saadaan lopulta kulkeutumaan UI:lle asti.
* Siivotaan `BlueprintTransformer` reitittämään globaalit ja layout-kohtaiset synteesiarvot tallenteesta API-vastaukseen.
* Korjataan Header/Kansilehtien muodostamisongelma (`visible_metadata`), jotta se reagoi dynaamisesti Output Profilen valintoihin UI ja PDF katselussa.

### M3: Database Cache Restructuring
* Päivitetään DB Schemat (`v2_core.py` -> `ExecutionRecord`) ottamaan vastaan välimuistimainen, moniprofiilinen tallennuslogiikka synteeseille (säännölliset Opaque Stripe ID:t `prf_...` avaimina teksteille).

### M4: The Print-Worker Extraction (Render Job)
* Reititetään LLM koodi (`text_consolidation_hook`) ja Asynkroninen työ uuteen `generate_profile_synthesis_and_pdf` funktioon.
* Rakennetaan Controller-rajapintaan mekanismi, joka tulosteen hakemisen (GET) sijaan kykenee reagoimaan tyhjiin synteesi-viiksiin käynnistämällä uuden renderöintityön automaattisesti taustalla. 
