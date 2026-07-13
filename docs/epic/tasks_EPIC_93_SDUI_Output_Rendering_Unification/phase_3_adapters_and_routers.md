# Phase 3: Universal Output Adapters & Synthesis Integration

## Objective
Implement Part 1, Section 3 of Epic 93 (Universaali Tulostus). We will wire the headless `ReportDataDto` directly to the output ports (SDUI, PDF, REST API) and shift Synthesis Generation entirely into the Pipeline A (DAG).

## Architectural Constraints (Fail-Fast & Zero-Compromise)
- **Strict Data Contracts:** Only `ReportDataDto` is the valid SSOT payload.
- **No HTML/Markdown in DTOs:** Synthesis must generate purely structured data (`GlobalSynthesisDTO`) via Pydantic model enforcing.
- **Topological Validity:** Synthesis step in the DAG must strictly depend on extraction and the `MatrixReducer`.

## Execution Steps

### 1. Refactor MatrixReducer into the DAG lifecycle
Currently, Phase 2 injected `MatrixReducer` at the very end of `DAGExecutor.execute_workflow()`. However, the Synthesis LLM (which is a node in the DAG) needs this reduced matrix as input.
- **Action**: Modify `backend_v2/services/orchestrator/dag_executor.py`. Move the `MatrixReducer` logic either into a pre-synthesis lifecycle hook OR implement it inside `LogicNodeStrategy` so that it emits the `LightweightMatrixDTO` into the event trace before the `synthesis_generation` step executes.

### 2. Update `seed_data.json` (DAG Synthesis Integration)
- **Action**: Add a new `prompt_block` with ID `synthesis_generation` to `backend_v2/seed/seed_data.json`.
  - Type: `llm`
  - Output Schema: Maps to `GlobalSynthesisDTO` (executive_summary, urgency_level).
- **Action**: Update the target `workflows` in `seed_data.json` to include the `synthesis_generation` step, declaring a dependency on the extraction steps and the matrix reducer.

### 3. Wire API Routers and Execution Service
- **Action**: Update `backend_v2/services/execution.py` to strip out calls to the legacy `text_consolidation_hook` and `generate_report_hook` (if not fully deleted in Phase 4 yet).
- **Action**: Route the SDUI endpoint `/sdui` in `executions.py` to use `sdui_mapper_service.py` to convert `ReportDataDto` into `ReportView`.
- **Action**: Route the PDF endpoint `/render_pdf` to use the modernized `pdf_generator.py` (updated in Phase 1) which accepts `ReportDataDto`.

## Verification
- Run `backend_audit_loop.py` to verify typing (`mypy`) and formatting (`ruff`).
- Execute a test workflow to ensure the DAG successfully invokes the `synthesis_generation` step, returning `GlobalSynthesisDTO` inside the final `ReportDataDto`.
