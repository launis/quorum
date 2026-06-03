# Epic: Gemini 2.5 Pro Context Caching & Theory Grounding

## Tavoite
Aktivoida Google Vertex AI:n Context Caching (-75 % kustannussäästö API-kuluihin) Quorumin matriisiajoissa Gemini 2.5 Pro -mallilla. Tämä saavutetaan keräämällä ja injektoimalla työnkulun tieteelliset teoriat (`theory_grounding`) muuttumattomaksi staattiseksi koodilohkoksi promptin alkuun, jotta Googlen 32 768 tokenin minimiraja ylittyy taatusti.

## Tausta
Quorumin nykyiset rinnakkaiset matriisisteppien ajot (esim. 15-30 steppiä) jäävät juuri välimuistirajan alle (n. 25 000 tokenia), jolloin jokainen API-kutsu maksaa täyden hinnan (n. 0,70 $ - 1,30 $ per steppi, johtuen kalliista $5.00/1M output-tokeneista). Nostamalla alkupromptin painoa teoriatiedolla ylitämme 32k tokenin rajan ja saamme rinnakkaiset kutsut lukemaan staattisen osan välimuistista.

## Kustannuslaskelma (Gemini 2.5 Pro)
- **Nykytila:** 15 steppiä ilman välimuistia maksaa n. 7,50 $ - 8,00 $.
- **Tavoitetila:** 15 steppiä välimuistilla maksaa n. 4,60 $ (säästö 40-50 %). Laatu paranee, koska malli saa eksplisiittiset teoriadokumentit (esim. Toulminin argumentaatiomalli) hallusinoinnin sijaan.

## Vaiheistus (Phases)

### Phase 1: Paikallisen teoriatietokannan luonti (Theory Repository)
1. **Lokaali hakemisto:** Luodaan `c:\src\quorum\data\theories\` (tai vastaava), johon tallennetaan staattisia `.md` -tiedostoja akateemisista teorioista.
2. **Kartoitus:** Yhdistetään matriisien `citation_reference` näihin lokaaleihin tiedostoihin (esim. `Toulmin, Stephen E. 2003` -> `toulmin_argumentation.md`).
3. **Täytedokumentti:** Luodaan "Academic Baseline" -dokumentti, joka ladataan mukaan aina, jos valittujen teorioiden token-määrä ei yksin riitä rikkomaan 32 768 tokenin rajaa.

### Phase 2: Theory Fetcher -palvelu
1. **Uusi palvelu:** Luodaan `backend_v2/services/orchestrator/theory_fetcher.py`.
2. **Logiikka:** Palvelu lukee tulevan työnkulun (Workflow) askeleet, poimii uniikit `citation_reference` -arvot, hakee vastaavat tekstit ja palauttaa massiivisen `<GLOBAL_THEORY_GROUNDING>` XML-blokin.

### Phase 3: Prompt Compiler -integraatio (Prompt Segregation)
1. **Päivitys:** Muokataan `backend_v2/services/orchestrator/prompt_compiler_adapter.py`.
2. **Injektointi:** Lisätään kerätty `global_theory_block` välittömästi `base_system_prompt` tai `system_content` -kärkeen niin, että se on sataprosenttisen staattinen jokaiselle matriisin askeleelle.

### Phase 4: Moottorin (Engine) päivitys
1. **Suoritus:** Muokataan työnkulun moottoria (`backend_v2/services/orchestrator/strategies/llm.py` / `engine.py`), jotta se kutsuu Theory Fetcheriä ennen kuin jakaa askeleet rinnakkaisiin taskeihin (Isolate/Async).
2. **Säästö:** Varmistetaan, että globaali konteksti (`frozen_ctx`) sisältää tuon teoriablokin.

## Avoinna olevat kysymykset / Arkkitehtuuripäätökset
- Missä muodossa ja kuka tuottaa nuo akateemiset "täytetekstit" (Markdown, PDF, vector DB)? Aloitammeko staattisilla Markdown-tiedostoilla `data/theories/` -kansiossa?
- Halutaanko matriiseista (`precise`, `strict`, `deep`) siirtää tiettyjä mekaanisia rutiineja Flash-malliin kustannusten optimoimiseksi vielä pidemmälle?

## Seuraavat askeleet
Kun tämä Epic on hyväksytty, voidaan ajaa komento `/tier1-planner` tämän dokumentin osoitteeseen, jolloin Antigravity purkaa nämä vaiheet askeleen kokoisiin `implementation_plan.md` -suorituksiin.
