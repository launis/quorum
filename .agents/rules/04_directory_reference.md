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
        <banned_pattern>Defining Pydantic classes or local Enums organically inside service files or routers.</banned_pattern>
        <mandatory_pattern>ALL Single Source of Truth (SSOT) data structures, requests, and domain models MUST be placed inside `backend_v2/models/` (e.g. `v2_core.py`, `enums.py`). No models can live outside this boundary.</mandatory_pattern>
        <catastrophic_reason>Scattered models cause circular import crashes and duplicate Pydantic definitions across different micro-services.</catastrophic_reason>
    </rule_block>

    <rule_block id="frontend_feature_isolation">
        <banned_pattern>Mixing specific UI feature code (e.g. Studio Canvas) into `lib/core/` or `lib/shared/` folders, or cross-importing deep between different features.</banned_pattern>
        <mandatory_pattern>Flutter code MUST strictly adhere to Feature-First isolation in `client_app_v2/lib/features/`. Shared abstract logic belongs in `core/` or `shared/`.</mandatory_pattern>
        <catastrophic_reason>Cross-feature spaghetti imports break the Riverpod reactive dependency tree and cause massive compilation bottlenecks.</catastrophic_reason>
    </rule_block>

    <rule_block id="ephemeral_storage_mandate">
        <banned_pattern>Creating ad-hoc testing scripts, JSON data dumps, or Python debug runners randomly in the root folder or source folders.</banned_pattern>
        <mandatory_pattern>All AI-generated temporary sandbox files, debugging scripts, and scratchpads MUST be written exclusively to the `scratch/` directory.</mandatory_pattern>
        <catastrophic_reason>Dumping scratch files across the workspace pollutes the Git repository, confuses human developers, and breaks automated quality gate scanning.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<master_system_index>
    <instruction>The High-Level Abstraction Map. Do not expect every file to be listed here. Use this to orient your search and navigation.</instruction>

    <module path="backend_v2/api/routers/">
        <responsibility>HTTP REST ENDPOINTS ONLY</responsibility>
        <key_domains>execution/, iam/, studio/, system/, output_profiles.py</key_domains>
    </module>
    
    <module path="backend_v2/services/">
        <responsibility>CORE BUSINESS LOGIC & ORCHESTRATION</responsibility>
        <key_domains>blueprint.py, studio.py, execution.py, auth.py, llm_task_executor.py, orchestrator/</key_domains>
    </module>
    
    <module path="backend_v2/models/">
        <responsibility>SSOT PYDANTIC SCHEMAS & ENUMS</responsibility>
        <key_domains>v2_core.py, enums.py</key_domains>
    </module>
    
    <module path="backend_v2/seed/">
        <responsibility>ZERO-DEPLOY STATIC DATA VAULT</responsibility>
        <key_domains>seed_data.json, run_seed.py, wipe_user_data.py</key_domains>
    </module>

    <module path="backend_v2/hooks/">
        <responsibility>DETERMINISTIC & HYBRID LLM MODIFIERS</responsibility>
        <key_domains>interaction_hook.py</key_domains>
    </module>

    <module path="backend_v2/utils/">
        <responsibility>MATHEMATICAL ENGINES & UTILITIES</responsibility>
        <key_domains>math_utils.py, scoring/ (BARS, Dampening, Sigmoid)</key_domains>
    </module>

    <module path="client_app_v2/lib/features/">
        <responsibility>RIVERPOD SDUI VERTICAL FEATURES</responsibility>
        <key_domains>studio/ (Admin Canvas), execution/ (Dashboards), auth/</key_domains>
    </module>

    <module path="client_app_v2/lib/core/">
        <responsibility>FLUTTER FOUNDATION & GLOBAL BOUNDARIES</responsibility>
        <key_domains>error/app_error_boundary.dart, models/enums.dart, network/</key_domains>
    </module>
    
    <module path="client_app_v2/lib/l10n/">
        <responsibility>STRICT INTERNATIONALIZATION STRINGS</responsibility>
        <key_domains>app_en.arb, app_fi.arb</key_domains>
    </module>

    <module path="docs/architecture/">
        <responsibility>CONSOLIDATED ARCHITECTURE MANIFESTOS</responsibility>
        <key_domains>10 markdown files covering System 1 vs 2, Evaluation, and Desktop-First patterns.</key_domains>
    </module>
    
    <module path="scratch/">
        <responsibility>SANDBOX FOR AI EXPERIMENTS & DEBUGGING</responsibility>
        <key_domains>Disposable test scripts, JSON dumps, log extraction.</key_domains>
    </module>
</master_system_index>
