# Tracker: Wikipedia MCP Integration & Dynamic Tool Capability Protocol Standardization
@[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md] @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md]`
  - [x] Step 1.1: Add ToolCapability to enums.py and BaseSearchTool to tools.py
  - [x] Step 1.2: Update Flutter AllowedMcpTool for Full-Duplex Serialization Parity
  - [x] Step 1.3: Refactor TavilyTool input validation to use StandardSearchInputDTO
  - [x] Step 1.4: Upgrade DummyTestTool in test_dispatcher.py
  - [x] Step 1.5: Verify Phase 1 Cleanups Quality Gate
  - [x] Step 2.1: Implement Capability Indexing in ToolDispatcher
  - [x] Step 2.2: Refactor mcp_tool_loop.py to use resolve_primary_search_tool
  - [x] Step 2.3: Add Wikipedia settings to settings.py and test overrides
  - [x] Step 2.4: Unit tests for domain tools, dispatcher, and settings
  - [x] Step 3.1: Create Wikipedia Domain Models
  - [x] Step 3.2: Implement Wikipedia Client
  - [x] Step 3.3: Create unit tests for Wikipedia Client
  - [x] Step 4.1: Implement WikipediaSearchTool and WikipediaReadTool
  - [x] Step 4.2: Register Wikipedia Tools in ToolDispatcher
  - [x] Step 4.3: Create unit tests for Wikipedia Tools
  - [x] Step 4.4: Update MCP tool loop unit tests
  - [ ] Step 5.1: Add capability field to AllowedMCPTool
  - [ ] Step 5.2: Backup and mutate master seed_data.json
  - [ ] Step 5.3: Pre-flight in-memory validation gate
  - [ ] Step 5.4: Execute seed data injection and database transfer
  - [ ] Step 5.5: Post-seeding database persistence roundtrip verification
  - [ ] Step 6.1: Execute Targeted Unit and Integration Tests
  - [ ] Step 6.2: Execute Flutter Domain Parity Verification
  - [ ] Step 7.1: Run Backend Global Quality Gate
  - [ ] Step 8.1: Create and Synchronize Knowledge Items
  - [ ] Step 8.2: Synchronize Directory Reference
  - [ ] Step 8.3: Execute Tier 7 Architectural Documentation Workflow

- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md] @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend `.py` files:
  - [ ] @[backend_v2/models/domain/system_config.py]
  - [ ] @[backend_v2/models/domain/tools.py]
  - [ ] @[backend_v2/models/domain/wikipedia.py] [NEW]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/services/mcp/dispatcher.py]
  - [ ] @[backend_v2/services/mcp/mcp_tool_loop.py]
  - [ ] @[backend_v2/services/mcp/tools/tavily.py]
  - [ ] @[backend_v2/services/mcp/tools/wikipedia.py] [NEW]
  - [ ] @[backend_v2/services/mcp/wikipedia_client.py] [NEW]
  - [ ] @[backend_v2/settings.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter `.dart` files:
  - [ ] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md] @[ki_mcp_tool_protocol.md] @[ki_prompt_generation_architecture.md] @[ki_zero_permissive_typing.md] @[ki_god_code_prevention.md] @[ki_opentelemetry_logfire_observability.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_mcp_tool_protocol.md]`: Document `ToolCapability(StrEnum)` (defined in plan), `BaseTool.capability`, `BaseSearchTool`, `StandardSearchInputDTO` (defined in plan), `ToolDispatcher` capability indexing, fail-fast 404/500 invariants, and the Cloud-Agnostic Secret Management & Credential Ingress Protocol.
     - `@[ki_prompt_generation_architecture.md]`: Detail multi-tool OpenAI schema declarations and capability injection into LLM prompts.
     - `@[ki_zero_permissive_typing.md]`: Document strict DTO contracts (`StandardSearchInputDTO` and `WikipediaReadInputDTO` defined in plan) and elimination of untyped `**kwargs` in search tool execution.
     - `@[ki_god_code_prevention.md]`: Document decoupling of tool implementations into standalone classes under `backend_v2/services/mcp/tools/` and capability-driven dispatching.
     - `@[ki_opentelemetry_logfire_observability.md]`: Document `MCPAuditTrace` OpenTelemetry spans (`mcp.tool_call`).
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register newly created modules: `backend_v2/models/domain/wikipedia.py`, `backend_v2/services/mcp/wikipedia_client.py`, `backend_v2/services/mcp/tools/wikipedia.py`, and test suites.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing newly established invariants in present tense without historical language or plan IDs:
       - `@[docs/architecture/03_cognitive_orchestration_engine.md]`: Document Dynamic Capability-Driven MCP Dispatcher (ToolCapability SEARCH), primary search tool resolution, and multi-tool orchestration.
       - `@[docs/architecture/02_data_seeding_and_ontology.md]`: Document `mcp_gateways` ontology with `capability` attributes on `AllowedMCPTool` and `AllowedMcpTool`.
       - `@[docs/architecture/00_README_META_ARCHITECTURE.md]`: Document native Wikipedia MCP tool integration.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md] @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

