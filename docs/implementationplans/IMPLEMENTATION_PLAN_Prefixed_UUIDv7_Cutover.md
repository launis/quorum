<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Universal PrefixedUUID7 Cutover (Model A), Studio Default Anchor Eradication & Topological Graph Mathematics Synchronization

## 1. Objective & Architectural Background

Prior to executing `EPIC 160` (B2B SaaS IAM) and decomposing `PostgresEntityAdapter`, Quorum eliminates the legacy hybrid entity identifier split (7 `TEXT PRIMARY KEY` configuration tables using 16-character UUIDv4 truncation versus 5 `UUID PRIMARY KEY` operational tables using 32-character RFC 9562 UUIDv7) across all 12 PostgreSQL 19 tables in accordance with `@[docs/arkkitehtuurin_parannuskohteet.md]` Chapter 2 and Chapter 2.5 (**Model A: Universal `PrefixedUUID7`**) and `@[docs/tiede.md]` Section 4.2:

1. **Universal 32-Hex RFC 9562 `UUIDv7` & `EntityPrefix` SSOT (`@[backend_v2/models/core_base.py#L199-L229]`, `@[backend_v2/models/enums.py#L228-L244]`, `@[backend_v2/models/enums.py#L283-L286]`):**
   - Lock `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"` across the entire application.
   - Remove `_UUID7_DELEGATED_PREFIXES` and `uuid.uuid4().hex[:16]` branching from `generate_opaque_id(prefix)` so every call delegates unconditionally to `generate_uuid7_opaque_id(prefix)`.
   - Add `SCALE = "sc"` to `EntityPrefix` so every persisted and nested entity prefix (specifically and exhaustively: `org`, `usr`, `sys`, `blk`, `stp`, `sr`, `wf`, `prf`, `exe`, `rep`, `nod`, `edg`, `tda`, `sc`) is governed by `EntityPrefix` SSOT, and update `SystemConfigID.MCP_GATEWAYS` to a canonical 32-hex RFC 9562 `UUIDv7` value.
