# Hooks System Documentation (V5.1 / Phase 9 Hardening)

## Overview

**Hooks** are deterministic Python functions executed by the `GraphEngine` at specific points in a step's lifecycle. They provide a mechanism for:

1. **Input Pre-processing (Pre-hooks)**: executed before the Agent's LLM call.
2. **Output Post-processing (Post-hooks)**: executed after the Agent's handler returns.
3. **Deterministic Logic**: Pure code execution without LLM variance.
4. **External Integrations**: Google Search, Database Archival, etc.

> [!IMPORTANT]
> **Strict DTO Mandate (V5.1)**:
> 1. All hooks must output strict **Pydantic V2 Models** (`ConfigDict(strict=True, extra="ignore")`). Loose dictionaries (`aux_data`) are strictly forbidden.
> 2. All hooks must **Fail Fast** using `AppException` with a specific `ErrorCode` (RFC 7807 compliance). `try-except pass` is banned.

---

## Architecture

### 1. Blackboard Pattern (`context_variables`)
Hooks interact with the `WorkflowState` primarily through `context_variables`.

* **Read**: Hooks read input data from `state.context_variables`.
    * **Strict Access**: Use `state.get_context(ModelType)` or `inflate()` to ensure type safety. DO NOT access raw dicts.
* **Write**: Hooks return a **new** state with updated `context_variables` containing their Pydantic result model.
* **Immutability**: `WorkflowState` is frozen. Hooks use `state.model_copy(update=...)`.

### 2. Strict Pydantic Models (backend/models/domain.py)
Every hook typically has a corresponding result model:

| Hook | Result Model | Description |
| :--- | :--- | :--- |
| `sanitize_text` | `SanitizationResult` | Redacted inputs & threat logs |
| `detect_performative_patterns` | `LinguisticsResult` | Detected "AI-ese" patterns |
| `execute_google_search` | `SearchResult` | Structured search items |
| `verify_structure` | `ValidationResult` | Pass/Fail status & errors |
| `apply_scoring_logic` | `ScoringResult` | Calculated totals & penalties |
| `generate_report` | `ReportResult` | Final Markdown & metadata |

### 3. Zero-Fallback Principle (Fail Fast)
Hooks do **not** fail silently.
* If a configuration (`settings.SEARCH_ENGINE_ID`) is missing and required, they raise `AppException`.
* If a critical dependency is unavailable, they raise `ErrorCode.SERVICE_DEPENDENCY_MISSING`.

---

## Hook Reference

### 1. Security Hooks (`backend/hooks/security.py`)
#### `sanitize_text_hook` (Pre-hook)
* **Action**: Scans inputs for PII (SSN, Phone) and Banned Phrases.
* **Inputs**: Accesses `WorkflowInputs` object strictly.
* **Behavior**: Raises `AppException` (403) for critical threats.

### 2. Search Hooks (`backend/hooks/search.py`)
#### `execute_google_search` (Post-hook for Analyst)
* **Action**: Executes Google Custom Search based on Analyst hypotheses.
* **Gating**: Respects `enable_vertex_search` setting. Gracefully returns empty results ONLY if explicitly disabled by the user setting.
* **Fail Fast**: If enabled but missing keys (`API_KEY`, `CX_ID`), it strictly raises an `AppException(SEARCH_CONFIG_ERROR)` to alert the user, rather than silently failing.
* **Output**: `SearchResult` containing list of `SearchResultItem`.

### 3. Scoring Hooks (`backend/hooks/scoring.py`)
#### `apply_scoring_logic` (Post-hook)
* **Action**: Aggregates scores from all judges and applies deterministic penalties (Security/Logic).
* **Safety Clamp**: Ensures scores never drop below `scale_min` (e.g., 0.1) to prevent Pydantic validation errors (`>= 0.1`) that would crash the pipeline.
* **Output**: `ScoringResult`. **Overwrites** `JudgeOutput` with authoritative scores.

### 4. Reporting Hooks (`backend/hooks/reporting.py`)
#### `generate_report` (Post-hook)
* **Action**: Renders the final PDF/Markdown report using Jinja2 templates.
* **Strict Context**: Instantiates `ReportContext` Pydantic model. Fails immediately if domain data is missing.
* **Output**: `ReportResult` (wraps the generated Markdown).

### 5. Integrity Hooks (`backend/hooks/integrity.py`)
#### `verify_citation_integrity` (Post-hook)
* **Action**: Verifies that quotes used by Analyst and Judges actually exist in the source texts.
* **Fail Fast**: Raises `AppException` if the LLM hallucination rate > 50%.
* **Output**: `CitationAudit` (logged in metadata).

---

## Developer Guide: Creating a New Hook

1. **Define Model**: Create a result model in `backend/models/domain.py` with `strict=True`.
2. **Implement Hook**: Create a function in `backend/hooks/`.
    ```python
    def my_hook(state: WorkflowState) -> WorkflowState:
        # 1. Validate Input (Fail Fast)
        inputs = state.context_variables.get("inputs")
        if not inputs:
            raise AppException(message="Missing input data.", error_code=ErrorCodes.VALIDATION_FAILED)

        # 2. Logic (Deterministic)
        result = MyHookResult(value=100)

        # 3. Update State (Immutable)
        new_context = state.context_variables.copy()
        new_context["my_hook_result"] = result
        return state.model_copy(update={"context_variables": new_context})
    ```
3. **Register**: Add it to `HOOK_MAPPING` in `backend/core/engine.py`.
