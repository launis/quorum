# Implementation Plan: Phase 2 - Context Compiler & Prompt XML Grounding

This task implements the XML-based prompt injection of mechanical anchors into the system prompts of the Causal Analyst and Performativity Detector agents, and updates the seed data instructions.

## Scoping

### Target (Modify)
- [ ] [prompt_factory.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py) - Compile and inject the `<mechanical_anchors>` XML block.
- [ ] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) - Update matrix role/rules descriptions to refer to `<mechanical_anchors>`.

### Context (Read-Only)
- [x] [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py) - Prompt Compiler (Immutable baseline).
- [x] [metrics.py](file:///c:/src/quorum/backend_v2/hooks/metrics.py)
- [x] [linguistics.py](file:///c:/src/quorum/backend_v2/hooks/linguistics.py)

---

## Technical Specifications & Architectural Invariants

> [!IMPORTANT]
> **Prompt Compiler Immutability & Grounding Invariants**:
> - DO NOT modify `prompt_compiler.py` directly (`prompt_compiler_immutability`).
> - Perform the XML assembly in the `PromptFactory` instead.
> - All new system instructions, matrix modifications, and rules MUST remain 100% in English (`cross_language_mapping_mandate`).
> - All database modifications must be done via the seed vault, not by direct database file mutation (`direct_database_mutation`).

### XML Mechanical Anchors Structure
For steps involving performativity or causal analysis, `PromptFactory` will extract `profiler_metrics` and `linguistics_result` from the `llm_context_data` and construct this XML segment:
```xml
<mechanical_anchors>
  <text_metrics>
    <word_count>{word_count}</word_count>
    <say_do_gap>{say_do_gap}</say_do_gap>
    <automation_bias>{automation_bias}</automation_bias>
  </text_metrics>
  <detected_performative_phrases>
    <phrase_count>{phrase_count}</phrase_count>
    <items>
      <phrase>{phrase1}</phrase>
      <phrase>{phrase2}</phrase>
    </items>
  </detected_performative_phrases>
</mechanical_anchors>
```

---

## Detailed Milestones

### Milestone 1: Dynamic Step Detection in PromptFactory
- **Goal**: Identify when the current prompt execution concerns performativity or causal analyst.
- **Source**: Epic Phase 2, Toimenpide 1.
- **Actions**:
  1. Inspect the `criteria_blocks` parameter in `PromptFactory.build` to detect matrix blocks matching causal or performativity slugs (`matrix_causal_analyst`, `block_taskperformativity`).

### Milestone 2: XML Anchor Construction & Injection
- **Goal**: Compile and inject `<mechanical_anchors>` into the system prompt.
- **Source**: Epic Phase 2, Toimenpide 1.
- **Actions**:
  1. Safely extract `profiler_metrics` and `linguistics_result` from `llm_context_data`.
  2. Format the `<mechanical_anchors>` XML block cleanly.
  3. Inject it into `base_system_prompt` after the `role_block` section.

### Milestone 3: Seed Data Matrix Instructions Evolution
- **Goal**: Instruct the LLM agents to respect the physical anchors.
- **Source**: Epic Phase 2, Toimenpide 2 & 3.
- **Actions**:
  1. Modify `backend_v2/seed/seed_data.json` to update the `ai_description` of Performativity and Causal Analyst blocks.
  2. Instruct the agents that they MUST base their qualitative assessments on the values in `<mechanical_anchors>` (e.g. if `say_do_gap` is high, performativity and sycophancy are indicated).
  3. Commands to run seed update:
     ```powershell
     uv run python backend_v2/seed/run_seed.py local
     ```

---

## Testing & Quality Gate Plan

### Integration Tests
- Run backend tests to verify that PromptFactory output is correct and compilation succeeds:
  ```powershell
  uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py
  ```

---

## Session Handover
To execute this step iteratively in a new session, run:
```powershell
/tier2-execute --plan="docs/epic/tasks_EPIC_57/phase2_prompt_grounding.md"
```