2. **PostgreSQL 19 Native 16-Byte `UUIDv7` Across All 12 Tables & Symmetric Adapter Bridge (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L308]`, `@[backend_v2/database/postgres/entity_adapter.py#L828-L2366]`):**
   - Upgrade tables 1–7 (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) to `id UUID PRIMARY KEY DEFAULT uuidv7()`, `created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL`, and `CHECK (uuid_extract_version(id) = 7)`.
   - Upgrade all cross-table relational foreign keys across tables 1–10 (specifically and exhaustively: `users.organization_id`, `prompt_blocks.organization_id`, `steps.organization_id`, `steps.role_block_id`, `steps.extraction_protocol_block_id`, `steps.execution_persona_block_id`, `workflows.organization_id`, `workflows.default_profile_id`, `workflows.mcp_gateway_id`, `workflows.model_registry_id`, `output_profiles.workflow_id`, `output_profiles.organization_id`, `executions.workflow_id`, `executions.active_profile_id`, `executions.output_profile_id`, `executions.organization_id`, `report_artifacts.execution_id`, `report_artifacts.workflow_id`, `report_artifacts.profile_id`) to native `UUID` columns with `CHECK (uuid_extract_version(<column>) = 7)` constraints.
   - Standardize `@[backend_v2/database/postgres/entity_adapter.py#L828-L2366]` so all 12 tables convert between `{prefix}_{32_hex}` and 16-byte `uuid.UUID` exclusively via `parse_prefixed_uuid7()` and `format_prefixed_uuid7()`.
3. **Deterministic `@[backend_v2/seed/seed_data.json#L1-L22793]` 32-Hex `UUIDv7` Cutover & `@[scripts/sanitize_seed_vault.py#L635-L692]` Auto-Generation:**
   - Deterministically migrate all 16-character entity IDs (including `wor_`-prefixed workflows normalized to `wf_` and `sc_`-prefixed matrix scales) and all relational foreign key references in `@[backend_v2/seed/seed_data.json#L1-L22793]` to canonical 32-hex RFC 9562 `UUIDv7` identifiers (`{prefix}_{32_hex}`).
   - Enhance `@[scripts/sanitize_seed_vault.py#L445-L548]` and `@[scripts/sanitize_seed_vault.py#L635-L692]` to automatically inspect every entity and nested `TDAAssertion` / scale entry in `@[backend_v2/seed/seed_data.json#L1-L22793]`: if a new row or atom assertion is added without a canonical 32-hex `UUIDv7` identifier, `sanitize_seed_vault.py` generates one via `generate_uuid7_opaque_id()` and writes it back atomically prior to seeding.
4. **Hardcoded Studio Draft Anchor Eradication & Direct Causal Cohesion Matrix Binding (`@[backend_v2/services/studio/workflow_service.py#L348-L390]`, `@[backend_v2/services/studio/workflow_service.py#L677-L729]`, `@[backend_v2/models/domain/workflow.py#L25-L217]`, `@[backend_v2/models/domain/step.py#L125-L185]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L79-L123]`):**
   - Replace hardcoded `criteria_block_ids=["blk_440a5fef9331451b"]` in `StudioWorkflowService.create_step_draft` with dynamic lookup from `all_blocks` for the first `PromptBlockCategory.MATRIX` or `PromptBlockCategory.CRITERIA` block (raising `AppException(ErrorCodes.STATE_INTEGRITY_ERROR)` if missing).
   - Replace `default_profile_id="prf_0000000000000000"` in `StudioWorkflowService.create_workflow_draft` with `default_profile_id=None`, set `Workflow.mcp_gateway_id` default to `None` with dynamic lookup from `self.system_repo`, and tighten `Workflow.mcp_gateway_id` and `Workflow.model_registry_id` regex patterns to `r"^sys_[a-fA-F0-9]{32}$"`.
   - Bind the causal cohesion BARS matrix directly to `Step.criteria_block_ids` on `StepType.CAUSAL_DISCOVERY` in `@[backend_v2/models/domain/step.py#L125-L185]`, remove the `causal_cohesion_block_id` side-channel parameter from `Workflow.get_allowed_layout_targets` (`@[backend_v2/models/domain/workflow.py#L194-L217]`), read the matrix block ID and its 5 BARS `TDAAssertion` rows directly from the step's hydrated `MatrixPromptBlock` inside `_append_causal_fusion_and_cohesion_events` (`@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L79-L123]`), and delete `causal_cohesion_matrix_block_id` from `@[backend_v2/settings.py#L47-L1087]` as well as `CAUSAL_COHESION_TDA_IDS` and `CAUSAL_COHESION_CLAIMS` from `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L80-L302]`.
5. **100% Synchronization of `@[docs/tiede.md]` Section 4.2 Topological Graph Mathematics (`@[backend_v2/models/dtos/causal_discovery.py#L208-L228]`, `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart#L61-L78]`, `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L64-L238]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]`, `@[backend_v2/settings.py#L47-L1087]`):**
   - Add 0-token topological metrics `largest_component_ratio: float` ($r_{\text{LCC}} \in [0.0, 1.0]$), `branch_convergence_ratio: float` ($r_{\text{conv}} \in [0.0, 1.0]$), and `steering_coupling_ratio: float` ($\kappa_{\text{steer}} \in [0.0, 1.0]$) to `AntiFluffAuditDTO` and Flutter's `AntiFluffAuditDto`, and define `[NEW]` `CounterfactualSimulationResultDTO` (with fields `retracted_root_id`, `collapsed_node_ids`, `surviving_node_ids`, `collapse_ratio`, `max_cascade_depth`).
   - Compute $r_{\text{LCC}}$, $r_{\text{conv}}$, and $\kappa_{\text{steer}}$ in `compute_causal_tda_fusion_result` (`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L64-L238]`).
   - Enforce Equation (13) Guttman tier thresholds (`causal_cohesion_l2_min_nodes = 2`, `causal_cohesion_l3_min_nodes = 5`, `causal_cohesion_l4_min_nodes = 10`, `causal_cohesion_l5_min_nodes = 15`, `causal_cohesion_l2_lcc_min = 0.35`, `causal_cohesion_l3_lcc_min = 0.50`, `causal_cohesion_l4_lcc_min = 0.70`, `causal_cohesion_l5_lcc_min = 0.85`, `causal_cohesion_l4_convergence_min = 0.05`) and Algorithm 1 counterfactual retraction simulation (`simulate_counterfactual_retraction`) in `CausalCohesionEvaluator` (`@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]`).

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[docs/arkkitehtuurin_parannuskohteet.md#L51-L193]`
- `@[docs/tiede.md#L156-L413]`
- `@[backend_v2/seed/run_seed.py]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: Pre-Implementation Technical Debt Cleanups & Core ID SSOT**<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L445-L548]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L551-L574]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L577-L606]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L609-L632]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L635-L692]`<br>`[MODIFY] @[backend_v2/models/core_base.py#L199-L229]`<br>`[MODIFY] @[backend_v2/models/core_base.py#L232-L289]`<br>`[MODIFY] @[backend_v2/models/core_base.py#L292-L336]`<br>`[MODIFY] @[backend_v2/models/enums.py#L228-L244]`<br>`[MODIFY] @[backend_v2/models/enums.py#L283-L286]` | Permissive `.get()` lookups (`b.get("id", "")`, `s.get("score")`, `w.get("id")`) in `scripts/sanitize_seed_vault.py`; variable-length `{16,32}` regex in `OPAQUE_STRIPE_ID_REGEX`; `_UUID7_DELEGATED_PREFIXES` branching and `uuid.uuid4().hex[:16]` truncation in `generate_opaque_id`. | Replace `.get()` lookups in `scripts/sanitize_seed_vault.py` with explicit key membership checks; lock `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`; route `generate_opaque_id` unconditionally to `generate_uuid7_opaque_id`; add `SCALE = "sc"` to `EntityPrefix` and update `SystemConfigID.MCP_GATEWAYS` to 32-hex UUIDv7. | Pruned `_UUID7_DELEGATED_PREFIXES` and `length` truncation branching; one universal 32-hex RFC 9562 UUIDv7 generator across all entity prefixes. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/core_base.py backend_v2/models/enums.py scripts/sanitize_seed_vault.py --micro` |
| **Phase 2: Deterministic Seed Vault 32-Hex UUIDv7 Cutover & Auto-Sanitizer**<br>`[MODIFY] @[backend_v2/seed/seed_data.json#L1-L22793]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L445-L548]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py#L635-L692]` | Legacy 16-hex entity IDs, `wor_` workflow prefix drift, and manual ID crafting when adding new rows or `TDAAssertion` entries to `seed_data.json`. | Deterministically migrate all entity IDs and relational foreign keys in `seed_data.json` to `{prefix}_{32_hex_uuidv7}`; extend `sanitize_seed_vault.py` to auto-generate missing or non-32-hex `UUIDv7` identifiers via `generate_uuid7_opaque_id()` and persist them atomically to `seed_data.json`. | Pruned external migration sidecar tables; deterministic in-place relational ID replacement verified by `run_seed.py local --dry-run`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict` |
| **Phase 3: PostgreSQL 19 12-Table Native UUIDv7 DDL & Symmetric Adapter Bridge**<br>`[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L308]`<br>`[MODIFY] @[backend_v2/database/postgres/entity_adapter.py#L828-L2366]`<br>`[MODIFY] @[scripts/audit_zero_orm_strictness.py#L550-L579]` | Hybrid split where 7 tables (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) used `TEXT PRIMARY KEY` and untyped `TEXT` foreign keys while 5 tables used `UUID`. | Define `id UUID PRIMARY KEY DEFAULT uuidv7()`, `created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL`, `CHECK (uuid_extract_version(id) = 7)`, and native `UUID` foreign keys across all 12 tables; apply symmetric `parse_prefixed_uuid7` / `format_prefixed_uuid7` across all 12 tables in `PostgresEntityAdapter` and verify via `audit_sql_migration_file`. | Pruned table-specific `TEXT` vs `UUID` branching in `PostgresEntityAdapter`; every table primary key and foreign key uses the identical 16-byte binary `UUIDv7` bridge. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict` |
| **Phase 4: Studio Draft Anchor Eradication & Direct Causal Cohesion Matrix Binding**<br>`[MODIFY] @[backend_v2/services/studio/workflow_service.py#L348-L390]`<br>`[MODIFY] @[backend_v2/services/studio/workflow_service.py#L677-L729]`<br>`[MODIFY] @[backend_v2/models/domain/workflow.py#L25-L217]`<br>`[MODIFY] @[backend_v2/models/domain/workflow.py#L194-L217]`<br>`[MODIFY] @[backend_v2/models/domain/step.py#L42-L185]`<br>`[MODIFY] @[backend_v2/models/domain/step.py#L125-L185]`<br>`[MODIFY] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L79-L123]` | Hardcoded `"blk_440a5fef9331451b"`, `"prf_0000000000000000"`, `"sys_8172bda70c8641c5"`, and `cfg_model_registry_\d{2}` defaults; side-channel `settings.causal_cohesion_matrix_block_id`, `causal_cohesion_block_id` parameter, and hardcoded `CAUSAL_COHESION_TDA_IDS` / `CAUSAL_COHESION_CLAIMS` tuples. | Resolve Studio draft protocol and criteria blocks dynamically from `prompt_block_repo` and `system_repo`; require `criteria_block_ids` on `StepType.CAUSAL_DISCOVERY` in `Step.validate_step_consistency`; pass the step's hydrated `MatrixPromptBlock` rows (`id` and `claim`) directly from `_append_causal_fusion_and_cohesion_events` to `CausalCohesionEvaluator`. | Pruned `causal_cohesion_block_id` override parameter from `Workflow.get_allowed_layout_targets` and deleted `causal_cohesion_matrix_block_id` from `Settings`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/workflow_service.py backend_v2/models/domain/workflow.py backend_v2/models/domain/step.py backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py --test --ast-strict` |
| **Phase 5: Topological Graph Mathematics (`r_LCC`, `r_conv`, $\kappa_{\text{steer}}$, `simulate_counterfactual_retraction`) & Full-Duplex Parity**<br>`[MODIFY] @[backend_v2/models/dtos/causal_discovery.py#L208-L228]`<br>`[MODIFY] @[backend_v2/models/dtos/causal_discovery.py#L305-L332]`<br>`[MODIFY] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart#L61-L78]`<br>`[MODIFY] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L64-L238]`<br>`[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L80-L302]`<br>`[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]`<br>`[MODIFY] @[backend_v2/settings.py#L47-L1087]`<br>`[MODIFY] @[scripts/_ast_guardrails.py#L2670-L2714]` | Evaluating causal cohesion solely on degree-zero `isolated_concept_count` (vulnerable to dyad fragmentation $A \to B, C \to D$ and 2-node stub graphs passing L5); missing `r_LCC`, `r_conv`, $\kappa_{\text{steer}}$, and counterfactual retraction simulation. | Add `largest_component_ratio`, `branch_convergence_ratio`, `steering_coupling_ratio`, and `[NEW]` `CounterfactualSimulationResultDTO` across Python and Dart DTOs; compute them in `compute_causal_tda_fusion_result`; enforce Equation (13) Guttman gates and Algorithm 1 `simulate_counterfactual_retraction` in `CausalCohesionEvaluator`; tighten `QGR030` in `scripts/_ast_guardrails.py` to 32-hex format. | Zero LLM calls added: all topological metrics ($r_{\text{LCC}}, r_{\text{conv}}, \kappa_{\text{steer}}$) and Algorithm 1 BFS cascades execute deterministically in $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ time ($< 1\text{ ms}$, 0 tokens). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/causal_discovery.py backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py backend_v2/services/orchestrator/causal_cohesion_evaluator.py backend_v2/settings.py scripts/_ast_guardrails.py --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/causal_discovery_dto.dart --build` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

1. **`TD_DICT_GET` Eradication in `@[scripts/sanitize_seed_vault.py#L445-L548]` and `@[scripts/sanitize_seed_vault.py#L577-L606]`:**
   - Replace `b.get("id", "")` on line 467 with `str(b["id"]) if "id" in b else ""`.
   - Replace `s.get("score")` on line 473 with `s["score"] if "score" in s else None`.
   - Replace `w.get("id")` on line 593 with `w["id"] if "id" in w else None`.
2. **Legacy 16-Hex Truncation Removal in `@[backend_v2/models/core_base.py#L199-L229]`:**
   - Remove `_UUID7_DELEGATED_PREFIXES` and the `uuid.uuid4().hex[:bounded_len]` branch so all generated Opaque Stripe IDs use a single 32-hex RFC 9562 `UUIDv7` pipeline.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Pre-Implementation Technical Debt Cleanups &amp; Core PrefixedUUID7 SSOT Lock">
    <targets>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L445-L548]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L551-L574]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L577-L606]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L609-L632]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L635-L692]</target>
      <target>[MODIFY] @[backend_v2/models/core_base.py#L199-L229]</target>
      <target>[MODIFY] @[backend_v2/models/core_base.py#L232-L289]</target>
      <target>[MODIFY] @[backend_v2/models/core_base.py#L292-L336]</target>
      <target>[MODIFY] @[backend_v2/models/enums.py#L228-L244]</target>
      <target>[MODIFY] @[backend_v2/models/enums.py#L283-L286]</target>
    </targets>
    <constraint invariant="single_pipeline_invariant_mandate">
      All entity identifiers across all prefixes MUST flow through a single 32-hex RFC 9562 UUIDv7 generation and validation pipeline with zero 16-hex fallback branches.
    </constraint>
    <constraint invariant="opaque_stripe_id_ssot_constant_mandate">
      All models and validators MUST bind OPAQUE_STRIPE_ID_REGEX from backend_v2.models.core_base and EntityPrefix from backend_v2.models.enums.
    </constraint>
    <action>
      1. In `@[scripts/sanitize_seed_vault.py#L445-L548]` and `@[scripts/sanitize_seed_vault.py#L577-L606]`, eliminate the 3 pre-existing `TD_DICT_GET` technical debt findings by replacing `b.get("id", "")`, `s.get("score")`, and `w.get("id")` with explicit key membership checks (`"id" in b`, `"score" in s`, `"id" in w`).
      2. In `@[backend_v2/models/enums.py#L228-L244]`, add `SCALE = "sc"` to `EntityPrefix` so all 14 canonical prefixes (`wf`, `stp`, `sr`, `prf`, `blk`, `sys`, `exe`, `usr`, `org`, `tda`, `rep`, `nod`, `edg`, `sc`) are governed by `EntityPrefix`. In `@[backend_v2/models/enums.py#L283-L286]`, update `SystemConfigID.MCP_GATEWAYS` from `"sys_8172bda70c8641c5"` to `"sys_0195f3a00000700080008172bda70c86"`.
      3. In `@[backend_v2/models/core_base.py#L199-L229]`, update `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`, delete `_UUID7_DELEGATED_PREFIXES`, and refactor `generate_opaque_id(prefix: EntityPrefix | str)` to validate the prefix against `EntityPrefix` and delegate unconditionally to `generate_uuid7_opaque_id(EntityPrefix(prefix_str))`, verifying `@[backend_v2/models/core_base.py#L232-L289]` (`parse_prefixed_uuid7`) and `@[backend_v2/models/core_base.py#L292-L336]` (`format_prefixed_uuid7`).
    </action>
  </step>

  <step id="2" name="Phase 2: Deterministic seed_data.json 32-Hex UUIDv7 Cutover &amp; sanitize_seed_vault.py Auto-ID Generator">
    <targets>
      <target>[MODIFY] @[backend_v2/seed/seed_data.json#L1-L22793]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L445-L548]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L551-L574]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L577-L606]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L609-L632]</target>
      <target>[MODIFY] @[scripts/sanitize_seed_vault.py#L635-L692]</target>
    </targets>
    <constraint invariant="database_schema_hallucination">
      Preserve all root collection structures, qualitative prompt texts (system_prompt, ai_description, concept_description, extraction_rule), and relational topology in seed_data.json while deterministically upgrading IDs to 32-hex UUIDv7.
    </constraint>
    <action>
      1. In `@[scripts/sanitize_seed_vault.py#L445-L548]`, `@[scripts/sanitize_seed_vault.py#L551-L574]`, `@[scripts/sanitize_seed_vault.py#L577-L606]`, `@[scripts/sanitize_seed_vault.py#L609-L632]`, and `@[scripts/sanitize_seed_vault.py#L635-L692]`, implement deterministic 16-hex-to-32-hex RFC 9562 `UUIDv7` mapping (preserving existing 16-hex entropy in the lower 64 bits of a valid version-7, variant-`0b10` 128-bit UUID and normalizing `wor_` workflow prefixes to `wf_`) across all top-level collections (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) and nested references (`criteria_block_ids`, `role_block_id`, `extraction_protocol_block_id`, `execution_persona_block_id`, `task_blueprint`, `depends_on`, `workflow_id`, `default_profile_id`, `mcp_gateway_id`, `model_registry_id`, `target_block_order`, `matrix_synthesis_groups`, `variance_target_block`, `user_role_target_block`, `scales[].id`, `tda_assertions[].tda_id`, `depends_on_tda_ids`).
      2. Add automatic missing-ID generation to `sanitize_prompt_blocks`, `sanitize_steps`, `sanitize_workflows`, and `sanitize_output_profiles` in `@[scripts/sanitize_seed_vault.py#L445-L548]` and `@[scripts/sanitize_seed_vault.py#L635-L692]`: whenever a new entity row, scale, or `TDAAssertion` is added to `@[backend_v2/seed/seed_data.json#L1-L22793]` without a canonical 32-hex `UUIDv7` identifier matching `OPAQUE_STRIPE_ID_REGEX`, generate a fresh canonical identifier via `generate_uuid7_opaque_id(EntityPrefix.<TYPE>)` and persist it atomically to `@[backend_v2/seed/seed_data.json#L1-L22793]` before `run_seed.py` executes.
      3. Also bind the causal cohesion BARS matrix block ID directly into the `criteria_block_ids` list of every `StepType.CAUSAL_DISCOVERY` step in `@[backend_v2/seed/seed_data.json#L1-L22793]`, and verify 100% in-memory schema and referential integrity via `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`.
    </action>
  </step>

  <step id="3" name="Phase 3: PostgreSQL 19 12-Table Native UUIDv7 DDL &amp; Symmetric Adapter Bridge">
    <targets>
      <target>[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L308]</target>
      <target>[MODIFY] @[backend_v2/database/postgres/entity_adapter.py#L828-L2366]</target>
      <target>[MODIFY] @[scripts/audit_zero_orm_strictness.py#L550-L579]</target>
    </targets>
    <constraint invariant="service_layer_hydration_firewall">
      All 12 PostgreSQL 19 tables MUST store primary keys and relational foreign keys as native 16-byte UUIDv7 values, converting symmetrically at the PostgresEntityAdapter boundary via parse_prefixed_uuid7 and format_prefixed_uuid7.
    </constraint>
    <action>
      1. Update `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L308]` so tables 1–7 (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) declare `id UUID PRIMARY KEY DEFAULT uuidv7()`, `created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL`, and `CONSTRAINT enforce_<table_singular>_uuidv7 CHECK (uuid_extract_version(id) = 7)`, and convert all relational foreign key columns across tables 1–10 (`users.organization_id`, `prompt_blocks.organization_id`, `steps.organization_id`, `steps.role_block_id`, `steps.extraction_protocol_block_id`, `steps.execution_persona_block_id`, `workflows.organization_id`, `workflows.default_profile_id`, `workflows.mcp_gateway_id`, `workflows.model_registry_id`, `output_profiles.workflow_id`, `output_profiles.organization_id`, `executions.workflow_id`, `executions.active_profile_id`, `executions.output_profile_id`, `executions.organization_id`, `report_artifacts.execution_id`, `report_artifacts.workflow_id`, `report_artifacts.profile_id`) from `TEXT` to `UUID` with `REFERENCES ...` and `CHECK (uuid_extract_version(<col>) = 7)`. Update the PG 17 fallback `DO $$` block to cover the `VIRTUAL` timestamp columns cleanly.
      2. Update `@[backend_v2/database/postgres/entity_adapter.py#L828-L2366]` (`PostgresEntityAdapter` and its SQL statements) so all 10 entity and binary tables bind `$N::uuid` parameters via `parse_prefixed_uuid7()` on write/query/delete and reconstitute canonical `{prefix}_{32_hex}` strings via `format_prefixed_uuid7()` on row hydration.
      3. Extend `audit_sql_migration_file` in `@[scripts/audit_zero_orm_strictness.py#L550-L579]` to verify that none of the 12 canonical tables in `001_pg19_uuidv7_schema.sql` declare `id TEXT PRIMARY KEY`.
    </action>
  </step>

  <step id="4" name="Phase 4: Studio Draft Anchor Eradication &amp; Direct Causal Cohesion Matrix Binding">
    <targets>
      <target>[MODIFY] @[backend_v2/services/studio/workflow_service.py#L348-L390]</target>
      <target>[MODIFY] @[backend_v2/services/studio/workflow_service.py#L677-L729]</target>
      <target>[MODIFY] @[backend_v2/models/domain/workflow.py#L25-L217]</target>
      <target>[MODIFY] @[backend_v2/models/domain/workflow.py#L194-L217]</target>
      <target>[MODIFY] @[backend_v2/models/domain/step.py#L42-L185]</target>
      <target>[MODIFY] @[backend_v2/models/domain/step.py#L125-L185]</target>
      <target>[MODIFY] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L79-L123]</target>
    </targets>
    <constraint invariant="zero_db_hardcoding_mandate">
      NEVER hardcode specific database entity IDs in domain models, Studio draft creators, or DAG wave orchestrators; resolve defaults dynamically from repositories or step blueprint relationships.
    </constraint>
    <action>
      1. In `@[backend_v2/services/studio/workflow_service.py#L677-L729]` (`create_step_draft`), resolve both `protocol_block_id` (`b.category_id == PromptBlockCategory.PROTOCOL`) and `default_criteria_id` (`b.category_id in (PromptBlockCategory.MATRIX, PromptBlockCategory.CRITERIA)`) dynamically from `all_blocks`, raising `AppException` with `ErrorCodes.STATE_INTEGRITY_ERROR` if either is missing, and remove hardcoded `"blk_440a5fef9331451b"`.
      2. In `@[backend_v2/services/studio/workflow_service.py#L348-L390]` (`create_workflow_draft`) and `@[backend_v2/models/domain/workflow.py#L25-L217]` (`Workflow`), set `default_profile_id=None`, change `Workflow.mcp_gateway_id` default to `None` with `pattern=r"^sys_[a-fA-F0-9]{32}$"`, change `Workflow.model_registry_id` pattern to `r"^sys_[a-fA-F0-9]{32}$"`, and resolve `mcp_gateway_id` dynamically from `self.system_repo` in `create_workflow_draft`.
      3. In `@[backend_v2/models/domain/step.py#L42-L185]` and `@[backend_v2/models/domain/step.py#L125-L185]` (`Step.validate_step_consistency`), enforce that `StepType.CAUSAL_DISCOVERY` steps declare at least one `criteria_block_id` (their BARS causal cohesion matrix). Remove the `causal_cohesion_block_id: str | None = None` side-channel parameter from `@[backend_v2/models/domain/workflow.py#L194-L217]` (`Workflow.get_allowed_layout_targets`).
      4. In `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L79-L123]` (`_append_causal_fusion_and_cohesion_events`), resolve `cohesion_matrix_id = src_step_def.criteria_block_ids[0]` and extract the 5 BARS `TDAAssertion` definitions from `state.blocks_by_id[cohesion_matrix_id]`, passing them directly to `evaluator.evaluate_causal_cohesion(...)`.
    </action>
  </step>

  <step id="5" name="Phase 5: Topological Graph Mathematics Synchronization, Counterfactual Simulation &amp; Full-Duplex Parity">
    <targets>
      <target>[MODIFY] @[backend_v2/models/dtos/causal_discovery.py#L208-L228]</target>
      <target>[MODIFY] @[backend_v2/models/dtos/causal_discovery.py#L305-L332]</target>
      <target>[MODIFY] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart#L61-L78]</target>
      <target>[MODIFY] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L64-L238]</target>
      <target>[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L80-L302]</target>
      <target>[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]</target>
      <target>[MODIFY] @[backend_v2/settings.py#L47-L1087]</target>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L2670-L2714]</target>
    </targets>
    <constraint invariant="full_duplex_serialization_parity_mandate">
      Maintain 1:1 field and serialization parity between backend Pydantic V2 DTOs in causal_discovery.py and frontend Freezed models in causal_discovery_dto.dart.
    </constraint>
    <action>
      1. In `@[backend_v2/models/dtos/causal_discovery.py#L208-L228]` (`AntiFluffAuditDTO`) and `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart#L61-L78]` (`AntiFluffAuditDto`), add `largest_component_ratio: float` (default `1.0`), `branch_convergence_ratio: float` (default `0.0`), and `steering_coupling_ratio: float` (default `0.0`) with `@field_validator` bounds `[0.0, 1.0]`. In `@[backend_v2/models/dtos/causal_discovery.py#L305-L332]` and `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart#L61-L78]`, define `[NEW]` `CounterfactualSimulationResultDTO` / `CounterfactualSimulationResultDto` containing `retracted_root_id: str`, `collapsed_node_ids: list[str]`, `surviving_node_ids: list[str]`, `collapse_ratio: float`, and `max_cascade_depth: int`.
      2. In `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L64-L238]` (`compute_causal_tda_fusion_result`), compute Weakly Connected Components on the undirected projection of `deliverable_nodes` to derive `largest_component_ratio` ($r_{\text{LCC}}$), compute the fraction of deliverable nodes with `InDegree >= 2` to derive `branch_convergence_ratio` ($r_{\text{conv}}$), and compute the fraction of zero-internal-in-degree deliverable root claims supported by dialogue nodes to derive `steering_coupling_ratio` ($\kappa_{\text{steer}}$).
      3. In `@[backend_v2/settings.py#L47-L1087]`, delete `causal_cohesion_matrix_block_id` and add `causal_cohesion_l2_min_nodes = 2`, `causal_cohesion_l3_min_nodes = 5`, `causal_cohesion_l4_min_nodes = 10`, `causal_cohesion_l5_min_nodes = 15`, `causal_cohesion_l2_lcc_min = 0.35`, `causal_cohesion_l3_lcc_min = 0.50`, `causal_cohesion_l4_lcc_min = 0.70`, `causal_cohesion_l5_lcc_min = 0.85`, and `causal_cohesion_l4_convergence_min = 0.05`.
      4. In `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L80-L302]` and `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]`, delete `CAUSAL_COHESION_TDA_IDS` and `CAUSAL_COHESION_CLAIMS`, accept the step's hydrated BARS atom `(tda_id, claim)` pairs in `evaluate_causal_cohesion`, enforce Equation (13) Guttman predicates (`total_nodes`, `largest_component_ratio`, `branch_convergence_ratio`, `isolated_ratio`, `not audit.cycle_detected`), and implement `simulate_counterfactual_retraction(graph: CausalGraphPayloadDTO, retracted_node_id: str, conjunctive: bool = True) -> CounterfactualSimulationResultDTO` per `@[docs/tiede.md]` Algorithm 1.
      5. In `@[scripts/_ast_guardrails.py#L2670-L2714]` (`QuorumGuardrailVisitor.visit_Constant`), update the `QGR030` remediation and mock ID length checks to enforce the unified 32-hex `{prefix}_{32_hex}` format across all test fixtures and run the global backend and Flutter quality gates.
    </action>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — Universal 32-Hex PrefixedUUID7 & Connected Argument Graph):**
  - Calling `generate_opaque_id(prefix)` for every member of `EntityPrefix` returns a 32-hex RFC 9562 version-7 string matching `r"^([a-z]{2,5})_[a-f0-9]{32}$"` that roundtrips through `parse_prefixed_uuid7` and `format_prefixed_uuid7`.
  - A connected 15-node acyclic deliverable graph with $r_{\text{iso}} = 0.0$, $r_{\text{LCC}} = 1.0$, and $r_{\text{conv}} = 0.20$ passes BARS Levels 1 through 5 (`score = 5.0`), and `simulate_counterfactual_retraction` accurately reports downstream collapsed and surviving node sets in both conjunctive ($\bigwedge$) and disjunctive ($\bigvee$) modes.
- **Scenario 2 (Negative Path 1 — Prefix Mismatch, Non-UUIDv7 & Missing Studio Draft Blocks):**
  - Passing a 16-hex legacy ID (`"wf_a8f1d71000000001"`), a version-4 UUID, or a mismatched prefix (`"stp_..."` to `EntityPrefix.WORKFLOW`) into `parse_prefixed_uuid7` raises `AppException` with `ErrorCodes.VALIDATION_FAILED`.
  - Calling `StudioWorkflowService.create_step_draft` when no `MATRIX`/`CRITERIA` block exists in `prompt_block_repo` raises `AppException` with `ErrorCodes.STATE_INTEGRITY_ERROR`.
- **Scenario 3 (Negative Path 2 — ISTQB Boundary Value Analysis on Dyad Fragmentation & Node Cardinality):**
  - A fragmented graph of 5 disjoint 2-node pairs ($N = 10$, $r_{\text{iso}} = 0.0$, $|\mathcal{V}_{\text{LCC}}| = 2 \implies r_{\text{LCC}} = 0.20 < 0.35$) fails Level 2 (`l2_passed = False`) and clamps deterministically to the Novice floor (`score = 1.0`).
  - Boundary node counts $N \in \{0, 1, 4, 9, 14\}$ (`min - 1` for Levels 1–5) deterministically fail their respective Guttman tier gates even when $r_{\text{iso}} = 0.0$ and $r_{\text{LCC}} = 1.0$.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
