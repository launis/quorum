# Phase 2: Consensus Architecture Refactor (Epic 60)

Source: Epic 60, ACTION-1, ACTION-5, ACTION-6

## 1. Goal
Implement a 100% Pydantic-type-safe consensus architecture by replacing manual dictionary extraction and tuple-based voting with validated Pydantic projections and pure mathematical functions. This addresses the critical bug in `ExtractionPayload` and removes WET violations in `resolve_majority_vote`.

## 2. Target Files
- `TARGET (Modify)`: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- `CONTEXT (Read-Only)`: `c:\src\quorum\docs\epic\epic_60_system2_reliability_audit.md`

## 3. Architectural Invariants & Hardening Mandates
- **[01-python-backend.md - strict_pydantic_v2_rust]**: "Force the Fail-Fast pipeline by using `.model_validate()`. Any structure not matching the strict model must CRASH immediately..."
- **[hardening.xml - Rule 8 (duck_typing_token_shield_exception)]**: "The `extra="ignore"` configuration in Pydantic is STRICTLY PROHIBITED at all times, with the absolute exception of... internal Data Projection Models designed to purely extract a subset of keys from a rich payload." (We use this for `ConsensusVotePayload`).
- **[hardening.xml - Rule 88 (srp_god_method_mandate)]**: "Break down massive God Methods... Extract distinct logical blocks into isolated private helper methods to uphold the Single Responsibility Principle..."

## 4. Implementation Steps

### Step 1: Create `ConsensusVotePayload` (ACTION-5)
- In `chunk_worker.py`, replace `ExtractionPayload` with the exact schema defined in ACTION-5:
```python
class ConsensusVotePayload(BaseModel):
    """Projects consensus-relevant fields from a raw LLM vote dict.

    Uses extra='ignore' to safely extract only the fields that
    evaluate_extraction reads via getattr(), discarding schema-specific
    extras (atom_id, structural_location, localized_anchors_found, etc.).
    """
    model_config = ConfigDict(frozen=True, extra="ignore")
    exact_quotes: list[str] = []
    contextual_override: bool = False
    override_reason: str | None = None
    reasoning_steps: str | None = ""
    semantic_reasoning: str | None = ""
```

### Step 2: Extract Pure Consensus Function (ACTION-1)
- Replace `_apply_minority_veto` with the pure function `_apply_majority_consensus`:
```python
def _apply_majority_consensus(statuses: list[str]) -> str:
    """Apply pure 2/3 majority consensus over pre-evaluated verdicts..."""
    pass_count = statuses.count("PASS")
    if pass_count >= 2:
        return "PASS"
    if statuses.count("FAIL") >= 2:
        return "FAIL"
    return "DLQ"
```

### Step 3: Implement `_merge_consensus_fields` Helper (ACTION-6)
- Create `_merge_consensus_fields(payloads: list[ConsensusVotePayload], statuses: list[str], final_status: str) -> dict[str, Any]` exactly as detailed in the Epic. This function applies 2/3 majority to overrides and plurality to quotes, extracting data strictly from the Pydantic models.

### Step 4: Refactor `resolve_majority_vote`
- Migrate the evaluation loops in `resolve_majority_vote` to use the new Pydantic payloads.
- **Path A (shuffled_atoms)**: Validate `ConsensusVotePayload.model_validate(v)`, call `evaluate_extraction` with `is_negative_rule`, calculate consensus, and use `_merge_consensus_fields` to update the dictionary.
- **Path B (block-level)**: Do the same but with `is_negative_rule=False`.
- This eliminates all `v.get(...)` calls for extraction logic.

### Step 5: Documentation Update
- Update `c:\src\quorum\docs\architecture\06_evaluation_and_scoring.md` to reflect the new `ConsensusVotePayload` projection pattern and the pure `_apply_majority_consensus` logic (removing minority veto references).

## 5. Testing & Quality Gate Plan
- **Unit Tests:** Add/Update tests for `_apply_majority_consensus` and `_merge_consensus_fields` to ensure correct majority and plurality behaviors.
- **Integration Tests:** Verify that ENSEMBLE runs now correctly utilize `AnchorValidationService` due to the fixed `exact_quotes` mapping.
- **Universal Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/ --test`.

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/epic_60_tracker.md`
