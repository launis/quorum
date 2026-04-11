# Phase 3: Runtime-ajon valmistelu (Rakenteellinen Silppuaminen)

## Objective
Luodaan työnkulun "RunTime" -vaiheen valmisteleva pre-hook tai input processing -logiikka, joka "litistää" (flatten) tietokantaan lukitun 75-atomikysymyksen matriisin sokeaksi yksitasoiseksi luetteloksi ja sekoittaa kysymykset satunnaisesti.

## TARGET (Modify)
- `backend_v2/hooks/input_processing.py` (tai uusi `pre_hook` dedikoitu silppuamiseen)
- `backend_v2/services/orchestrator/dag_executor.py` (jos vaatii suoran HookState manipuloinnin ennen promptien lähettämistä)

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py` (Atomien ja matriisien lukeminen HookStatesta)
- `backend_v2/core/hook_registry.py`

## Architectural Constraints (V2 Sequence)
1. **Pydantic Models:** HookState:a prosessoidaan HookResult-olioiden palauttamalla `state_delta` muuttujalla, itse päätila on Pydantic `frozen=True` -tilassa eikä sitä voi mutatoida suoraan.
2. **Deterministic Processing:** `random.shuffle()` pitää olla ennakoitavissa logeissa tai sille seedataan vakioarvo suorituksen (`execution_id`) perusteella forensisen uudelleenajon tueksi.

## Design / Implementation specifics
* Järjestelmä lukee kaikki tähän askeliin assosioidut atoomit.
* Se rakentaa listan kysymyksiä, missä kukin kysymys on muotoa `{"atom_id": "xyz", "question": "..."}` ja sekoittaa ne.
* Tämä riisuttu lista toimitetaan DAG-moottorin seuraavalle vaiheelle sokeaan skannaukseen. Alkuperäinen konteksti ja 5-portaisen tason assosiaatio pidetään piilossa.

## Verification & Quality Gate Plan
* Yksikkötestit hookille, validoiden että palautettu HookResult.state_delta on oikein sekoitettu mutta riisuttu lista alkuperäisestä datasta, ja että ID:t eivät ole hukassa.
* Komento: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/input_processing.py --test`
