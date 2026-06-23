# Implementation Plan - Phase 2: MCP Tool Loop Enhancements (Ensemble, Verification & Self-Correction)

This implementation plan covers the improvements to the MCP tool calling cycle, including parallel Best-of-3 ensemble calls, contextual overrides for lower strictness levels, and agentic self-reflection loop fallback checks.

## User Review Required

> [!IMPORTANT]
> - Relies on `asyncio.TaskGroup` for Best-of-3 concurrency.
> - Invokes an additional fast LLM task (`CitationCorrectionResult`) if strictness level is 100 and physical anchoring fails.
> - Bypasses physical anchoring checks entirely if strictness is less than 100.
> - Accumulates and sums token usage for all ensemble calls and self-correction loops.

## Proposed Changes

### Domain & Service Layer

#### [MODIFY] [mcp.py](file:///c:/src/quorum/backend_v2/models/domain/mcp.py)
- **Source:** Epic §5, Fix 9 (Agentic Self-Reflection Loop)
- **Changes:**
  - Define the `CitationCorrectionResult` Pydantic model:
    ```python
    class CitationCorrectionResult(V2CoreBase):
        """Result of the citation self-correction LLM task."""
        corrected_claim: str = Field(description="The verbatim corrected claim text found in the source context.")
    ```

#### [MODIFY] [mcp_tool_loop.py](file:///c:/src/quorum/backend_v2/services/mcp/mcp_tool_loop.py)
- **Source:** Epic §5, Fix 7, 8, 9
- **Changes:**
  - **Imports:** Import `AnchorValidationService` from `backend_v2.services.orchestrator.anchor_validation_service` and `asyncio`.
  - **TaskGroup Ensemble (Fix 8):**
    - Wrap the Phase 0 citation extraction in an `asyncio.TaskGroup` to run **3 calls in parallel** (Best-of-3 ensemble).
    - Protect each call inside the task group with `try-except` blocks.
    - Implement a majority vote algorithm:
      * Let `N` be the number of successful runs.
      * Keep claims whose normalized forms (using `AnchorValidationService.normalize_text_with_mapping()[0]`) appear in:
        * `>= 2/3` successful runs (if N == 3)
        * `>= 2/2` successful runs (if N == 2)
        * `>= 1/1` successful runs (if N == 1)
      * Discard all other hallucinated or statistical anomaly claims.
      * Re-construct `CitationExtractionResult` with consensus claims.
    - Accumulate token usage of all ensemble calls in Phase 0 plus Phase 2.
  - **Contextual Override (Fix 7):**
    - Retrieve `strictness_level` from `validation_context.get("strictness_level", 100)` or default to 100.
    - If `strictness_level < 100`, bypass `AnchorValidationService.strict_match` verification entirely for Tavily searches, allowing semantic searches.
  - **Agentic Self-Reflection Loop (Fix 9):**
    - If `strictness_level >= 100`, perform `AnchorValidationService.strict_match(source_context, [claim])`.
    - Catch `SemanticEvidenceError` (or trigger it when `strict_match` returns `False`).
    - If caught, execute a fast self-correction LLM task:
      * Use static system instruction `_SELF_CORRECTION_SYSTEM_INSTRUCTION` (in English) to search for the verbatim claim text in `source_context`.
      * `_SELF_CORRECTION_SYSTEM_INSTRUCTION` system prompt details:
        ```python
        _SELF_CORRECTION_SYSTEM_INSTRUCTION = (
            "<system_directive>\n"
            "  <objective>Locate and return the exact physical substring from the source context "
            "that is semantically equivalent to the failed claim.</objective>\n"
            "  <rule>The returned corrected_claim MUST be a 100% exact substring match from the "
            "source context (including case, spaces, and diacritics).</rule>\n"
            "  <rule>Do not paraphrase or summarize.</rule>\n"
            "</system_directive>"
        )
        ```
      * Execute task using `executor.execute_structured_task()` against `CitationCorrectionResult`.
      * Verify if `corrected_claim` is a valid exact substring of `source_context` using `AnchorValidationService.strict_match`.
      * If verified, update the claim text.
      * If self-reflection fails to find an exact substring, raise `SemanticEvidenceError`.
    - Accumulate and sum token usage of the self-correction tasks.

---

## Verification Plan

### Automated Tests
- Create unit tests in `backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py` to verify:
  1. Ensemble vote consensus: 3 runs with conflicting extractions resolve to majority consensus correctly.
  2. Strictness override: when `strictness_level < 100`, Tavily search runs without exact substring checks.
  3. Agentic self-reflection loop: if exact check fails and self-reflection finds matching string, it corrects claim; if not found, it crashes step.
- Run the backend audit loop:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/mcp_tool_loop.py --test
  ```

---

## Session Handover

To execute this plan iteratively, start a NEW chat session and run:
```powershell
/tier2-execute --target docs/epic/tasks_EPIC_85_Analysis_Refinements_and_XAI_Fixes/phase2_mcp_tool_loop.md
```
