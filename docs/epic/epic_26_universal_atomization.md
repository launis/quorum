# Epic 26: Universal Matrix Atomization & UI Tabular Reporting

## Tavoite
Poistaa kaikki mahdollisuudet kognitiivisesti joustavien "pehmeiden mittareiden" (standardi Pydantic-tulos float/int pisteytysenä) laskentaan ja siirtää 100 % asiantuntijamatriiseista toimimaan sokealla ylhäältä alas hajautettavalla AtomFlatteningHook Map-Reduce arkkitehtuurilla. 

Lisäksi tavoitteena on saattaa loppuun UI:n forensinen audit trail: yhdistää konsolipohjaisen `lue_tulokset.py`:n matemaattinen näyttö (Tasojen 1-6 osumat per matriisi) Flutter-pohjaiseen Admin Studioon (SDUI) lopullisen raporttinäkymän häntäksi.

## Arkkitehtuuriset Muutokset
1. **Pehmeyden Poisto (PromptCompiler Deprecation):** Poistetaan `prompt_compiler.py`:stä kokonaan mahdollisuus LLM:llä generoida `step_4_final_score` -arvoja. Jatkossa pisteytys pakotetaan syntymään globaalisti ja ainoastaan `waterfall_scoring_hook`:in (sokean matemaattisen Boolen alikerroksen) kautta.
2. **Kattava Hook-injektio (Seeding):** Kaikki asiantuntijasolmut (Steps/Task Blueprints), jotka pitävät sisällään matriiseja, muutetaan `seed_data.json` tietokannassa sisältämään `atom_flattening_hook` esi-ajokseen ja `waterfall_scoring_hook` post-ajokseen.
3. **SDUI Tabular Matrix Widget (Flutter):** Luodaan uusi Widget (esim. `AtomMatrixTableWidget`), joka vastaanottaa `ScorecardControllerin` aggregoiman `level_breakdown` datan ja `true_atoms`/`total_atoms` tiedot. Taulukko esitetään PDF-raportin ja näytön viimeisenä kruununjalokivenä osoittamaan kovan tason atomianalyysi osumineen per Taso (T1-T6).

## Toteutuksen Vaiheet
*   **Phase 1:** Backend-pään standardointi tietokannalle ja skeemoille.
*   **Phase 2:** Epic 25 siivouksen ja `prompt_compiler.py` -kovettamisen loppuunvienti (estäen manuaalisen pisteytyksen).
*   **Phase 3:** Flutter SDUI Widgettien refaktorointi vastaanottamaan uudet Data Transfer Objectit.

## Lupaussopimus (SDUI Zero-Math)
Flutter-asiakasohjelma ei ikinä laske keskiarvoja eikä tulkitse Taso-osumia (Hits/Total) numeerisina lukuina, vaan ne syötetään suoraan REST API:sta muotoiltuina `String` riveinä, pitäen No-String SDUI mandatessa kiinni.
