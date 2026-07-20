# Phase 2: SchemaFactory Registry Pattern & PromptCompiler SDUI Enforcement

> **Source**: Epic 106 — Phase 2
> **Domain**: Backend (Python)
> **PromptCompiler Immutability Exception**: USER APPROVED (Epic 106, Phase 2)

## Goal

Replace the hardcoded `SchemaFactory` routing with a Strategy + Registry pattern keyed by `expected_sdui_type`. Ensure `PromptCompiler` uses `StepRule.expected_sdui_type` as the SSOT for both schema validation and prompt formatting instructions. Remove `formatting_directives` dependency from `llm.py`.

## Architectural Invariants (Injected)

- `prompt_compiler_immutability`: Protected file — USER has explicitly granted modification permission for Epic 106.
- `orchestrator_god_object_fragility`: Full blast-radius analysis required when modifying orchestrator files.
- `execution_synthesis_tier_decoupling`: `PromptBlocks` are for cognitive instructions. `expected_sdui_type` is for structural enforcement.
- `strict_pydantic_v2_rust`: Registry must return strict Pydantic V2 models.
- `universal_fail_fast`: Unknown `expected_sdui_type` values MUST raise `AppException(ErrorCodes.SCHEMA_ERROR)`, not `KeyError`.
- `python_314_modern_syntax`: Use `match/case` for routing, not `if/elif`.
- `pep257_google_style_docstrings`: All new classes/functions must have Google-style docstrings.

## Pre-Execution Baseline

