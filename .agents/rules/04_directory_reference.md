# REPOSITORY DIRECTORY REFERENCE (V2.6)

<system_map>
    <instruction>The internal workspace directory roles mapped explicitly for target prioritization based on live directory scans:</instruction>
    
    <layer id="backend" path="backend_v2/">
        <description>The Core Engine (Python 3.14). Strict Pydantic V2 / FastAPI Async Monolith architecture maintaining Serverless execution.</description>
        <directory path="api/routers/">Segmented HTTP REST V2 endpoints separated by feature boundary (execution, iam, studio, system).</directory>
        <directory path="core/">Core configuration, lifecycle settings, and system-level setup.</directory>
        <directory path="database/">The Unified Data Repository. Abstract Storage engines for local (TinyDB) and production (Firestore).</directory>
        <directory path="hooks/">Pure deterministic CPU-bound algorithmic logic files (Integrity, Reporting, Scoring filters, Security, Vertex Search).</directory>
        <directory path="llm/">
            <description>Standardized interface API proxies connecting internal systems to LLM SDKs (LiteLLM, GenAI).</description>
            <file_rules>
                <file path="client.py">CORE ENTRYPOINT. Contains `LLMClient.from_strategy()`. ALWAYS use this to invoke LLMs via `run_structured_task()` or `run_chat()`.</file>
                <file path="provider.py">LOW-LEVEL ABSTRACTION. Direct usage of this file to bypass `client.py` is BANNED.</file>
            </file_rules>
        </directory>
        <directory path="models/">
            <description>The Absolute SSOT (Single Source of Truth) schema configurations. Subdivided into domain, dtos, and view.</description>
            <file_rules>
                <file path="enums.py">CENTRAL ENUM DEFINITIONS. The absolute source for system-wide constants and types enforcing the No-String Mandate.</file>
            </file_rules>
        </directory>
        <directory path="seed/">
            <description>Zero-Deploy initialization architecture. Features `backups` and `scripts`.</description>
            <file_rules>
                <file path="seed_data.json">Global mathematical logic templates and base definitions.</file>
                <file path="run_seed.py">Ensures database integration parities and bootstrap.</file>
            </file_rules>
        </directory>
        <directory path="services/">
            <description>Complex business orchestration processing logic routines. Subdivided into drivers, mcp, orchestrator (with strategies).</description>
        </directory>
        <file path="main.py">FastAPI framework server execution point instantiating web boundaries.</file>
        <file path="worker.py">ARQ Worker loop driving automated DAG task resolutions concurrently.</file>
    </layer>

    <layer id="frontend" path="client_app_v2/">
        <description>The Cognitive Studio IDE (Flutter / Dart 3). Follows a standard Feature-First layout powered defensively by Riverpod 3 State Management.</description>
        <directory path="lib/core/">
            <description>Foundational system layers (api, environment, error, logging, models, network, state, ui).</description>
            <file_rules>
                <file path="models/enums.dart">CENTRAL FRONTEND ENUMS. Ensures 1-to-1 architectural parity with the backend's strict enum definitions.</file>
            </file_rules>
        </directory>
        <directory path="lib/features/">Features divided vertically: auth, execution, settings, shell, studio. Implements dynamic BFF parsing.</directory>
        <directory path="lib/l10n/">Localization storage mechanisms natively enforcing the codebase strict No-String Rule.</directory>
        <directory path="lib/router/">GoRouter navigational constraints resolving deep linking rules effectively against application authorization states.</directory>
        <directory path="lib/shared/">Shared models and widgets reusable across features.</directory>
        <file path="lib/app.dart">Top-level Application Shell enforcing global UI Theme protocols seamlessly wrapping `AppErrorBoundary`.</file>
        <file path="pubspec.yaml">Dart dependencies and asset declarations.</file>
    </layer>

    <layer id="ephemeral_storage" path="tmp/">
        <description>The AI Workspace Sandbox. A designated scratch directory for temporary execution and artifacts.</description>
        <instruction>All Antigravity-generated temporary scripts, debugging logs, and testing programs MUST be siloed here to protect the core architectural boundaries.</instruction>
    </layer>

    <layer id="root_environment" path="/">
        <description>Primary development setup files natively guiding automated systems.</description>
        <directory path=".agents/rules/">Master Architectural Directives natively formatted via structural constraints guiding intelligent machine compilation behaviors (AI Only).</directory>
        <directory path=".agents/workflows/">Autonomous procedural orchestration playbooks ensuring code alterations properly resolve across specific isolated AI logic paths.</directory>
        <directory path="scripts/">Cross-functional development utilities. Features `flutter_audit_loop.py` which unifies CD routines.</directory>
        <file path="AGENTS.md">The Core Root Agent Configuration file ensuring foundational Windows 11 context laws exist natively before anything else.</file>
        <file path="backend_debug.log">Crucial Server Runtime trace logs exposing hidden Python/FastAPI validation faults natively generated during asynchronous events.</file>
        <file path="client_debug.log">Crucial Client Runtime trace logs exposing frontend Freezed parsing failures, Dart mapping errors, and user HTTP interruptions.</file>
    </layer>
</system_map>
