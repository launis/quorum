# Implementation Plan: Blind Extraction Doctrine (V4.3)

**Tavoite:** Nollata 19,6 % haamuvarianssi poistamalla LLM:ltä kognitiivinen tuomiovalta. Siirrämme mallin roolin Tuomarista Sokeaksi Poimijaksi (Blind Extraction Engine) menettämättä Chain of Thought -kyvykkyyttä.

**Arkkitehtuuriset Mandaatit:**
1. **ACCEPT/REJECT -täyskielto & Pydantic-aggregaatio:** LLM palauttaa vain `mechanical_trace` ja `exact_quote`. Pydantic-backend päättelee kooditasolla säännön täyttymisen.
2. **Kognitiivisen Kitkan Pelastus (TRACE REQUIREMENT):** Vanhat arviointiohjeet siirretään suoraan `mechanical_trace` -vaatimuksiksi.
3. **Kielimuurin Ohitus ja STRICT FIT:** Ankkurit käännetään kohdekielelle lennosta. Tekstin on täytettävä ehto fyysisesti – jos asiaa joutuu rationalisoimaan (puolustusasianajaja-ilmiö), osuma hylätään.

---

## Vaihe 1: Datan Refaktorointi (Zero-Interpretation Injektio)
Käytämme täsmätyökalua (`scratch/v4_3_evidence_refactor.py`), joka säilyttää liiketoimintalogiikan mutta pakottaa rikostutkija-formaatin koko tietokantaan.

1. **Skriptin Logiikka (`seed_data.json`):**
   * Muuntaa `If [X] -> ACCEPT` muotoon `EXTRACTION CONDITION: [X]`.
   * Muuntaa `If [Y] -> REJECT` muotoon `NEGATIVE CONDITION (RETURN NULL IF MET): [Y]`.
   * Muuntaa `ENFORCEMENT RULE` muotoon `TRACE REQUIREMENT: In mechanical_trace...`.
   * Päivittää makrotason (PromptBlock/Scale) System Directivet (korvaa Evaluate -> Extract ja kieltää Null Hypothesiksen rationalisoinnin).

2. **Suoritus ja Tietokannan Seeding:**
   * Ajetaan refaktorointiskripti: `uv run python scratch/v4_3_evidence_refactor.py`
   * Pyyhitään vanha tietokanta ja ladataan uudet säännöt lokaaliin TinyDB-kantaan: `uv run python backend_v2/seed/run_seed.py local`.
   * *(Kriittistä: ilman tätä uudet säännöt eivät tule voimaan backendissä.)*

## Vaihe 2: Arkkitehtuurin Rakenteellinen Sulkeminen (Backend)
1. Päivitetään LLM:n Pydantic ResponseFormat (`backend_v2`):
   * Poistetaan kentät `rule_satisfied` ja `mapped_state` mallin tuottamasta output-rajapinnasta.
   * Pakotetaan LLM palauttamaan vain `mechanical_trace` ja `exact_quote`.
2. **Pydantic Turvaportti (Phantom Boolean -esto):**
   * Estetään LLM-hallusinaatiot, joissa malli vuotaa merkkijonoja kuten `"null"`, `"N/A"`, tai `"Ei löydy"`.
   * Lisätään `@computed_field evidence_found` varustettuna sanitoinnilla: jos `exact_quote.strip().lower()` on listalla `["null", "none", "n/a", "false", "", "ei löydy", "not found", "-", "ei mainittu", "none detected", "[]", "{}", "ei sovelleta", "ei lainausta", "no quote", "ei ole"]`, se tulkitaan arvoon `False`.
3. Arvioinnin laskenta siirretään Python-funktiolle `calculate_rule_satisfied(inverse_evidence)`, joka on 100 % deterministinen.

## Vaihe 3: Quality Gate ja Backend Audit
Muutosten jälkeen koodin ja tietokannan eheys on taattava. Järjestelmä ei saa kaatua.
1. Ajetaan `uv run python scratch/verify_claims.py` varmistamaan JSONin struktuuri.
2. Ajetaan datan arkkitehtuuritestit ja matriisien eheystarkistukset suoraan pytestillä: 
   `uv run pytest backend_v2/tests/unit/test_seed_architectural_guardrails.py backend_v2/tests/unit/test_matrix_data_integrity.py -v`
3. Suoritetaan koodimuutoksille lopullinen koodin laatuportti: 
   `uv run python scripts\backend_audit_loop.py backend_v2/ --test --openapi`

## Vaihe 4: Varianssin Todentaminen (0 % Tavoite)
1. Kun kanta ja backend on puhdistettu V4.3-tasolle, ajetaan testit samalla datalla kahdesti uudelleen.
2. Ajetaan robusti `scratch/diff_executions.py`.
3. **Hyväksymiskriteeri (DoD):** Mismatch-laskuri näyttää 0. LLM on toiminut erehtymättömänä poimijana ja Pydantic aukottomana tuomarina.
