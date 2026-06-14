# Epic Execution Consistency Tracker

Tämä dokumentti ohjaa ajojen epäjohdonmukaisuuksien (Variance 38%) juurisyiden iteratiivista korjaamista. Tavoitteena laskea varianssi alle 10% ja nostaa Cohen's Kappa yli 0.80.

## Tehtävät (Docs/Epic/Tasks_Execution_Consistency)

- [x] **P0: Contextual Override -siivous (Seed Vault)**
  - Tiedosto: `task_P0_contextual_override.md`
  - Kuvaus: Poistetaan "Do not evaluate" ja tyhjät TDA:t tietokannasta.
- [x] **P1: Schema Purity Mandate & Clean Slate Retries**
  - Tiedosto: `task_P1_schema_purity.md`
  - Kuvaus: Pydantic Strict Mode, kielto keksiä uusia kenttiä promptissa, puhtaan pöydän retryt.
- [x] **P2: Seed Vault Broken Atoms -siivous**
  - Tiedosto: `task_P2_seed_vault_audit.md`
  - Kuvaus: Tyhjien ja alimittaisten `extraction_rule` -sääntöjen korjaus/poisto.
- [x] **P3: Dual Negation Hazard (Code-as-a-Judge)**
  - Tiedosto: `task_P3_dual_negation.md`
  - Kuvaus: Inverse-logiikan poisto promptista, siirto puhtaasti backendin immuuttiin flippaukseen.
- [x] **P4: Atom-to-Rule Mapping & Sokea DTO** (Status: VERIFIED)
  - Laajennettu `FlattenedAtom`-skeema pitämään sisällään lähdesäännöt ja niihin liittyvät metatiedot
  - `localization_compiler.py`:ssä toteutettu logiikka rubriikkien rajaamiseksi vain tiettyyn atomin iteraatioon
  - `ChunkWorker`-tasolla ajettu "sokea" DTO-projektio ilman ympäröivää hälyä
  - MagicMockien turvallinen käsittely ChunkWorkerissa (Testit läpi)
- [x] **P5: Retry-logiikan vahvistus**
  - Tiedosto: `task_P5_retry_logic.md`
  - Kuvaus: `FAIL_FAST_MAX_RETRIES` nosto 1 -> 3 (Toteutettu ja testattu enums.py:ssä).

## Työnkulku
1. Käynnistä `/tier2-execute` -työnkulku kullekin tehtävälle erikseen. (Huom. P0 ja P2 voivat sopia myös suoraan `/tier3-database-reset` -käsittelyyn).
2. Päivitä tätä trackeria (ruksi ruutuun `[x]`), kun kukin taski on läpäissyt auditointiluupit (`backend_audit_loop.py`).
3. Lopuksi aja `diff_executions.py` varmistaaksesi, että tavoitemetriikat on saavutettu.