---

## Instructions for the Execution Agent

1. **Strict Quality Gate Verification**:
   - For backend changes, execute `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` after completing every cohesive step.
   - For Flutter model changes, execute `uv run python scripts/flutter_audit_loop.py <target_path> --build`.
   - Never skip quality gates.

2. **Atomic Commits Mandate**:
   - Instruct the user to perform an atomic `git commit` with English messages after every passed quality gate.
   - Use strict Conventional Commits syntax (`feat(mcp): ...`, `refactor(mcp): ...`, `test(mcp): ...`).

3. **Workspace Relative References**:
   - Use exclusively `@-references` (`@[backend_v2/...]`). Never use hardcoded absolute filesystem paths.

4. **Continuous Execution Protocol**:
   - When invoked via `/tier2-execute --full-auto`, proceed autonomously through the plan steps as long as quality gates pass 100%.
   - Halt immediately upon any quality gate failure or when triggering context budget limits (>8 turns, 3 commits, >5 files) to output `/tier5-session-handover`.

---

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-CAP-001** | Define `ToolCapability(StrEnum)` and `BaseSearchTool` contract with `StandardSearchInputDTO` | Step 1.1 | [ ] Pending |
| **REQ-CAP-002** | Update Flutter `AllowedMcpTool` with `capability` field to guarantee Full-Duplex Serialization Parity | Step 1.2 | [ ] Pending |
| **REQ-CAP-003** | Refactor `TavilyTool.execute` to validate inputs strictly via `StandardSearchInputDTO` | Step 1.3 | [ ] Pending |
| **REQ-CAP-004** | Upgrade `DummyTestTool` with `capability` property to satisfy `BaseTool` abstract interface | Step 1.4 | [ ] Pending |
| **REQ-CAP-005** | Verify Phase 1 foundational leaf contracts compile and pass backend audit loop | Step 1.5 | [ ] Pending |
| **REQ-DISP-001** | Implement eager capability indexing and `resolve_primary_search_tool` in `ToolDispatcher` | Step 2.1 | [ ] Pending |
| **REQ-DISP-002** | Refactor `mcp_tool_loop.py` to route search dynamically via `resolve_primary_search_tool` | Step 2.2 | [ ] Pending |
| **REQ-CFG-001** | Centralize `mcp_wikipedia_*` settings on `Settings` model with binary dev clamping and test overrides | Step 2.3 | [ ] Pending |
| **REQ-TEST-001** | Implement unit tests for domain tools, capability dispatcher, and settings invariants | Step 2.4 | [ ] Pending |
| **REQ-DTO-001** | Create Wikipedia Pydantic V2 DTO hierarchy with `ConfigDict(strict=True, extra="forbid", frozen=True)` | Step 3.1 | [ ] Pending |
| **REQ-CLI-001** | Implement asynchronous `WikipediaClient` with redirect following, title encoding, and fail-fast 404/500 | Step 3.2 | [ ] Pending |
| **REQ-TEST-002** | Implement ISTQB unit tests for `WikipediaClient` covering positive, negative, and timeout paths | Step 3.3 | [ ] Pending |
| **REQ-TOOL-001** | Implement `WikipediaSearchTool` and `WikipediaReadTool` conforming to `BaseSearchTool` and `BaseTool` | Step 4.1 | [ ] Pending |
| **REQ-TOOL-002** | Register `WikipediaSearchTool` and `WikipediaReadTool` in global `DISPATCHER` in `mcp_tool_loop.py` | Step 4.2 | [ ] Pending |
| **REQ-TEST-003** | Implement unit tests for Wikipedia tools validating schema declarations and audit traces | Step 4.3 | [ ] Pending |
| **REQ-TEST-004** | Update MCP tool loop unit tests to verify dynamic capability-based multi-tool execution | Step 4.4 | [ ] Pending |
| **REQ-SEED-001** | Add `capability: ToolCapability` field to `AllowedMCPTool` domain model | Step 5.1 | [ ] Pending |
| **REQ-SEED-002** | Backup and surgically append Wikipedia tools with capabilities to `sys_8172bda70c8641c5` in `seed_data.json` | Step 5.2 | [ ] Pending |
| **REQ-SEED-003** | Run pre-flight in-memory validation via `run_seed.py local --dry-run` and atom integrity audit | Step 5.3 | [ ] Pending |
| **REQ-SEED-004** | Execute seed data injection into `data/db_v2.json` with automatic backup and parity check | Step 5.4 | [ ] Pending |
| **REQ-SEED-005** | Verify physical database persistence roundtrip by deserializing injected record from TinyDB | Step 5.5 | [ ] Pending |
| **REQ-AUD-001** | Execute targeted unit and integration tests across backend MCP subsystem | Step 6.1 | [ ] Pending |
| **REQ-AUD-002** | Execute Flutter domain parity and gateway tests verifying strict capability parsing | Step 6.2 | [ ] Pending |
| **REQ-AUD-003** | Execute global backend audit loop gate across entire `backend_v2` test suite | Step 7.1 | [ ] Pending |
| **REQ-DOC-001** | Create `ki_mcp_tool_protocol.md` and synchronize existing architectural Knowledge Items | Step 8.1 | [ ] Pending |
| **REQ-DOC-002** | Register all newly created domain models, clients, tools, and test suites in `04_directory_reference.md` | Step 8.2 | [ ] Pending |
| **REQ-DOC-003** | Execute fully parameterized `/tier7-describe-architecture` updating architecture pillars | Step 8.3 | [ ] Pending |

