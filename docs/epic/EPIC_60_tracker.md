# Epic 60 Tracker: System 2 Reliability Audit

## 1. Konteksti ja Tavoitteet (Miksi olemme tässä?)
Järjestelmän LLM-evaluointimoottorissa (System 2) havaittiin merkittävää epävakautta ja varianssia peräkkäisissä ajoissa täysin identtisillä syötteillä (Self-Consistency 78-80 %). Tämä arpominen johtui arkkitehtuuritason rakenteellisista virheistä (kuten `ExtractionPayload` vs `exact_quotes` -bugeista), käänteisistä logiikoista ja epäselvistä kognitiivisista säännöistä. 
**Tavoitteemme** on toteuttaa 100 % Pydantic-tyyppiturvallinen konsensusarkkitehtuuri ja deterministinen korjausluuppi. Tämä poistaa arvailun (dict.get) ja nostaa arviointien itsekonsistenssin matemaattisesti stabiilille tasolle.

## 2. Mitä on tapahtunut?
Edellisessä sessiossa (Tier 1 Planner) laaja Epic 60 auditoitiin ja pilkottiin neljään toteutussuunnitelmaan (Implementation Plan):
1. Enum-siivous ja Retryjen yhtenäistäminen.
2. Konsensus-arkkitehtuurin Pydantic-refaktorointi (kriittiset bugikorjaukset).
3. Self-Healing -optimointi (Pydantic-kireystasojen täsmentäminen mallille).
4. Kognitiivisten TDA-sääntöjen siementäminen tietokantaan.

Käyttäjä ajoi tämän jatkuvan suorituksen käynnistävän komennon: `/tier5-resume --target docs/epic/epic_60_tracker.md` ja pyysi täydentämään kontekstin myös tähän seurantaan.

## 3. Implementation Plans (Jatkuva Suoritus)

- [x] `c:\src\quorum\docs\epic\tasks_epic_60\phase1_enum_cleanup.md` - Enum Cleanup and Retry Unification (ACTION-7)
- [x] `c:\src\quorum\docs\epic\tasks_epic_60\phase2_chunk_worker_refactor.md` - Consensus Architecture Refactor (ACTION-1, ACTION-5, ACTION-6)
- [x] `c:\src\quorum\docs\epic\tasks_epic_60\phase3_prompt_compiler.md` - Self-Healing Optimization (ACTION-2)
- [x] `c:\src\quorum\docs\epic\tasks_epic_60\phase4_seed_database.md` - Seed Corrected Rules (ACTION-3)

## 4. Tila ja Seuraavat Vaiheet

**TEHTY:** Phase 4 tietokantasiemennys suoritettu. ChunkWorkerin ExceptionGroup -käsittely korjattu (Fail-Fast toimii). Rate-limit-testit ohitettu mock-providerilla. Myös ENSEMBLE-ajon kohtalokas Pydantic extra_forbidden -bugi on löydetty ja korjattu puhtaasti sanakirja-injektiolla. Uutena lisäyksenä: Tier 4 Bug Hunting -tutkinta ratkaisi finaaliajon kaataneen `reasoning_steps` "Field missing" -Pydantic ValidationError -ongelman poistamalla virheelliset pop-kutsut `chunk_worker.py` -tiedostosta. Kaikki yksikkötestit menivät läpi (100% vihreä) ja ydinarkkitehtuuri on eheytynyt.

**SEURAAVAKSI:** Käyttäjä on aloittamassa raskaat manuaaliset testiajot `run_local.bat` avulla luodakseen dataa diff-raporttia varten. Järjestelmä on nyt odotustilassa. Käyttäjä komentaa `/tier6-execution-monitor` manuaalisesti ajojen alettua, jonka jälkeen asetumme valvomaan logeja. Ajojen päätyttyä tulokset analysoidaan käyttäen `c:\src\quorum\scratch\diff_executions.py` -skriptiä.
