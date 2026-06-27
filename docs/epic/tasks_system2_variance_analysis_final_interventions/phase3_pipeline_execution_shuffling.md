# Implementation Plan: Phase 3 - Pipeline Execution & Normalization

## Goal
Implement pipeline execution hardening including Unicode sanitization, fuzzy matching for pre-flight routing to prevent route divergence, and random deterministic atom shuffling per ensemble run to counter positional bias.

## Proposed Changes

---

### Component: Input Normalization

#### [MODIFY] [normalization.py](file:///c:/src/quorum/backend_v2/utils/normalization.py)
- **Changes**:
  - In `normalize_evaluation_input`, implement canonical Unicode NFC normalization:
    ```python
    import unicodedata
    cleaned = unicodedata.normalize("NFC", text)
    ```
  - Remove all zero-width characters (ZWSP, ZWJ, ZWNJ, BOM, soft hyphens):
    ```python
    cleaned = re.sub(r'[\u200b\u200c\u200d\ufeff\u00ad]', '', cleaned)
    ```
  - Normalize various dash forms and smart/curly quotes into straight ASCII characters:
    ```python
    cleaned = cleaned.replace('\u2013', '-').replace('\u2014', '-')
    cleaned = cleaned.replace('\u201c', '"').replace('\u201d', '"')
    cleaned = cleaned.replace('\u2018', "'").replace('\u2019', "'")
    ```
  - *(Source: Epic Section 2.3)*

---

### Component: Extractive Sensor Service

#### [MODIFY] [extractive_sensor_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/extractive_sensor_service.py)
- **Changes**:
  - Add fuzzy-match helper utilizing `rapidfuzz` (already in dependencies):
    ```python
    @staticmethod
    def _fuzzy_match(source_text: str, anchor: str, threshold: float = 95.0) -> bool:
        """Fuzzy match tolerating minor typos/OCR issues in the source text."""
        from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
        if AnchorValidationService.strict_match(source_text, [anchor]):
            return True
        from rapidfuzz import fuzz
        return fuzz.partial_ratio(anchor.lower(), source_text.lower()) >= threshold
    ```
  - Update `pre_evaluate` matching loop to check fuzzy matching on `syntactic_anchors` with a 95.0% threshold fallback.
  - *(Source: Epic Section 2.2)*

---

### Component: Chunk Worker Orchestrator

#### [MODIFY] [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py)
- **Changes**:
  - Extract available source document IDs from `global_source_text` or `user_payload` using regular expression matching:
    ```python
    import re
    source_text_to_scan = global_source_text or user_payload or ""
    extracted_source_ids = list(set(re.findall(r'<matrix_input\s+source_id="([^"]+)"', source_text_to_scan)))
    if not extracted_source_ids:
        extracted_source_ids = ["N/A"]
    ```
  - Pass the extracted `extracted_source_ids` list as `source_document_ids` argument to `compiler.build_dynamic_schema` in the `local_dynamic_schema` compilation step.
  - In `_safe_execute` function, implement deterministic atom shuffling per ensemble iteration (index > 0):
    ```python
    if index > 0 and has_shuffled_atoms and chunk is not None:
        import random
        rng = random.Random(index)  # Deterministic seed per ensemble index
        shuffled_items = list(chunk.items)
        rng.shuffle(shuffled_items)
        chunk = chunk.model_copy(update={"items": shuffled_items})
    ```
  - *(Source: Epic Section 2.4, 2.8)*

## Hardening Constraints
- **Rule 12 (`no_naked_dicts_in_state`)**: Ensure state projections remain strictly typed and validated.
- **Rule 17 (`the_duct_tape_ban`)**: Maintain zero resource leaks and complete error raising.

## Verification Plan

### Automated Tests
Run verification tests for the normalization, extractive sensor, and chunk worker modules:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/utils/normalization.py backend_v2/services/orchestrator/extractive_sensor_service.py backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py --test
```

### Documentation Update
Update [docs/architecture/reporting_and_display_theory.md](file:///c:/src/quorum/docs/architecture/reporting_and_display_theory.md) to log positional bias mitigations and input normalizations.

## Session Handover
To execute this plan in the next session:
```powershell
/tier2-execute --target docs/epic/tasks_system2_variance_analysis_final_interventions/phase3_pipeline_execution_shuffling.md
```
