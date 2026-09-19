# Direct-ID Relational Architecture & Heuristic Prefix Eradication Tracker

## Plan Context
- Source Plan: `@[C:\Users\risto\.gemini\antigravity-ide\brain\ddaa7db7-f5a0-4cd9-8443-e2fbf66a2bd6\implementation_plan.md]`
- Status: In Progress

## Tasks Checklist

- [x] **Milestone 1: Core Directives, System Rules & Knowledge Base SSOT**
  - [x] Strengthen `<rule_block id="ban_heuristic_identifier_matching">` in `AGENTS.md`
  - [x] Synchronize `00-antigravity-core.md` with catastrophic ban and add `<rule_block id="positive_id_set_filtering_mandate">`
  - [x] Add `<rule_block id="direct_id_relational_mandate">` in `01-python-backend.md`
  - [x] Add `<rule_block id="positive_id_relations_and_zero_heterogeneous_bags">` in `ki_zero_permissive_typing.md`
  - [x] Verify formatting and git checkpoint

- [x] **Milestone 2: Domain Model Separation (`Workflow`)**
  - [x] Add `get_allowed_prompt_block_targets` returning strictly concrete `blk_...` PromptBlock IDs in `backend_v2/models/domain/workflow.py`
  - [x] Refactor `get_allowed_layout_targets` to compose `get_allowed_prompt_block_targets` with `TargetBlockType`
  - [x] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/workflow.py --test`
  - [x] Git checkpoint

- [x] **Milestone 3: Studio Service & Resumption Service Modernization**
  - [x] Update `output_profile_service.py` to call `target_wf.get_allowed_prompt_block_targets(all_steps)` directly (eradicate `startswith("glb_")`)
  - [x] Update `test_output_profile_service.py` mock to bind `get_allowed_prompt_block_targets`
  - [x] Modernize `resumption_service.py` to verify `workflow_step_ids.issubset(record.step_states.keys())` (eradicate `sys_` and `system.rag.preflight` prefix checks)
  - [x] Run quality gates on both services and add ISTQB negative tests
  - [x] Git checkpoint

- [x] **Milestone 4: Matrix Domain Parser Cleanups & Strict Hydration**
  - [x] Modernize payload parsing with `TraceMatrixPayloadDTO.model_validate` (eradicate duck-typing & `# noqa: QGR012`)
  - [x] Eradicate lazy fallback chaining on `profile_syntheses`
  - [x] Hydrate step evals into `dict[str, AtomResultDTO]` (eradicate duck-typing & `# noqa: QGR012`)
  - [x] Modernize `input_mappings` resolution via direct dot notation and positive key filtering (eradicate `elif not mapped_val.startswith("$")` and `# noqa: QGR012`)
  - [x] Expand `test_matrix_domain_parser.py` with positive `expected_inputs_map` and ISTQB negative partitions
  - [x] Run quality gate on `matrix_domain_parser.py`
  - [x] Git checkpoint

- [x] **Milestone 5: SourceDocumentPacker & Orchestrator LLM Strategy Modernization**
  - [x] Create `ContextTargetFilterDTO` in `source_document_packer.py`
  - [x] Refactor `resolve_context_targets(input_mappings)` returning `ContextTargetFilterDTO`
  - [x] Modernize `pack()` signature (eradicate `inputs_payload: Any`, `list[Any]`, and legacy `allowed_keys` shim)
  - [x] Modernize filtering to inspect `ContextTargetFilterDTO` directly (eradicate `not k.startswith("$steps")`)
  - [x] Fix Python 2 exception syntax (`except (TypeError, ValueError):`) and variable scoping (`item.block_id`)
  - [x] Modernize `llm.py` caller site
  - [x] Modernize `test_source_document_packer.py` and implement ISTQB negative boundary tests
  - [x] Run quality gate on `source_document_packer.py` and `llm.py`
  - [x] Git checkpoint

- [x] **Milestone 6: PrintableSourcesAdapter Sanitization Modernization**
  - [x] Modernize internal step reference filtering using `EntityPrefix.STEP_REFERENCE` while preserving Harvard academic citations
  - [x] Run quality gate on `printable_sources_adapter.py`
  - [x] Git checkpoint

- [ ] **Milestone 7: Global Completion & Regression Verification**
  - [ ] Run full test suite regression across all modified components
  - [ ] Final audit reporting and session wrap-up
