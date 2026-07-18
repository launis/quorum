# Phase 1A: Backend Models, Enums & Settings Foundation

> **Source:** Epic 101, Phase 1 (Steps 1-6), Phase 3 (Steps 1-2), Section 4 Quality Gates (Payload Bloat, State Sovereignty)

## Goal

Establish the strict Pydantic V2 model foundation, new enum, and settings parameters required by all subsequent phases. This plan touches ONLY leaf-level foundation files — no orchestration logic.

## Architectural Invariants (Injected)

- `strict_model_location`: All new models → `backend_v2/models/domain/`
- `strict_pydantic_v2_rust`: `ConfigDict(frozen=True, extra="forbid", strict=True)`
- `strict_configuration_segregation`: Atom ceiling in `settings.py`, enum in `enums.py`
- `python_314_modern_syntax`: PEP 695, `Annotated`, no legacy `Optional`
- `pydantic_annotated_fields_mandate`: Use `Annotated[type, Field(...)]` syntax
- `pep257_google_style_docstrings`: All classes and methods

---

## Milestone 1.1: `EngineOverrideStrategy` Enum

**Source: Epic Phase 3, Step 1**

### TARGET (Modify): [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py)

Add a new strictly typed `EngineOverrideStrategy(StrEnum)` with values:
- `PRE_HYDRATED_SYNTHESIS = "PRE_HYDRATED_SYNTHESIS"`
- `DYNAMIC_TOOL_AGENT = "DYNAMIC_TOOL_AGENT"`

Place it alphabetically near the existing strategy enums. Follow the modern `StrEnum` pattern used throughout `enums.py`.

### CONTEXT (Read-Only):
- `backend_v2/models/v2_core.py` — to verify no naming collisions

---

## Milestone 1.2: `engine_override` Field on `StepRule`

**Source: Epic Phase 3, Step 2**

### TARGET (Modify): [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)

Add to `StepRule` (line ~765):
```python
engine_override: Annotated[
    EngineOverrideStrategy | None,
    Field(description="Optional override to route this step to a non-default execution strategy.")
] = None
```

Import `EngineOverrideStrategy` from `backend_v2.models.enums`.

### CONTEXT (Read-Only):
- `backend_v2/models/enums.py` (just modified above)

---

## Milestone 1.3: `GlobalAtomBlackboard` Domain Model

**Source: Epic Phase 1, Step 6**

### TARGET (New): [blackboard.py](file:///c:/src/quorum/backend_v2/models/domain/blackboard.py)

Create a new file with the following strict Pydantic model:

```python
"""Domain models for the RAG Pre-Flight Global Atom Blackboard."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.services.orchestrator.two_pass_atomizer import DraftAtomList


class GlobalAtomBlackboard(V2CoreBase):
    """Immutable blackboard aggregating extracted atoms grouped by source input file.

    Attributes:
        atoms_by_input: Mapping of input file keys to their extracted atom lists.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    atoms_by_input: Annotated[
        dict[str, DraftAtomList],
        Field(description="Extracted atoms keyed by their source input file key (e.g. 'product_text')."),
    ]
```

> **CRITICAL IMPORT DEPENDENCY:** `DraftAtomList` is currently defined in `two_pass_atomizer.py`. Per the Epic's mandate (Phase 1 Step 6), these models (`DraftAtomList`, `DraftExtractedAtom`) MUST be migrated to `backend_v2/models/domain/` during this milestone. See Milestone 1.4.

---

## Milestone 1.4: Migrate `DraftAtomList` & `DraftExtractedAtom` to Domain Models

**Source: Epic Phase 1, Step 6 — "MUST be migrated to `backend_v2/models/domain/` as the SSOT"**

### Destructive Operation Inventory — `two_pass_atomizer.py` (exported symbols):

| Symbol | Current Location | New Location | Action |
|---|---|---|---|
| `DraftExtractedAtom` | `two_pass_atomizer.py:19` | `backend_v2/models/domain/blackboard.py` | MOVE |
| `DraftAtomList` | `two_pass_atomizer.py:30` | `backend_v2/models/domain/blackboard.py` | MOVE |
| `TwoPassAtomizer` | `two_pass_atomizer.py:38` | Stays in `two_pass_atomizer.py` | NO CHANGE |

### TARGET (Modify): [two_pass_atomizer.py](file:///c:/src/quorum/backend_v2/services/orchestrator/two_pass_atomizer.py)

