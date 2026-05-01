# REPOSITORY DIRECTORY REFERENCE (V2.6)

<system_map>
    <instruction>The internal workspace directory roles mapped explicitly for target prioritization based on live directory scans:</instruction>
    
    <layer id="backend" path="backend_v2/">
        <description>The Core Engine (Python 3.14). Strict Pydantic V2 / FastAPI Async Monolith architecture maintaining Serverless execution.</description>
        <directory path="api/routers/">
            <description>Segmented HTTP REST V2 endpoints separated by feature boundary (execution, iam, studio, system).</description>
            <file_rules>
                <file path="execution/">Ajonhallinta ja historian haku (executions.py, workflows.py, scorecard.py).</file>
                <file path="iam/">Identiteetti- ja tenant-hallinta (auth.py, organizations.py, users.py).</file>
                <file path="studio/">Blueprint CRUD ja konfiguraatiot (prompt_blocks.py, steps.py, model_registry.py, mcp_gateways.py, system_configs.py, workflows.py).</file>
                <file path="system/">Järjestelmän terveys ja telemetria (health.py, telemetry.py).</file>
                <file path="output_profiles.py">Tulostusprofiilien ja näkymien (SDUI) reititys.</file>
            </file_rules>
        </directory>
        <directory path="core/">
            <description>Core configuration, lifecycle settings, and system-level setup.</description>
            <file_rules>
                <file path="hook_registry.py">Suorituksenaikaiset välityspalvelut (hooks) kognition muunteluun.</file>
                <file path="registry.py">Kriittinen V2 Adapteri agenttien ja Pydantic-tehtävien välillä.</file>
            </file_rules>
        </directory>
        <directory path="database/">
            <description>The Unified Data Repository. Abstract Storage engines for local (TinyDB) and production (Firestore).</description>
            <file_rules>
                <file path="repositories/">Decoupled interfaces enforcing the Interface Segregation Principle (ISP) (e.g., audit.py, execution.py).</file>
            </file_rules>
        </directory>
        <directory path="hooks/">Pure deterministic CPU-bound algorithmic logic files (Integrity, Reporting, Scoring filters, Security, Vertex Search).</directory>
        <directory path="llm/">
            <description>Standardized interface API proxies connecting internal systems to LLM SDKs (LiteLLM, GenAI).</description>
            <file_rules>
                <file path="client.py">CORE ENTRYPOINT. Contains `LLMClient.from_strategy()`. ALWAYS use this to invoke LLMs via `run_structured_task()` or `run_chat()`.</file>
                <file path="provider.py">LOW-LEVEL ABSTRACTION. Direct usage of this file to bypass `client.py` is BANNED.</file>
                <file path="mock.py">Mandatory mock framework for LLM unit testing.</file>
                <file path="mock_data.py">Mandatory JSON mock fixtures for deterministic Pytest runs.</file>
            </file_rules>
        </directory>
        <directory path="models/">
            <description>The Absolute SSOT (Single Source of Truth) schema configurations. Subdivided into domain, dtos, and view.</description>
            <file_rules>
                <file path="enums.py">CENTRAL ENUM DEFINITIONS. The absolute source for system-wide constants and types enforcing the No-String Mandate.</file>
            </file_rules>
        </directory>
        <directory path="seed/">
            <description>Zero-Deploy initialization architecture (The Seed Vault). Features `backups` and `scripts`.</description>
            <file_rules>
                <file path="seed_data.json">Global mathematical logic templates and base definitions.</file>
                <file path="run_seed.py">Ensures database integration parities and bootstrap (Hard Reset).</file>
                <file path="wipe_user_data.py">The 'Soft Reset' mechanism clearing dynamic executions and workflows while preserving seeded configs.</file>
                <file path="harvest_output_profile.py">Surgical Extraction / Inverse Merge script to safely pull UI-created output profiles back into seed_data.json.</file>
            </file_rules>
        </directory>
        <directory path="services/">
            <description>Complex business orchestration processing logic routines. Subdivided into drivers, mcp, and orchestrator.</description>
            <file_rules>
                <file path="llm_task_executor.py">Central orchestration point enforcing Fail-Fast structured execution for cognitive workflows.</file>
                <file path="mcp/">Model Context Protocol loop execution directory for tool-based LLM routing.</file>
            </file_rules>
        </directory>
        <directory path="scripts/">Backendin sisäiset aputyökalut, kuten OpenAPI-skeemojen automaattinen generointi.</directory>
        <directory path="templates/">Jinja2/HTML pohjat dynaamiselle PDF- ja tulostusraporttigeneroinnille (PDF Service).</directory>
        <directory path="tests/">Automaattisen laatuportin (Pytest) yksikkö- ja integraatiotestit.</directory>
        <directory path="utils/">Uudelleenkäytettävät apufunktiot, graafiset piirtotyökalut (kuten rader/scatter_chart) ja muut apuohjelmat.</directory>
        <file path="main.py">FastAPI framework server execution point instantiating web boundaries and hook registries.</file>
        <file path="worker.py">ARQ Worker loop driving automated DAG task resolutions concurrently.</file>
    </layer>

    <layer id="frontend" path="client_app_v2/">
        <description>The Cognitive Studio IDE (Flutter / Dart 3). Follows a standard Feature-First layout powered defensively by Riverpod 3 State Management.</description>
        <directory path="lib/core/">
            <description>Foundational system layers (api, environment, error, logging, models, network, state, ui).</description>
            <file_rules>
                <file path="error/app_error_boundary.dart">Global UI Error Boundary. Gracefully traps CheckedFromJsonExceptions without crashing the app.</file>
                <file path="models/enums.dart">CENTRAL FRONTEND ENUMS. Ensures 1-to-1 architectural parity with the backend's strict enum definitions.</file>
            </file_rules>
        </directory>
        <directory path="lib/features/">
            <description>Features divided vertically: auth, execution, settings, shell, studio. Implements dynamic BFF parsing.</description>
            <file_rules>
                <file path="execution/views/">SDUI Execution and reporting views (dashboard_view.dart, execution_report_view.dart).</file>
                <file path="studio/views/">Admin Studio workflows, SystemInspector infinite canvas, and PromptBlock editors.</file>
                <file path="studio/views/widgets/xai/">SDUI komponentit XAI-matriisien rakenteelliseen esittämiseen ilman lokaalia matematiikkaa.</file>
            </file_rules>
        </directory>
        <directory path="lib/l10n/">Localization storage mechanisms natively enforcing the codebase strict No-String Rule (.arb files).</directory>
        <directory path="lib/router/">GoRouter navigational constraints utilizing Stripe-type Opaque IDs without heavy Extra object payloads.</directory>
        <directory path="lib/shared/">Shared models and widgets reusable across features.</directory>
        <directory path="lib/theme/">Globaalit tyylimäärittelyt (Colors, Typography) Desktop-First UI:ta varten.</directory>
        <directory path="lib/utils/">Yhteiset dart-apufunktiot ja rakenteet.</directory>
        <file path="lib/app.dart">Top-level Application Shell enforcing global UI Theme protocols seamlessly wrapping `AppErrorBoundary`.</file>
        <file path="pubspec.yaml">Dart dependencies and asset declarations.</file>
    </layer>

    <layer id="ephemeral_storage" path="scratch/">
        <description>The AI Workspace Sandbox. A designated scratch directory for temporary execution, one-off automated refactoring tools, and Quality Gate verification scripts.</description>
        <instruction>All Antigravity-generated temporary scripts, debugging logs, and testing programs MUST be siloed here to protect the core architectural boundaries.</instruction>
    </layer>

    <layer id="root_environment" path="/">
        <description>Primary development setup files natively guiding automated systems.</description>
        <directory path=".agents/rules/">Ainoa paikka virallisille arkkitehtuurin säännöille ja AI-agenttien rajoitteille.</directory>
        <directory path=".agents/workflows/">Autonomous procedural orchestration playbooks ensuring code alterations properly resolve across specific isolated AI logic paths.</directory>
        <directory path="data/">Paikallinen konfiguraatiodata, workflows -prototyyppimäärittelyt JSON-muodossa ja lokaali TinyDB tietokanta.</directory>
        <directory path="docs/architecture/">
            <description>Puhtaasti arkkitehtuurin kuvaus- ja dokumentaatiokansio.</description>
            <file_rules>
                <file path="01_backend_api_and_core.md">API-kerros ja Asynkroninen tapahtumahallinta (Arq).</file>
                <file path="02_domain_models.md">Pydantic Domain-mallit ja Opaque ID säännöt.</file>
                <file path="03_business_services_and_dag.md">Liiketoimintalogiikka ja DAG-orkestraattori.</file>
                <file path="04_hooks_and_llm.md">Dynaamiset kognition muuttajat (Hooks) ja LLM-infrastruktuuri.</file>
                <file path="05_data_persistence_and_seeding.md">Tietokanta, Repositoriot ja Nollakonfiguraatio-seedaus.</file>
                <file path="06_desktop_first_flutter_client.md">Flutter Client V2 (Desktop-First, SDUI, Riverpod).</file>
                <file path="07_infrastructure_and_observability.md">Infrastruktuuri, Docker, ja Observabiliteetti (Logfire).</file>
                <file path="08_dynamic_rendering_engine.md">Raportoinnin Renderöintimoottori (Jinja2, WeasyPrint).</file>
                <file path="09_evaluation_and_scoring.md">Kognitiivinen Arviointi, BARS ja Pisteidenlaskenta.</file>
            </file_rules>
        </directory>
        <directory path="docs/epic/">"Tehtävälista / Backlog". Täällä on puhtaasti toimintaohjeita siitä, mitä asioita pitää koodissa korjata tai rakentaa seuraavaksi. Kun Epic on koodattu, se on ikään kuin "tehty".</directory>
        <directory path="scripts/">Cross-functional development utilities. Features `flutter_audit_loop.py` and `backend_audit_loop.py` which unifies CD routines.</directory>
        <file path="AGENTS.md">The Core Root Agent Configuration file ensuring foundational Windows 11 context laws exist natively before anything else.</file>
        <file path="backend_debug.log">Crucial Server Runtime trace logs exposing hidden Python/FastAPI validation faults natively generated during asynchronous events.</file>
        <file path="client_debug.log">Crucial Client Runtime trace logs exposing frontend Freezed parsing failures, Dart mapping errors, and user HTTP interruptions.</file>
    </layer>
</system_map>
