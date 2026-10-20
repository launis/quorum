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

# Task Tracker: Wikipedia MCP Integration & Dynamic Tool Capability Protocol Standardization

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md]  
**Tracker:** @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md]

## Session Handover Context
- **Achieved**: Formulated, researched, and validated the standalone implementation plan `docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md`. Generated and verified the durable double-entry bookkeeping tracker `docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md` passing 100% of structural audits (`scripts/audit_tracker_output.py`), markdown boundary audits (`scripts/audit_markdown_boundaries.py`), and neuro-symbolic parity checks (`scripts/audit_plan_tracker_parity.py`).
- **Learned**: Dynamic capability abstraction (`ToolCapability.SEARCH`) completely eliminates provider branching (`TAVILY_TOOL_ID`) in `mcp_tool_loop.py`. Flutter Freezed `AllowedMcpTool` must be updated with `@Default('search') String capability` to prevent deserialization failure when fetching studio gateways. External Wikimedia responses require ingress sanitization before Pydantic validation.
- **Remaining**: Execute Phase 1 through Phase 8 under continuous full-auto mode.
- **Resume Command**: `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Wikipedia_MCP_Integration.md] @[docs/implementationplans/TRACKER_Wikipedia_MCP_Integration.md]`

## Execution Steps
### Phase 1: Pre-Implementation Cleanups & 1-Hop Caller Conformance
- [ ] Step 1.1: Add ToolCapability to enums.py and BaseSearchTool to tools.py
- [ ] Step 1.2: Update Flutter AllowedMcpTool for Full-Duplex Serialization Parity
- [ ] Step 1.3: Refactor TavilyTool input validation to use StandardSearchInputDTO
- [ ] Step 1.4: Upgrade DummyTestTool in test_dispatcher.py
- [ ] Step 1.5: Verify Phase 1 Cleanups Quality Gate

### Phase 2: Tool Dispatcher Indexing, Conductor Loop & Settings SSOT
- [ ] Step 2.1: Implement Capability Indexing in ToolDispatcher
- [ ] Step 2.2: Refactor mcp_tool_loop.py to use resolve_primary_search_tool
- [ ] Step 2.3: Add Wikipedia settings to settings.py and test overrides
- [ ] Step 2.4: Unit tests for domain tools, dispatcher, and settings

### Phase 3: Domain Models & Asynchronous Wikipedia Client
- [ ] Step 3.1: Create Wikipedia Domain Models
- [ ] Step 3.2: Implement Wikipedia Client
- [ ] Step 3.3: Create unit tests for Wikipedia Client

### Phase 4: Wikipedia MCP Tools & Dispatcher Registration
- [ ] Step 4.1: Implement WikipediaSearchTool and WikipediaReadTool
- [ ] Step 4.2: Register Wikipedia Tools in ToolDispatcher
- [ ] Step 4.3: Create unit tests for Wikipedia Tools
- [ ] Step 4.4: Update MCP tool loop unit tests

### Phase 5: Seed Data Mutation, Ingress Injection & Database Transfer Program
- [ ] Step 5.1: Add capability field to AllowedMCPTool
- [ ] Step 5.2: Backup and mutate master seed_data.json
- [ ] Step 5.3: Pre-flight in-memory validation gate
- [ ] Step 5.4: Execute seed data injection and database transfer
- [ ] Step 5.5: Post-seeding database persistence roundtrip verification

### Phase 6: Automated Testing Strategy (ISTQB & Parity Gates)
- [ ] Step 6.1: Execute Targeted Unit and Integration Tests
- [ ] Step 6.2: Execute Flutter Domain Parity Verification

### Phase 7: Global Audit & Quality Gates
- [ ] Step 7.1: Run Backend Global Quality Gate

### Phase 8: As-Built Architectural Documentation & Knowledge Item Synchronization
- [ ] Step 8.1: Create and Synchronize Knowledge Items
- [ ] Step 8.2: Synchronize Directory Reference
- [ ] Step 8.3: Execute Tier 7 Architectural Documentation Workflow
