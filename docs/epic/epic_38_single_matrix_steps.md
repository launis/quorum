# EPIC 38: 1:1 Matrix-to-Step Architectural Enforcement (Micro-Steps)

**Status:** BACKLOG
**Objective:** Palautetaan alkuperäinen arkkitehtuurinen tarkoitus: Jokaisella Workflow-stepillä saa olla tasan yksi (1) matriisi arvioitavanaan. Puretaan nykyinen "Monoliitti-Analyst", joka arvioi 13 matriisia samanaikaisesti.

## Arkkitehtuurinen Pohdinta & Ongelmat
Tällä hetkellä järjestelmän Workflow-konfiguraatio (`seed_data.json`) on ajautunut tilaan, jossa kymmeniä PromptBlock-matriiseja on niputettu yhden ainoan suoritusaskeleen (esim. `Analyst`) taakse.

**Tämän aiheuttamat ongelmat:**
1. **Persona Dilution (Persoonan laimeneminen):** Tekoäly joutuu käyttämään yhtä ja samaa "Analyst"-yleispromptia arvioidakseen 13 täysin erilaista viitekehystä (esim. Toulmin, Bloom, Goodhart). Arkkitehtuurinen tarkoitus oli, että jokaisella viitekehyksellä on oma spesifi "asiantuntijansa" (esim. Toulmin -> Logician).
2. **Käyttökokemus (Observability):** Käyttöliittymässä (Cognitive Studio) näkyy vain yksi "Analyst"-steppi, joka pyörii kymmeniä minuutteja. Käyttäjä ei tiedä, mitä matriisia kone juuri nyt pureskelee.
3. **Modulaarisuuden rikkoutuminen:** Jos käyttäjä haluaa luoda kevyen Workflow'n, jossa on vain Toulmin ja Bloom, se on mahdotonta, jos ne on koodattu kiinteästi kiinni raskaaseen Analyst-steppiin muiden mukana.

**Ratkaisu (1:1 Micro-Steps):**
Kun jokaisella stepillä on vain yksi matriisi:
- **Täydellinen eristys:** System Prompt voidaan hienosäätää tismalleen tuolle yhdelle matriisille. (Zero-Prompt-Leakage).
- **Rinnakkaissuoritus (Concurrency):** Riippumattomat matriisi-stepit voidaan ajaa rinnakkain (Async), mikä pudottaa kymmenien minuuttien ajoajan murto-osaan!
- **Granulaarinen UI:** Käyttäjä näkee käyttöliittymästä tarkasti: "Toulmin Analysis... Done. Bloom's Taxonomy... Running."

## Toteutussuunnitelma (Implementation Plan)

### Vaihe 1: Datan Pilkkominen (`seed_data.json`)
- [ ] Etsi nykyiset raskaat stepit (esim. `Analyst`, `block_role_analyst`).
- [ ] Luo uudet spesifit stepit jokaista olemassa olevaa matriisia kohden (esim. `Step_Toulmin`, `Step_Bloom`, `Step_Goodhart`).
- [ ] Määritä kunkin stepin `dependencies` -listaan vain ja ainoastaan kyseinen yksi matriisi.
- [ ] Päivitä Workflow-määrittelyt (`workflows` taulu/määrittelyt) kutsumaan näitä uusia micro-steppejä peräkkäin (tai rinnakkain).

### Vaihe 2: Validointi ja UI
- [ ] Varmista `AtomFlatteningHook` -logiikasta, ettei se hajoa, vaikka sille annetaan vain yhden matriisin atomit kerrallaan (pienemmät chunk-määrät).
- [ ] Varmista, että Client App UI (Flutter) kestää visuaalisesti sen, että steppejä on listassa enemmän (scrollaava lista aktiivisista suorituksista).

## Riippuvuudet
- Vaatii koko tietokannan / siemendatan uudelleenluonnin (Epic 3 Database Reset -workflow).