1. Remove `DraftExtractedAtom` and `DraftAtomList` class definitions.
2. Add import: `from backend_v2.models.domain.blackboard import DraftAtomList, DraftExtractedAtom`
3. Add `dlq_status` field to `DraftAtomList` (see below).

### TARGET (Modify): [blackboard.py](file:///c:/src/quorum/backend_v2/models/domain/blackboard.py)

Move classes here. Add DLQ sentinel field per Epic Section 4 (TaskGroup Cascade Isolation):

```python
class DraftExtractedAtom(V2CoreBase):
    """Draft representation of an atom before AliasEngine hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    reasoning: Annotated[str, Field(description="Chain-of-thought logic.")]
    resolved_claim: Annotated[str, Field(description="The cleaned claim.")]
    source_quote: Annotated[str, Field(description="The exact quote from text.")]
    draft_id: Annotated[str, Field(description="A short temporary ID assigned by LLM, e.g. a0, a1.")]


class DraftAtomList(V2CoreBase):
    """Wrapper for a list of draft atoms returned by structured task execution."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    atoms: Annotated[list[DraftExtractedAtom], Field(description="List of extracted draft atoms.")]
    dlq_status: Annotated[
        str | None,
        Field(default=None, description="DLQ sentinel marker. Set to 'FAILED/DLQ' on structural failures."),
    ]
```

### Import Proxy Pattern:

Because `DraftAtomList` and `DraftExtractedAtom` are imported from `two_pass_atomizer.py` by external consumers like `llm.py`, temporarily retain re-exports in `two_pass_atomizer.py`:

```python
# @deprecated — Import from backend_v2.models.domain.blackboard instead.
from backend_v2.models.domain.blackboard import DraftAtomList, DraftExtractedAtom  # noqa: F401
```

> **MANDATORY TEST UPDATE:** You MUST actively update the imports in `backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py` and `test_atomizer.py` to point to the new `backend_v2.models.domain.blackboard` SSOT. Do NOT let unit tests rely on the deprecated proxy, as this will trigger the Anti-TDD Trap during audit loops.

### CONTEXT (Read-Only):
- `backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py`
- `backend_v2/tests/unit/services/orchestrator/test_atomizer.py`
- `backend_v2/services/orchestrator/strategies/llm.py`

---

## Milestone 1.5: Add `"progress"` to `TraceEvent.event_type` Literal

**Source: Epic Phase 1, Step 5 — "state.py must be updated to include 'progress'"**

### TARGET (Modify): [state.py](file:///c:/src/quorum/backend_v2/models/state.py)

Change the `event_type` Literal on `TraceEvent` (line ~122) from:
```python
event_type: Literal["input", "reasoning", "decision", "error", "output", "tombstone", "evidence_override"]
```
to:
```python
event_type: Literal["input", "reasoning", "decision", "error", "output", "tombstone", "evidence_override", "progress"]
```

### CONTEXT (Read-Only):
- `backend_v2/models/execution_core.py`

---

## Milestone 1.6: Add `max_extracted_atoms_per_document` to `settings.py`

**Source: Epic Section 4 — Payload Bloat Risk (Atom Ceiling)**

### TARGET (Modify): [settings.py](file:///c:/src/quorum/backend_v2/settings.py)

Add a new field using the strict `Annotated` pattern with native default assignment:
```python
max_extracted_atoms_per_document: Annotated[
    int,
    Field(description="Fail-Fast ceiling for extracted atoms per document. Prevents TinyDB bloat.")
] = 500
```

### CONTEXT (Read-Only): None.

---

## Testing & Quality Gate Plan

### Unit Tests:
1. **`test_blackboard_models.py`** — Validate `GlobalAtomBlackboard.model_validate()` with correct data, `extra="forbid"` rejection, `frozen=True` immutability, and `dlq_status` sentinel.
2. **`test_engine_override_enum.py`** — Validate enum values and string serialization.
3. **`test_trace_event_progress.py`** — Validate `TraceEvent(event_type="progress")` passes schema validation.

### Quality Gate:
```
uv run python scripts/backend_audit_loop.py backend_v2/models/ --test
```

---

## Session Handover
```
Achieved: Foundation models, enums, and settings for Epic 101 RAG pipeline.
Remaining: Phase 1B (DAGExecutor Pre-Flight logic), Phase 2 (Synthesis Strategy), Phase 3 (SDUI Routing).
```
