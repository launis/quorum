# Phase 3: Prompt Rule Refactoring and Database Re-seed

## 1. Yhteenveto
Tässä vaiheessa suoritetaan siementietokannan (Seed Vault) siivous ja migraatio. Luodaan Python-skripti, joka muokkaa master-seed-dataa asettamalla `allow_contextual_override = true` kolmelle ennalta määritellylle käsitteelliselle säännölle, refaktoroi epävakaat promptit puhtaiksi listapohjaisiksi uuttopyynnöiksi (poistaen IF-AND-ONLY-IF- ja ONLY-monimutkaisuudet), ja suorittaa TinyDB-kehitystietokannan re-seedauksen.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) - Master-siementietokannan JSON.

### B. Luotavat tiedostot (Target - New)
* [modify_seed_override.py](file:///c:/src/quorum/tmp/modify_seed_override.py) - Vakaa siementietokannan mutaatioskripti väliaikaishakemistossa.

### C. Lukuoikeus (Context - Read-Only)
* [03_seed_vault.md](file:///c:/src/quorum/.agents/rules/03_seed_vault.md) - Siementietokannan migraatio- ja seeding-säännöt.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Mutaatioskriptin luonti (`tmp/modify_seed_override.py`)
* **Tiedosto**: `tmp/modify_seed_override.py` (kirjoitettava `tmp/`-väliaikaishakemistoon sääntöjen mukaisesti)
* **Tehtävä**: Kirjoita Python-skripti, joka suorittaa seuraavat asiat deterministisesti:
  1. Ottaa varmuuskopion `backend_v2/seed/seed_data.json` -tiedostosta kansioon `backend_v2/seed/backups/`.
  2. Lataa tiedoston ja parsii JSON-sisällön.
  3. Paikantaa ja asettaa `"allow_contextual_override": true` säännöille `tda_e6a0c9d3eb6c443f` (Toulmin Falsification), `tda_567ee46c35852f54` (Bloom Novel Synthesis) ja `tda_4b9a2c1f38e7456d` (Goodhart Socratic Steering).
  4. **Promptien refaktorointi**: Poistaa epävakaista siemenistä (kuten `tda_d204baf0bdf74ff7`, `tda_569f87a921a2fb69`, `tda_58cbd7271f491351`) monimutkaiset luonnollisen kielen sääntöohjeet ("NEGATIVE CONDITION", "IF AND ONLY IF", "ONLY") ja muuttaa ne yksinkertaisiksi rinnakkaisten tietojen uuttopyynnöiksi (esim. *"Extract exact quotes matching X into list A. Extract exact quotes matching Y into list B."*).
  5. Kirjoittaa muokatun JSON-rakenteen takaisin `seed_data.json` -tiedostoon säilyttäen täsmällisen sisennyksen (2 välilyöntiä) ja estäen ASCII-koodaukset (`ensure_ascii=False`).
* **Arkkitehtuurisääntö**: Kaikki tietokannan mutaatiot on tehtävä deterministisellä Python-skriptillä, ei yhdelläkään terminal inline sed/awk -komennolla.
* **Source**: Epic 59, Section 5.

### Milestone 2: Mutaatioskriptin suoritus
* **Tehtävä**: Ohjeista käyttäjää ajamaan luotu mutaatioskripti PowerShellissä:
  ```powershell
  uv run python tmp/modify_seed_override.py
  ```
* **Source**: Epic 59, Section 5.

### Milestone 3: Kehitystietokannan re-seedaus
* **Tehtävä**: Wipataan ja re-seedataan TinyDB kehitystietokanta (`data/db_v2.json`) ottamaan käyttöön uudet skeemat ja ohitussäännöt:
  ```powershell
  uv run python backend_v2/seed/run_seed.py local
  ```
* **Arkkitehtuurisääntö**: `run_command`-työkalun suoran ajon kielto Windows 11:ssä; kaikki testit ja re-seedaaminen on ohjeistettava ja delegoitava käyttäjän ajettavaksi PowerShellissä.
* **Source**: Epic 59, Section 5 & rule_block id="direct_database_mutation".

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset testit (Pytest)
Aja siementietokannan skeematestit varmistaaksesi, että Pydantic hyväksyy uuden master-seedin rakenteen ilman virheitä:
```powershell
uv run pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v
```

---

## 5. Istunnon Handover (Session Handover)

> [IMPORTANT]
> Aina onnistuneen työvaiheen ja auditointisilmukan jälkeen suorita kansion tarkka commit:
> `git add backend_v2/seed/seed_data.json`
> `git commit -m "feat(epic-59): completed seed migration and prompt refactoring"`

Kun tämä vaihe on täysin valmis ja laatuportit ovat vihreänä, merkitse tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` täytetyksi askeleeksi (`[x]`).

Siirry seuraavaan vaiheeseen ajamalla:
```powershell
/tier5-resume --target docs/epic/tasks_EPIC_59/phase4_verification_and_hardening.md
```
