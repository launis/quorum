# REPOSITORY DIRECTORY LAWS & ROUTING (V3.0)

<domain_boundary>
    <role>ARCHITECTURAL ROUTING & DIRECTORY LAWS</role>
    <instruction>These rules govern WHERE code is allowed to be written. You must use these routing laws to find the correct folders for business logic, UI components, and API endpoints.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="backend_router_vs_service_separation">
        <banned_pattern>Writing core business logic, Pydantic data transformations, database querying, or LLM orchestration directly inside `api/routers/` endpoints.</banned_pattern>
        <mandatory_pattern>FastAPI `api/routers/` MUST ONLY contain HTTP protocol parsing, payload validation mapping, and immediate delegation to a service class. All heavy logic MUST be routed to `services/` (e.g. `studio.py`, `execution.py`).</mandatory_pattern>
        <catastrophic_reason>Mixing HTTP logic with Business Logic destroys testability, violates the Single Responsibility Principle, and makes the API impossible to refactor.</catastrophic_reason>
    </rule_block>

    <rule_block id="strict_model_location">
        <banned_pattern>Defining Pydantic classes or local Enums organically inside service files or routers, or dumping new models into the monolithic `v2_core.py`.</banned_pattern>
        <mandatory_pattern>ALL Single Source of Truth (SSOT) data structures, requests, and domain models MUST be placed inside `backend_v2/models/` using strict Interface Segregation. You MUST separate pure SSOT database shapes into `domain/`, API payloads into `dtos/`, and static LLM instructions into `prompts/`. No models can live outside this boundary.</mandatory_pattern>
        <catastrophic_reason>Scattered models cause circular import crashes. Dumping API requests and SSOT domains into the same "God File" (like `v2_core.py`) destroys boundary isolation and causes router-to-service import deadlocks.</catastrophic_reason>
    </rule_block>

    <rule_block id="frontend_feature_isolation">
        <banned_pattern>Mixing specific UI feature code (e.g. Studio Canvas) or feature-specific SDUI Freezed models into `lib/core/` or `lib/shared/` folders, or cross-importing deep between different features.</banned_pattern>
        <mandatory_pattern>Flutter code MUST strictly adhere to Feature-First isolation in `client_app_v2/lib/features/` (e.g., `execution/models/` and `execution/providers/`). Shared abstract logic belongs in `core/` or `shared/`. Legacy monolithic proxy models are strictly banned; all models must be decoupled Freezed classes to enable strict UI decoupling and Riverpod O(1) lookups.</mandatory_pattern>
        <catastrophic_reason>Cross-feature spaghetti imports break the Riverpod reactive dependency tree and cause massive compilation bottlenecks. Monolithic models prevent strict UI decoupling and O(1) state resolution.</catastrophic_reason>
    </rule_block>

    <rule_block id="ephemeral_storage_mandate">
        <banned_pattern>Creating ad-hoc testing scripts, JSON data dumps, or Python debug runners randomly in the root folder, source folders, or a local `./scratch` folder.</banned_pattern>
        <mandatory_pattern>All AI-generated temporary sandbox files, debugging scripts, and scratchpads MUST be written exclusively to the IDE's conversation artifact directory: `<appDataDir>\brain\<conversation-id>\scratch\`.</mandatory_pattern>
        <catastrophic_reason>Dumping scratch files across the workspace pollutes the Git repository, confuses human developers, and breaks automated quality gate scanning.</catastrophic_reason>
    </rule_block>

    <rule_block id="test_directory_isolation">
        <banned_pattern>Placing test files alongside production code (e.g., `services/test_auth.py`).</banned_pattern>
        <mandatory_pattern>Test files MUST strictly mirror the production directory structure but reside in their respective isolated test roots:
        - Python Backend: `backend_v2/tests/...`
        - Flutter Frontend: `client_app_v2/test/...`
        </mandatory_pattern>
        <catastrophic_reason>Mixing test files with production code creates bloat, triggers false-positives in security scanners, and risks deploying mock data logic into production environments.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<master_system_index>
    <instruction>The High-Level Abstraction Map. Do not expect every file to be listed here. Use this to orient your search and navigation.</instruction>

    <module path="backend_v2/api/routers/">
        <responsibility>HTTP REST ENDPOINTS ONLY</responsibility>
        <key_domains>execution/, iam/ (Auth Orphan), studio/, system/, output_profiles.py</key_domains>
    </module>
    
    <module path="backend_v2/services/">
        <responsibility>DECOUPLED PILLAR CAPABILITIES</responsibility>
        <key_domains>
          - Pillar 2 (Ontology): studio/, translation_service.py
          - Pillar 3 (Orchestration): execution.py, web_fetcher.py, mcp/, orchestrator/ (engines/, strategies/, DAG logic)
          - Pillar 4 (SDUI): blueprint.py, sdui_mapper_service.py, pdf_generator.py
          - Pillar 5 (Resilience): pii_analyzer.py, usage_service.py, progress.py
          - Pillar 6 (Atom Graph): document_extraction.py, chat_parser.py, source_verification_service.py
          - Orphan (Missing Capability): auth.py
        </key_domains>
    </module>
    
    <module path="backend_v2/worker.py">
        <responsibility>BACKGROUND EXECUTION (PILLAR 3)</responsibility>
        <key_domains>Celery async task processing and DAG initiation</key_domains>
    </module>
    
    <module path="backend_v2/models/">
        <responsibility>SSOT PYDANTIC SCHEMAS, DTOS & PROMPT ASSETS</responsibility>
        <key_domains>domain/ (SSOT DB shapes), dtos/ (API boundaries), view/ (SDUI Polymorphic Blocks), prompts/ (LLM templates), v2_core.py, state.py, enums.py</key_domains>
    </module>

    <module path="backend_v2/core/">
        <responsibility>CORE ARCHITECTURE & REGISTRIES</responsibility>
        <key_domains>registry.py (SSOT for TaskRegistry and SchemaBuilderRegistry), template_processor.py</key_domains>
    </module>
    
    <module path="backend_v2/database/">
        <responsibility>DATA PERSISTENCE & REPOSITORIES (PILLAR 2)</responsibility>
        <key_domains>interfaces.py, wrapper.py, repositories/</key_domains>
    </module>
    
    <module path="backend_v2/seed/">
        <responsibility>ZERO-DEPLOY STATIC DATA VAULT</responsibility>
        <key_domains>seed_data.json, run_seed.py, wipe_user_data.py</key_domains>
    </module>

    <module path="backend_v2/hooks/">
        <responsibility>DETERMINISTIC & HYBRID LLM MODIFIERS (PILLAR 1)</responsibility>
        <key_domains>interaction_hook.py</key_domains>
    </module>

    <module path="backend_v2/llm/">
        <responsibility>FOUNDATIONAL MODEL ORCHESTRATION & ADAPTERS</responsibility>
        <key_domains>adapters/, mock.py, provider.py</key_domains>
    </module>

    <module path="backend_v2/utils/">
        <responsibility>MATHEMATICAL ENGINES & SYSTEM INVARIANTS (PILLAR 1)</responsibility>
        <key_domains>alias_engine.py, math_utils.py, scoring/</key_domains>
    </module>

    <module path="client_app_v2/lib/features/">
        <responsibility>RIVERPOD SDUI VERTICAL FEATURES (O(1) STATE PROVIDERS)</responsibility>
        <key_domains>studio/ (Pillar 2), execution/ (Pillar 4 SDUI Dashboards & DTOs), auth/ (Orphan)</key_domains>
    </module>

    <module path="client_app_v2/lib/core/">
        <responsibility>FLUTTER FOUNDATION & GLOBAL BOUNDARIES</responsibility>
        <key_domains>error/app_error_boundary.dart, models/enums.dart, network/</key_domains>
    </module>
    
    <module path="client_app_v2/lib/shared/">
        <responsibility>SHARED UI WIDGETS & CROSS-DOMAIN MODELS</responsibility>
        <key_domains>widgets/ (e.g. i18n_text_field.dart), models/ (e.g. i18n_text.dart, sdui_block_dto.dart)</key_domains>
    </module>
    
    <module path="client_app_v2/lib/l10n/">
        <responsibility>STRICT INTERNATIONALIZATION STRINGS</responsibility>
        <key_domains>app_en.arb, app_fi.arb</key_domains>
    </module>

    <module path="docs/architecture/">
        <responsibility>CONSOLIDATED ARCHITECTURE MANIFESTOS</responsibility>
        <key_domains>00_README_META_ARCHITECTURE.md (Meta-Governance), 6 Capability-Driven Pillar documents (System Context, Ontology, Orchestration, SDUI, Resilience, Enriched Atom Graph Engine).</key_domains>
    </module>
    
    <module path=".agents/rules/">
        <responsibility>GLOBAL IDE RULES & ARCHITECTURAL INVARIANTS</responsibility>
        <key_domains>00-antigravity-core.md, language-specific constraints, directory reference.</key_domains>
    </module>

    <module path=".agents/workflows/">
        <responsibility>AGENTIC EXECUTION PLAYBOOKS & QUARANTINE PROTOCOLS</responsibility>
        <key_domains>Tier 0 (Planning) to Tier 8 (Auditing) slash commands and Hybrid XML Sandwich schemas.</key_domains>
    </module>

    <module path="scratch/">
        <responsibility>SANDBOX FOR AI EXPERIMENTS & DEBUGGING</responsibility>
        <key_domains>Disposable test scripts, JSON dumps, log extraction.</key_domains>
    </module>
</master_system_index>
