# Phase 3: Polymorphic Seed Migration and Database Re-seed

## 1. Yhteenveto
Tässä vaiheessa luodaan deterministinen Python-skripti, joka muokkaa master-seed-dataa `backend_v2/seed/seed_data.json` ottamalla käyttöön `allow_contextual_override = true` kolmelle ennalta määritellylle käsitteelliselle TDA-säännölle. Lopuksi suoritetaan paikallisen kehitystietokannan tyhjennys ja uudelleensyöttö (re-seed).

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) - Quorum-master-tietokant ब्लूप्रिंट.

### B. Luotavat tiedostot (Target - New)
* [modify_seed_override.py](file:///c:/src/quorum/tmp/modify_seed_override.py) - Vakaa seed-mutaatioskripti väliaikaishakemistossa.

### C. Lukuoikeus (Context - Read-Only)
* [03_seed_vault.md](file:///c:/src/quorum/.agents/rules/03_seed_vault.md) - Tietokannan migraatio- ja seedaussäännöt.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Mutaatioskriptin luonti (`tmp/modify_seed_override.py`)
* **Tiedosto**: `tmp/modify_seed_override.py`
* **Tehtävä**: Luo deterministinen skripti, joka:
  1. Tekee aikaleimatun varmuuskopion `backend_v2/seed/seed_data.json` tiedostosta kansioon `backend_v2/seed/backups/`.
  2. Avaa tiedoston `json.load()` -funktiolla.
  3. Etsii ja päivittää säännöt `tda_e6a0c9d3eb6c443f`, `tda_567ee46c35852f54` ja `tda_4b9a2c1f38e7456d` asettamalla niihin kentän `"allow_contextual_override": true`.
  4. Kirjoittaa tuloksen takaisin `json.dump(..., indent=2, ensure_ascii=False)` -funktiolla.
* **Arkkitehtuurisääntö**: Kaikki tietokannan mutaatiot on tehtävä deterministisellä Python-skriptillä, ei yhdelläkään terminal inline sed/awk -komennolla.
* **Source**: Epic 59, Section 5 & rule_block id="inline_terminal_scripting".

### Milestone 2: Mutaation suoritus ja varmistus
* **Tehtävä**: Pyydä käyttäjää ajamaan `tmp/modify_seed_override.py` PowerShellissä.
  ```powershell
  uv run python tmp/modify_seed_override.py
  ```
* **Source**: Epic 59, Section 5.

### Milestone 3: Kehitystietokannan tyhjennys ja re-seedaaminen
* **Tehtävä**: Suoritetaan paikallinen kehitystietokannan re-seedaus:
  ```powershell
  uv run python backend_v2/seed/run_seed.py local
  ```
* **Source**: Epic 59, Section 5.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset testit (Pytest)
Aja seed-skeeman yhdenmukaisuustesti varmistaaksesi, että Pydantic hyväksyy uuden master-seedin rakenteen ilman virheitä:
```powershell
uv run pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v
```

---

## 5. Istunnon Handover (Session Handover)

> [!NOTE]
> Kun tämä vaihe on valmis ja testit menevät läpi, päivitä tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` asettamalla tämä vaihe tilaan `[x]`.

Aloita seuraava vaihe ajamalla:
```powershell
/tier5-resume --target docs/epic/tasks_EPIC_59/phase4_verification_and_hardening.md
```
