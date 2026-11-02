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

# Phase 5: B2B Invitation Flow, Time-Bound Execution Assignments (`ExecutionAssignment`), 4-Tier RBAC Matrix, Self-Service Profile & GDPR Soft-Delete Webhook

**Overview:** Create `EmailService` in `[NEW] @[backend_v2/services/auth/email_service.py]` and `ExecutionAssignmentService` in `[NEW] @[backend_v2/services/execution/assignment_service.py]`, implement cryptographic B2B invitations and cohort batch invitations (`OrganizationService.create_invitation`, `OrganizationService.create_invitation_batch`, and `OrganizationService.accept_invitation` with the 1:1 Flat Identity Collision Guard in `@[backend_v2/services/auth/organization_service.py#L41-L360]`), enforce the 4-Tier RBAC Governance Matrix (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`) across `UserService` (`@[backend_v2/services/auth/user_service.py#L45-L826]`), `OrganizationService` (`@[backend_v2/services/auth/organization_service.py#L320-L360]`), and `ExecutionLifecycleService` (`@[backend_v2/services/execution/lifecycle_service.py#L23-L248]`), implement GDPR Soft-Delete anonymization (`UserService.delete_user` in `@[backend_v2/services/auth/user_service.py#L310-L430]` and Firebase deletion webhook in `@[backend_v2/api/routers/iam/auth.py#L43-L104]`), and expose SafeLinks-immune Time-Bound Execution Assignment endpoints under `/api/v2/execution/executions/assignments` in `@[backend_v2/api/routers/execution/executions.py#L57-L89]`.
**Source:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]

**Target Files:**
- `[NEW] @[backend_v2/services/auth/email_service.py]`
- `[NEW] @[backend_v2/services/execution/assignment_service.py]`
- `[MODIFY] @[backend_v2/services/auth/organization_service.py#L41-L360]`
- `[MODIFY] @[backend_v2/services/auth/organization_service.py#L320-L360]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L45-L826]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L287-L297]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L310-L430]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L432-L562]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L564-L690]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L692-L707]`
- `[MODIFY] @[backend_v2/services/auth/user_service.py#L709-L751]`
- `[MODIFY] @[backend_v2/services/auth/__init__.py#L148-L152]`
- `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L23-L248]`
- `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L51-L94]`
- `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L96-L143]`
- `[MODIFY] @[backend_v2/services/execution/ingress_service.py#L306-L533]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`
- `[MODIFY] @[backend_v2/api/routers/iam/users.py#L92-L125]`
- `[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L69-L88]`
- `[MODIFY] @[backend_v2/api/routers/execution/executions.py#L57-L89]`
- `[NEW] @[backend_v2/tests/unit/services/auth/test_email_service.py]`
- `[NEW] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_user_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **5. B2B Invitations, Time-Bound Execution Assignments (`ExecutionAssignment`), Autonomous Email Dispatch (`EmailService`), 4-Tier RBAC Matrix & GDPR Soft-Delete**<br>`[NEW] @[backend_v2/services/auth/email_service.py]`<br>`[NEW] @[backend_v2/services/execution/assignment_service.py]`<br>`[MODIFY] @[backend_v2/services/auth/organization_service.py#L41-L360]`<br>`[MODIFY] @[backend_v2/services/auth/organization_service.py#L320-L360]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L45-L826]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L287-L297]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L310-L430]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L432-L562]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L564-L690]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L692-L707]`<br>`[MODIFY] @[backend_v2/services/auth/user_service.py#L709-L751]`<br>`[MODIFY] @[backend_v2/services/auth/__init__.py#L148-L152]`<br>`[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L23-L248]`<br>`[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L51-L94]`<br>`[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L96-L143]`<br>`[MODIFY] @[backend_v2/services/execution/ingress_service.py#L306-L533]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`<br>`[MODIFY] @[backend_v2/api/routers/iam/users.py#L92-L125]`<br>`[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L69-L88]`<br>`[MODIFY] @[backend_v2/api/routers/execution/executions.py#L57-L89]`<br>`[NEW] @[backend_v2/tests/unit/services/auth/test_email_service.py]`<br>`[NEW] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_user_service.py]` | Hard SQL `DELETE` breaking `executions` foreign keys; silent cross-org account merging; `MEMBER`/`VIEWER` listing all org users and all org executions; `OrganizationUpdateDTO \| OrganizationCreate` union coercion in `OrganizationService.update_organization`; starting task timers on `GET` / email open (broken by SafeLinks bots); allowing multi-submit quota drain from a single task link. | Create `EmailService` in `[NEW] @[backend_v2/services/auth/email_service.py]` and `ExecutionAssignmentService` in `[NEW] @[backend_v2/services/execution/assignment_service.py]`; SHA-256 hashed tokens, `batch_id` cohort grouping, and `email_delivery_status`; Two-Phase SafeLinks-Immune Task Activation (`GET .../preview` read-only, `POST .../activate` starts `activated_at`); Dual-Clock Expiration ($\min(\text{hard\_deadline\_at}, \text{activated\_at} + \text{relative\_duration\_seconds})$); Combined JIT User Onboarding + 2FA; Locked vs. Assignee Input Partitioning; `AssignmentResultVisibility` (`CONFIRMATION_ONLY` vs. `FULL_REPORT_ACCESS`); 4-Tier RBAC Matrix (`VIEWER`/`MEMBER` self-only users and executions, `MANAGER` org metadata & task assignments, `ADMIN` invitations/users/BYOK, `ROOT` FinOps limits); GDPR Soft-Delete anonymization (`deleted_at = NOW()`). | Pruned background cron polling daemons for expired task links (evaluated deterministically against server UTC clock on read/write), avoided SMTP port `25` relays blocked by GCP Cloud Run, and reused `ExecutionIngressService.start_execution` as the single execution pipeline. | Unit and ISTQB BVA tests in `[NEW] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`, `[NEW] @[backend_v2/tests/unit/services/auth/test_email_service.py]`, `@[backend_v2/tests/unit/test_organization_service.py]`, and `@[backend_v2/tests/unit/test_user_service.py]`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Read the `<required_context_rules>` block, `00-antigravity-core.md`, and `01-python-backend.md` before executing any changes.</action>
    <constraint>Enforce `single_router_ssot_mandate`, `in_place_upsert_standard_mandate`, `unbounded_io_timeout_mandate`, and `rfc7807_dual_reporting_mandate` across all invitation, task assignment, RBAC, and GDPR soft-delete flows.</constraint>
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
    <backend>[NEW] @[backend_v2/services/auth/email_service.py]</backend>
    <backend>[NEW] @[backend_v2/services/execution/assignment_service.py]</backend>
    <backend>@[backend_v2/services/auth/organization_service.py#L41-L360]</backend>
    <backend>@[backend_v2/services/auth/organization_service.py#L320-L360]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L45-L826]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L287-L297]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L310-L430]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L432-L562]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L564-L690]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L692-L707]</backend>
    <backend>@[backend_v2/services/auth/user_service.py#L709-L751]</backend>
    <backend>@[backend_v2/services/auth/__init__.py#L148-L152]</backend>
    <backend>@[backend_v2/services/execution/lifecycle_service.py#L23-L248]</backend>
    <backend>@[backend_v2/services/execution/lifecycle_service.py#L51-L94]</backend>
    <backend>@[backend_v2/services/execution/lifecycle_service.py#L96-L143]</backend>
    <backend>@[backend_v2/services/execution/ingress_service.py#L306-L533]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L43-L104]</backend>
    <backend>@[backend_v2/api/routers/iam/users.py#L92-L125]</backend>
    <backend>@[backend_v2/api/routers/iam/organizations.py#L69-L88]</backend>
    <backend>@[backend_v2/api/routers/execution/executions.py#L57-L89]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/services/auth/test_email_service.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_organization_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_user_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`EmailService` in `[NEW] @[backend_v2/services/auth/email_service.py]` and `OrganizationService` in `@[backend_v2/services/auth/organization_service.py#L41-L360]` implement single and batch invitations (`create_invitation`, `create_invitation_batch`, `accept_invitation`) enforcing `allowed_email_domains`, role hierarchy, and the **1:1 Flat Identity Collision Guard** (`ErrorCodes.USER_ALREADY_ASSIGNED`).</item>
    <item>The 4-Tier RBAC Governance Matrix is enforced across `UserService` (`@[backend_v2/services/auth/user_service.py#L45-L826]`), `OrganizationService.update_organization` (`@[backend_v2/services/auth/organization_service.py#L320-L360]` accepting exclusively `OrganizationUpdateDTO`), and `ExecutionLifecycleService` (`@[backend_v2/services/execution/lifecycle_service.py#L23-L248]`), with soft-delete aware `LAST_ADMIN_PROTECTION` and immediate `RevocationCache.revoke_user_sessions` triggers on privilege/status mutations.</item>
    <item>`UserService.delete_user` (`@[backend_v2/services/auth/user_service.py#L310-L430]`) and `POST /api/v2/iam/auth/webhooks/firebase-user-deleted` (`@[backend_v2/api/routers/iam/auth.py#L43-L104]`) execute in-place GDPR Soft-Delete anonymization preserving `executions` foreign keys.</item>
    <item>`ExecutionAssignmentService` in `[NEW] @[backend_v2/services/execution/assignment_service.py]` and endpoints in `@[backend_v2/api/routers/execution/executions.py#L57-L89]` implement single and batch task assignments, SafeLinks-immune `GET .../preview`, JIT user onboarding + 2FA, explicit `POST .../activate`, Dual-Clock expiration, draft checkpointing, single-shot atomic submission via `ExecutionIngressService.start_execution` (`@[backend_v2/services/execution/ingress_service.py#L306-L533]`), and `AssignmentResultVisibility`.</item>
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
    <file>@[backend_v2/services/orchestrator/dag_executor/__init__.py] (Do not mutate DAG Orchestrator core; delegate assignment execution strictly to `ExecutionIngressService.start_execution`)</file>
    <file>@[client_app_v2/lib/router/router.dart] (Do not modify Flutter client files in Phase 5; reserved for Phase 6)</file>
  </anti_targets>

  <step id="5.1" name="Cryptographic B2B Invitations &amp; 1:1 Flat Identity Collision Guard">
    <action>
      - **`[NEW] @[backend_v2/services/auth/email_service.py]`, `[MODIFY] @[backend_v2/services/auth/organization_service.py#L41-L360]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`, `[NEW] @[backend_v2/tests/unit/services/auth/test_email_service.py]`, & `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`**:
        - Create `EmailService` in `[NEW] @[backend_v2/services/auth/email_service.py]` (operating on `TransactionalEmailItemDTO`, `TransactionalEmailBatchResultDTO`, `InvitationCreateDTO`, `InvitationAcceptRequestDTO`, `InvitationResponseDTO`, `InvitationBatchCreateDTO`, and `InvitationBatchResponseDTO` defined in Phase 1; Note: demolished `LoginResponse` was removed in Phase 1) implementing `send_invitation_emails` and `send_assignment_emails` (`list[TransactionalEmailItemDTO]` -> `TransactionalEmailBatchResultDTO`): when `email_transport_mode` on `Settings` is `"console"` on `EmailTransportMode` (local development and unit tests), logs structured delivery metadata with masked tokens and returns `"sent"` on `EmailDeliveryStatus`; when `email_transport_mode` on `Settings` is `"http_api"` on `EmailTransportMode` (GCP Cloud Run `europe-north1` production where outbound SMTP port `25` is blocked), dispatches a single bounded `httpx.AsyncClient` (`async with asyncio.timeout(email_http_timeout_seconds)`) HTTPS `POST` batch request on port `443` to `email_api_endpoint` on `Settings` authenticated with `email_api_key` on `Settings` from sender `email_from_address` (`"no-reply@qrum.ai"`) for 1–500 recipients (while Firebase Auth natively handles password reset and email verification emails), and updates `email_delivery_status` (`"sent"` or `"failed"` on `EmailDeliveryStatus`). Implement `OrganizationService.create_invitation(self, initiator: TokenData, org_id: str, payload: InvitationCreateDTO) -> InvitationResponseDTO` and `OrganizationService.create_invitation_batch(self, initiator: TokenData, org_id: str, payload: InvitationBatchCreateDTO) -> InvitationBatchResponseDTO` (`POST /api/v2/iam/organizations/{org_id}/invitations/batch`), generating a unique 256-bit URL-safe token (`secrets.token_urlsafe(32)`) per recipient, storing only its SHA-256 digest (`hashlib.sha256(raw_token.encode("utf-8")).hexdigest()`) in `invitations` with a 7-day `expires_at`, executing an all-or-nothing pre-flight validation pass across all recipients (up to 500) followed by a single atomic `conn.executemany` batch insert inside `PostgresUnitOfWork`, and dispatching the invitation emails via `EmailService`:
          1. Enforce that ONLY `ADMIN` (for their own `initiator.organization_id == org_id`) and `ROOT` members of `UserRole` can create or revoke invitations; reject `MANAGER`, `MEMBER`, and `VIEWER` members of `UserRole` with `PermissionDeniedError` (`ErrorCodes.PERMISSION_DENIED`).
          2. **Invitation Role Hierarchy & Allowed Email Domain Guard**: Reject any attempt by a non-`ROOT` `ADMIN` to create an invitation assigning the `ROOT` member of `UserRole` (`PermissionDeniedError`, `ErrorCodes.PERMISSION_DENIED`), enforce the organization's `allowed_email_domains` allowlist when non-empty (verifying `payload.email.split("@")[-1].lower() in organization.allowed_email_domains`, raising `PermissionDeniedError` with `ErrorCodes.PERMISSION_DENIED` if outside the allowlist), and reject creating a duplicate `PENDING` invitation for the same `(org_id, payload.email)` with `ConflictError` (`ErrorCodes.CONFLICT_ERROR`).
          3. Record structured audit events (`INVITATION_CREATED` and `INVITATION_REVOKED`) via `self.audit_service.log_event`.
        - Implement `OrganizationService.accept_invitation(self, initiator: TokenData, payload: InvitationAcceptRequestDTO) -> User`:
          - Verify token digest, `PENDING` status on `InvitationStatus`, and `expires_at > datetime.now(timezone.utc)` (raising `AppException` with `ErrorCodes.INVITATION_EXPIRED` if expired).
          - Enforce the **1:1 Flat Identity Collision Guard**: if the accepting user (`initiator.id` or `email`) already belongs to a different non-null `organization_id` (`existing_user.organization_id is not None and existing_user.organization_id != invitation.organization_id`), log `ErrorCodes.USER_ALREADY_ASSIGNED` and raise `ConflictError` (`409 Conflict`) to prevent silent cross-tenant account hijacking.
          - Transition the invitation status to `ACCEPTED` on `InvitationStatus` and record `INVITATION_ACCEPTED` via `self.audit_service.log_event`.
    </action>
  </step>

  <step id="5.2" name="4-Tier RBAC Governance (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`) &amp; Self-Service Profile (`name`, `language`, `theme_mode`)">
    <action>
      - **`[MODIFY] @[backend_v2/services/auth/user_service.py#L45-L826]`, `[MODIFY] @[backend_v2/services/auth/user_service.py#L287-L297]`, `[MODIFY] @[backend_v2/services/auth/user_service.py#L432-L562]`, `[MODIFY] @[backend_v2/services/auth/user_service.py#L564-L690]`, `[MODIFY] @[backend_v2/services/auth/user_service.py#L692-L707]`, `[MODIFY] @[backend_v2/services/auth/user_service.py#L709-L751]`, `[MODIFY] @[backend_v2/services/auth/organization_service.py#L41-L360]`, `[MODIFY] @[backend_v2/services/auth/organization_service.py#L320-L360]`, `[MODIFY] @[backend_v2/services/auth/__init__.py#L148-L152]`, `[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L69-L88]`, `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L23-L248]`, `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L51-L94]`, `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L96-L143]`, & `[MODIFY] @[backend_v2/tests/unit/test_user_service.py]`**:
        - **Self-Service User Profile Guard, Role Hierarchy & `LAST_ADMIN_PROTECTION` Hardening (`UserService` in `@[backend_v2/services/auth/user_service.py#L45-L826]`)**:
          1. In `UserService.list_users(self, initiator: TokenData)` (`@[backend_v2/services/auth/user_service.py#L692-L707]`): when `initiator.role` is `MEMBER` or `VIEWER` on `UserRole`, return exclusively `[u for u in all_users if u.id == initiator.id]`. When `initiator.role` is `MANAGER` or `ADMIN` on `UserRole`, return users belonging to `initiator.organization_id`.
          2. In `UserService.get_user(self, initiator: TokenData, target_id: str)` (`@[backend_v2/services/auth/user_service.py#L709-L751]`): allow `initiator.id == target_id` for all roles, allow `MANAGER` and `ADMIN` on `UserRole` when `user.organization_id == initiator.organization_id`, and reject cross-user lookups by `MEMBER` or `VIEWER` with `PermissionDeniedError`.
          3. In `UserService.update_user(self, initiator_id: str, target_id: str, updates: UserUpdate)` (`@[backend_v2/services/auth/user_service.py#L432-L562]`): when `initiator_id == target_id` (self-update), permit updating `name` (display name), `language` (`SystemLocale`: `fi` or `en`), and `theme_mode` (`"system"`, `"light"`, `"dark"`), and reject any attempt by a non-`ROOT` user to self-mutate `role`, `organization_id`, `is_active`, or `password` with `PermissionDeniedError` (`ErrorCodes.PERMISSION_DENIED`). Ensure `MANAGER` cannot update any other user's record (`initiator_id != target_id` raises `PermissionDeniedError`).
          4. **Unified Role Hierarchy & Privilege Escalation Guard**: In `UserService.update_user` (`@[backend_v2/services/auth/user_service.py#L432-L562]`) and `UserService.update_user_role` (`@[backend_v2/services/auth/user_service.py#L564-L690]`), enforce numeric role hierarchy (`ROOT: 40 > ADMIN: 30 > MANAGER: 20 > MEMBER: 10 > VIEWER: 5`) whenever `updates.role` or `new_role` is specified so a non-`ROOT` `ADMIN` can never promote a user to `ROOT` or modify a user with higher privileges (`PermissionDeniedError`, `ErrorCodes.PERMISSION_DENIED`).
          5. **Soft-Delete Aware `LAST_ADMIN_PROTECTION` on Role Demotion & Account Deactivation**: Update `UserService._count_org_admins` (`@[backend_v2/services/auth/user_service.py#L287-L297]`) to count only active, non-deleted administrators (`u.organization_id == org_id` and `ADMIN` role on `UserRole` and `u.is_active and u.deleted_at is None`), and enforce `LAST_ADMIN_PROTECTION` (`ConflictError`, `ErrorCodes.CONFLICT_ERROR`) in `UserService.update_user` (`@[backend_v2/services/auth/user_service.py#L432-L562]`) both when demoting the last active `ADMIN` (`updates.role` is not `None` and not `ADMIN` on `UserRole`) and when deactivating the last active `ADMIN` (`updates.is_active is False`).
          6. **Immediate Redis Kill-Switch on Privilege Mutation**: Whenever `UserService.update_user` (`@[backend_v2/services/auth/user_service.py#L432-L562]`) or `UserService.update_user_role` (`@[backend_v2/services/auth/user_service.py#L564-L690]`) changes a user's `role`, `organization_id`, or deactivates the account (`is_active = False`), immediately invoke `await self.revocation_cache.revoke_user_sessions(target_id, ttl_seconds=900)` (via `RevocationCache` created in Phase 4) so any active 15-minute `Quorum Local JWT` carrying stale role claims is invalidated in `< 1 ms`.
        - **Organization Profile vs. Platform FinOps Split (`OrganizationService.get_organization`, `OrganizationService.update_organization` in `@[backend_v2/services/auth/organization_service.py#L41-L360]` and `@[backend_v2/services/auth/organization_service.py#L320-L360]`, `AuthService.update_organization` in `@[backend_v2/services/auth/__init__.py#L148-L152]`, & `PUT /api/v2/iam/organizations/{id}` in `@[backend_v2/api/routers/iam/organizations.py#L69-L88]`)**:
          1. Restrict `OrganizationService.get_organization` and `OrganizationService.list_organizations` to `MANAGER`, `ADMIN`, and `ROOT` members of `UserRole` (rejecting `MEMBER` and `VIEWER` with `PermissionDeniedError`).
          2. Eliminate the legacy `OrganizationUpdateDTO | OrganizationCreate` union and `isinstance(data, OrganizationUpdateDTO)` coercion branch in `OrganizationService.update_organization(self, initiator: TokenData, org_id: PrefixedUUID7, data: OrganizationUpdateDTO) -> Organization` (`@[backend_v2/services/auth/organization_service.py#L320-L360]`), `AuthService.update_organization` (`@[backend_v2/services/auth/__init__.py#L148-L152]`), and `PUT /api/v2/iam/organizations/{id}` (`@[backend_v2/api/routers/iam/organizations.py#L69-L88]`) so organization updates accept **exclusively `data: OrganizationUpdateDTO`** (`the_zero_compromise_pledge`), while `POST /api/v2/iam/organizations` handles `OrganizationCreate`. Allow `MANAGER` and `ADMIN` members of `UserRole` (when `initiator.organization_id == org_id`) to update organization profile fields (`name` and `contact_email`), while raising `PermissionDeniedError` (`ErrorCodes.PERMISSION_DENIED`) if a `MANAGER` or `ADMIN` payload includes non-null mutations to platform-governed fields (`quota_limit`, `tpm_limit`, `rpm_limit`, `tier`, `subscription_status`, `is_active`, `billing_id`), and record `ORGANIZATION_UPDATED` via `self.audit_service.log_event`.
        - **Peer Execution Isolation in `ExecutionLifecycleService` (`@[backend_v2/services/execution/lifecycle_service.py#L23-L248]`, `@[backend_v2/services/execution/lifecycle_service.py#L51-L94]`, & `@[backend_v2/services/execution/lifecycle_service.py#L96-L143]`)**:
          1. In `ExecutionLifecycleService.list_executions` (`@[backend_v2/services/execution/lifecycle_service.py#L51-L94]`) and `ExecutionLifecycleService.get_execution` (`@[backend_v2/services/execution/lifecycle_service.py#L96-L143]`): permit org-wide execution visibility (`e.organization_id == initiator.organization_id`) exclusively for `MANAGER` and `ADMIN` members of `UserRole` (and global visibility for `ROOT`). For `MEMBER` and `VIEWER` members of `UserRole`, restrict visibility strictly to executions they created (`e.created_by == initiator.id`), preventing task participants from seeing peer executions within the same organization.
    </action>
  </step>

  <step id="5.3" name="GDPR Soft-Delete Anonymization &amp; Firebase Deletion Webhook">
    <action>
      - **`[MODIFY] @[backend_v2/services/auth/user_service.py#L310-L430]`, `[MODIFY] @[backend_v2/api/routers/iam/users.py#L92-L125]`, & `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`**:
        - Refactor `UserService.delete_user` (`@[backend_v2/services/auth/user_service.py#L310-L430]`) and `@[backend_v2/api/routers/iam/users.py#L92-L125]` to execute in-place GDPR Soft-Delete anonymization:
          1. Trigger `await self.revocation_cache.revoke_user_sessions(target_id, ttl_seconds=900)` first so active JWTs are blocked in `< 1 ms`.
          2. Update the `User` record in-place via `.model_copy(update={"is_active": False, "deleted_at": datetime.now(timezone.utc), "email": f"deleted_{target_id}@anonymized.quorum.local", "name": "Anonymized User", "firebase_uid": None})` so foreign keys on `executions` and `report_artifacts` remain 100% intact.
        - Add `POST /api/v2/iam/auth/webhooks/firebase-user-deleted` in `@[backend_v2/api/routers/iam/auth.py#L43-L104]` validating the `X-Quorum-Webhook-Signature` HMAC header against `firebase_webhook_secret` in `Settings` and invoking `UserService.soft_delete_by_firebase_uid(firebase_uid)`.
    </action>
  </step>

  <step id="5.4" name="Time-Bound Execution Assignments (`ExecutionAssignmentService`), SafeLinks-Immune Activation &amp; Combined JIT User Onboarding">
    <action>
      - **`[NEW] @[backend_v2/services/execution/assignment_service.py]`, `[NEW] @[backend_v2/services/auth/email_service.py]`, `[MODIFY] @[backend_v2/services/execution/ingress_service.py#L306-L533]`, `[MODIFY] @[backend_v2/api/routers/execution/executions.py#L57-L89]`, & `[NEW] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`**:
        - Create `ExecutionAssignmentService` in `[NEW] @[backend_v2/services/execution/assignment_service.py]` (operating on `ExecutionAssignment`, `ExecutionAssignmentCreateDTO`, `ExecutionAssignmentRecipientDTO`, `ExecutionAssignmentBatchCreateDTO`, `ExecutionAssignmentBatchResponseDTO`, `ExecutionAssignmentPreviewDTO`, `ExecutionAssignmentOnboardingRequestDTO`, `ExecutionAssignmentDraftDTO`, `ExecutionAssignmentSubmitDTO`, `ExecutionAssignmentResponseDTO`, and `TokenExchangeResponseDTO` defined in Phase 1) and expose endpoints under `/api/v2/execution/executions/assignments` in `@[backend_v2/api/routers/execution/executions.py#L57-L89]` (`single_router_ssot_mandate`):
          1. **Create Single or Cohort Batch Task Assignments (`POST /api/v2/execution/executions/assignments` & `POST /api/v2/execution/executions/assignments/batch`)**:
             - Guarded by `require_role` (`ROOT`, `ADMIN`, and `MANAGER` members of `UserRole`).
             - Generates a 256-bit token (`secrets.token_urlsafe(32)`), persists only its SHA-256 digest (`token_hash`) in `execution_assignments` (`id: tsk_<hex32>`), and binds `organization_id`, `assigned_email`, `workflow_id`, `output_profile_id`, `target_locale`, `locked_inputs` (`WorkflowInputs` pre-filled by the sender), `assignee_input_keys` (`list[str]` required from the recipient), `result_visibility` (`AssignmentResultVisibility`), `hard_deadline_at` (`TIMESTAMPTZ`), and optional `relative_duration_seconds` (`int | None`).
             - Enforces Role Scope, Allowed Email Domain Lock, Atomic Batch Pre-Flight Validation & Autonomous Email Dispatch (`EmailService`): `MANAGER` can assign tasks with `invited_role` set to `"MEMBER"` on `UserRole` (never `ADMIN`, `MANAGER`, or `ROOT`), and when `organization.allowed_email_domains` is non-empty, both `create_assignment` and `create_assignment_batch(self, initiator: TokenData, payload: ExecutionAssignmentBatchCreateDTO) -> ExecutionAssignmentBatchResponseDTO` verify that every recipient email domain is in `organization.allowed_email_domains` (`PermissionDeniedError`, `ErrorCodes.PERMISSION_DENIED`) and passes the **1:1 Flat Identity Collision Guard** (`ErrorCodes.USER_ALREADY_ASSIGNED` if any recipient email belongs to a different organization) before persisting a single row; `create_assignment_batch` deduplicates recipient emails, assigns a shared cohort `batch_id = generate_uuid7_opaque_id(EntityPrefix.ASSIGNMENT)`, generates a distinct `ExecutionAssignment` (`tsk_<hex32>`) and unique 256-bit token (`secrets.token_urlsafe(32)` -> SHA-256 `token_hash`) per recipient so each participant has an isolated countdown (`activated_at`), isolated `draft_inputs`, and isolated single-shot submission (`execution_id`), persists all rows atomically via PostgreSQL 19 `conn.executemany` inside `PostgresUnitOfWork`, dispatches localized (`fi` / `en`) task emails containing `organization_name`, `workflow_name`, `hard_deadline_at`, `relative_duration_seconds`, and `f"{frontend_app_base_url}/task/{raw_token}"` (using `frontend_app_base_url` from `Settings`) via `EmailService` (plus `POST /api/v2/execution/executions/assignments/{assignment_id}/resend` rotating the 256-bit `token_hash` and re-sending the email via `EmailService`), and records `ASSIGNMENT_BATCH_CREATED` via `audit_service.log_event`.
          2. **SafeLinks-Immune Idempotent Preview (`GET /api/v2/execution/executions/assignments/preview?token=...`)**:
             - Performs a **100% side-effect-free read** by `token_hash` returning `ExecutionAssignmentPreviewDTO` (`assignment_id`, `organization_name`, `workflow_name`, `assigned_email`, `requires_account_creation: bool`, `status`, `hard_deadline_at`, `relative_duration_seconds`, `activated_at`, `remaining_seconds`, `server_now_utc`).
             - Never mutates `status` or sets `activated_at` on `GET`, neutralizing premature countdown triggers from corporate email security scanners (Microsoft Defender SafeLinks, Proofpoint, Mimecast) and email tracking pixel pre-fetchers.
          3. **Combined Just-In-Time (JIT) User Onboarding (`POST /api/v2/execution/executions/assignments/onboard`)**:
             - When `requires_account_creation` is `True` (no existing `User` matches `assigned_email`), accepts `ExecutionAssignmentOnboardingRequestDTO` (`token`, `name`, `language`, `firebase_token` with verified 2FA claim `firebase.sign_in_second_factor`), verifies the token digest and `hard_deadline_at > datetime.now(timezone.utc)`, enforces the 1:1 Identity Collision Guard (`ErrorCodes.USER_ALREADY_ASSIGNED`), provisions the new `User` (`usr_<hex32>`) in `assignment.organization_id` with `role` set to `"MEMBER"` on `UserRole`, binds `assigned_user_id = user.id`, and returns a signed 15-minute `Quorum Local JWT` (`TokenExchangeResponseDTO`).
          4. **Explicit Human Task Activation (`POST /api/v2/execution/executions/assignments/{assignment_id}/activate`)**:
             - Requires an authenticated session whose email matches `assignment.assigned_email` (if `initiator.email.lower() != assignment.assigned_email.lower()`, logs `ErrorCodes.IDENTITY_MISMATCH` and raises `PermissionDeniedError`).
             - Verifies `datetime.now(timezone.utc) <= assignment.hard_deadline_at` (else transitions to `EXPIRED` on `AssignmentStatus` and raises `AppException` with `ErrorCodes.ASSIGNMENT_EXPIRED`).
             - Atomically sets `status` to `ACTIVATED` on `AssignmentStatus` and `activated_at = datetime.now(timezone.utc)` (idempotent if already `ACTIVATED`), starting the relative countdown window.
          5. **Draft Checkpointing (`PUT /api/v2/execution/executions/assignments/{assignment_id}/draft`)**:
             - While `status` is `ACTIVATED` on `AssignmentStatus` and `datetime.now(timezone.utc) <= effective_expires_at`, persists `draft_inputs` in `execution_assignments` so browser refreshes or network drops never lose user work.
          6. **Single-Shot Atomic Submission & Execution Trigger (`POST /api/v2/execution/executions/assignments/{assignment_id}/submit`)**:
             - Computes server-authoritative deadline:
               $$\text{effective\_expires\_at} = \min(\text{hard\_deadline\_at}, \text{activated\_at} + \text{relative\_duration\_seconds})$$
               (when `relative_duration_seconds` is set, else `hard_deadline_at`), plus `assignment_submission_grace_seconds` from `Settings` for in-flight uploads.
             - If `datetime.now(timezone.utc) > effective_expires_at + grace`, logs `ErrorCodes.ASSIGNMENT_EXPIRED` and raises `AppException`.
             - If `assignment.status` is `SUBMITTED` on `AssignmentStatus` or `assignment.execution_id is not None`, logs `ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED` and raises `ConflictError` (`409 Conflict`), preventing multi-submit FinOps quota drain.
             - Merges `assignment.locked_inputs` (authoritative sender inputs that cannot be overridden by the recipient) with the recipient's `assignee_inputs`, invokes `ExecutionIngressService.start_execution` (`@[backend_v2/services/execution/ingress_service.py#L306-L533]`), atomically updates `status` to `SUBMITTED` on `AssignmentStatus`, `submitted_at = datetime.now(timezone.utc)`, and `execution_id = record.id`, and records `ASSIGNMENT_SUBMITTED` via `audit_service.log_event`.
             - Enforces `AssignmentResultVisibility`: when `assignment.result_visibility` is `CONFIRMATION_ONLY` on `AssignmentResultVisibility`, `ExecutionLifecycleService.get_execution` and report endpoints return only submission confirmation metadata to the `MEMBER` assignee while exposing full forensic SDUI/PDF reports to `MANAGER`, `ADMIN`, and `ROOT`.
    </action>
  </step>

  <test_contracts>
    <contract name="test_assignment_preview_safelinks_idempotent_positive" category="positive">
      <input>Repeated `GET /api/v2/execution/executions/assignments/preview?token=...` requests simulating email scanner prefetch</input>
      <expected>Returns `ExecutionAssignmentPreviewDTO` with `status="pending"` and `activated_at=None` without starting countdown</expected>
    </contract>
    <contract name="test_assignment_activate_identity_mismatch_negative" category="negative">
      <input>`POST .../activate` called by an authenticated user whose email does not match `assignment.assigned_email`</input>
      <expected>Logs `ErrorCodes.IDENTITY_MISMATCH.name` and raises `PermissionDeniedError` (`403 Forbidden`)</expected>
    </contract>
    <contract name="test_assignment_submit_dual_clock_expiration_bva_boundary" category="boundary">
      <input>Submissions at `effective_expires_at - 1s`, `effective_expires_at`, `effective_expires_at + grace`, and `effective_expires_at + grace + 1s`</input>
      <expected>First three succeed; `effective_expires_at + grace + 1s` logs `ErrorCodes.ASSIGNMENT_EXPIRED.name` and raises `AppException`</expected>
    </contract>
    <contract name="test_assignment_submit_replay_already_submitted_negative" category="negative">
      <input>Second `POST .../submit` call on an assignment already in `SUBMITTED` status</input>
      <expected>Logs `ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED.name` and raises `ConflictError` (`409 Conflict`)</expected>
    </contract>
    <contract name="test_rbac_four_tier_matrix_boundaries_boundary" category="boundary">
      <input>`VIEWER`/`MEMBER`, `MANAGER`, `ADMIN`, and `ROOT` calling `list_users`, `update_user`, `update_organization`, `create_invitation`, and `list_executions`</input>
      <expected>`VIEWER`/`MEMBER` access only self profile and self executions (`e.created_by == initiator.id`); `MANAGER` updates org `name`/`contact_email` and creates assignments but receives `403` on general invitations, user role edits, and FinOps limits; `ADMIN` manages org users/invitations/BYOK but receives `403` on `ROOT` escalation or FinOps limits</expected>
    </contract>
    <contract name="test_gdpr_soft_delete_preserves_executions_positive" category="positive">
      <input>`UserService.delete_user` or Firebase deletion webhook invoked for a user with existing `ExecutionRecord` rows</input>
      <expected>Revokes Redis sessions (`revoked:usr:{id}`), anonymizes `email`/`name`, sets `deleted_at`, and leaves `executions` foreign keys intact</expected>
    </contract>
  </test_contracts>

  <validation_gate>
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/ backend_v2/services/execution/ backend_v2/api/routers/iam/ backend_v2/api/routers/execution/executions.py --test --ast-strict
  </validation_gate>
</execution_protocol>
```

