# Phase 2: Repository Reconstitution, Storage Blob Hydration & DAL Tests

**Overview:** Transition all Data Access Layer (Repository) methods from returning untyped `dict[str, Any]` to returning validated, frozen Pydantic Domain Models, replace all blob trace deserialization (`json.loads(decoded)`) with Rust-level Pydantic V2 hydration (`TypeAdapter(T).validate_json()`), atomically modernize 100% of repository unit tests, and update rule `service_layer_hydration_firewall` (@[.agents/rules/01-python-backend.md#L176-L178]) to align with the `repository_reconstitution_mandate` (@[.agents/rules/01-python-backend.md#L360-L362]).
**Target Files:**
- `[MODIFY]` @[backend_v2/database/repositories/execution.py#L92-L100]
- `[MODIFY]` @[backend_v2/database/repositories/system.py]
- `[MODIFY]` @[backend_v2/database/repositories/workflow.py]
- `[MODIFY]` @[backend_v2/database/repositories/knowledge.py]
- `[MODIFY]` @[backend_v2/database/repositories/identity.py]
- `[MODIFY]` @[backend_v2/database/repositories/audit.py]
- `[MODIFY]` @[backend_v2/database/repositories/component.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/task_blueprint.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/role.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/prompt_block.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/output_profile.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/matrix.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/extraction_protocol.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/execution_persona.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/agent.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_repositories_v2.py]
- `[MODIFY]` @[.agents/rules/01-python-backend.md#L176-L178]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify all foundational DTOs and database paths are strictly locked.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/database/repositories/execution.py#L92-L100] and the other 14 repository files.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Blob trace deserialization in @[backend_v2/database/repositories/execution.py#L92-L100] refactored: `data[field] = json.loads(decoded)` replaced with `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContextDTO.model_validate_json(blob_data)`.
    - [ ] Every DAL method in all 15 repository files updated to return typed Pydantic Domain models (`ConfigDict(frozen=True)`):
      - @[backend_v2/database/repositories/execution.py]
      - @[backend_v2/database/repositories/system.py]
      - @[backend_v2/database/repositories/workflow.py]
      - @[backend_v2/database/repositories/knowledge.py]
      - @[backend_v2/database/repositories/identity.py]
      - @[backend_v2/database/repositories/audit.py]
      - @[backend_v2/database/repositories/component.py]
      - @[backend_v2/database/repositories/components/task_blueprint.py]
      - @[backend_v2/database/repositories/components/role.py]
      - @[backend_v2/database/repositories/components/prompt_block.py]
      - @[backend_v2/database/repositories/components/output_profile.py]
      - @[backend_v2/database/repositories/components/matrix.py]
      - @[backend_v2/database/repositories/components/extraction_protocol.py]
      - @[backend_v2/database/repositories/components/execution_persona.py]
      - @[backend_v2/database/repositories/components/agent.py]
    - [ ] Service layer never sees `dict[str, Any]` from repository read calls; internal repositories validate raw driver dicts using `Model.model_validate(raw_dict)`.
    - [ ] All repository unit tests in @[backend_v2/tests/unit/test_repositories_v2.py] (and dedicated repository test suites) modernized atomically to assert typed Domain models.
    - [ ] Rule `service_layer_hydration_firewall` in @[.agents/rules/01-python-backend.md#L176-L178] updated to align with `repository_reconstitution_mandate` (@[.agents/rules/01-python-backend.md#L360-L362]).
    - [ ] Backend quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/database/repositories/execution.py]</backend>
    <backend>@[backend_v2/database/repositories/system.py]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py]</backend>
    <backend>@[backend_v2/database/repositories/knowledge.py]</backend>
    <backend>@[backend_v2/database/repositories/identity.py]</backend>
    <backend>@[backend_v2/database/repositories/audit.py]</backend>
    <backend>@[backend_v2/database/repositories/component.py]</backend>
    <backend>@[backend_v2/database/repositories/components/task_blueprint.py]</backend>
    <backend>@[backend_v2/database/repositories/components/role.py]</backend>
    <backend>@[backend_v2/database/repositories/components/prompt_block.py]</backend>
    <backend>@[backend_v2/database/repositories/components/output_profile.py]</backend>
    <backend>@[backend_v2/database/repositories/components/matrix.py]</backend>
    <backend>@[backend_v2/database/repositories/components/extraction_protocol.py]</backend>
    <backend>@[backend_v2/database/repositories/components/execution_persona.py]</backend>
    <backend>@[backend_v2/database/repositories/components/agent.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/hooks/` in Phase 2 (strictly reserved for Phase 3).
    - Do NOT modify `backend_v2/services/orchestrator/` in Phase 2 (strictly reserved for Phase 4).
    - Do NOT modify `backend_v2/services/execution.py` or service layer callers in Phase 2 (reserved for Phase 5).
    - Do NOT leave raw `dict[str, Any]` returns in repository method signatures (`repository_reconstitution_mandate`).
  </anti_targets>

  <step id="1" name="STORAGE BLOB HYDRATION MODERNIZATION">
    <action>Refactor @[backend_v2/database/repositories/execution.py#L92-L100] to replace `json.loads(decoded)` with Rust-level Pydantic V2 hydration: `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContextDTO.model_validate_json(blob_data)`.</action>
    <demolish>REMOVE: `data[field] = json.loads(decoded)` at @[backend_v2/database/repositories/execution.py#L92-L100]. REPLACE WITH: Rust-level `model_validate_json()` / `TypeAdapter(T).validate_json()` hydration.</demolish>
  </step>

  <step id="2" name="REPOSITORY RECONSTITUTION TO TYPED DOMAIN MODELS">
    <action>Refactor all DAL read methods across @[backend_v2/database/repositories/execution.py], @[backend_v2/database/repositories/system.py], @[backend_v2/database/repositories/workflow.py], @[backend_v2/database/repositories/knowledge.py], @[backend_v2/database/repositories/identity.py], @[backend_v2/database/repositories/audit.py], @[backend_v2/database/repositories/component.py], and all component repositories in @[backend_v2/database/repositories/components/] to return typed Pydantic Domain models (`ConfigDict(frozen=True)`).</action>
    <constraint invariant="repository_reconstitution_mandate">All DAL methods return strictly typed Pydantic models. Service layer never sees raw dicts.</constraint>
  </step>

  <step id="3" name="RULE SYNCHRONIZATION & ATOMIC DAL TESTS">
    <action>Update rule `service_layer_hydration_firewall` in @[.agents/rules/01-python-backend.md#L176-L178] to align with `repository_reconstitution_mandate` (@[.agents/rules/01-python-backend.md#L360-L362]).</action>
    <action>Modernize all unit test fixtures and assertions in @[backend_v2/tests/unit/test_repositories_v2.py] to assert typed domain model attributes instead of dictionary keys.</action>
  </step>

  <test_contracts>
    <test name="test_execution_repo_get_execution_returns_typed_model" category="positive">
      <input>mock_driver returning valid execution dictionary</input>
      <expected>returns ExecutionRecord instance with typed attributes</expected>
    </test>
    <test name="test_execution_repo_blob_hydration_valid_json" category="positive">
      <input>Storage driver containing valid JSON byte blobs for execution_trace</input>
      <expected>execution_trace hydrated into list[StepOutputDTO] without json.loads()</expected>
    </test>
    <test name="test_execution_repo_blob_hydration_corrupted_json_raises_app_exception" category="error_path">
      <input>Storage driver containing corrupted JSON bytes</input>
      <expected>raises AppException with ErrorCodes.DATA_CORRUPTION</expected>
    </test>
    <test name="test_workflow_repo_get_workflow_returns_typed_model" category="positive">
      <input>mock_driver returning valid workflow dictionary</input>
      <expected>returns Workflow instance with ConfigDict(frozen=True)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Backend Quality Gate for Repositories -->
    uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_repositories_v2.py --test
  </validation_gate>
</execution_protocol>
```
