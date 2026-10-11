# Phase 2: Configuration, DTOs, Studio Foundation & Parity

**Overview:** Establish the typed settings, domain enums, explicit error codes, and immutable Pydantic V2 DTOs for the causal discovery engine. Extend `backend_v2/settings.py` with sliding window, atom limit, dampening, and packet size parameters. Register `StepType.CAUSAL_DISCOVERY` in `backend_v2/models/enums.py` and explicit causal `ErrorCodes` in `backend_v2/exceptions.py`. Update `Step.validate_step_consistency` in `backend_v2/models/domain/step.py` to allow causal discovery steps without criteria matrices while enforcing `extraction_protocol_block_id` and `cognitive_tier`. Add `StepRule.causal_source_step_id` with `@model_validator` cross-field dependency validation and mirror in Dart `StepRule`. Register `StepType.CAUSAL_DISCOVERY` in `NODE_STRATEGY_REGISTRY`. Create 8 immutable Pydantic V2 DTOs in `backend_v2/models/dtos/causal_discovery.py` with cross-field referential integrity and mathematical identity validators, extend `StepPayloadValue` in `backend_v2/models/dtos/step_output.py`, and add compile-time localization keys in `client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb`.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 2: Configuration, DTOs, Studio Foundation & Parity

**Target Files:**
- `[MODIFY] @[backend_v2/settings.py#L54-L924]`
- `[MODIFY] @[backend_v2/models/enums.py#L125-L129]`
- `[MODIFY] @[backend_v2/exceptions.py#L129-L314]`
- `[MODIFY] @[backend_v2/models/domain/step.py#L33-L144]`
- `[MODIFY] @[backend_v2/models/domain/step.py#L147-L188]`
- `[MODIFY] @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L176-L357]`
- `[NEW] @[backend_v2/models/dtos/causal_discovery.py]`
- `[MODIFY] @[backend_v2/models/dtos/step_output.py#L59-L73]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/workflow.dart#L50-L70]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb#L2600-L2610]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb#L1887-L1897]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py#L110-L112]`
- `[MODIFY] @[backend_v2/tests/unit/test_settings.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_step.py]`
- `[NEW] @[backend_v2/tests/unit/models/dtos/test_causal_discovery_dtos.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/settings.py#L54-L924]`, `@[backend_v2/tests/unit/test_settings.py]` | Magic constants in sliding window loops, hardcoded window sizes, fallback `getattr(settings, ...)` access. | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. Causal discovery settings are explicitly injected into `SlidingWindowLinker` without mutating existing constructor defaults (`window_size = 4, overlap = 2`). | Speculative per-domain sliding window overrides and dynamic runtime reload factories. | `Settings.model_validate({})` strict type validation in unit tests; `backend_v2/tests/unit/test_settings.py`. |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77]` | Hardcoded magic packet size default (`packet_size = 50`) embedded in method signatures. | Dynamic parameter resolution in `TwoPassAtomizer._calculate_packets`: when `packet_size` is unspecified or None, resolve dynamically via `get_settings().two_pass_atomizer_packet_size`. Calling sites retain typed `list[ChunkPacketDTO]` unpacks. | Speculative chunk packet factory classes or mutating canonical `packet_keys` field. | Unit test verifying dynamic packet size binding in `test_two_pass_atomizer.py`; `backend_audit_loop.py`. |
| `@[backend_v2/models/enums.py#L125-L129]`, `@[backend_v2/exceptions.py#L129-L314]`, `@[backend_v2/tests/unit/test_enum_parity.py#L110-L112]` | Untyped string comparisons (`self.type == "llm"`), heuristic string matching, ad-hoc string literals for block types. Casing mismatch between backend snake_case and Dart camelCase. | `StepType.CAUSAL_DISCOVERY = "causal_discovery"` in `enums.py`. Explicit ErrorCodes in `exceptions.py`: `CAUSAL_DISCOVERY_EMPTY_DOCUMENT`, `CAUSAL_DISCOVERY_CYCLE_DETECTED`, `CAUSAL_DISCOVERY_DATA_STARVATION`. Zero mutation to `TargetBlockType`. Assert 1:1 cross-language parity for `TargetBlockType` remains intact. | Granular display mode permutations (isolated anti-fluff toggles, remediations toggles), speculative block type additions. | `backend_audit_loop.py` and `test_enum_parity.py` verifying enum and exception integrity. |
| `@[backend_v2/models/domain/step.py#L33-L144]`, `@[backend_v2/models/domain/step.py#L147-L188]`, `@[client_app_v2/lib/features/studio/models/workflow.dart#L50-L70]`, `@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]`, `@[backend_v2/services/orchestrator/dag_executor.py#L176-L357]`, `@[backend_v2/tests/unit/models/domain/test_step.py]` | Permissive validation allowing empty criteria on LLM steps, untyped step chaining flags, passing atoms bypassing `global_context_vars`. Unmirrored client fields causing `UnrecognizedKeyException` under `@JsonSerializable(disallowUnrecognizedKeys: true)`. Non-opaque stripe IDs bypassing regex. | Add `StepType.CAUSAL_DISCOVERY` branch to `Step.validate_step_consistency` allowing empty `criteria_block_ids` while enforcing `extraction_protocol_block_id` and `cognitive_tier`. Declare `StepRule.causal_source_step_id` with `pattern=OPAQUE_STRIPE_ID_REGEX` and `@model_validator(mode='after')` enforcing `causal_source_step_id in self.depends_on`. Mirror `@JsonKey(name: 'causal_source_step_id') String? causalSourceStepId` on Dart `StepRule` in `workflow.dart`. Register `StepType.CAUSAL_DISCOVERY -> _build_llm_strategy` in `NODE_STRATEGY_REGISTRY`. Update `NodeExecutor.execute` to handle `step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY)`. | Separate `CausalStep` domain model subclass, separate `CausalStepRule` class, or parallel step validation pipeline. | Unit tests asserting `AppException` when `extraction_protocol_block_id` is missing or when `causal_source_step_id` is not in `depends_on`; `flutter_audit_loop.py --build`. |
| [NEW] `@[backend_v2/models/dtos/causal_discovery.py]`, `@[backend_v2/models/dtos/step_output.py#L59-L73]`, [NEW] `@[backend_v2/tests/unit/models/dtos/test_causal_discovery_dtos.py]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys, dangling edge reference vulnerabilities, and unverified scoring arithmetic. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `CausalGraphPayloadDTO` enforces cross-field referential integrity via `@model_validator(mode='after')` verifying all edge `source_id`/`target_id`, `root_cause_node_ids`, and `isolated_node_ids` exist in `nodes`. `FairScoringBreakdownDTO` enforces mathematical identity `@model_validator(mode='after')` asserting `abs(raw_penalty_points - (deduplicated_penalty_points + dampened_savings_points)) < 1e-4` and all fields non-negative. `StepPayloadValue` extended with `CausalGraphPayloadDTO` and `CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrail passing in audit loop; comprehensive unit tests in `test_causal_discovery_dtos.py`. |
| `@[client_app_v2/lib/l10n/app_en.arb#L2600-L2610]`, `@[client_app_v2/lib/l10n/app_fi.arb#L1887-L1897]` | Hardcoded strings in Flutter presentation widgets, missing localized labels for causal diagnostics. | Compile-time localization keys in `app_en.arb` and `app_fi.arb`: `causalActionCardTitle`, `causalIntactClaimsSummary`, `causalOpenInspectorAction`, `causalInspectorTitle`, `causalRootCauseBadge`, `causalCascadingFaultBadge`, `causalRemediationLabel`. | Dynamic remote translation hooks or runtime string fallback chains. | `flutter gen-l10n` compile verification; Flutter audit loop. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify `backend_v2/services/orchestrator/engines/registry.py` exists, `EngineType` enum is registered in Python and Dart, and pre-hook string checks are eradicated from `dag_executor.py`.</action>
    <action>Look forward: Verify if Phase 2 DTO definitions and settings configuration establish strict type safety for Phase 3 engine execution and Phase 4 fusion wiring.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/02_phase2_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>Centralized settings added to backend_v2/settings.py: causal_discovery_window_size (4), causal_discovery_overlap (2), causal_discovery_max_atoms_per_window (25), causal_discovery_max_total_atoms (100), causal_secondary_fault_dampening (0.25), two_pass_atomizer_packet_size (50).</item>
    <item>StepType.CAUSAL_DISCOVERY defined in backend_v2/models/enums.py.</item>
    <item>Explicit ErrorCodes added to backend_v2/exceptions.py: CAUSAL_DISCOVERY_EMPTY_DOCUMENT, CAUSAL_DISCOVERY_CYCLE_DETECTED, CAUSAL_DISCOVERY_DATA_STARVATION.</item>
    <item>TargetBlockType 1:1 parity verified in backend_v2/tests/unit/test_enum_parity.py with zero block-type additions.</item>
    <item>Step.validate_step_consistency updated to permit StepType.CAUSAL_DISCOVERY without criteria blocks while enforcing extraction_protocol_block_id and cognitive_tier.</item>
    <item>StepRule extended with causal_source_step_id field and @model_validator(mode='after') enforcing causal_source_step_id in self.depends_on.</item>
    <item>NODE_STRATEGY_REGISTRY in backend_v2/services/orchestrator/strategies/registry.py maps StepType.CAUSAL_DISCOVERY to _build_llm_strategy.</item>
    <item>8 immutable Pydantic V2 DTOs created in backend_v2/models/dtos/causal_discovery.py enforcing ConfigDict(strict=True, extra="forbid", frozen=True).</item>
    <item>CausalGraphPayloadDTO cross-field referential integrity @model_validator verifies all edge endpoints, root cause IDs, and isolated node IDs exist in nodes.</item>
    <item>FairScoringBreakdownDTO mathematical identity @model_validator asserts abs(raw - (deduplicated + dampened_savings)) &lt; 1e-4 with all fields non-negative.</item>
    <item>StepPayloadValue in backend_v2/models/dtos/step_output.py extended to include CausalGraphPayloadDTO and CausalTdaFusionResultDTO with data_type="causal".</item>
    <item>Compile-time localization keys added to client_app_v2/lib/l10n/app_en.arb and app_fi.arb.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do not add new block types to TargetBlockType enum in backend_v2/models/enums.py.</forbidden>
    <forbidden>Do not use raw dictionaries or TypedDict in backend_v2/models/dtos/causal_discovery.py.</forbidden>
    <forbidden>Do not allow optional fallback keys or default dicts in DTO definitions.</forbidden>
    <forbidden>Do not mutate existing constructor defaults in SlidingWindowLinker.__init__.</forbidden>
    <forbidden>Do not create separate CausalStep domain subclasses.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/settings.py#L54-L924]</backend>
    <backend>@[backend_v2/models/enums.py#L125-L129]</backend>
    <backend>@[backend_v2/exceptions.py#L129-L314]</backend>
    <backend>@[backend_v2/models/domain/step.py#L33-L144]</backend>
    <backend>@[backend_v2/models/domain/step.py#L147-L188]</backend>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py#L176-L357]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/causal_discovery.py]</backend>
    <backend>@[backend_v2/models/dtos/step_output.py#L59-L73]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart#L50-L70]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb#L2600-L2610]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb#L1887-L1897]</frontend>
  </touched_artifacts>

  <step id="2.1" name="SETTINGS_CONFIGURATION">
    <action>In @[backend_v2/settings.py#L54-L924], add typed settings with PEP 593 Annotated syntax: causal_discovery_window_size: Annotated[int, Field(default=4, description="Sliding window size for causal argument linking")] = 4, causal_discovery_overlap: Annotated[int, Field(default=2, description="Overlap size for sliding window linking")] = 2, causal_discovery_max_atoms_per_window: Annotated[int, Field(default=25, description="Safety ceiling on claims extracted per window")] = 25, causal_discovery_max_total_atoms: Annotated[int, Field(default=100, description="Safety ceiling on total claims extracted for a document")] = 100, causal_secondary_fault_dampening: Annotated[float, Field(default=0.25, description="Penalty dampening factor for cascading secondary faults")] = 0.25, two_pass_atomizer_packet_size: Annotated[int, Field(default=50, description="Default block count per chunk packet in two-pass atomizer")] = 50.</action>
    <action>In @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77], dynamically bind the packet size parameter: when packet_size is unspecified or None, resolve dynamically via get_settings().two_pass_atomizer_packet_size.</action>
    <action>In @[backend_v2/tests/unit/test_settings.py], add unit tests asserting default values and validation constraints for the 6 new causal discovery settings.</action>
    <constraint invariant="the_zero_compromise_pledge">All settings must be strictly typed and validated via Pydantic Settings.</constraint>
  </step>

  <step id="2.2" name="ENUMS_AND_ERROR_CODES">
    <action>In @[backend_v2/models/enums.py#L125-L129], add StepType.CAUSAL_DISCOVERY = "causal_discovery". Retain TargetBlockType strictly without mutation.</action>
    <action>In @[backend_v2/exceptions.py#L129-L314], add explicit causal error codes to ErrorCodes: CAUSAL_DISCOVERY_EMPTY_DOCUMENT, CAUSAL_DISCOVERY_CYCLE_DETECTED, CAUSAL_DISCOVERY_DATA_STARVATION.</action>
    <action>In @[backend_v2/tests/unit/test_enum_parity.py#L110-L112], verify TargetBlockType 1:1 cross-language parity remains intact with zero block-type drift.</action>
    <constraint invariant="universal_fail_fast">Error codes must be explicit and mapped to RFC 7807 problem details.</constraint>
  </step>

  <step id="2.3" name="STEP_CONSISTENCY_AND_FUSION_SCHEMA">
    <action>In @[backend_v2/models/domain/step.py#L33-L144], update validate_step_consistency to add explicit branch for StepType.CAUSAL_DISCOVERY: criteria_block_ids are permitted to be empty, while enforcing extraction_protocol_block_id and cognitive_tier are non-null with AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>In @[backend_v2/models/domain/step.py#L147-L188], declare causal_source_step_id: Annotated[str | None, Field(default=None, pattern=OPAQUE_STRIPE_ID_REGEX, description="Reference to upstream causal discovery step for fusion atom extraction.")] = None on StepRule. Add @model_validator(mode='after') enforcing that when causal_source_step_id is not None, the value MUST exist in self.depends_on, raising AppException(ErrorCodes.VALIDATION_FAILED) if violated.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L50-L70], declare @JsonKey(name: 'causal_source_step_id') String? causalSourceStepId on StepRule Freezed model, maintaining 1:1 Full-Duplex Serialization Parity under disallowUnrecognizedKeys: true.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/registry.py#L69-L99], register StepType.CAUSAL_DISCOVERY -> _build_llm_strategy in NODE_STRATEGY_REGISTRY and verify NodeStrategyFactory.create_strategy dispatch.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L176-L357], update NodeExecutor.execute to handle step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY).</action>
    <action>In @[backend_v2/tests/unit/models/domain/test_step.py], implement unit tests asserting AppException on invalid StepType.CAUSAL_DISCOVERY and StepRule.causal_source_step_id not in depends_on.</action>
    <constraint invariant="studio_driven_parameterization_mandate">StepRule.causal_source_step_id enables Studio-driven fusion chaining without hardcoded heuristics.</constraint>
  </step>

  <step id="2.4" name="IMMUTABLE_CAUSAL_DISCOVERY_DTOS">
    <action>Create [NEW] @[backend_v2/models/dtos/causal_discovery.py] defining 8 strictly typed Pydantic V2 models with ConfigDict(strict=True, extra="forbid", frozen=True): CausalNodeDTO, CausalEdgeDTO, CausalGraphPayloadDTO, CausalRootCauseDiagnosisDTO, AntiFluffAuditDTO, PrescriptiveRemediationDTO, FairScoringBreakdownDTO, and CausalTdaFusionResultDTO.</action>
    <action>In CausalNodeDTO, define: node_id: str, claim: str, source_quote: str | None = None, paragraph_ref: str | None = None, status: ExecutionStatus, blame_parent_ids: list[str] = Field(default_factory=list), dependent_child_ids: list[str] = Field(default_factory=list), tda_score: float | None = None, tda_level_key: str | None = None.</action>
    <action>In CausalEdgeDTO, define: source_id: str, target_id: str, reasoning: str.</action>
    <action>In CausalGraphPayloadDTO, define: nodes: list[CausalNodeDTO], edges: list[CausalEdgeDTO] = Field(default_factory=list), root_cause_node_ids: list[str] = Field(default_factory=list), cycle_detected: bool = False, isolated_node_ids: list[str] = Field(default_factory=list). Add @model_validator(mode='after') asserting every edge.source_id and edge.target_id, every ID in root_cause_node_ids, and every ID in isolated_node_ids exists in {n.node_id for n in self.nodes}, raising ValueError on unextracted node references.</action>
    <action>In CausalRootCauseDiagnosisDTO, define: failing_node_id: str, root_cause_parent_id: str, paragraph_ref: str, explanation: str, penalty_points: float.</action>
    <action>In AntiFluffAuditDTO, define: isolated_concept_count: int, cycle_detected: bool, unsupported_claims_count: int, logical_cohesion_score: float, detected_hollow_terms: list[str] = Field(default_factory=list).</action>
    <action>In PrescriptiveRemediationDTO, define: target_node_id: str, required_action: str, unlocks_node_ids: list[str] = Field(default_factory=list), potential_score_impact: float.</action>
    <action>In FairScoringBreakdownDTO, define: independent_error_count: int, cascading_fault_count: int, raw_penalty_points: float, deduplicated_penalty_points: float, dampened_savings_points: float. Add @model_validator(mode='after') asserting abs(self.raw_penalty_points - (self.deduplicated_penalty_points + self.dampened_savings_points)) &lt; 1e-4, non-negativity across all penalty fields, and non-negativity on counts.</action>
    <action>In CausalTdaFusionResultDTO, define: graph: CausalGraphPayloadDTO, root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO] = Field(default_factory=list), anti_fluff_audit: AntiFluffAuditDTO, prescriptive_remediations: list[PrescriptiveRemediationDTO] = Field(default_factory=list), fair_scoring: FairScoringBreakdownDTO.</action>
    <action>In @[backend_v2/models/dtos/step_output.py#L59-L73], extend StepPayloadValue union with CausalGraphPayloadDTO | CausalTdaFusionResultDTO and StepOutputDTO.data_type literal with "causal".</action>
    <action>Create [NEW] @[backend_v2/tests/unit/models/dtos/test_causal_discovery_dtos.py] asserting referential integrity, mathematical identity, and non-negativity boundary partitions.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero naked dictionaries in state transit; all fields strictly validated.</constraint>
  </step>

  <step id="2.5" name="PRESENTATION_LOCALIZATION">
    <action>In @[client_app_v2/lib/l10n/app_en.arb#L2600-L2610], add compile-time localization keys: causalActionCardTitle ("Causal Argument Diagnosis"), causalIntactClaimsSummary ("{count} other claims verified logically sound"), causalOpenInspectorAction ("Open Interactive Inspector"), causalInspectorTitle ("Causal Graph Inspector"), causalRootCauseBadge ("Root Cause"), causalCascadingFaultBadge ("Cascading Fault"), causalRemediationLabel ("Prescriptive Remediation").</action>
    <action>In @[client_app_v2/lib/l10n/app_fi.arb#L1887-L1897], add Finnish localization keys: causalActionCardTitle ("Kausaalinen argumenttidiagnoosi"), causalIntactClaimsSummary ("{count} muuta väitettä todettu loogisesti kestäviksi"), causalOpenInspectorAction ("Avaa interaktiivinen tarkastin"), causalInspectorTitle ("Kausaaligraafin tarkastin"), causalRootCauseBadge ("Juurisyy"), causalCascadingFaultBadge ("Kerrannaisvirhe"), causalRemediationLabel ("Korjausehdotus").</action>
    <action>Run flutter gen-l10n in client_app_v2 to verify compile-time localization generation.</action>
    <action>Run uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build to execute build_runner code generation for StepRule.</action>
    <constraint invariant="dual_axis_localization_architecture">Axis 1 structural chrome managed strictly via compile-time .arb files with zero missing string fallbacks.</constraint>
  </step>

  <test_contracts>
    <test name="test_settings_causal_defaults" category="positive">
      <input>get_settings()</input>
      <expected>causal_discovery_window_size == 4, causal_discovery_overlap == 2, causal_discovery_max_atoms_per_window == 25, causal_discovery_max_total_atoms == 100, causal_secondary_fault_dampening == 0.25, two_pass_atomizer_packet_size == 50</expected>
    </test>
    <test name="test_two_pass_atomizer_dynamic_packet_size" category="positive">
      <input>TwoPassAtomizer._calculate_packets(hydrated_text, packet_size=None)</input>
      <expected>resolves packet size dynamically from get_settings().two_pass_atomizer_packet_size == 50</expected>
    </test>
    <test name="test_causal_graph_payload_referential_integrity_valid" category="positive">
      <input>CausalGraphPayloadDTO with nodes [node_0, node_1], edge from node_0 to node_1, root_cause_node_ids=[node_0], isolated_node_ids=[node_1]</input>
      <expected>validates successfully</expected>
    </test>
    <test name="test_causal_graph_payload_dangling_edge_source_raises_validation_error" category="error_path">
      <input>CausalGraphPayloadDTO with edge source_id referencing nonexistent node_999</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_causal_graph_payload_dangling_edge_target_raises_validation_error" category="error_path">
      <input>CausalGraphPayloadDTO with edge target_id referencing nonexistent node_999</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_causal_graph_payload_dangling_root_cause_raises_validation_error" category="error_path">
      <input>CausalGraphPayloadDTO with root_cause_node_ids referencing nonexistent node_999</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_causal_graph_payload_dangling_isolated_node_raises_validation_error" category="error_path">
      <input>CausalGraphPayloadDTO with isolated_node_ids referencing nonexistent node_999</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_fair_scoring_breakdown_identity_valid" category="positive">
      <input>FairScoringBreakdownDTO(independent_error_count=1, cascading_fault_count=2, raw_penalty_points=10.0, deduplicated_penalty_points=7.5, dampened_savings_points=2.5)</input>
      <expected>validates successfully (10.0 == 7.5 + 2.5)</expected>
    </test>
    <test name="test_fair_scoring_breakdown_identity_violation_raises_validation_error" category="error_path">
      <input>FairScoringBreakdownDTO with raw_penalty_points=10.0 but sum=8.0</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_fair_scoring_breakdown_negative_points_raises_validation_error" category="boundary">
      <input>FairScoringBreakdownDTO with raw_penalty_points=-1.0</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_fair_scoring_breakdown_negative_counts_raises_validation_error" category="boundary">
      <input>FairScoringBreakdownDTO with independent_error_count=-1</input>
      <expected>raises ValidationError</expected>
    </test>
    <test name="test_step_rule_causal_source_step_id_not_in_depends_on_raises_app_exception" category="error_path">
      <input>StepRule with causal_source_step_id="sr_1111111111111111" and depends_on=["sr_2222222222222222"]</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
    </test>
    <test name="test_step_rule_causal_source_step_id_in_depends_on_valid" category="positive">
      <input>StepRule with causal_source_step_id="sr_1111111111111111" and depends_on=["sr_1111111111111111", "sr_2222222222222222"]</input>
      <expected>validates successfully</expected>
    </test>
    <test name="test_step_rule_invalid_opaque_id_raises_validation_error" category="boundary">
      <input>StepRule with causal_source_step_id="invalid_id!"</input>
      <expected>raises ValidationError (violating OPAQUE_STRIPE_ID_REGEX)</expected>
    </test>
    <test name="test_step_causal_discovery_valid_without_criteria" category="positive">
      <input>Step with type=StepType.CAUSAL_DISCOVERY, criteria_block_ids=[], extraction_protocol_block_id="blk_1111222233334444", cognitive_tier=CognitiveTier.FAST</input>
      <expected>validates successfully</expected>
    </test>
    <test name="test_step_causal_discovery_missing_extraction_protocol_raises_app_exception" category="error_path">
      <input>Step with type=StepType.CAUSAL_DISCOVERY, extraction_protocol_block_id=None</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
    </test>
    <test name="test_step_causal_discovery_missing_cognitive_tier_raises_app_exception" category="error_path">
      <input>Step with type=StepType.CAUSAL_DISCOVERY, cognitive_tier=None</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
    </test>
    <test name="test_step_output_dto_payload_accepts_causal_payload" category="positive">
      <input>StepOutputDTO(step_id="stp_1111111111111111", block_id="blk_1111111111111111", data_type="causal", payload=CausalGraphPayloadDTO(nodes=[CausalNodeDTO(node_id="n0", claim="Test", status=ExecutionStatus.PASSED)]))</input>
      <expected>validates successfully with data_type="causal"</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/causal_discovery.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/models/domain/step.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test</action>
    <action>Execute: uv run pytest backend_v2/tests/unit/test_enum_parity.py</action>
    <action>Execute: uv run python scripts/_ast_guardrails.py to verify QGR001 and QGR002 compliance on causal_discovery.py</action>
    <action>Execute: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build</action>
    <action>Execute: uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/02_phase2_plan.md</action>
  </validation_gate>
</execution_protocol>
