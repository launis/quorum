# Implementation Plan - System 2 Variance Corrections (Gaps 1-5)

Tämä suunnitelma kuvaa toimenpiteet [system2_variance_analysis_report_critical_audit.md](file:///c:/src/quorum/docs/epic/system2_variance_analysis_report_critical_audit.md) -dokumentissa tunnistettujen viiden kriittisen puutteen (Gaps 1-5) korjaamiseksi järjestelmässä.

## User Review Required

> [!IMPORTANT]
> **Matemaattinen asymmetria ja kognitiivinen romahdus**:
> 1. **Gap 1 (Symmetrinen gating)**: FAIL-enemmistöjen (2-1 split) muuttaminen `CONTESTED`-tilaan pitää Guttman-waterfallin elossa positiivisille säännöille, mutta asettaa lievän sakon. Tämä on loogisesti oikein, mutta suosii loivaa tulkintaa.
> 2. **Gap 3 (Järjestelmäromahduksen esto)**: Jos matriisi on `INDETERMINATE`, palautetaan 500-virheen sijaan hallittu `total_score = None`. Tämä vaatii, että frontend sietää `total_score = null` tai `total_score: None` vastauksia.

---

## Proposed Changes

### 1. [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py)

#### [MODIFY] [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py)
Päivitetään `resolve_majority_vote` -funktio suorittamaan gating-tasoitus myös silloin, kun enemmistö on `FAIL`.

* **Muutoskohta (rivit 173-190 ja 235-252)**:
  Symmetrisoidaan äänestysrakenne siten, että jos `fail_votes > pass_votes` mutta `confidence <= 0.67` (eli 2-1 split), status ylikirjoitetaan arvoon `CONTESTED`.

---

### 2. [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py)

#### [MODIFY] [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py)
Korjataan dynaamisen sakon laskenta relative-kaavan mukaiseksi ja estetään fatal-kaatuminen `INDETERMINATE`-matriiseille.

* **Muutoskohta 1 (rivit 963-968)**:
  Päivitetään dynaaminen sakko vastaamaan suhteellista kaavaa:
  ```python
  if raw_score is not None and n_contested > 0 and global_total > 0:
      penalty_factor = (n_contested / global_total) * 0.15
      raw_score = raw_score * (1.0 - penalty_factor)
      raw_score = max(raw_score, math_min)
      penalty_pct = penalty_factor * 100
      justification = f"[DYNAMIC PENALTY APPLIED: -{penalty_pct:.1f}% for CONTESTED atoms]\n{justification}"
  ```
* **Muutoskohta 2 (apply_scoring_logic_hook, rivit 233-240)**:
  Jos `count == 0` (koska matriisi ohitettiin `raw_score = None` takia), tarkistetaan onko syynä validi `[INDETERMINATE]` -merkintä matriisin justificationissa. Jos on, palautetaan hallittu `HookResult` pistemäärällä `None` kaatumisen sijaan.

---

### 3. [test_prompt_compiler.py](file:///c:/src/quorum/backend_v2/tests/integration/test_prompt_compiler.py)

#### [MODIFY] [test_prompt_compiler.py](file:///c:/src/quorum/backend_v2/tests/integration/test_prompt_compiler.py)
Päivitetään integraatiotesti heijastamaan uutta puhtaasti sensoripohjaista arkkitehtuuria (poistetaan poistetun legacy Vice-ohjeen testaus).

* **Muutoskohta (rivit 62-71)**:
  Poistetaan `expected_inverse_text` -muuttuja ja siihen liittyvä `assert expected_inverse_text in rubrics` -väite. Tilalle lisätään assertion säännön XML-rakenteelle ilman Vice-lisätekstiä.

---

## Verification Plan

### Automated Tests
- Ajetaan testit `backend_v2/tests/integration/test_prompt_compiler.py` varmistamaan, että integraatiotesti menee läpi.
- Ajetaan testit `backend_v2/tests/unit/hooks/test_scoring.py` ja varmistetaan, että uusi relative-sakko ja indeterminate-bypass toimivat.
- Suoritetaan backendin auditointilooppi:
  `uv run python scripts/backend_audit_loop.py . --test`

### Manual Verification
- Varmistetaan `backend_debug.log` -tiedostosta, että kognitiivinen romahdus single-matrix -vaiheissa ei enää johda 500-virheeseen, vaan tuottaa hallitun `scoring_result` -pistemäärän `None`.