---

# Session Handover Context

## Achieved
- Formulated and verified standalone implementation plan `docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md` through Tier 0 System 2 Research, Red-Team Falsification, and Five-Axis Deconstruction.
- Generated durable double-entry bookkeeping tracker `docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md` with 1:1 step tracking (27 steps), post-implementation hardening checklists (10 backend `.py` production targets, 1 frontend `.dart` production target), and complete Requirements Traceability Matrix.

## Learned
- Dynamic capability abstraction (ToolCapability SEARCH) completely eliminates provider branching (`TAVILY_TOOL_ID`) in `mcp_tool_loop.py`, enabling zero-touch addition of arbitrary future search engines.
- Adding `capability` to backend `AllowedMCPTool` requires synchronous updating of Flutter Freezed `AllowedMcpTool` with `@Default('search') String capability` to prevent `CheckedFromJsonException` crashes during studio gateway fetching (`disallowUnrecognizedKeys: true`).
- External Wikimedia response envelopes contain evolving metadata keys (`continue`, `batchcomplete`, `searchinfo`), requiring an Ingress Sanitization Gate in `WikipediaClient` before strict Pydantic `model_validate` (`extra="forbid"`).

## Remaining
- Execute Phase 1: Pre-Implementation Cleanups & Foundational Contracts (Steps 1.1 to 1.5).
- Execute Phase 2: Tool Dispatcher Capability Indexing, Conductor Loop & Settings SSOT (Steps 2.1 to 2.4).
- Execute Phase 3: Domain Models & Asynchronous Wikipedia Client (Steps 3.1 to 3.3).
- Execute Phase 4: Wikipedia MCP Tools & Dispatcher Registration (Steps 4.1 to 4.4).
- Execute Phase 5: Seed Data Mutation, Ingress Injection & Database Transfer Program (Steps 5.1 to 5.5).
- Execute Phase 6: Automated Testing Strategy (ISTQB & Parity Gates) (Steps 6.1 to 6.2).
- Execute Phase 7: Global Audit & Quality Gates (Step 7.1).
- Execute Phase 8: Knowledge Item Synchronization & Architectural Documentation (Steps 8.1 to 8.3).

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md] @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md]
```