Before modifying ANY file, the executing agent MUST:
1. Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`
2. Record the passing test count and coverage as `[BASELINE]` metric.

---

## Milestone 2.0: Pydantic Strictness & Seed Data Migration

**Source**: Epic 106, Phase 2

### TARGET (Modify): [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py) & `seed_data.json`

- In `v2_core.py`, update `StepRule.expected_sdui_type` (line ~784) to include `"grid"` in the Literal: `Literal["markdown", "hero_insight", "grid"] | None`.
- **CRITICAL MIGRATION**: Since `SchemaFactory` will fail-fast on unknown SDUI types, the executing agent MUST create and run a one-off python script to safely update `backend_v2/seed/seed_data.json`. The script must iterate over all `steps` in the JSON and if `expected_sdui_type` is missing or `null`, set it to `"grid"`. Do NOT use file replacement tools manually for 30+ JSON blocks to avoid truncation risks.

---

## Milestone 2.1: Create SchemaBuilder Strategy Registry

**Source**: Epic 106, Phase 2 (SchemaFactory Registry Pattern)

### TARGET (New): [registry.py](file:///c:/src/quorum/backend_v2/core/registry.py)

Create a new file implementing the Strategy + Registry pattern:

```python
"""SDUI Schema Builder Registry.

Maps expected_sdui_type string keys to concrete SchemaBuilderStrategy
implementations, enforcing the Open-Closed Principle.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes


class SchemaBuilderStrategy(ABC):
    """Abstract base for SDUI schema builder strategies."""

    @abstractmethod
    def build_schema(self, **kwargs: Any) -> type[BaseModel]:
        """Build and return the Pydantic model for this SDUI type.

        Args:
            **kwargs: Strategy-specific parameters (criteria, locale, etc.).

        Returns:
            A dynamically constructed Pydantic V2 model class.

        Raises:
            AppException: If schema construction fails.
        """
        ...


# Registry: Maps expected_sdui_type → SchemaBuilderStrategy
_SDUI_SCHEMA_REGISTRY: dict[str, type[SchemaBuilderStrategy]] = {}


def register_sdui_schema(sdui_type: str) -> ...:
    """Decorator to register a SchemaBuilderStrategy for an SDUI type."""
    ...


def get_schema_strategy(sdui_type: str) -> type[SchemaBuilderStrategy]:
    """Resolve strategy by SDUI type.

    Raises:
        AppException: SCHEMA_ERROR if sdui_type is not registered (Fail-Fast).
    """
    ...
```

**Registry Eager Loading Mandate**: All concrete strategy classes MUST be imported in `backend_v2/core/__init__.py` to guarantee eager registration at system startup.

### Concrete Strategies:

1. **`MarkdownSchemaStrategy`**: Returns the static `GlobalSynthesisDTO` — eliminates unnecessary `create_model()` overhead for synthesis/markdown steps.
2. **`GridSchemaStrategy`**: Encapsulates the dynamic column generation logic currently inside `SchemaFactory.build_dynamic_schema()`.

---

## Milestone 2.2: Refactor SchemaFactory to Delegate via Registry

**Source**: Epic 106, Phase 2

### TARGET (Modify): [schema_factory.py](file:///c:/src/quorum/backend_v2/services/orchestrator/schema_factory.py)

- The `SchemaFactory` becomes a **thin delegator**. It resolves the strategy from the registry using `expected_sdui_type` and delegates schema construction.
- Remove any hardcoded `if "sp_7a..."` string matching blocks.
- The `build_dynamic_schema()` method signature gains a new parameter: `expected_sdui_type: str`.
- Internal routing:
  ```python
  match expected_sdui_type:
      case "markdown":
          strategy = get_schema_strategy("markdown")
          return strategy.build_schema(...)
      case "grid":
          strategy = get_schema_strategy("grid")
          return strategy.build_schema(criteria=criteria, ...)
      case _:
          raise AppException(
              message=f"Fail-Fast: Unknown expected_sdui_type '{expected_sdui_type}'",
              status_code=500,
              details={"error_code": ErrorCodes.SCHEMA_ERROR.value},
          )
  ```
- **CRITICAL**: The existing `build_dynamic_schema()` method signature in `prompt_compiler.py` and its internal callers MUST be updated to pass the new `expected_sdui_type` parameter.

### CONTEXT (Read-Only):
- [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py) — `StepRule.expected_sdui_type` field (line 784).

---

## Milestone 2.3: Update PromptCompiler to Thread `expected_sdui_type`

**Source**: Epic 106, Phase 2

### TARGET (Modify): [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py) & [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py)

- In `prompt_compiler.py`: Update `build_dynamic_schema()` to accept `expected_sdui_type` and forward it to `SchemaFactory`.
- In `llm.py` (lines ~563 and ~620): Extract `expected_sdui_type=step.expected_sdui_type` and explicitly pass it into `self.compiler.build_dynamic_schema(...)`.
- Ensure formatting instructions injected into the system prompt are sourced from `expected_sdui_type` semantics (e.g., "markdown" → "Output your response as structured semantic Markdown") rather than relying on legacy directives.

### CONTEXT (Read-Only):
- [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py) — Verify the `expected_sdui_type` threading path: `StepRule` → `DAGExecutor` → `LLMNodeStrategy.execute()` → `SchemaFactory`.

---

## Milestone 2.4: Remove `formatting_directives` from `llm.py`

**Source**: Epic 106, Phase 2

### TARGET (Modify): [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py)

- **DELETE** lines 336 and 456-458 that read `output_profile.formatting_directives` and inject them into `exec_params`.
- Formatting directives are now exclusively sourced from `PromptBlock` (e.g., `EXECUTION_PERSONA` category) by the `PromptCompiler`.
- Ensure `tone_instruction` is still correctly sourced from `OutputProfile` (it is retained).
- **CRITICAL**: This deletion MUST be committed atomically with Phase 2.5 (worker.py cleanup). If Phase 2.5 is not ready, this milestone MUST wait.

### CONTEXT (Read-Only):
- [worker.py](file:///c:/src/quorum/backend_v2/worker.py) — Lines 795-797. Phase 2.5 handles this file.

---

## Bidirectional Integration Check

- **Producer**: `StepRule.expected_sdui_type` is populated by seed data (verified: lines 7614-7826 of `seed_data.json` already contain `"expected_sdui_type": "markdown"` for synthesis steps). Grid steps will need explicit `"expected_sdui_type": "grid"` values — the executing agent MUST verify seed data completeness.
- **Consumer**: `SchemaFactory` → `PromptCompiler` → `LLMNodeStrategy`.

---

## Destructive Operation Inventory: `llm.py` formatting_directives removal

| Symbol | Location Before | Location After | Status |
|--------|----------------|----------------|--------|
| `formatting_directives=list(p.formatting_directives)` | `llm.py:336` | REMOVED | **INTENTIONALLY DROPPED** — Formatting is now sourced from PromptBlock via PromptCompiler |
| `if output_profile.formatting_directives:` block | `llm.py:456-458` | REMOVED | **INTENTIONALLY DROPPED** — Same reason |

---

## Testing & Quality Gate Plan

1. **Unit Tests for Registry**:
   - Test `get_schema_strategy("markdown")` returns `MarkdownSchemaStrategy`.
   - Test `get_schema_strategy("grid")` returns `GridSchemaStrategy`.
   - Test `get_schema_strategy("unknown")` raises `AppException(ErrorCodes.SCHEMA_ERROR)`.
2. **Integration Tests**:
   - Existing `test_schema_factory.py` tests must pass with the new `expected_sdui_type` parameter.
   - Existing `test_dag_executor.py` tests must pass with the threading change.
3. **Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

---

## Documentation Mandate

After completing all milestones:
- Update `docs/architecture/` to document the new SchemaBuilder Registry Pattern.
- Create a Knowledge Item (KI) in `<appDataDir>/knowledge/sdui_schema_registry/` documenting the SDUI Schema Builder Registry Pattern and usage rules.
- Update `.agents/rules/04_directory_reference.md` to add `backend_v2/core/registry.py` under the models/core module.

---

## Session Handover

```
Achieved: Phase 2 complete — SchemaFactory uses Strategy+Registry, PromptCompiler threads expected_sdui_type, formatting_directives removed from llm.py.
Learned: SchemaFactory existing tests need expected_sdui_type parameter updates. PromptCompiler immutability exception was user-approved.
Remaining: Phase 2.5 (Worker migration), Phase 3 (Flutter cleanup).
```
