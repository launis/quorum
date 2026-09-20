# Phase 3: Phase 1 to Phase 2 Boundary & Synthesis DTO Hardening

**Overview:** Hardening the boundary between Phase 1 matrix evaluation and Phase 2 synthesis reporting. Eradicate dummy packet generation and the `[NO_BLOCK]` sentinel in `TwoPassAtomizer`, enforce strongly typed `list[EvaluatedAtomDTO]` stratification in `SynthesisPayloadCompressor`, establish `DataStarvationEvent` and `NodeExecutionUpdateDTO` in `backend_v2/events/domain_events.py`, package `SynthesisDistillationDTO` in `SynthesisDistiller`, eliminate silent exception swallowing across orchestrator engines (`synthesis_engine.py`, `tda_engine.py`), and eradicate 100% of dynamic reflection (`getattr`, `hasattr`, `object.__setattr__`) across worker and synthesis test suites.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 3: Phase 1 to Phase 2 Boundary & Synthesis DTO Hardening
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295]
- `[MODIFY]` @[backend_v2/workers/synthesis_reducers.py#L54-L91]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py#L179-L381]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_reducer.py#L22-L228]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234]
- `[MODIFY]` @[backend_v2/workers/synthesis_tasks.py#L120-L205]
- `[MODIFY]` @[backend_v2/workers/variance_synthesis.py#L48-L222]
- `[NEW]` @[backend_v2/events/domain_events.py]
- `[MODIFY]` @[backend_v2/models/dtos/synthesis.py#L27-L41]
- `[MODIFY]` @[backend_v2/models/dtos/atom_result.py#L146-L175]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis.py#L27-L40]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py#L1155-L1213]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_proxy.py#L7-L31]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py#L94-L164]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py#L25-L47]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py#L16-L41]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 2 established typed IngressInputValue, EvaluatedAtomDTO, and frozen theory/schema manifests.</action>
    <action>Look forward: Verify that Phase 4 hook pipelines consume typed synthesis outputs and domain events without reflection.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/03_placeholder_phase3.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>TwoPassAtomizer._calculate_packets in @[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491] returns empty list [] when not block_keys, completely demolishing the NO_BLOCK dummy sentinel.</item>
    <item>TwoPassAtomizer.execute_phase_0, execute_phase_1, and execute_phase_1_drafts short-circuit immediately on empty packets with zero LLM API calls, returning empty models and zero TokenUsage.</item>
    <item>SynthesisPayloadCompressor.compress_synthesis_payload and inner _prune_and_stratify_evaluations in @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295] accept list[EvaluatedAtomDTO], access item.status, item.exact_quotes, item.atom_id, and eradicate silent except (AttributeError, TypeError): pass on line 291.</item>
    <item>[NEW] @[backend_v2/events/domain_events.py] defines DataStarvationEvent and NodeExecutionUpdateDTO under ConfigDict(strict=True, frozen=True, extra="forbid").</item>
    <item>SynthesisDistillationDTO is defined in @[backend_v2/models/dtos/synthesis.py#L27-L41] and emitted by synthesis_distiller_hook in @[backend_v2/services/orchestrator/synthesis_distiller.py#L179-L381] as a strongly typed, frozen DTO with zero naked dicts.</item>
    <item>MatrixReducer.reduce_matrix in @[backend_v2/services/orchestrator/matrix_reducer.py#L22-L228] and SynthesisEngine in @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240] / TDAEngine in @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234] eliminate silent exception swallowing (except (TypeError, KeyError): pass) in favor of Fail-Fast validation.</item>
    <item>SynthesisReducers.handle_starvation_if_detected in @[backend_v2/workers/synthesis_reducers.py#L54-L91] validates DataStarvationEvent directly, eliminating TypeAdapter(dict[str, Any]) and Python 2 comma syntax.</item>
    <item>VarianceSynthesis.build_variance_metrics_and_task in @[backend_v2/workers/variance_synthesis.py#L48-L222] extracts metrics using LinguisticsResultDTO and LightweightMatrixOutput without QGR016 banned ternaries or silent (None, None) fallbacks.</item>
    <item>Worker and synthesis test suites (@[backend_v2/tests/unit/test_worker_synthesis.py#L27-L40], @[backend_v2/tests/unit/test_worker.py#L1155-L1213], @[backend_v2/tests/unit/test_worker_proxy.py#L7-L31], @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py#L94-L164], @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py#L25-L47], @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py#L16-L41]) eradicate 100% of dynamic reflection (getattr, hasattr, object.__setattr__).</item>
    <item>Quality gates pass: uv run python scripts/backend_audit_loop.py on all touched modules with >90% coverage and zero fatal AST guardrail violations.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT modify SDUI presentation models or Flutter UI during Phase 3 (reserved for Phase 6; includes GenericStatusResponseDTO).</forbidden>
    <forbidden>Do NOT alter matrix hook execution pipeline or result projector during Phase 3 (reserved for Phase 4).</forbidden>
    <forbidden>Do NOT modify prompt compiler or state reducer during Phase 3 (reserved for Phase 5).</forbidden>
    <forbidden>Do NOT introduce fallback dictionary parsing in Pydantic validators.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py#L54-L91]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py#L179-L381]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py#L22-L228]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234]</backend>
    <backend>@[backend_v2/workers/synthesis_tasks.py#L120-L205]</backend>
    <backend>@[backend_v2/workers/variance_synthesis.py#L48-L222]</backend>
    <backend>[NEW] @[backend_v2/events/domain_events.py]</backend>
    <backend>@[backend_v2/models/dtos/synthesis.py#L27-L41]</backend>
    <backend>@[backend_v2/models/dtos/atom_result.py#L146-L175]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis.py#L27-L40]</backend>
    <backend>@[backend_v2/tests/unit/test_worker.py#L1155-L1213]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_proxy.py#L7-L31]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py#L94-L164]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py#L25-L47]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py#L16-L41]</backend>
  </touched_artifacts>

  <pre_implementation_cleanups>
    <cleanup id="C1" target="@[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491]">
      <description>Demolish [NO_BLOCK] dummy sentinel and eradicate LLM calls on text lacking block keys (Lines 54-55).</description>
      <remedy>Return empty list [] when not block_keys; short-circuit immediately in execute_phase_0, execute_phase_1, and execute_phase_1_drafts.</remedy>
    </cleanup>
    <cleanup id="C2" target="@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295]">
      <description>Eradicate silent except (AttributeError, TypeError): pass (Line 291) and ev.get('atom_id') or ev.get('tda_id') (Line 195).</description>
      <remedy>Raise structured AppException(ErrorCodes.VALIDATION_FAILED) and access canonical ev.atom_id via static dot notation.</remedy>
    </cleanup>
    <cleanup id="C3" target="@[backend_v2/workers/synthesis_reducers.py#L54-L91]">
      <description>Eradicate Python 2 comma exception except OSError, ValidationError, ValueError, KeyError: (Line 354), TypeAdapter(dict[str, Any]) (Line 222), and silent except: pass (Lines 74, 285).</description>
      <remedy>Catch with PEP 3110 syntax except (OSError, ValidationError, ValueError, KeyError): and validate DataStarvationEvent directly without dict adapters.</remedy>
    </cleanup>
    <cleanup id="C4" target="@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240]">
      <description>Eradicate silent except (TypeError, KeyError): pass (Lines 99, 151).</description>
      <remedy>Fail-Fast raising AppException(ErrorCodes.VALIDATION_FAILED) on corrupted blackboard or matrix reducer payload.</remedy>
    </cleanup>
    <cleanup id="C5" target="@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234]">
      <description>Eradicate silent except (TypeError, KeyError): pass (Line 92).</description>
      <remedy>Fail-Fast raising AppException(ErrorCodes.VALIDATION_FAILED) on corrupted blackboard payload.</remedy>
    </cleanup>
    <cleanup id="C6" target="@[backend_v2/workers/variance_synthesis.py#L48-L222]">
      <description>Eradicate QGR016 banned ternaries (Lines 158, 161, 162), TypeAdapter(dict[str, Any]) (Lines 116, 129), silent except: pass (Lines 124, 134), and return None, None (Line 141).</description>
      <remedy>Validate LinguisticsResultDTO and LightweightMatrixOutput directly; raise AppException(ErrorCodes.VALIDATION_FAILED) if required metrics are missing.</remedy>
    </cleanup>
    <cleanup id="C7" target="@[backend_v2/workers/synthesis_tasks.py#L120-L205]">
      <description>Eradicate distilled_data: dict[str, Any] (Line 127) and QGR016 banned ternaries (Lines 134, 135, 289, 290, 331).</description>
      <remedy>Type distilled_data as SynthesisDistillationDTO and access language and title_map via static dot notation.</remedy>
    </cleanup>
    <cleanup id="C8" target="@[backend_v2/tests/unit/test_worker_synthesis.py#L27-L40]">
      <description>Eradicate getattr(payload, 'profile_syntheses', None) (Line 32) and hasattr(v, 'model_dump') (Line 38).</description>
      <remedy>Assert directly on typed ExecutionUpdateDTO and RenderedSynthesisCache using static dot notation and isinstance(v, BaseModel).</remedy>
    </cleanup>
    <cleanup id="C9" target="@[backend_v2/tests/unit/test_worker.py#L1155-L1213]">
      <description>Eradicate 8x getattr/hasattr/get fallback chains (Lines 1191-1207, 1418, 1525).</description>
      <remedy>Assert directly against typed ExecutionUpdateDTO.profile_syntheses and saved_cache.data_starvation fields.</remedy>
    </cleanup>
    <cleanup id="C10" target="@[backend_v2/tests/unit/test_worker_proxy.py#L7-L31]">
      <description>Eradicate hasattr/getattr inspection of module symbols (Lines 9, 18, 19, 36, 47).</description>
      <remedy>Inspect f.__name__ on WorkerSettings.functions and use direct identity assertion rw.WorkerSettings is WorkerSettings.</remedy>
    </cleanup>
    <cleanup id="C11" target="@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py#L94-L164]">
      <description>Eradicate object.__setattr__(state, 'inputs', 'invalid_inputs_string') (Line 191) and state_delta['distilled_inputs'] subscripting.</description>
      <remedy>Construct invalid HookState directly via typed constructor and access typed SynthesisDistillationDTO properties.</remedy>
    </cleanup>
  </pre_implementation_cleanups>

  <five_column_directives>
| Target Symbol / Boundary [File Path &amp; Exact Symbol] | Banned Anti-Pattern [Exact duct-tape, .get(), reflection, silent error suppression] | Approved Modern Invariant [Exact DTO, Fail-Fast AppException, typed dot notation] | Demolition &amp; Pruning Scope [Exact dead sentinel, fallback key, or loose mapping] | Mathematical Proof Anchor [Exact unit test, ISTQB partition, exception assert] |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491]` (`_calculate_packets`, `execute_phase_0`, `execute_phase_1`, `execute_phase_1_drafts`) | `packets.append(("[NO_BLOCK]", "[NO_BLOCK]", []))` dummy packet generation forcing LLM execution on unformatted inputs | Return empty list `[]` when `not block_keys`; short-circuit immediately in `execute_phase_0`, `execute_phase_1`, and `execute_phase_1_drafts` returning empty models and zero `TokenUsage` | Demolish `[NO_BLOCK]` sentinel completely from codebase | Unit test in `test_two_pass_atomizer.py` verifying `_calculate_packets("") == []` and zero LLM calls dispatched |
| `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295]` (`compress_synthesis_payload`, `_prune_and_stratify_evaluations`, `_strip_heavy_keys`) | `evals: list[dict[str, Any]]`, `item.get("status")`, `item.get("exact_quotes") or []`, `ev.get("atom_id") or ev.get("tda_id")`, and `except (AttributeError, TypeError): pass` (Line 291) | Accept `list[EvaluatedAtomDTO]`, access `item.status`, `item.exact_quotes`, `item.atom_id` via static dot notation; Fail-Fast raising `AppException(ErrorCodes.VALIDATION_FAILED)` on invalid objects | Demolish dictionary `.get()` fallback lookups, key guessing, and silent error swallowing | Unit tests in `test_synthesis_payload_compressor.py` asserting typed stratification and `AppException` on invalid objects |
| `@[backend_v2/events/domain_events.py]` [NEW] | Loose dictionary event passing and ad-hoc event bags | Define `DataStarvationEvent` with `event_type: Literal["starvation"] = "starvation"` and `NodeExecutionUpdateDTO` under `ConfigDict(strict=True, frozen=True, extra="forbid")` | Eradicate untyped event payload instantiation | Unit test verifying Pydantic V2 validation rejection of unauthorized keys with `extra="forbid"` |
| `@[backend_v2/models/dtos/synthesis.py#L27-L41]` | Returning naked dictionary `delta` in synthesis hook state | Define `SynthesisDistillationDTO` with fields `distilled_inputs`, `historical_context`, `title_map`, `matrices_to_explain`, `source_alias_map`, `output_profile_id`, `target_locale`, `language`, `alias_registry`, `max_extensions` under `ConfigDict(strict=True, frozen=True, extra="forbid")`, with mapping helpers | Demolish raw dict delta construction in `synthesis_distiller.py` | Unit test in `test_synthesis_distiller_wiring.py` asserting `SynthesisDistillationDTO` payload integrity |
| `@[backend_v2/services/orchestrator/synthesis_distiller.py#L179-L381]` (`synthesis_distiller_hook`) | `inputs.dynamic_inputs.get("steps")`, `except (ValidationError, TypeError, ValueError): pass` (Line 244), raw dictionary `delta` construction (Lines 368-380) | Direct typed step traversal via `inputs.dynamic_inputs`; Fail-Fast `raise AppException(ErrorCodes.VALIDATION_FAILED)` on invalid steps; return `HookDeltaDTO(delta=SynthesisDistillationDTO(...).model_dump())` and typed `SynthesisDistillationDTO` | Delete silent exception suppression and untyped dictionary construction | Unit tests in `test_synthesis_distiller_wiring.py` passing with zero reflection |
| `@[backend_v2/services/orchestrator/matrix_reducer.py#L22-L228]` (`reduce_matrix`) | `_dict_adapter = TypeAdapter(dict[str, Any])`, `raw_content = evt.content.model_dump()`, and `content.get("results")` dictionary laundering | Direct typed inspection of `StepOutputDTO` or `AtomResultDTO` from `evt.content`; direct access `evt.content.results` | Delete `_dict_adapter` and `.get("results")` lookups | Unit tests in `test_matrix_reducer.py` asserting typed atom extraction without dict adapters |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240]` (`execute`) | `except (TypeError, KeyError): pass` (Lines 99, 151) | Direct typed inspection of `GlobalAtomBlackboard` and `matrix_reducer_output`; Fail-Fast `raise AppException(ErrorCodes.VALIDATION_FAILED)` on malformed payloads; unconditionally emit `DataStarvationEvent` when `total_atoms <= settings.synthesis_starvation_threshold` | Eradicate silent exception catching | Unit test asserting `DataStarvationEvent` emission when `total_atoms == 0` and Fail-Fast on corrupted request |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234]` (`execute`) | `except (TypeError, KeyError): pass` (Line 92) | Inspect blackboard via typed models; Fail-Fast `raise AppException(ErrorCodes.VALIDATION_FAILED)` | Eradicate silent exception catching | Unit test asserting Fail-Fast on corrupted blackboard |
| `@[backend_v2/workers/synthesis_reducers.py#L54-L91]` (`extract_user_role_from_trace`, `handle_starvation_if_detected`, `handle_synthesis_failure_state`, `recover_trace_telemetry`) | `TypeAdapter(dict[str, Any]).validate_python` (Lines 66, 222), `t_content.get("event_type") == "starvation"`, silent `except: pass` (Lines 74, 285), and Python 2 comma syntax `except OSError, ValidationError, ValueError, KeyError:` (Line 354) | Inspect `DataStarvationEvent` directly via `TypeAdapter(DataStarvationEvent).validate_python` or `isinstance(trace_evt.content, DataStarvationEvent)`; PEP 3110 exception syntax; Fail-Fast structured error logging | Eradicate `TypeAdapter(dict[str, Any])` and comma exception syntax | Unit tests in `test_worker.py` asserting 100% deterministic starvation short-circuiting |
| `@[backend_v2/workers/synthesis_tasks.py#L120-L205]` (`create_matrix_sections_tasks`, `create_row_explanations_task`) | `distilled_data: dict[str, Any]`, ternary lazy fallbacks (Lines 134, 135, 289, 290, 331) | Accept `distilled_data: SynthesisDistillationDTO`; access `distilled_data.language` and `distilled_data.title_map` via static dot notation; resolve settings and metadata directly | Demolish loose dictionary parameter and ternary fallback lookups | Unit tests in `test_worker_synthesis.py` passing with typed distillation inputs |
| `@[backend_v2/workers/variance_synthesis.py#L48-L222]` (`build_variance_metrics_and_task`) | `TypeAdapter(dict[str, Any])` (Lines 116, 129), silent `except: pass` (Lines 124, 134), silent `return None, None` (Line 141), and QGR016 banned ternaries (Lines 158, 161, 162) | Validate `LinguisticsResultDTO` and `LightweightMatrixOutput` directly; raise `AppException(ErrorCodes.VALIDATION_FAILED)` if required metrics are missing | Demolish untyped dictionary adapters, silent pass blocks, and fallback returns | Unit tests in `test_worker_synthesis.py` verifying metric extraction without reflection |
| `@[backend_v2/tests/unit/test_worker_synthesis.py#L27-L40]` &amp; `@[backend_v2/tests/unit/test_worker.py#L1155-L1213]` | `getattr(payload, "profile_syntheses", None)`, `hasattr(v, "model_dump")`, 8x `getattr`/`hasattr`/`get` fallback chains in `test_worker.py` (Lines 1191-1207, 1418, 1525) | Static dot-notation access on typed `ExecutionUpdateDTO` and `RenderedSynthesisCache` models (`call_payload.profile_syntheses["prof_..."]`, `saved_cache.data_starvation.event_type`) | Eradicate reflection and dictionary fallbacks across test assertions | Tests pass 100% with zero QGR001 reflection warnings under `_ast_guardrails.py` |
| `@[backend_v2/tests/unit/test_worker_proxy.py#L7-L31]` &amp; `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py#L94-L164]` | `hasattr`/`getattr` calls in `test_worker_proxy.py` and `object.__setattr__(state, "inputs", ...)` (Line 191) in `test_synthesis_distiller_wiring.py` | Inspect `f.__name__` on functions, `dir(worker_mod)` or direct identity assertions; instantiate valid immutable `HookState` objects instead of using `object.__setattr__` | Eradicate `object.__setattr__` and reflection calls | Clean execution of `test_worker_proxy.py` and `test_synthesis_distiller_wiring.py` |
  </five_column_directives>

  <step id="3.1" name="Two-Pass Atomizer Empty Packet Short-Circuit &amp; Demolition of [NO_BLOCK] Sentinel">
    <action>Refactor @[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491]:</action>
    <action>- In _calculate_packets: if not block_keys, return empty list [] instead of constructing dummy [("[NO_BLOCK]", "[NO_BLOCK]", [])] packet envelopes.</action>
    <action>- In execute_phase_0: if not packets, return GlobalOntologyMap(entities=[], macro_rules=[]) and TokenUsage() immediately without dispatching TaskGroup or caching calls.</action>
    <action>- In execute_phase_1: if not packets, return ([], TokenUsage()) immediately without dispatching TaskGroup or caching calls.</action>
    <action>- In execute_phase_1_drafts: if not packets, return DraftAtomList(atoms=[], dlq_status=None) and TokenUsage() immediately without dispatching TaskGroup or caching calls.</action>
    <demolish>REMOVE: `NO_BLOCK` sentinel in @[backend_v2/services/orchestrator/two_pass_atomizer.py#L35-L491]. REPLACE WITH: empty packet list `[]` and immediate zero-LLM short-circuiting.</demolish>
  </step>

  <step id="3.2" name="Synthesis Payload Compressor &amp; EvaluatedAtomDTO Strict Stratification">
    <action>Refactor @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295]:</action>
    <action>- Ensure EvaluatedAtomDTO in @[backend_v2/models/dtos/atom_result.py#L146-L175] contains exact_quotes: Annotated[list[str], Field(default_factory=list)].</action>
    <action>- Update _prune_and_stratify_evaluations to accept evals: list[EvaluatedAtomDTO] | list[dict[str, Any]], accessing item.status, item.exact_quotes, item.atom_id via static dot-notation.</action>
    <action>- Eradicate ev.get("atom_id") or ev.get("tda_id"); use canonical ev.atom_id.</action>
    <action>- Eradicate silent except (AttributeError, TypeError): pass on line 291; raise structured AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <demolish>REMOVE: `except (AttributeError, TypeError): pass` in @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L295]. REPLACE WITH: Fail-Fast AppException(ErrorCodes.VALIDATION_FAILED).</demolish>
  </step>

  <step id="3.3" name="Domain Events SSOT &amp; DataStarvationEvent / NodeExecutionUpdateDTO Packaging">
    <action>Create [NEW] @[backend_v2/events/domain_events.py]:</action>
    <action>- Define DataStarvationEvent inheriting from V2CoreBase with event_type: Literal["starvation"] = "starvation", total_atoms: int, reason: str, ConfigDict(strict=True, frozen=True, extra="forbid").</action>
    <action>- Define NodeExecutionUpdateDTO inheriting from V2CoreBase with status, step_states, error, execution_trace, context_variables, frozen_context, steps, ConfigDict(strict=True, frozen=True, extra="forbid").</action>
    <action>- Re-export DataStarvationEvent in @[backend_v2/models/dtos/base.py] for backward compatibility.</action>
  </step>

  <step id="3.4" name="Synthesis Distiller Hook &amp; SynthesisDistillationDTO Integration">
    <action>Define SynthesisDistillationDTO in @[backend_v2/models/dtos/synthesis.py#L27-L41]:</action>
    <action>- Model fields: distilled_inputs: str, historical_context: str | None = None, title_map: dict[str, str] = Field(default_factory=dict), matrices_to_explain: list[MatrixExplanationContextDTO] = Field(default_factory=list), source_alias_map: dict[str, str] = Field(default_factory=dict), output_profile_id: str | None = None, target_locale: str = "en", language: str = "en", alias_registry: dict[str, str] = Field(default_factory=dict), max_extensions: int = 5, ConfigDict(strict=True, frozen=True, extra="forbid").</action>
    <action>- Implement __getitem__, __contains__, keys(), values(), items() mapping methods for zero-regression compatibility.</action>
    <action>Refactor @[backend_v2/services/orchestrator/synthesis_distiller.py#L179-L381]:</action>
    <action>- Replace inputs.dynamic_inputs.get("steps") with typed traversal.</action>
    <action>- Eradicate except (ValidationError, TypeError, ValueError): pass on line 244; raise structured AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>- Return HookResult(success=True, state_delta=HookDeltaDTO(delta=SynthesisDistillationDTO(...).model_dump(mode="json"))).</action>
    <demolish>REMOVE: raw dictionary delta construction in @[backend_v2/services/orchestrator/synthesis_distiller.py#L179-L381]. REPLACE WITH: typed SynthesisDistillationDTO packaging.</demolish>
  </step>

  <step id="3.5" name="Matrix Reducer &amp; Orchestrator Engines Fail-Fast Hardening">
    <action>Refactor @[backend_v2/services/orchestrator/matrix_reducer.py#L22-L228]:</action>
    <action>- Type results extraction using StepOutputDTO instead of _dict_adapter.validate_python and content.get("results").</action>
    <action>Refactor @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240]:</action>
    <action>- Eradicate except (TypeError, KeyError): pass on lines 99 and 151; raise AppException(ErrorCodes.VALIDATION_FAILED) on corrupted payload.</action>
    <action>- Verify that total_atoms &lt;= settings.synthesis_starvation_threshold unconditionally emits DataStarvationEvent.</action>
    <action>Refactor @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234]:</action>
    <action>- Eradicate except (TypeError, KeyError): pass on line 92; raise AppException(ErrorCodes.VALIDATION_FAILED) on corrupted blackboard.</action>
    <demolish>REMOVE: `except (TypeError, KeyError): pass` in @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240] and @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L234]. REPLACE WITH: typed model inspection and Fail-Fast AppException(ErrorCodes.VALIDATION_FAILED).</demolish>
  </step>

  <step id="3.6" name="Background Worker Synthesis Tasks, Reducers &amp; Variance Synthesis Hardening">
    <action>Refactor @[backend_v2/workers/synthesis_reducers.py#L54-L91]:</action>
    <action>- In extract_user_role_from_trace: eradicate TypeAdapter(dict[str, Any]) and except ValidationError, TypeError, ValueError: pass; inspect LightweightMatrixOutput directly.</action>
    <action>- In handle_starvation_if_detected: eradicate TypeAdapter(dict[str, Any]) and t_content.get("event_type") == "starvation"; inspect DataStarvationEvent directly.</action>
    <action>- In handle_synthesis_failure_state: replace Python 2 comma syntax except OSError, ValidationError, ValueError, KeyError: on line 354 with PEP 3110 syntax except (OSError, ValidationError, ValueError, KeyError):.</action>
    <action>- In recover_trace_telemetry: structured error logging and Fail-Fast.</action>
    <action>Refactor @[backend_v2/workers/synthesis_tasks.py#L120-L205]:</action>
    <action>- Accept distilled_data: SynthesisDistillationDTO; access distilled_data.language and distilled_data.title_map via static dot notation.</action>
    <action>- Eradicate QGR016 banned ternaries on lines 134, 135, 289, 290, 331.</action>
    <action>Refactor @[backend_v2/workers/variance_synthesis.py#L48-L222]:</action>
    <action>- Migrate linguistic and authenticity score extraction to strongly typed LinguisticsResultDTO and LightweightMatrixOutput models.</action>
    <action>- Raise structured AppException(ErrorCodes.VALIDATION_FAILED) if required metrics are missing; eradicate silent return None, None on line 141 and QGR016 banned ternaries on lines 158, 161, 162.</action>
    <demolish>REMOVE: `TypeAdapter(dict[str, Any]).validate_python(trace_evt.content)` and `t_content.get("event_type") == "starvation"` in @[backend_v2/workers/synthesis_reducers.py#L54-L91]. REPLACE WITH: direct DataStarvationEvent inspection.</demolish>
    <demolish>REMOVE: `distilled_data: dict[str, Any]` in @[backend_v2/workers/synthesis_tasks.py#L120-L205]. REPLACE WITH: strongly typed SynthesisDistillationDTO.</demolish>
  </step>

  <step id="3.7" name="Test Suites Modernization &amp; Co-Located Dynamic Reflection Eradication">
    <action>Refactor @[backend_v2/tests/unit/test_worker_synthesis.py#L27-L40]:</action>
    <action>- Eradicate getattr(payload, "profile_syntheses", None) (Line 32) and hasattr(v, "model_dump") (Line 38); assert directly using dot notation and isinstance(v, BaseModel).</action>
    <action>Refactor @[backend_v2/tests/unit/test_worker.py#L1155-L1213]:</action>
    <action>- Eradicate 8x getattr/hasattr/get fallback chains (Lines 1191-1207, 1418, 1525); assert directly against typed ExecutionUpdateDTO and RenderedSynthesisCache fields.</action>
    <action>Refactor @[backend_v2/tests/unit/test_worker_proxy.py#L7-L31]:</action>
    <action>- Eliminate hasattr/getattr calls; inspect f.__name__ on WorkerSettings.functions and assert rw.WorkerSettings is WorkerSettings.</action>
    <action>Refactor @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py#L94-L164]:</action>
    <action>- Eliminate object.__setattr__ mutation (Line 191) and state_delta dict subscripting; assert against typed properties.</action>
    <action>Update @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py#L25-L47] and @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py#L16-L41] for typed EvaluatedAtomDTO and SynthesisDistillationDTO contracts.</action>
    <action>Add unit test asserting _calculate_packets("") returns [] and TwoPassAtomizer makes zero LLM calls on text lacking block markers.</action>
    <action>Add unit test asserting DataStarvationEvent emitted by SynthesisEngine is detected 100% by synthesis_reducers.py.</action>
  </step>

  <validation_gate>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/two_pass_atomizer.py --test</action>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/workers/synthesis_reducers.py --test</action>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test</action>
  </validation_gate>
</execution_protocol>
```
