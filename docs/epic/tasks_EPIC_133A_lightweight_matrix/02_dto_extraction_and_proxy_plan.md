# Phase 2: DTO Extraction & Strangler Fig Proxy

**Overview:** Create a new DTO file and extract targeted DTOs into it, leaving a Strangler Fig Proxy in the original file to maintain imports.
**Target Files:** 
- `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]`
- `c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - `atom_evaluation.py` successfully encapsulates `ReasoningStepDTO`, `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `ReducedAtomDTO`, and `LightweightMatrixDTO`.
    - All unit tests pass, and coverage remains above 90%.
  </dod_checklist>

  <required_context_rules>
    - @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
    - @[c:\src\quorum\.agents\rules\01-python-backend.md]
    - @[c:\src\quorum\.agents\rules\04_directory_reference.md]
    - @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT modify the inner business logic of the extracted DTOs yet (Phase 3).
    - Do NOT update the 23+ consumer imports in this phase (Phase 4).
  </anti_targets>

  <step id="1" name="DTO EXTRACTION">
    <action>Create a new file `c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py`.</action>
    <action>Migrate the following classes from `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]` into the new file in dependency order: `ReasoningStepDTO`, `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `ReducedAtomDTO`, `LightweightMatrixDTO`.</action>
    <action>CRITICAL DEPENDENCY MIGRATION: You MUST also copy all required imports (e.g., `AliasEngine`, `AnchorValidationService`, `LLMExtractedQuote`, `LaxVisualIntent`, `get_lexical_fuzz_threshold`) AND the 4 global configuration variables (`_settings`, `_schema_max_quotes_target`, `_schema_max_quotes`, `_schema_max_quote_length`) to the new `atom_evaluation.py` file to prevent `NameError` crashes.</action>
  </step>

  <step id="2" name="STRANGLER FIG RE-EXPORT">
    <action>In the original `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]`, add re-export imports for ALL migrated classes from `atom_evaluation.py` (specifically: `from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO, ...`).</action>
    <constraint>This ensures zero import breakage across all 23+ consumer files.</constraint>
  </step>

  <validation_gate>
    - Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
    - Verify zero-behavioral change: ALL existing tests MUST pass without modification.
  </validation_gate>
</execution_protocol>
```
