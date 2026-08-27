# REPOSITORY DIRECTORY LAWS & ROUTING (V3.0)

<domain_boundary>
    <role>ARCHITECTURAL ROUTING & DIRECTORY LAWS</role>
    <instruction>These rules govern WHERE code is allowed to be written. You must use these routing laws to find the correct folders for business logic, UI components, and API endpoints.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="backend_router_vs_service_separation">
        <mandate>NEVER write business logic, Pydantic data transformations, database querying, or LLM orchestration directly inside `api/routers/`. FastAPI routers MUST ONLY contain HTTP parsing, payload validation mapping, and immediate delegation to `services/` (e.g. `studio.py`, `execution.py`).</mandate>
    </rule_block>

    <rule_block id="strict_model_location">
        <mandate>NEVER define Pydantic classes or local Enums organically inside service files/routers, or dump new models into monolithic `v2_core.py`. ALL SSOT data structures MUST be placed in `backend_v2/models/`: pure business models in `domain/` (raw dicts from DB hydrated in Service layer, NO ORM shapes), API payloads in `dtos/`, and static LLM instructions in `prompts/`.</mandate>
    </rule_block>

    <rule_block id="frontend_feature_isolation">
        <mandate>NEVER mix feature UI code (e.g. Studio Canvas) or feature-specific SDUI Freezed models into `lib/core/` or `lib/shared/`, or cross-import deep between features. Flutter code MUST adhere to Feature-First isolation in `client_app_v2/lib/features/` (e.g., `execution/models/`, `execution/providers/`). Shared abstract logic belongs in `core/` or `shared/`.</mandate>
    </rule_block>

    <rule_block id="ephemeral_storage_mandate">
        <mandate>NEVER create ad-hoc testing scripts, JSON data dumps, or Python debug runners in root, source folders, or legacy `tmp\`. ALL AI temporary files, debug scripts, and scratchpads MUST be written exclusively to `<appDataDir>\brain\<conversation-id>\scratch\`. Epics and Implementation Plans MUST NOT list scratch files in Target boundaries.</mandate>
    </rule_block>

    <rule_block id="test_directory_isolation">
        <mandate>NEVER place test files alongside production code or directly into `tests/` root without test pyramid categorization. Test files MUST strictly mirror production structure categorized into test pyramid roots:
        - Python Backend: `backend_v2/tests/unit/...`, `backend_v2/tests/integration/...`, `backend_v2/tests/e2e/...`
        - Flutter Frontend: `client_app_v2/test/unit/...`, `client_app_v2/test/integration/...`, `client_app_v2/test/e2e/...`</mandate>
    </rule_block>
</catastrophic_system_bans>

<master_system_index>
    <instruction>High-Level Abstraction Map for search and navigation.</instruction>

    <module path="backend_v2/api/routers/">
        <responsibility>HTTP REST ENDPOINTS ONLY</responsibility>
        <key_domains>execution/, iam/, studio/, system/, output_profiles.py</key_domains>
    </module>
    
    <module path="backend_v2/services/">
        <responsibility>DECOUPLED PILLAR CAPABILITIES</responsibility>
        <key_domains>
          - Pillar 2 (Ontology): studio/, translation_service.py
          - Pillar 3 (Orchestration): execution.py, web_fetcher.py, llm_task_executor.py, mcp/, drivers/, file_driver.py, flattener.py, storage.py, orchestrator/ (engines/, strategies/, prompt_compiler.py, prompt_compiler_adapter.py, rag_preflight_service.py, chunking_service.py, dag_compiler.py, dag_executor.py, synthesis_distiller.py, synthesis_payload_compressor.py, matrix_explanation_service.py)
          - Pillar 4 (SDUI): blueprint.py, sdui_mapper_service.py, pdf_generator.py, localization.py, sdui/adapters/ (authenticity_adapter.py, executive_summary_adapter.py, global_score_adapter.py, matrix_graphs_adapter.py, matrix_summary_table_adapter.py, mcp_audit_adapter.py, metadata_adapter.py, penalties_adapter.py, printable_sources_adapter.py, synthesis_text_adapter.py, variance_adapter.py, warning_card_adapter.py, xai_highlights_adapter.py)
          - Pillar 5 (Resilience): pii_analyzer.py, usage_service.py, progress.py
          - Pillar 6 (Atom Graph): document_extraction.py, chat_parser.py, source_verification_service.py, matrix_domain_parser.py, orchestrator/ (anchor_validation_service.py, two_pass_atomizer.py, topological_evaluator.py, sliding_window_linker.py, extractive_sensor_service.py, enriched_dag_executor.py, result_projector.py)
          - Orphan: auth.py
        </key_domains>
    </module>
    
    <module path="backend_v2/worker.py">
        <responsibility>BACKGROUND EXECUTION (PILLAR 3)</responsibility>
        <key_domains>Arq 2026 async task processing and DAG initiation (isolated worker files)</key_domains>
    </module>
    
    <module path="backend_v2/models/">
        <responsibility>SSOT PYDANTIC SCHEMAS, DTOS & PROMPT ASSETS</responsibility>
        <key_domains>core_base.py (I18nText SSOT), domain/ (Pure Business Models, NO ORM shapes), dtos/ (API boundaries), view/ (SDUI Blocks), prompts/ (LLM directives SSOT), v2_core.py, state.py, enums.py</key_domains>
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
        <responsibility>DETERMINISTIC & HYBRID LLM MODIFIERS (PILLAR 1/3)</responsibility>
        <key_domains>scoring.py, interaction_hook.py, validation.py, pre/post processing hooks</key_domains>
    </module>

    <module path="backend_v2/llm/">
        <responsibility>FOUNDATIONAL MODEL ORCHESTRATION & ADAPTERS</responsibility>
        <key_domains>adapters/, mock.py, provider.py</key_domains>
    </module>

    <module path="backend_v2/utils/">
        <responsibility>MATHEMATICAL ENGINES & SYSTEM INVARIANTS (PILLAR 1)</responsibility>
        <key_domains>alias_engine.py, math_utils.py, ranked_round_robin.py, scoring/</key_domains>
    </module>

    <module path="client_app_v2/lib/features/">
        <responsibility>RIVERPOD SDUI VERTICAL FEATURES (O(1) STATE PROVIDERS)</responsibility>
        <key_domains>studio/ (Pillar 2/4 Workflow & Profile Editors), execution/ (Pillar 4 SDUI Dashboards & DTOs), shell/ (Pillar 4 Presentation), auth/, settings/</key_domains>
    </module>

    <module path="client_app_v2/lib/core/">
        <responsibility>FLUTTER FOUNDATION & GLOBAL BOUNDARIES</responsibility>
        <key_domains>error/app_error_boundary.dart, models/enums.dart, network/</key_domains>
    </module>
    
    <module path="client_app_v2/lib/shared/">
        <responsibility>SHARED UI WIDGETS & CROSS-DOMAIN MODELS</responsibility>
        <key_domains>widgets/ (i18n_text_field.dart), models/ (i18n_text.dart, sdui_block_dto.dart)</key_domains>
    </module>
    
    <module path="client_app_v2/lib/l10n/">
        <responsibility>STRICT INTERNATIONALIZATION STRINGS</responsibility>
        <key_domains>app_en.arb, app_fi.arb</key_domains>
    </module>

    <module path="docs/architecture/">
        <responsibility>CONSOLIDATED ARCHITECTURE MANIFESTOS</responsibility>
        <key_domains>00_README_META_ARCHITECTURE.md, 6 Capability-Driven Pillar documents</key_domains>
    </module>
    
    <module path=".agents/rules/">
        <responsibility>GLOBAL IDE RULES & ARCHITECTURAL INVARIANTS</responsibility>
        <key_domains>00-antigravity-core.md, language constraints, directory reference</key_domains>
    </module>

    <module path=".agents/workflows/">
        <responsibility>AGENTIC EXECUTION PLAYBOOKS & QUARANTINE PROTOCOLS</responsibility>
        <key_domains>Tier 0 (Planning) to Tier 8 (Auditing) slash commands</key_domains>
    </module>

    <module path="<appDataDir>\knowledge\">
        <responsibility>AI AGENT KNOWLEDGE BASE & LONG-TERM MEMORY</responsibility>
        <key_domains>Knowledge Items (KIs), architectural snapshots, and patterns</key_domains>
    </module>

    <module path="scratch/">
        <responsibility>SANDBOX FOR AI EXPERIMENTS & DEBUGGING</responsibility>
        <key_domains>Disposable test scripts, JSON dumps, log extraction</key_domains>
    </module>
</master_system_index>
