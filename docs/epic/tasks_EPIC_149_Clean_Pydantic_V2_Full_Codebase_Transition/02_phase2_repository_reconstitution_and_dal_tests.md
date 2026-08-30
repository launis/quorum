# Phase 2: Repository Reconstitution, Storage Blob Hydration & DAL Tests

**Overview:** Transition all Data Access Layer (Repository) methods from returning untyped `dict[str, Any]` to returning validated, frozen Pydantic Domain Models, replace all blob trace deserialization (`json.loads(decoded)`) with Rust-level Pydantic V2 hydration (`TypeAdapter(T).validate_json()`), modernize `backend_v2/database/interfaces.py` protocol definitions, atomically modernize 100% of repository unit tests across `backend_v2/tests/unit/database/`, and update rule `service_layer_hydration_firewall` (@[.agents/rules/01-python-backend.md#L176-L178]) to align with the `repository_reconstitution_mandate` (@[.agents/rules/01-python-backend.md#L360-L362]).
**Target Files:**
- `[MODIFY]` @[backend_v2/database/interfaces.py]
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
- `[MODIFY]` @[backend_v2/tests/unit/database/test_repository.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/test_component.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/test_system.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/test_execution.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/test_workflow.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/test_knowledge.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/test_identity.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/test_audit.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_agent.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_role.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_matrix.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/components/test_extraction_protocol.py]
- `[NEW]` @[backend_v2/tests/unit/database/repositories/components/test_execution_persona.py]
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
    - [ ] Protocol definitions in @[backend_v2/database/interfaces.py] updated to return typed Domain models across all 15 interfaces (`IExecutionRepository`, `IWorkflowRepository`, `IKnowledgeRepository`, `IIdentityRepository`, `IAuditRepository`, `IComponentRepository`, `ITaskBlueprintRepository`, `IRoleRepository`, `IPromptBlockRepository`, `IOutputProfileRepository`, `IMatrixRepository`, `IExtractionProtocolRepository`, `IExecutionPersonaRepository`, `IAgentRepository`, `ISystemRepository`).
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
    - [ ] All repository unit tests in @[backend_v2/tests/unit/test_repositories_v2.py] and dedicated test suites in `backend_v2/tests/unit/database/repositories/` modernized atomically to assert typed Domain models.
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
    <backend>@[backend_v2/database/interfaces.py]</backend>
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
    <backend_v2>@[backend_v2/database/repositories/components/matrix.py]</backend_v2>
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

  ## Phase 1: Pre-Implementation Cleanups & Technical Debt Eradication
  - **`backend_v2/database/repositories/execution.py`**:
    - Purge banned `.get()` calls on `data` dictionary (e.g. line 121, 147, 178, 228, 238) and replace with direct access or Pydantic validation.
    - Purge broad `except Exception:` handlers without typed `AppException` wrapping or re-raising (lines 155, 285, 317).
  - **`backend_v2/database/repositories/workflow.py`**:
    - Replace `Workflow(**data)` (line 71) with `Workflow.model_validate(data, strict=False)`.
    - Unify `get_workflow` and `get_workflow_definition` to return `Workflow | None`.
  - **`backend_v2/database/repositories/identity.py`**:
    - Unify `get_organization` and `get_organization_model` to return `Organization | None`.
    - Modernize `list_organizations` to return `list[Organization]`.
  - **`backend_v2/database/repositories/components/output_profile.py`**:
    - Unify `get_all_output_profiles` and `get_all_output_profiles_models` to return `list[OutputProfile]`.
  - **`backend_v2/database/interfaces.py`**:
    - Update all repository protocols to define typed Domain return types matching implementations.

  ## 5-Column Architectural Directive Table

  | 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
  | :--- | :--- | :--- | :--- | :--- |
  | **Storage Blob Hydration** (`repositories/execution.py#L92-L100`) | Banned `data[field] = json.loads(decoded)` and loose dictionary string parsing | Use Rust-level `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContextDTO.model_validate_json(blob_data)` | Zero intermediate wrapper dicts; validate directly from raw bytes | Corrupted JSON bytes triggers Fail-Fast `AppException` with `ErrorCodes.DATA_CORRUPTION` |
  | **Execution Repository** (`repositories/execution.py`) | Banned `.get("field")` and returning untyped dictionaries for executions or audit trails | All DAL methods return `ExecutionRecord | None`, `list[ExecutionRecord]`, or `MCPAuditTrace` instances | No parallel DTO conversion in repository; direct Pydantic model validation | `test_execution.py` verifying typed `ExecutionRecord` attributes and blob hydration |
  | **Workflow Repository** (`repositories/workflow.py`) | Banned `Workflow(**data)` legacy instantiation and returning raw `dict[str, Any]` for steps and workflows | Reconstitute DAL to return `Workflow | None`, `list[Workflow]`, `V2Step | None`, and `list[V2Step]` via `Workflow.model_validate(data)` | Delete parallel `get_workflow` vs `get_workflow_definition` duplicate methods | `test_workflow.py` verifying typed `Workflow` and `V2Step` model returns |
  | **System Repository** (`repositories/system.py`) | Banned returning raw `dict[str, Any]` for system configurations | Return strictly typed `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `SystemConfigPerformativeLexicons` | Unified system config query methods without redundant fallback branches | `test_system.py` asserting typed `SystemConfig*` instances with `strict=True` |
  | **Knowledge Repository** (`repositories/knowledge.py`) | Banned returning raw dicts for concepts and prompt templates | Return typed `list[BannedPhrase]`, `PromptTemplateDTO`, and `list[Concept]` | Pure Pydantic models; zero raw dictionary queries returning to callers | `test_knowledge.py` verifying typed model returns for all knowledge queries |
  | **Identity Repository** (`repositories/identity.py`) | Banned separate `get_organization` (dict) and `get_organization_model` (model) duplicate paths | Single canonical `get_organization(...) -> Organization | None` and `list_organizations(...) -> list[Organization]` | Delete duplicate `get_organization_model` method; single SSOT method | `test_identity.py` asserting `Organization` and `User` Pydantic models |
  | **Audit Repository** (`repositories/audit.py`) | Banned returning raw dicts for audit logs and usage records | Return `list[AuditLogEntry]` and `list[UsageRecord]` strictly validated via Pydantic | Direct TypeAdapter validation from query results; no manual dictionary loops | `test_audit.py` asserting typed `AuditLogEntry` and `UsageRecord` models |
  | **Component Repositories** (`repositories/components/*.py`) | Banned returning raw `dict[str, Any]` from `task_blueprint.py`, `role.py`, `prompt_block.py`, `output_profile.py`, `matrix.py`, `extraction_protocol.py`, `execution_persona.py`, `agent.py` | Each component DAL returns its typed Pydantic Domain Model (`TaskBlueprint`, `Role`, `PromptBlock`, `OutputProfile`, `Matrix`, `ExtractionProtocol`, `ExecutionPersona`, `Agent`) | Replaced duplicate `*_models` methods with unified typed methods | Component test suites in `tests/unit/database/repositories/components/` verifying 100% typed returns |
  | **Database Interfaces** (`database/interfaces.py`) | Banned protocols specifying `dict[str, Any]` return signatures | Modernize all 15 protocol definitions to declare typed Pydantic Domain model return types | Strict Interface Segregation Principle; zero ambiguous signatures | MyPy `--strict` verification across `database/interfaces.py` and `database/repositories/` |
  | **Rule Synchronization** (`01-python-backend.md#L176-L178`) | Banned conflicting rule stating "Repository returns raw polymorphic dict[str, Any]" | Update `service_layer_hydration_firewall` to mandate that DAL returns strictly typed Pydantic models | Aligned with `repository_reconstitution_mandate` (#L360-L362) | Markdown boundary verification and rules consistency audit |

  <step id="1" name="STORAGE BLOB HYDRATION MODERNIZATION">
    <action>Refactor @[backend_v2/database/repositories/execution.py#L92-L100] to replace `json.loads(decoded)` with Rust-level Pydantic V2 hydration: `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContextDTO.model_validate_json(blob_data)`.</action>
    <demolish>REMOVE: `data[field] = json.loads(decoded)` at @[backend_v2/database/repositories/execution.py#L92-L100]. REPLACE WITH: Rust-level `model_validate_json()` / `TypeAdapter(T).validate_json()` hydration.</demolish>
  </step>

  <step id="2" name="REPOSITORY RECONSTITUTION TO TYPED DOMAIN MODELS">
    <action>Refactor all DAL read methods across @[backend_v2/database/repositories/execution.py], @[backend_v2/database/repositories/system.py], @[backend_v2/database/repositories/workflow.py], @[backend_v2/database/repositories/knowledge.py], @[backend_v2/database/repositories/identity.py], @[backend_v2/database/repositories/audit.py], @[backend_v2/database/repositories/component.py], and all component repositories in @[backend_v2/database/repositories/components/] to return typed Pydantic Domain models (`ConfigDict(frozen=True)`).</action>
    <constraint invariant="repository_reconstitution_mandate">All DAL methods return strictly typed Pydantic models. Service layer never sees raw dicts.</constraint>
  </step>

  <step id="3" name="DATABASE PROTOCOL INTERFACES MODERNIZATION">
    <action>Refactor all 15 protocol definitions in @[backend_v2/database/interfaces.py] to specify strictly typed Pydantic Domain Model return signatures matching the reconstituted repository implementations.</action>
    <constraint invariant="python_314_modern_syntax">All protocol signatures use strict typing, PEP 695 / PEP 593 syntax, and zero naked dict returns.</constraint>
  </step>

  <step id="4" name="RULE SYNCHRONIZATION & ATOMIC DAL TESTS">
    <action>Update rule `service_layer_hydration_firewall` in @[.agents/rules/01-python-backend.md#L176-L178] to align with `repository_reconstitution_mandate` (@[.agents/rules/01-python-backend.md#L360-L362]).</action>
    <action>Modernize all unit test fixtures and assertions in @[backend_v2/tests/unit/test_repositories_v2.py] and dedicated test suites in @[backend_v2/tests/unit/database/repositories/] to assert typed domain model attributes instead of dictionary keys.</action>
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
    <test name="test_execution_repo_blob_hydration_empty_bytes_raises_app_exception" category="error_path">
      <input>Storage driver returning 0-byte empty blob</input>
      <expected>raises AppException with ErrorCodes.DATA_CORRUPTION</expected>
    </test>
    <test name="test_workflow_repo_get_workflow_returns_typed_model" category="positive">
      <input>mock_driver returning valid workflow dictionary</input>
      <expected>returns Workflow instance with ConfigDict(frozen=True)</expected>
    </test>
    <test name="test_workflow_repo_get_step_returns_typed_model" category="positive">
      <input>mock_driver returning valid step dictionary</input>
      <expected>returns V2Step instance with typed attributes</expected>
    </test>
    <test name="test_system_repo_get_model_registry_returns_typed_model" category="positive">
      <input>mock_driver returning valid model_registry system_config dictionary</input>
      <expected>returns SystemConfigModelRegistry instance</expected>
    </test>
    <test name="test_system_repo_missing_config_raises_resource_not_found" category="error_path">
      <input>mock_driver returning empty query result</input>
      <expected>raises ResourceNotFoundError with resource_type='system_config'</expected>
    </test>
    <test name="test_identity_repo_get_organization_returns_typed_model" category="positive">
      <input>mock_driver returning valid organization dictionary</input>
      <expected>returns Organization instance with ConfigDict(strict=True)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Backend Quality Gate for Repositories -->
    uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test
    uv run python scripts/backend_audit_loop.py backend_v2/database/interfaces.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_repositories_v2.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/database/ --test
  </validation_gate>
</execution_protocol>
```

