<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

# Phase 1: Pre-Implementation Technical Debt Cleanups, Zero-ORM Identity Schema & `PrefixedUUID7` DTOs

**Overview:** Demolish the four obsolete historical IAM draft documents and `backend_v2/services/auth/constants.py`, remediate touched-scope technical debt in IAM models, repositories, and test suites, centralize IAM and BYOK taxonomies, error codes, and settings in `enums.py`, `exceptions.py`, and `settings.py`, define strict `PrefixedUUID7` DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) in `backend_v2/models/auth.py` and `backend_v2/models/domain/execution.py`, and extend the PostgreSQL 19 Zero-ORM schema (`001_pg19_uuidv7_schema.sql`), `PostgresEntityAdapter`, `PostgresUnitOfWork`, `audit_zero_orm_strictness.py`, and hermetic `in_memory_uow.py` with `invitations`, `tenant_secrets`, `execution_assignments`, and Dual-Layer Tenant Isolation.
**Source:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]

**Target Files:**
- `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 1 (Valmistelu).md]`
- `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 2 (Integraatio).md]`
- `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2.md]`
- `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026.md]`
- `[DELETE] @[backend_v2/services/auth/constants.py]`
- `[MODIFY] @[backend_v2/settings.py]`
- `[MODIFY] @[backend_v2/models/enums.py]`
- `[MODIFY] @[backend_v2/exceptions.py#L129-L321]`
- `[MODIFY] @[backend_v2/models/auth.py#L48-L63]`
- `[MODIFY] @[backend_v2/models/auth.py#L66-L79]`
- `[MODIFY] @[backend_v2/models/auth.py#L82-L103]`
- `[MODIFY] @[backend_v2/models/auth.py#L112-L230]`
- `[MODIFY] @[backend_v2/models/auth.py#L233-L274]`
- `[MODIFY] @[backend_v2/models/auth.py#L280-L358]`
- `[MODIFY] @[backend_v2/models/auth.py#L440-L469]`
- `[MODIFY] @[backend_v2/models/auth.py#L501-L556]`
- `[MODIFY] @[backend_v2/models/auth.py#L573-L582]`
- `[MODIFY] @[backend_v2/models/auth.py#L585-L598]`
- `[MODIFY] @[backend_v2/models/auth.py#L601-L610]`
- `[MODIFY] @[backend_v2/models/auth.py#L613-L624]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L85-L129]`
- `[MODIFY] @[backend_v2/seed/seed_data.json]`
- `[MODIFY] @[scripts/sanitize_seed_vault.py]`
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/database/postgres/uow.py]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/database/interfaces.py]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L25-L272]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L60-L72]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L163-L175]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L219-L228]`
- `[MODIFY] @[backend_v2/services/auth/repositories.py#L15-L78]`
- `[MODIFY] @[backend_v2/services/auth/repositories.py#L81-L182]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_auth.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_auth_models.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_auth_validator.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_identity.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Identity Schema, Pre-Flight Tech Debt & `PrefixedUUID7` DTOs**<br>`[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 1 (Valmistelu).md]`<br>`[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 2 (Integraatio).md]`<br>`[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2.md]`<br>`[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026.md]`<br>`[DELETE] @[backend_v2/services/auth/constants.py]`<br>`[MODIFY] @[backend_v2/settings.py]`<br>`[MODIFY] @[backend_v2/models/enums.py]`<br>`[MODIFY] @[backend_v2/exceptions.py#L129-L321]`<br>`[MODIFY] @[backend_v2/models/auth.py#L48-L63]`<br>`[MODIFY] @[backend_v2/models/auth.py#L66-L79]`<br>`[MODIFY] @[backend_v2/models/auth.py#L82-L103]`<br>`[MODIFY] @[backend_v2/models/auth.py#L112-L230]`<br>`[MODIFY] @[backend_v2/models/auth.py#L233-L274]`<br>`[MODIFY] @[backend_v2/models/auth.py#L280-L358]`<br>`[MODIFY] @[backend_v2/models/auth.py#L440-L469]`<br>`[MODIFY] @[backend_v2/models/auth.py#L501-L556]`<br>`[MODIFY] @[backend_v2/models/auth.py#L573-L582]`<br>`[MODIFY] @[backend_v2/models/auth.py#L585-L598]`<br>`[MODIFY] @[backend_v2/models/auth.py#L601-L610]`<br>`[MODIFY] @[backend_v2/models/auth.py#L613-L624]`<br>`[MODIFY] @[backend_v2/models/domain/execution.py#L85-L129]`<br>`[MODIFY] @[backend_v2/seed/seed_data.json]`<br>`[MODIFY] @[scripts/sanitize_seed_vault.py]`<br>`[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`<br>`[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`<br>`[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`<br>`[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`<br>`[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`<br>`[MODIFY] @[backend_v2/database/postgres/uow.py]`<br>`[MODIFY] @[scripts/audit_zero_orm_strictness.py]`<br>`[MODIFY] @[backend_v2/database/interfaces.py]`<br>`[MODIFY] @[backend_v2/database/repositories/identity.py#L25-L272]`<br>`[MODIFY] @[backend_v2/services/auth/repositories.py#L15-L78]`<br>`[MODIFY] @[backend_v2/services/auth/repositories.py#L81-L182]`<br>`[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`<br>`[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_auth.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_auth_models.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`<br>`[MODIFY] @[backend_v2/tests/unit/services/studio/test_auth_validator.py]`<br>`[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`<br>`[MODIFY] @[backend_v2/tests/unit/database/repositories/test_identity.py]`<br>`[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`<br>`[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`<br>`[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]` | Raw Firebase UID as SQL PK; `hashids` library; inline `UserRole`/`SubscriptionStatus` in `auth.py`; legacy 16-char `"org_system000000"` string in `ROOT_SYSTEM` on `SystemOrganizations`, `seed_data.json`, and `PostgresEntityAdapter`; missing `frozen=True` on `User`/`Organization`/`TokenData`; `driver.get` in `identity.py`; 3 `TD_ISTQB_NEGATIVE` warnings in `test_auth.py`, `test_auth_validator.py`, and `test_seed_and_collection_stage.py`; and 4 `TD_MODEL_FACTORY` warnings in `test_auth_models.py`. | Native PostgreSQL 19 `UUID PRIMARY KEY DEFAULT uuidv7()` bridged via `_to_pg_uuid` / `_from_pg_uuid` to RFC 9562 `PrefixedUUID7` (`usr_<hex32>`, `org_<hex32>`, `inv_<hex32>`, `sec_<hex32>`, `tsk_<hex32>`); `ROOT_SYSTEM = "org_0195f3a0000070008000000000000001"` and `SYSTEM_ROOT_USER_ID = "usr_0195f3a00000700a83fd6b3d77c748f4"`; `firebase_uid VARCHAR(128) UNIQUE NOT NULL`; `deleted_at TIMESTAMPTZ`; Dual-Layer Tenant Isolation (`WHERE organization_id = $1` + `RESET quorum.current_org`); hermetic `InMemoryAsyncPgConnection` SQL emulation for `invitations`, `tenant_secrets`, and `execution_assignments`; `ConfigDict(strict=True, extra="forbid", frozen=True)`. | Pruned N:M user-organization membership join tables and special-case `"org_system000000"` string shims in `PostgresEntityAdapter`; enforced flat 1:1 `organization_id` on `User`. | `uv run python scripts/backend_audit_loop.py backend_v2/models/auth.py backend_v2/database/repositories/identity.py --test --ast-strict` (0 findings) and `ZORM004`/`ZORM006` AST verification. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Read the `<required_context_rules>` block, `00-antigravity-core.md`, `01-python-backend.md`, `03_seed_vault.md`, and `04_directory_reference.md` before executing any changes.</action>
    <constraint>Enforce `zero_loss_mandate`, `the_zero_compromise_pledge`, `the_no_legacy_mandate`, and `preflight_schema_assertion_mandate` across all schema, DTO, and adapter updates.</constraint>
  </step>

  <demolish>
  - `LEGACY_SYSTEM`
  - `JWT_SECRET`
  - `JWT_ALGORITHM`
  - `LEGACY_SYSTEM_ROOT_USER_ID`
  - `LEGACY_SYSTEM_ORG_ID`
  - `LEGACY_ROOT_MASTER_ID`
  - `TokenPayload`
  - `LoginResponse`
  - `verify_user_token`
  </demolish>

  <touched_artifacts>
    <backend>[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 1 (Valmistelu).md]</backend>
    <backend>[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 2 (Integraatio).md]</backend>
    <backend>[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2.md]</backend>
    <backend>[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026.md]</backend>
    <backend>[DELETE] @[backend_v2/services/auth/constants.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/models/enums.py]</backend>
    <backend>@[backend_v2/exceptions.py#L129-L321]</backend>
    <backend>@[backend_v2/models/auth.py#L48-L63]</backend>
    <backend>@[backend_v2/models/auth.py#L66-L79]</backend>
    <backend>@[backend_v2/models/auth.py#L82-L103]</backend>
    <backend>@[backend_v2/models/auth.py#L112-L230]</backend>
    <backend>@[backend_v2/models/auth.py#L233-L274]</backend>
    <backend>@[backend_v2/models/auth.py#L280-L358]</backend>
    <backend>@[backend_v2/models/auth.py#L440-L469]</backend>
    <backend>@[backend_v2/models/auth.py#L501-L556]</backend>
    <backend>@[backend_v2/models/auth.py#L573-L582]</backend>
    <backend>@[backend_v2/models/auth.py#L585-L598]</backend>
    <backend>@[backend_v2/models/auth.py#L601-L610]</backend>
    <backend>@[backend_v2/models/auth.py#L613-L624]</backend>
    <backend>@[backend_v2/models/domain/execution.py#L85-L129]</backend>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <backend>@[scripts/sanitize_seed_vault.py]</backend>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/database/postgres/uow.py]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/database/interfaces.py]</backend>
    <backend>@[backend_v2/database/repositories/identity.py#L25-L272]</backend>
    <backend>@[backend_v2/services/auth/repositories.py#L15-L78]</backend>
    <backend>@[backend_v2/services/auth/repositories.py#L81-L182]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py]</backend>
    <backend>@[backend_v2/tests/unit/test_auth.py]</backend>
    <backend>@[backend_v2/tests/unit/test_auth_models.py]</backend>
    <backend>@[backend_v2/tests/unit/test_enum_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_auth_validator.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_workflow_service.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_identity.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>All four obsolete IAM draft markdown documents (`[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 1 (Valmistelu).md]`, `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 2 (Integraatio).md]`, `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2.md]`, and `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026.md]`) and `[DELETE] @[backend_v2/services/auth/constants.py]` are physically deleted.</item>
    <item>`UserRole`, `SubscriptionStatus`, `InvitationStatus`, `AssignmentStatus`, `AssignmentResultVisibility`, `EmailTransportMode`, `EmailDeliveryStatus`, `SecretScope`, `SecretStorageMode`, and `EntityPrefix` (`INVITATION = "inv"`, `TENANT_SECRET = "sec"`, `ASSIGNMENT = "tsk"`) are defined in `@[backend_v2/models/enums.py]`, and new IAM/BYOK error codes are registered in `@[backend_v2/exceptions.py#L129-L321]`.</item>
    <item>`Organization`, `User`, `TokenData`, and all newly created IAM, Invitation, Task Assignment, and BYOK DTOs in `@[backend_v2/models/auth.py]` and `@[backend_v2/models/domain/execution.py#L85-L129]` enforce `ConfigDict(strict=True, extra="forbid", frozen=True)` and `OPAQUE_STRIPE_ID_REGEX` (`ROOT_SYSTEM = "org_0195f3a0000070008000000000000001"` and `SYSTEM_ROOT_USER_ID = "usr_0195f3a00000700a83fd6b3d77c748f4"`), while `LEGACY_SYSTEM`, `TokenPayload`, and `LoginResponse` are demolished.</item>
    <item>`users`, `organizations`, `invitations`, `tenant_secrets`, and `execution_assignments` tables in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[scripts/audit_zero_orm_strictness.py]`, and `@[backend_v2/tests/fakes/in_memory_uow.py]` enforce 15-table PostgreSQL 19 `UUID PRIMARY KEY DEFAULT uuidv7()` parity and Dual-Layer Tenant Isolation (`WHERE organization_id = $1` + `RESET quorum.current_org` in `@[backend_v2/database/postgres/uow.py]`).</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <file>@[backend_v2/services/orchestrator/dag_executor/__init__.py] (Do not mutate DAG Orchestrator core during Phase 1 IAM schema & DTO setup)</file>
    <file>@[client_app_v2/lib/router/router.dart] (Do not modify Flutter routing in Phase 1; reserved strictly for Phase 6)</file>
  </anti_targets>

  <step id="1.1" name="Obsolete Document Demolition &amp; Touched-Scope Technical Debt Remediation">
    <action>
      - Physically delete the four superseded historical IAM draft documents:
        - `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 1 (Valmistelu).md]`
        - `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2 - Osa 2 (Integraatio).md]`
        - `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026 vrs2.md]`
        - `[DELETE] @[docs/epic/B2B SaaS IAM-arkkitehtuuri 2026.md]`
      - **`[MODIFY] @[backend_v2/database/repositories/identity.py#L25-L272]`, `[MODIFY] @[backend_v2/database/repositories/identity.py#L60-L72]`, `[MODIFY] @[backend_v2/database/repositories/identity.py#L163-L175]`, `[MODIFY] @[backend_v2/database/repositories/identity.py#L219-L228]`, `[MODIFY] @[backend_v2/database/interfaces.py]`, `[MODIFY] @[backend_v2/services/auth/repositories.py#L15-L78]`, `[MODIFY] @[backend_v2/services/auth/repositories.py#L81-L182]`, & `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`**:
        - Eliminate `TD_DICT_GET` warnings on lines 69 and 172 of `@[backend_v2/database/repositories/identity.py#L25-L272]` by delegating identity persistence through the typed `EntityPersistencePort` / `PostgresEntityAdapter` contract (`[MODIFY] @[backend_v2/database/interfaces.py]`, `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`, and `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`) with zero untyped `.get()` dictionary calls, and synchronize `@[backend_v2/services/auth/repositories.py#L15-L78]`, `@[backend_v2/services/auth/repositories.py#L81-L182]`, and `@[backend_v2/tests/fakes/in_memory_repositories.py]`.
      - **`[MODIFY] @[backend_v2/tests/unit/test_auth.py]`, `[MODIFY] @[backend_v2/tests/unit/test_auth_models.py]`, `[MODIFY] @[backend_v2/tests/unit/services/studio/test_auth_validator.py]`, `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`, `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_identity.py]`, `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`, & `[MODIFY] @[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`**:
        - Remediate the 3 `TD_ISTQB_NEGATIVE` warnings in `@[backend_v2/tests/unit/test_auth.py]`, `@[backend_v2/tests/unit/services/studio/test_auth_validator.py]`, and `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]` by adding explicit negative partition test functions (`test_*_failure`, `test_*_invalid`, `test_*_error`), remediate the 4 `TD_MODEL_FACTORY` warnings in `@[backend_v2/tests/unit/test_auth_models.py]` by replacing raw dict literals inside `Organization.model_validate` and `User.model_validate` with typed `ModelFactory` / constructor calls, and atomically synchronize all IAM, seed, and entity adapter test fixtures (`@[backend_v2/seed/seed_data.json]`, `@[scripts/sanitize_seed_vault.py]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`, `@[backend_v2/tests/unit/database/repositories/test_identity.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, and `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`) with `ROOT_SYSTEM = "org_0195f3a0000070008000000000000001"` in `SystemOrganizations`, `SYSTEM_ROOT_USER_ID = "usr_0195f3a00000700a83fd6b3d77c748f4"` in `@[backend_v2/models/auth.py#L82-L103]`, and `OPAQUE_STRIPE_ID_REGEX`.
      - **`[DELETE] @[backend_v2/services/auth/constants.py]` & `[MODIFY] @[backend_v2/settings.py]`**:
        - Delete `[DELETE] @[backend_v2/services/auth/constants.py]` (eradicating `JWT_SECRET`, `JWT_ALGORITHM`, `LEGACY_SYSTEM_ROOT_USER_ID`, `LEGACY_SYSTEM_ORG_ID`, and `LEGACY_ROOT_MASTER_ID`, and relocating canonical `SYSTEM_ROOT_USER_ID = "usr_0195f3a00000700a83fd6b3d77c748f4"` to `@[backend_v2/models/auth.py#L82-L103]` and re-exporting it in `@[backend_v2/services/auth/__init__.py#L59-L202]`) and declare environment-injected settings on `Settings` in `@[backend_v2/settings.py]`: `jwt_secret_key: Annotated[SecretStr, Field(description="HMAC-SHA256 secret key for Quorum Local JWT signing")]`, `jwt_algorithm: Annotated[str, Field(default="HS256", description="JWT signing algorithm")]`, `jwt_access_token_expire_minutes: Annotated[int, Field(default=15, ge=5, le=60, description="Quorum Local JWT lifetime in minutes")]`, `require_mfa: Annotated[bool, Field(default=True, description="Enforce mandatory Multi-Factor Authentication (2FA) claim on token exchange")] = True`, `service_auth_secret: Annotated[SecretStr | None, Field(default=None, description="Shared secret for headless CLI/CI service token exchange")] = None`, `iam_revocation_ttl_seconds: Annotated[int, Field(default=900, ge=300, description="Redis kill-switch TTL in seconds")]`, `auth_edge_rpm_limit: Annotated[int, Field(default=20, ge=5, le=300, description="Sliding-window requests per minute per client IP for public auth, invitation, and assignment endpoints")] = 20`, `assignment_submission_grace_seconds: Annotated[int, Field(default=60, ge=0, le=600, description="Grace window in seconds for in-flight task assignment submissions")] = 60`, `email_transport_mode: Annotated[EmailTransportMode, Field(default="console", description="Transactional email transport mode: console for local dev/tests or http_api for GCP Cloud Run HTTPS batch delivery")]`, `email_from_address: Annotated[str, Field(default="no-reply@qrum.ai", min_length=3, description="Canonical sender email address aligned with primary_domain")] = "no-reply@qrum.ai"`, `email_api_endpoint: Annotated[str | None, Field(default=None, description="HTTPS transactional batch email API endpoint URL on port 443")] = None`, `email_api_key: Annotated[SecretStr | None, Field(default=None, description="Secret API key for transactional email provider injected via GCP Secret Manager")] = None`, `email_http_timeout_seconds: Annotated[float, Field(default=10.0, ge=1.0, le=60.0, description="Bounded timeout in seconds for HTTPS transactional email batch API calls")] = 10.0`, `frontend_app_base_url: Annotated[str, Field(default="https://app.qrum.ai", min_length=8, description="Canonical frontend base URL for constructing /task/<token> and invitation links")] = "https://app.qrum.ai"`, `kms_master_key_id: Annotated[str | None, Field(default=None, description="Cloud KMS key resource URI for BYOK envelope encryption")]`, and `firebase_webhook_secret: Annotated[SecretStr | None, Field(default=None, description="Shared HMAC secret for Firebase user deletion webhooks")]`.
    </action>
  </step>

  <step id="1.2" name="Taxonomies, ErrorCodes &amp; Strict `PrefixedUUID7` Identity &amp; Assignment Models">
    <action>
      - **`[MODIFY] @[backend_v2/models/enums.py]`, `[MODIFY] @[backend_v2/exceptions.py#L129-L321]`, & `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`**:
        - Migrate `UserRole` and `SubscriptionStatus` from `@[backend_v2/models/auth.py#L48-L63]` and `@[backend_v2/models/auth.py#L66-L79]` into `@[backend_v2/models/enums.py]` (re-exporting them explicitly in `@[backend_v2/models/auth.py]` via `from backend_v2.models.enums import UserRole as UserRole, SubscriptionStatus as SubscriptionStatus`), remove `LEGACY_SYSTEM` from `SystemOrganizations` in `@[backend_v2/models/auth.py#L82-L103]` and set `ROOT_SYSTEM = "org_0195f3a0000070008000000000000001"`, and update `@[backend_v2/tests/unit/test_enum_parity.py]`.
        - Extend `EntityPrefix` in `@[backend_v2/models/enums.py]` with `INVITATION = "inv"`, `TENANT_SECRET = "sec"`, and `ASSIGNMENT = "tsk"`.
        - Define `InvitationStatus(StrEnum)` (`PENDING = "pending"`, `ACCEPTED = "accepted"`, `EXPIRED = "expired"`, `REVOKED = "revoked"`), `AssignmentStatus(StrEnum)` (`PENDING = "pending"`, `ACTIVATED = "activated"`, `SUBMITTED = "submitted"`, `COMPLETED = "completed"`, `EXPIRED = "expired"`, `REVOKED = "revoked"`), `AssignmentResultVisibility(StrEnum)` (`CONFIRMATION_ONLY = "confirmation_only"`, `FULL_REPORT_ACCESS = "full_report_access"`), `EmailTransportMode(StrEnum)` (`CONSOLE = "console"`, `HTTP_API = "http_api"`), `EmailDeliveryStatus(StrEnum)` (`PENDING = "pending"`, `SENT = "sent"`, `FAILED = "failed"`), `SecretScope(StrEnum)` (`LLM_PROVIDER = "llm_provider"`, `MCP_GATEWAY = "mcp_gateway"`), and `SecretStorageMode(StrEnum)` (`ENVELOPE_KMS = "envelope_kms"`, `CLOUD_SECRET_MANAGER = "cloud_secret_manager"`) in `@[backend_v2/models/enums.py]`.
        - Add `MFA_REQUIRED = "MFA_REQUIRED"`, `USER_ALREADY_ASSIGNED = "USER_ALREADY_ASSIGNED"`, `INVITATION_EXPIRED = "INVITATION_EXPIRED"`, `ASSIGNMENT_EXPIRED = "ASSIGNMENT_EXPIRED"`, `ASSIGNMENT_ALREADY_SUBMITTED = "ASSIGNMENT_ALREADY_SUBMITTED"`, `IDENTITY_MISMATCH = "IDENTITY_MISMATCH"`, and `SECRET_RESOLUTION_FAILED = "SECRET_RESOLUTION_FAILED"` to `ErrorCodes` in `@[backend_v2/exceptions.py#L129-L321]`.
      - **`[MODIFY] @[backend_v2/models/auth.py#L112-L230]`, `[MODIFY] @[backend_v2/models/auth.py#L233-L274]`, `[MODIFY] @[backend_v2/models/auth.py#L280-L358]`, `[MODIFY] @[backend_v2/models/auth.py#L440-L469]`, `[MODIFY] @[backend_v2/models/auth.py#L501-L556]`, `[MODIFY] @[backend_v2/models/auth.py#L573-L582]`, `[MODIFY] @[backend_v2/models/auth.py#L585-L598]`, `[MODIFY] @[backend_v2/models/auth.py#L601-L610]`, `[MODIFY] @[backend_v2/models/auth.py#L613-L624]`, & `[MODIFY] @[backend_v2/models/domain/execution.py#L85-L129]`**:
        - Enforce `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` across `Organization`, `OrganizationUpdateDTO`, `UserBase`, `User`, `TokenData`, and all DTOs in `@[backend_v2/models/auth.py]`, and delete the obsolete legacy `TokenPayload` (`@[backend_v2/models/auth.py#L573-L582]`) and `LoginResponse` (`@[backend_v2/models/auth.py#L585-L598]`) DTOs (`the_no_legacy_mandate`), replacing `LoginResponse` with newly created `TokenExchangeResponseDTO`.
        - Bind `id` fields on `Organization` (`org_<hex32>`) and `User` (`usr_<hex32>`) to `OPAQUE_STRIPE_ID_REGEX` and `generate_uuid7_opaque_id(EntityPrefix.ORG)` / `generate_uuid7_opaque_id(EntityPrefix.USER)` from `@[backend_v2/models/core_base.py]`.
        - Add `allowed_email_domains: Annotated[list[str], Field(default_factory=list, description="Optional allowlist of lowercase email domains permitted for organization invitations and task assignments")]` to `Organization` and `OrganizationUpdateDTO`, add `firebase_uid: Annotated[str | None, Field(default=None, min_length=1, max_length=128, description="External Firebase Auth UID")] = None` and `deleted_at: Annotated[datetime | None, Field(default=None, description="GDPR soft-deletion timestamp")] = None` to `User`, extend `ImpersonationRequest` (`@[backend_v2/models/auth.py#L601-L610]`) and `ImpersonationResponse` (`@[backend_v2/models/auth.py#L613-L624]`) with `target_id: PrefixedUUID7` and mandatory `reason: Annotated[str, Field(min_length=5, max_length=500, description="Mandatory ticket or support justification for break-glass impersonation")]`, and add `mfa_verified: Annotated[bool, Field(default=True, description="Whether the session satisfied Multi-Factor Authentication")] = True`, `jti: Annotated[str | None, Field(default=None, min_length=1, description="RFC 7519 unique JWT identifier for O(1) session revocation")] = None`, `actor_id: Annotated[PrefixedUUID7 | None, Field(default=None, description="RFC 8693 Actor ID when session is an administrative impersonation")] = None`, `iat: Annotated[int | None, Field(default=None, ge=0, description="Token issued-at UTC epoch timestamp in seconds")] = None`, and `exp: Annotated[int | None, Field(default=None, ge=0, description="Token expiration UTC epoch timestamp in seconds")] = None` to `TokenData`.
        - Create and define the following strict Pydantic V2 models in `@[backend_v2/models/auth.py]` and `@[backend_v2/models/domain/execution.py#L85-L129]`:
          - Create `TokenExchangeRequestDTO` defined with `firebase_token: Annotated[str | None, Field(default=None, min_length=10, description="External Firebase ID Token for interactive sessions")] = None`, `target_user_id: Annotated[PrefixedUUID7 | None, Field(default=None, description="Target seeded user ID for headless CLI, E2E, or local development token exchange")] = None`, `service_auth_secret: Annotated[SecretStr | None, Field(default=None, description="Optional shared service secret for headless M2M token exchange")] = None`, and a strict `@model_validator(mode="after")` enforcing mutual exclusivity (`(self.firebase_token is not None) ^ (self.target_user_id is not None)`, logging `ErrorCodes.VALIDATION_FAILED` and raising `ValueError` immediately if neither or both are supplied).
          - Create `TokenExchangeResponseDTO` defined with `access_token: Annotated[str, Field(min_length=10)]`, `token_type: Annotated[Literal["bearer"], Field(default="bearer")]`, `expires_in_seconds: Annotated[int, Field(ge=60)]`, `user: Annotated[User, Field(description="Authenticated user profile")]`.
          - Create `LogoutRequestDTO` defined with `revoke_all_sessions: Annotated[bool, Field(default=False, description="When True, revokes all active sessions for the user across all devices")] = False` (`ConfigDict(strict=True, extra="forbid", frozen=True)`).
          - Create `LogoutResponseDTO` (inheriting from `BaseResponseDTO`) defined with `status: Annotated[Literal["logged_out"], Field(default="logged_out")] = "logged_out"`, `revoked_jti: Annotated[str, Field(min_length=1, description="Revoked RFC 7519 token identifier")]`, and `all_sessions_revoked: Annotated[bool, Field(default=False, description="Whether all active sessions for the user were revoked")] = False`.
          - Create `CliSessionStateDTO` defined with `access_token: Annotated[str, Field(min_length=10)]`, `expires_at_monotonic: Annotated[float, Field(ge=0.0)]`, and `user_id: Annotated[PrefixedUUID7, Field(description="Authenticated CLI user ID")]` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) to encapsulate headless CLI / E2E session state without naked dicts or tuples (`the_zero_compromise_pledge` & `ban_anonymous_state_tuples`).
          - Create `Invitation` defined with `id` (`inv_<hex32>`), `organization_id` (`org_<hex32>`), `email` (`EmailStr`), `role` (`LaxUserRole`), `token_hash` (`str`), `status` (`InvitationStatus`), `email_delivery_status` (`Annotated[EmailDeliveryStatus, Field(default="pending", description="Transactional email delivery status")]`), `invited_by` (`usr_<hex32>`), `expires_at` (`datetime`), `created_at` (`datetime`).
          - Create `InvitationCreateDTO`, Create `InvitationAcceptRequestDTO`, and Create `InvitationResponseDTO` (inheriting from `BaseResponseDTO`), plus Create `InvitationBatchCreateDTO` (`recipients: Annotated[list[InvitationCreateDTO], Field(min_length=1, max_length=500)]`) and Create `InvitationBatchResponseDTO` (inheriting from `BaseResponseDTO`, containing `created_count: int` and `invitations: list[InvitationResponseDTO]`).
          - Create `ExecutionAssignment` defined with `id` (`tsk_<hex32>`), `batch_id` (`Annotated[PrefixedUUID7 | None, Field(default=None, description="Optional cohort batch identifier grouping bulk-created task assignments")] = None`), `organization_id` (`org_<hex32>`), `assigned_email` (`EmailStr`), `assigned_user_id` (`PrefixedUUID7 | None`), `invited_role` (`LaxUserRole`, defaulting to `"MEMBER"` on `UserRole`), `workflow_id` (`PrefixedUUID7`), `output_profile_id` (`PrefixedUUID7 | None`), `target_locale` (`SystemLocale`), `locked_inputs` (`WorkflowInputs`), `assignee_input_keys` (`list[str]`), `draft_inputs` (`WorkflowInputs`), `token_hash` (`str`), `status` (`AssignmentStatus`), `email_delivery_status` (`Annotated[EmailDeliveryStatus, Field(default="pending", description="Transactional email delivery status")]`), `result_visibility` (`AssignmentResultVisibility`), `hard_deadline_at` (`datetime`), `relative_duration_seconds` (`int | None`), `activated_at` (`datetime | None`), `submitted_at` (`datetime | None`), `execution_id` (`PrefixedUUID7 | None`), `created_by` (`PrefixedUUID7`), `created_at` (`datetime`).
          - Create `ExecutionAssignmentCreateDTO`, Create `ExecutionAssignmentRecipientDTO` (`email: EmailStr`, `name: Annotated[str | None, Field(default=None, min_length=1, max_length=120)] = None`, `target_locale: SystemLocale | None = None`), Create `ExecutionAssignmentBatchCreateDTO` (`recipients: Annotated[list[ExecutionAssignmentRecipientDTO], Field(min_length=1, max_length=500)]` plus shared `workflow_id`, `output_profile_id`, `target_locale`, `locked_inputs`, `assignee_input_keys`, `result_visibility`, `hard_deadline_at`, and `relative_duration_seconds`), Create `ExecutionAssignmentBatchResponseDTO` (inheriting from `BaseResponseDTO`, containing `batch_id: PrefixedUUID7`, `created_count: int`, and `assignments: list[ExecutionAssignmentResponseDTO]`), Create `TransactionalEmailItemDTO` (`entity_id: PrefixedUUID7`, `recipient_email: EmailStr`, `recipient_name: str | None = None`, `locale: SystemLocale`, `subject: str`, `html_body: str`, and `action_url: SecretStr` wrapping the raw token URL so cleartext tokens are never exposed in logs), Create `TransactionalEmailBatchResultDTO` (`sent_count: int`, `failed_count: int`, and `delivery_statuses: dict[PrefixedUUID7, EmailDeliveryStatus]`), Create `ExecutionAssignmentPreviewDTO`, Create `ExecutionAssignmentOnboardingRequestDTO`, Create `ExecutionAssignmentDraftDTO`, Create `ExecutionAssignmentSubmitDTO`, and Create `ExecutionAssignmentResponseDTO` (inheriting from `BaseResponseDTO`).
          - Create `TenantSecretDTO` (including `kek_version: Annotated[str, Field(min_length=1, max_length=128, description="Cloud KMS or local KEK version identifier used to wrap encrypted_dek")]` for zero-downtime NIST SP 800-57 master key rotation), Create `TenantSecretCreateDTO`, Create `TenantSecretResponseDTO` (exposing `id`, `organization_id`, `scope`, `target_identifier`, `storage_mode`, `configured: bool`, `masked_hint: str`, `kek_version: str`, `updated_at: datetime`, and NEVER exposing raw secret bytes or plaintext keys), and Create `ResolvedCredentialDTO` (holding `secret_value: SecretStr`).
    </action>
  </step>

  <step id="1.3" name="PostgreSQL 19 Zero-ORM Identity, Invitation, Task Assignment &amp; Secrets Schema + Dual-Layer Tenant Isolation">
    <action>
      - **`[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`, `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`, `[MODIFY] @[backend_v2/database/postgres/uow.py]`, `[MODIFY] @[scripts/audit_zero_orm_strictness.py]`, & `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py]`**:
        - Extend `organizations` table in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` with `allowed_email_domains JSONB NOT NULL DEFAULT '[]'::jsonb` and extend `users` table (`id UUID PRIMARY KEY DEFAULT uuidv7()` bridged to `PrefixedUUID7` `usr_<hex32>`, `organization_id UUID NOT NULL REFERENCES organizations(id)`) with `firebase_uid VARCHAR(128) UNIQUE` and `deleted_at TIMESTAMPTZ`.
        - Add `invitations` (`id UUID PRIMARY KEY DEFAULT uuidv7()` bridged to `inv_<hex32>`, including `email_delivery_status VARCHAR(32) NOT NULL DEFAULT 'pending'`), `tenant_secrets` (`id UUID PRIMARY KEY DEFAULT uuidv7()` bridged to `sec_<hex32>`), and `execution_assignments` (`id UUID PRIMARY KEY DEFAULT uuidv7()` bridged to `tsk_<hex32>`, including `batch_id UUID` bridged to optional `tsk_<hex32>` for cohort batch grouping and `email_delivery_status VARCHAR(32) NOT NULL DEFAULT 'pending'`) to the closed DDL table set in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, expand `CLOSED_POSTGRES_TABLES` in `ZORM004` inside `[MODIFY] @[scripts/audit_zero_orm_strictness.py]` from 12 to 15 tables (`"invitations"`, `"tenant_secrets"`, `"execution_assignments"`), and register their column names in `APPROVED_ADAPTER_RECORD_COLUMNS` (`ZORM006`).
        - In `PostgresUnitOfWork` (`[MODIFY] @[backend_v2/database/postgres/uow.py]`), enforce `RESET quorum.current_org;` inside the `finally` block prior to releasing the `asyncpg` connection back to `PostgresPoolManager`, enforce explicit parameterized `WHERE organization_id = $1` filtering on every tenant-scoped query in `PostgresEntityAdapter` (`[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]` and `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`), and extend `_InMemoryPostgresStore.seed_tables` and `InMemoryAsyncPgConnection` in `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py]` to emulate `"invitations"`, `"tenant_secrets"`, `"execution_assignments"`, `executemany` batch inserts, and `RESET quorum.current_org` for hermetic `PostgresEntityAdapter` unit tests.
    </action>
  </step>

  <test_contracts>
    <contract name="test_token_exchange_request_dto_mutual_exclusivity_positive" category="positive">
      <input>Valid `TokenExchangeRequestDTO` instantiated with `firebase_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"` and `target_user_id=None`</input>
      <expected>Model validates cleanly with `strict=True, extra="forbid", frozen=True`</expected>
    </contract>
    <contract name="test_token_exchange_request_dto_both_fields_supplied_negative" category="negative">
      <input>`TokenExchangeRequestDTO` instantiated with both `firebase_token` and `target_user_id` non-null</input>
      <expected>Raises `ValidationError` logging `ErrorCodes.VALIDATION_FAILED`</expected>
    </contract>
    <contract name="test_token_exchange_request_dto_neither_field_supplied_negative" category="negative">
      <input>`TokenExchangeRequestDTO` instantiated with both `firebase_token=None` and `target_user_id=None`</input>
      <expected>Raises `ValidationError` logging `ErrorCodes.VALIDATION_FAILED`</expected>
    </contract>
    <contract name="test_postgres_entity_adapter_iam_tables_roundtrip_positive" category="positive">
      <input>Valid `User`, `Organization`, `Invitation`, `TenantSecretDTO`, and `ExecutionAssignment` entities with `PrefixedUUID7` IDs</input>
      <expected>Persists and reconstitutes 1:1 via `PostgresEntityAdapter` and `InMemoryUnitOfWork` with `RESET quorum.current_org` executed on transaction exit</expected>
    </contract>
    <contract name="test_postgres_entity_adapter_invalid_prefix_uuid_negative" category="negative">
      <input>`User` or `Invitation` with non-UUIDv7 or un-prefixed primary key string</input>
      <expected>Raises `ValidationError` / `AppException` rejecting malformed `OPAQUE_STRIPE_ID_REGEX` identifier</expected>
    </contract>
    <contract name="test_invitation_and_assignment_batch_bounds_boundary" category="boundary">
      <input>`InvitationBatchCreateDTO` and `ExecutionAssignmentBatchCreateDTO` with `0`, `1`, `500`, and `501` recipients</input>
      <expected>`1` and `500` pass validation; `0` and `501` raise `ValidationError`</expected>
    </contract>
  </test_contracts>

  <validation_gate>
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/auth.py backend_v2/database/repositories/identity.py backend_v2/database/postgres/entity_adapter/ --test --ast-strict
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py
  </validation_gate>
</execution_protocol>
```

