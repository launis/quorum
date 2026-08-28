> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified)**

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Zero-Variance Engine & Seed Hygiene Hardening

**Goal:** Eliminate LLM evaluation variance and Boolean status inversion by:
1. Fixing `ExtractiveSensorService.evaluate_atom_boolean_batch` to properly invert status on `node.atom.inverse_evidence` for all negative/penalty assertions across any dataset (resolving 77%+ of all variance at the engine level).
2. Sanitizing 4 legacy corrupted placeholder concept descriptions in `backend_v2/seed/seed_data.json` into pure, universal ontological concept definitions without dataset-specific overfitting.
3. Adding rigorous unit tests and verifying variance reduction on live real data (`docs/jwdatat`).

---

## Target Scope & Files

### TARGET Files
- **[MODIFY]** `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L301-L419]`
- **[MODIFY]** `@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L314-L365]`
- **[MODIFY]** `@[backend_v2/seed/seed_data.json#L970-L3235]`

### CONTEXT Files (Read-Only SSOT)
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/01-python-backend.md]`
- `@[.agents/rules/03_seed_vault.md]`
- `@[.agents/rules/05_llm_architecture.md]`
- `@[backend_v2/models/v2_core.py#L153-L257]`

---

## 5-Column Architectural Directives

| 1. Kohdealue & Skoopit (Target Scope) | 2. 🚫 KIELLETTY PURKKA (Eradicated Duct-Tape) | 3. 🎯 TEE NÄIN (Approved Best Practice) | 4. ✂️ KARSITTU YLISUUNNITTELU (Pruned Over-Engineering) | 5. 🔒 VERIFIOINTI & FAIL-FAST (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`extractive_sensor_service.py`** (`evaluate_atom_boolean_batch`) | Sokea `status = PASSED if eval_result.is_true else FAILED` ilman `inverse_evidence` -tarkistusta. | `node_map = {n.atom.tda_id: n for n in nodes}`<br>`if node.atom.inverse_evidence:`<br>`  status = ExecutionStatus.FAILED if eval_result.is_true else ExecutionStatus.PASSED`<br>`else:`<br>`  status = ExecutionStatus.PASSED if eval_result.is_true else ExecutionStatus.FAILED` | Ei luoda uusia välikerroksia tai sääntökohtaisia erikoispurkkia; käytetään suoraan yleistä `LinkedAtomGraph.atom.inverse_evidence` -kenttää. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py` |
| **`test_extractive_sensor_service.py`** | Testien puute `inverse_evidence`-haaran Bo3-evaluaatiolle. | Dedikoidut positiiviset ja negatiiviset testitapaukset: 1) `inverse_evidence=True` ja `is_true=False` $\rightarrow$ `PASSED`, 2) `inverse_evidence=True` ja `is_true=True` $\rightarrow$ `FAILED`. | Ei käytetä live-verkkoa; mockataan `LLMTaskExecutor` puhtailla Pydantic-malleilla. | `backend_audit_loop.py` menee läpi 100 % vihreänä. |
| **`seed_data.json`** (4 roskatekstiatomia) | Jättää kenttiin kehittäjäkommentteja (`DEPRECATED...`), rikkinäisiä lauseita (`in an block`) tai kielto-ohjeita (`Do not judge...`). | Korvataan kentät puhtailla universaaleilla konseptikuvauksilla (esim. *"Juxtaposition of concepts without synthesis"*, *"Expression of unhedged certainty without empirical data"*). | Ei ylisoviteta sääntöjä tiettyyn aineistoon tai testidokumenttiin; säilytetään yleispätevä ontologia. | `uv run python backend_v2/seed/run_seed.py local` |

---

```xml
<execution_protocol>
  <phase id="1" name="GENERIC ENGINE INVERSE EVIDENCE STATUS RESOLUTION">
    <step id="1.1" name="Inspect node resolution and inverse_evidence mapping in ExtractiveSensorService">
      <target>@[backend_v2/services/orchestrator/extractive_sensor_service.py#L301-L419]</target>
      <action>
        Build a local node lookup map: `node_map: dict[str, LinkedAtomGraph] = {node.atom.tda_id: node for node in nodes}`.
        When iterating over `result.results` and resolving `call_tda_id = alias_engine.resolve_alias(alias)`:
        Extract the target atom's `inverse_evidence` property from `node_map[call_tda_id].atom.inverse_evidence`.
        Assign status with strict mathematical polarity:
        ```python
        is_inverse = node_map[call_tda_id].atom.inverse_evidence
        if is_inverse:
            status = ExecutionStatus.FAILED if eval_result.is_true else ExecutionStatus.PASSED
        else:
            status = ExecutionStatus.PASSED if eval_result.is_true else ExecutionStatus.FAILED
        ```
      </action>
      <constraint invariant="rfc7807_dual_reporting_mandate">Preserve all existing structured extensions (coaching, contextual_override, falsification, remediation_steps) without modification.</constraint>
    </step>

    <step id="1.2" name="Add comprehensive unit tests for inverse_evidence batch evaluation">
      <target>@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L314-L365]</target>
      <action>
        Add two dedicated asynchronous unit tests:
        1. `test_extractive_sensor_service_evaluate_atom_boolean_batch_inverse_evidence_passed`:
           Tests an atom with `inverse_evidence=True` when LLM returns `is_true=False` (no poison found) -> Asserts resulting status is `ExecutionStatus.PASSED`.
        2. `test_extractive_sensor_service_evaluate_atom_boolean_batch_inverse_evidence_failed`:
           Tests an atom with `inverse_evidence=True` when LLM returns `is_true=True` (poison detected) -> Asserts resulting status is `ExecutionStatus.FAILED`.
      </action>
      <constraint invariant="mocking_mandate_for_llm">Rely strictly on AsyncMock for LLMTaskExecutor and LLMClient with zero real network calls.</constraint>
    </step>

    <step id="1.3" name="Run Backend Quality Gate on ExtractiveSensorService">
      <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test`.</action>
      <constraint invariant="quality_gate_execution">Ensure Ruff, MyPy, and Pytest all pass with 0 warnings.</constraint>
    </step>
  </phase>

  <phase id="2" name="SEED DATA DATA DEBT SANITIZATION & RE-SEEDING">
    <step id="2.1" name="Vault Backup & Sanitization of Corrupted Concept Descriptions">
      <target>@[backend_v2/seed/seed_data.json#L970-L3235]</target>
      <action>
        1. Create a timestamped vault backup:
           `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_hygiene_cleanup.json`
        2. Clean the 4 identified corrupted concept description fields into clear ontological definitions:
           - `tda_b7dfe23403db4db5b92a29a8bda9957c` (line 982): replace `"DEPRECATED - V4 uses tda_assertions directly."` with `"Juxtaposition of concepts or entities listed in succession without explaining their relational connection or synthesis."`
           - `tda_2d12f15e1c2d4488b7c2ef32d0ccfa26` (line 1419): replace `"Do not judge subjectively."` with `"Expression of absolute, unhedged certainty regarding outcomes or facts without empirical data, uncertainty margins, or epistemic qualifiers."`
           - `tda_fda64d221181411fa70843a88689b27b` (line 2674): replace `"Do not evaluate completeness."` with `"Identification and naming of potential confounding variables or alternative factors that could explain the observed outcome."`
           - `tda_43516f120e4a415bb0ee3a878a53a5bc` (line 3229): replace mangled duplicate instruction with `"Identification of specific structural flaws or methodological weaknesses in one's own proposal or analysis."`
      </action>
      <constraint invariant="prompt_preservation_mandate">Modify only the 4 corrupted concept descriptions; do not alter unaffected prompts or introduce dataset-specific terms.</constraint>
    </step>

    <step id="2.2" name="Re-seed Local Database">
      <action>Execute: `uv run python backend_v2/seed/run_seed.py local` to synchronize sanitized seed definitions to local SQLite/PostgreSQL database.</action>
      <constraint invariant="database_schema_hallucination">Verify 100% successful database seeding with 0 validation errors.</constraint>
    </step>
  </phase>

  <phase id="3" name="GENERIC E2E VARIANCE FALSIFICATION & INTEGRATION TEST">
    <step id="3.1" name="Execute Live E2E Variance Test on Real PDF Data">
      <action>
        Execute the 2-run variance runner:
        PowerShell: `$env:DEV_EXECUTION_MODE="full"; uv run python scripts/run_e2e_variance_test.py docs\jwdatat`
      </action>
      <constraint invariant="anti_hallucination_read">Inspect generated diff report in `scratch/` and verify that Boolean status inversions and corrupted concept evaluations are resolved.</constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Unit Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test
uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py
```

### Database Seeding Gate
```powershell
uv run python backend_v2/seed/run_seed.py local
```

### Live E2E Variance Gate
```powershell
$env:DEV_EXECUTION_MODE="full"
uv run python scripts/run_e2e_variance_test.py docs\jwdatat
```
