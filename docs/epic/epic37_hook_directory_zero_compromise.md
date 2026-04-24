# Epic 37: Full Hook Directory Zero-Compromise Hardening

> **Audit Status:** [IN PROGRESS: Extending the Fail-Fast architecture to the entire backend_v2/hooks directory.]

## 1. Description and Motivation
Epic 34 successfully hardened the core orchestration hooks (Reporting, Scoring Matrices, Input Processing, Translation). However, an audit reveals that the `backend_v2/hooks/` directory still contains widespread legacy "defensive programming" (e.g., `.get()` and `isinstance(..., dict)`) in secondary hooks and helper modules. 

**The Violations:**
- **Secondary Scoring Hooks:** `calculate_evaluation_fidelity_hook` and `evaluate_judge_passivity_hook` in `scoring.py` still use `data.get("step_guard")` and dictionary iteration.
- **Synthesis Engine:** `synthesis.py` still relies on `hook_metadata.get("target_locale")` and heavy `isinstance` type-checking blocks.
- **Security & Validation:** `security.py` begins with `if not inputs or not isinstance(inputs, dict):`. `validation.py` extracts system warnings via `.get("_system_warnings", [])`.
- **Ancillary Hooks:** Other modules (e.g., `archival.py`, `hydration.py`, `metrics.py`) lack explicit strict boundary models.

**Objective:** Achieve 100% Pydantic strictness across all 18 files in `backend_v2/hooks/`. Eradicate all remaining `dict` sniffing. Every hook must validate its `inputs` and `metadata` via a specific DTO (e.g., `SecurityPayloadDTO`) and Fail-Fast with an `AppException(400)`.

## 2. Phase 9 Backend Hardening Mandates (Tier 2 Audit Checklist)
Tässä Epicissä tullaan soveltamaan täysimittaista `/tier2-hardening-backend` -looppia kaikkiin hookkeihin. Koodin tulee läpäistä seuraavat 24+ Phase 9 -sääntöä:

1. **`the_zero_compromise_pledge`**: Ei `.get("default")` fallbackeja. Pydantic-validointi pakollinen rajapinnoilla.
2. **`the_duct_tape_ban` / `silent_failures`**: Ei "God Blockeja" (`except Exception: pass`). Virheet heitettävä `AppException`:ina.
3. **`no_naked_dicts_in_state`**: Ei raakoja sanakirjoja (dict) tilanhallinnassa. Pydantic-mallit pakollisia.
4. **`strict_pydantic_v2_rust`**: Käytä vain `.model_validate()`, ei vanhaa `parse_obj()`. `extra='forbid'` käytössä.
5. **`opaque_stripe_id_mandate`**: Vain `usr_123` jne. Ei kokonaisluku-ID:itä tai slugeja.
6. **`python_314_modern_syntax`**: PEP 695 generics, modernit unionit (`| None`), ei `Optional[X]`.
7. **`zero_legacy_fallback_hacks`**: Ei `@model_validator` -purkkakorjauksia vanhan V1 datan hyväksymiseksi.
8. **`frozen_state_mutability`**: Domain-mallit muuttumattomia (`ConfigDict(frozen=True)`).
9. **`pydantic_native_field_priority`**: Suosi Pydanticin natiivia `Field(ge=0)` validaatiota manuaalisen validaattorin sijaan.
10. **`zero_type_ignore_shortcuts`**: Ei `# type: ignore` merkintöjä ilman tarkkaa Mypy error-koodia ja perustelua.
11. **`pydantic_namespace_collisions`**: Ei inline-skeemoja. Kaikki uudet DTO:t `models/` -kansiossa.
12. **`security_logging_ban`**: Lokeihin ei saa printata käyttäjien prompteja (PII) tai raakadataa.
13. **`polymorphic_routing_o1`**: Käytä Discriminated Unioneita tarvittaessa.
14. **`no_string_l10n`**: Ei kovakoodattuja näyttötekstejä.
15. **`llm_structured_execution_mandate`**: Kaikki LLM-kutsut tiukasti rajatun tyypityksen läpi.
16. **`global_settings_import`**: `get_settings` tuotava tiedoston alussa.
17. **`no_inline_imports`**: Ei inline importteja funktioiden sisällä. Kaikki importit tiedoston alussa (PEP 8).
18. **`Synthesis.py Standard`**: Koodi pilkottava "Pure Functions" muodossa. Sisäkkäisten iterointien tilalla O(1) hajautustaulut.

## 3. Implementation Phases

### Phase 1: Secondary Scoring Logic (`scoring.py`)
- **Target:** `calculate_evaluation_fidelity_hook`, `evaluate_judge_passivity_hook`.
- **Action:** Create `StepGuardDTO`, `StepFalsifierDTO`, and `StepPanelDTO`. Rip out `guard_model.get("security_check")`. Suorita täysi Tier 2 auditointi tiedostolle.

### Phase 2: Synthesis Core Strictness (`synthesis.py`)
- **Target:** `synthesis_hook` and helper functions.
- **Action:** Enforce strict metadata models. Replace `hook_metadata.get("target_locale")` with `SynthesisMetadataDTO`. Eradicate `isinstance(step_data, dict)` checks. Suorita täysi Tier 2 auditointi.

### Phase 3: Security & Validation Boundaries (`security.py`, `validation.py`)
- **Target:** All hook boundaries in these files.
- **Action:** Implement `SecurityPayloadDTO` and update `validation.py` to intercept warnings strictly. Suorita täysi Tier 2 auditointi.

### Phase 4: Ancillary Hooks Hardening
- **Target:** `metrics.py`, `archival.py`, `hydration.py`, `linguistics.py`, `integrity.py`.
- **Action:** Perform a blanket audit. Ensure every file declares strict input schemas, removes `isinstance` checks, siirtää inline importit ylös ja päivittää tyypityksen `python_314_modern_syntax` tasolle.

## 4. Verification Mandate
- Each modified hook must pass the `scripts/backend_audit_loop.py` Universal Quality Gate.
- 100% Type safety and 0 Ruff warnings.
- Kaikki testit suoritetaan täydellä Traceability Matrix -listauksella, varmistaen että jokainen yllä oleva Phase 9 sääntö kuittautuu tasolla (Pass/Fail/NA) yksittäistä tiedostoa muokatessa.
