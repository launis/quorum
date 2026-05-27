# Implementation Plan: Phase 3 - XAI Reporter Agent Integration

This task implements the integration of the newly ground mechanical anchors and cross-comparison variance checks within the final XAI Reporter step and the report generation hook.

## Scoping

### Target (Modify)
- [ ] [reporting.py](file:///c:/src/quorum/backend_v2/hooks/reporting.py) - Calculate mechanical-cognitive variance and inject it as a strict extension into `report_context`.
- [ ] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) - Define criteria prompts for the `step_xai_reporter` to verify the alignment between mechanical anchors and cognitive evaluations.

### Context (Read-Only)
- [x] [xai.py](file:///c:/src/quorum/backend_v2/models/domain/xai.py)
- [x] [variance_engine.py](file:///c:/src/quorum/backend_v2/utils/scoring/variance_engine.py)
- [x] [report.py](file:///c:/src/quorum/backend_v2/models/dtos/report.py)

---

## Technical Specifications & Architectural Invariants

> [!IMPORTANT]
> **Tripartite Rendering Boundary & Failure Isolation**:
> - The backend MUST NOT produce raw HTML or markdown components (e.g., Markdown tables) in the DTO payload. It only passes structured DTO data (`tripartite_rendering_boundary`).
> - Variance calculations and alignment verdicts must be strictly num-driven (`strict_math_display_isolation`).
> - The XAI Reporter must execute structured Pydantic DTO extraction without custom regex parsing (`llm_structured_execution_mandate`).

### Integration Loop & Variance Verification
In `generate_report_hook` (`reporting.py`):
1. Extract `llm_authenticity_score` from `step_detector` (Performativity Output). If `step_detector` is missing, default to `3.0` (as a safe baseline, but crash Fast if required fields inside existing models are corrupted).
2. Extract the number of performative fill phrases from `step_profiler` / `step_linguistics`.
3. Invoke `calculate_mechanical_cognitive_variance(authenticity_score, performative_phrases_count)` from `variance_engine.py` to obtain `variance_score` and `alignment_verdict`.
4. Construct a `VarianceValidationExtension` instance:
   ```python
   ext = VarianceValidationExtension(
       mechanical_metric_ref="performative_patterns_count",
       cognitive_metric_ref="authenticity_score",
       variance_score=variance_score,
       alignment_verdict=alignment_verdict
   )
   ```
5. Dynamically inject the extension into the polymorphic `output_extensions` list in `report_context` to make it accessible to the UI.

---

## Detailed Milestones

### Milestone 1: Reporting Hook Enhancement
- **Goal**: Integrate the Variance Engine inside `generate_report_hook`.
- **Source**: Epic Phase 3, Toimenpide 1 & 3.
- **Actions**:
  1. Modify `backend_v2/hooks/reporting.py` to import `calculate_mechanical_cognitive_variance` and `VarianceValidationExtension`.
  2. Implement extraction of the performativity authenticity score and performative fillers count from step states.
  3. Execute the variance check and inject the `VarianceValidationExtension` into the context extensions mapping.

### Milestone 2: XAI Reporter Prompts Seed Evolution
- **Goal**: Hardcode alignment rules into XAI Reporter criteria block prompts.
- **Source**: Epic Phase 3, Toimenpide 2.
- **Actions**:
  1. Locate `criteria_block_ids` for `step_xai_reporter` in `seed_data.json`.
  2. Modify the criteria block system prompts to instruct the LLM to cross-examine whether the Causal Analyst and Performativity Detector were properly grounded in the mekaaniset ankkurit.
  3. Run seeder to apply configuration:
     ```powershell
     uv run python backend_v2/seed/run_seed.py local
     ```

---

## Testing & Quality Gate Plan

### Integration Tests
- Create `tests/integration/test_xai_reporter_integration.py` which mocks step outputs and runs `generate_report_hook` natively to verify that `VarianceValidationExtension` is generated, type-validates cleanly, and has correct values.

### Execution Command
```powershell
uv run pytest tests/integration/test_xai_reporter_integration.py
uv run python scripts/backend_audit_loop.py backend_v2/hooks/reporting.py --test
```

---

## Session Handover
To execute this step iteratively in a new session, run:
```powershell
/tier2-execute --plan="docs/epic/tasks_EPIC_57/phase3_xai_reporter_synthesis.md"
```
