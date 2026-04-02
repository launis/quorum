# REPOSITORY DIRECTORY & ARCHITECTURE REFERENCE (V2.5)

<catastrophic_system_bans>
    <rule_block id="dna_bypass">
        <banned_pattern>Modifying `db_v2.json` (Runtime DB) directly or writing silent fallback defaults into Python logic.</banned_pattern>
        <mandatory_pattern>Database structure modifications MUST exclusively target `backend_v2/seed/seed_data.json` globally. Fallbacks within domain operations are strictly illegal.</mandatory_pattern>
        <catastrophic_reason>Runtime structure bypassing collapses the mathematical fail-fast mappings built during system instantiation.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="anemic_routers_cognition_ban">
        <banned_pattern>Placing agent behavior, logic branches, or cognition directly inside FastAPI router endpoints.</banned_pattern>
        <mandatory_pattern>API Routers MUST remain purely anemic HTTP connector endpoints. Heavy cognition execution strictly resides in `services/` or `hooks/`.</mandatory_pattern>
    </rule_block>
    <rule_block id="flutter_pure_display">
        <banned_pattern>Managing complex LLM token logic, branching decisions, or generative pipeline state inside Dart functions.</banned_pattern>
        <mandatory_pattern>Flutter Studio strictly consumes pre-computed logical JSON trees via Riverpod BFF (Backend-For-Frontend) APIs. 0% AI cognition logic exists on the client interface.</mandatory_pattern>
    </rule_block>
    <rule_block id="mandatory_mcp_log_check">
        <banned_pattern>Guessing the cause of a reported system crash blindly or demanding the user to run print scripts natively.</banned_pattern>
        <mandatory_pattern>You MUST inherently search the active `backend_debug.log` and `client_debug.log` logs autonomously matching stack traces via `grep_search` or `view_file` BEFORE proposing bug solutions.</mandatory_pattern>
    </rule_block>
</architectural_invariants>

<system_map>
    <instruction>The internal workspace directory roles mapped explicitly for target prioritization:</instruction>
    
    <layer id="backend" path="backend_v2/">
        <description>The Core Engine (Python 3.14). Strict Pydantic V2 / FastAPI Async Monolith architecture maintaining Serverless execution.</description>
        <directory path="api/routers/">Segmented HTTP REST V2 endpoints separated by feature boundary (execution, iam, studio).</directory>
        <directory path="database/">The Unified Data Repository. Abstract Storage engines for local (TinyDB) and production (Firestore).</directory>
        <directory path="hooks/">Pure deterministic CPU-bound algorithmic logic files (Integrity, Reporting, Scoring filters, Security, Vertex Search).</directory>
        <directory path="llm/">
            <description>Standardized interface API proxies connecting internal systems to LLM SDKs (LiteLLM, GenAI).</description>
            <file_rules>
                <file path="client.py">CORE ENTRYPOINT. Contains `LLMClient.from_strategy()`. ALWAYS use this to invoke LLMs via `run_structured_task()` for strict JSON or `run_chat()` for text.</file>
                <file path="provider.py">LOW-LEVEL ABSTRACTION. Contains `LLMFactory`. Direct usage of this file to bypass `client.py` is BANNED.</file>
                <file path="mock.py">TESTING MOCK. Mandatory integration point for all Pytest unit tests hitting LLM interfaces, loading scenarios from `mock_data.py`.</file>
            </file_rules>
        </directory>
        <directory path="models/">The Absolute SSOT (Single Source of Truth) schema configurations. Pydantic V2 definitions bridging Network DTOs, State DAG nodes, and Auth rules.</directory>
        <directory path="seed/">Zero-Deploy initialization architecture. Contains `seed_data.json` providing global mathematical logic templates, and `run_seed.py` ensuring database integration parities.</directory>
        <directory path="services/">Complex business orchestration processing logic routines. E.g., The core Async DAG Executor orchestrator and the dynamic PDF Blueprint generator.</directory>
        <file path="main.py">FastAPI framework server execution point instantiating web boundaries.</file>
        <file path="worker.py">ARQ (Asynchronous Redis Queue) Worker loop driving automated DAG task resolutions concurrently.</file>
    </layer>

    <layer id="frontend" path="client_app_v2/">
        <description>The Cognitive Studio IDE (Flutter / Dart 3). Follows a standard Feature-First layout powered defensively by Riverpod 3 State Management.</description>
        <directory path="lib/core/">Foundational system layers including Global HTTP configurations, unified Error Boundaries natively trapping GUI failures, and application logs.</directory>
        <directory path="lib/features/">Application divided vertically via domain functionality. Implements dynamic BFF parsing building widgets straight from internal ViewModel structures natively.</directory>
        <directory path="lib/l10n/">Localization storage mechanisms natively enforcing the codebase strict No-String Rule (exclusively translating `app_en.arb`).</directory>
        <directory path="lib/router/">GoRouter navigational constraints resolving deep linking rules effectively against application authorization states.</directory>
        <file path="app.dart">Top-level Application Shell enforcing global UI Theme protocols seamlessly wrapping `AppErrorBoundary`.</file>
    </layer>

    <layer id="root_environment" path="/">
        <description>Primary development setup files natively guiding automated systems.</description>
        <directory path=".agents/rules/">Master Architectural Directives natively formatted via structural constraints guiding intelligent machine compilation behaviors (AI Only).</directory>
        <directory path=".agents/workflows/">Autonomous procedural orchestration playbooks ensuring code alterations properly resolve across specific isolated AI logic paths.</directory>
        <file path="AGENTS.md">The Core Root Agent Configuration file ensuring foundational Windows 11 context laws exist natively before anything else.</file>
        <file path="backend_debug.log">Crucial Server Runtime trace logs exposing hidden Python/FastAPI validation faults natively generated during asynchronous events.</file>
        <file path="client_debug.log">Crucial Client Runtime trace logs exposing frontend Freezed parsing failures, Dart mapping errors, and user HTTP interruptions.</file>
        <file path="run_all.py">PowerShell executable effectively integrating Docker and FastApi services instantly inside modern environments.</file>
    </layer>
</system_map>
