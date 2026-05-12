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
        <directory path="hooks/">
            <description>Pure deterministic CPU-bound algorithmic logic files (Integrity, Reporting, Scoring filters, Security, Vertex Search) and Hybrid LLM hooks.</description>
            <file_rules>
                <file path="interaction_hook.py">Hybrid Truth -arkkitehtuurin mukainen rooliluokittelu (Passenger -> Architect). Yhdistää deterministisen control_ratio-laskennan ja `execute_structured_task()` LLM-kutsut fail-fast Pydantic -validoinnilla.</file>
            </file_rules>
        </directory>
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
                <file path="v2_core.py">Zero-Defaults AtomResponse ja DTO-skeemojen (Strictness Level) aukoton lähde. Määrittää tekoälyn "Alphabetical Keys" -säännöt.</file>
            </file_rules>
        </directory>
        <directory path="seed/">
            <description>Zero-Deploy initialization architecture (The Seed Vault). Features `backups` and `scripts`.</description>
            <file_rules>
                <file path="seed_data.json">The absolute SSOT for System Configs, PromptBlocks, and deterministic TDAAssertions. Ei sisällä enää LLM-atomisaatiota tai legacy-rakenteita (micro_atoms).</file>
                <file path="run_seed.py">Ensures database integration parities and bootstrap (Hard Reset).</file>
                <file path="wipe_user_data.py">The 'Soft Reset' mechanism clearing dynamic executions and workflows while preserving seeded configs.</file>
                <file path="harvest_output_profile.py">Surgical Extraction / Inverse Merge script to safely pull UI-created output profiles back into seed_data.json.</file>
            </file_rules>
        </directory>
        <directory path="services/">
            <description>Complex business orchestration processing logic routines. Subdivided into drivers, mcp, and orchestrator.</description>
            <file_rules>
                <file path="llm_task_executor.py">Central orchestration point enforcing Fail-Fast structured execution for cognitive workflows. Sisältää dynaamisen Pydantic-kontekstivalidoinnin (Validation Context) sekä Prompt Topology ja Tail-End Injection -logiikan Prefix Cachingin eheyden säilyttämiseksi retry-luupeissa.</file>
                <file path="orchestrator/anchor_validation_service.py">TDD-testattava palvelu deterministiseen O(N) RapidFuzz -ankkurointiin ja Semantic Fallback (NLI) -kaskadiin LLMTaskExecutorin tukena.</file>
                <file path="orchestrator/matrix_reducer.py">Suorittaa Three-State Logic (PASSED, FAILED, DLQ) synkronisen reduktion Map-Reduce asynkronisista kimpaleista (chunks) TDA-sääntöjen aggregaatiomoodien (EXISTS vs ALL_MUST_COMPLY) mukaisesti.</file>
                <file path="mcp/">Model Context Protocol loop execution directory for tool-based LLM routing.</file>
            </file_rules>
        </directory>
        <directory path="scripts/">Backendin sisäiset aputyökalut, kuten OpenAPI-skeemojen automaattinen generointi.</directory>
        <directory path="templates/">Jinja2/HTML pohjat dynaamiselle PDF- ja tulostusraporttigeneroinnille (PDF Service).</directory>
        <directory path="tests/">
            <description>Automaattisen laatuportin (Pytest) yksikkö- ja integraatiotestit.</description>
            <file_rules>
                <file path="integration/">Integraatiotestit, jotka varmistavat komponenttien välisen datavirran ja logiikkainjektiot (esim. test_prompt_compiler.py).</file>
                <file path="unit/">Rakenteellisesti peilaavat yksikkötestit. Yksikkötestien tiedostopolkujen ON PAKKO vastata tismalleen lähdekoodin arkkitehtuuripolkuja (esim. services/orchestrator/test_prompt_compiler.py), tai Universal Quality Gate hylkää suorituksen.</file>
            </file_rules>
        </directory>
        <directory path="utils/">
            <description>Uudelleenkäytettävät apufunktiot, matemaattinen ydin ja graafiset piirtotyökalut.</description>
            <file_rules>
                <file path="math_utils.py">Core Mathematical Utilities. Sisältää keskitetyt StrictnessConfig-määritykset, Sigmoid- ja Lerp-skaalaukset sekä Score Clamping -turvamekanismit.</file>
                <file path="scoring/">Soft Scoring V3 -laskentamoottorit (Koearvostelu/Waterfall, Syväarvostelu/Dampening, Lineaarinen/MAD Outlier Rejection, Painotettu/Sigmoid). Suoritetaan asynkronisesti eristettynä DAG-ajosta tulostusprofiilien kireystasojen (strictness_level) perusteella.</file>
            </file_rules>
        </directory>
        <file path="main.py">FastAPI framework server execution point instantiating web boundaries and hook registries.</file>
        <file path="worker.py">ARQ Worker loop driving automated DAG task resolutions concurrently. Vastaa Virtuaalisten Järjestelmäaskeleiden (esim. sys_render_) suorittamisesta (Decoupled Scoring) sekä 'evaluate_chunk_job' -operaatioista osana skaalautuvaa Map-Reduce arkkitehtuuria.</file>
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
                <file path="execution/views/">SDUI Execution and reporting views (dashboard_view.dart, execution_report_view.dart). Sisältää Strictness UI -elementit, Zero-Math SDUI -badget sekä Virtual System Steps -näkyvyyden yhtenäisessä askellistassa (StepCard).</file>
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
                <file path="01_engine_architecture.md">Pääarkkitehtuuri ja järjestelmän ydin.</file>
                <file path="02_domain_models.md">Pydantic Domain-mallit ja Opaque ID säännöt.</file>
                <file path="03_api_and_async_core.md">API-kerros ja Asynkroninen tapahtumahallinta (Arq).</file>
                <file path="04_workflow_and_dag.md">Työnkulkujen orkestrointi ja DAG-rakenteet.</file>
                <file path="05_llm_and_hooks.md">Dynaamiset kognition muuttajat (Hooks) ja LLM-infrastruktuuri.</file>
                <file path="06_evaluation_and_scoring.md">Kognitiivinen Arviointi, BARS, Deterministinen TDA-Seeding ja Pisteidenlaskenta.</file>
                <file path="07_desktop_first_flutter.md">Flutter Client V2 (Desktop-First, SDUI, Riverpod).</file>
                <file path="08_dynamic_rendering_sdui.md">Raportoinnin Renderöintimoottori ja SDUI-näkymät.</file>
                <file path="09_data_persistence.md">Tietokanta, Repositoriot ja Nollakonfiguraatio-seedaus.</file>
                <file path="10_infrastructure_and_logs.md">Infrastruktuuri, Docker, ja Observabiliteetti (Logfire).</file>
                <file path="11_empirical_scoring_report.md">Empiirinen laskentaraportti ja tulokset.</file>
            </file_rules>
        </directory>
        <directory path="docs/epic/">"Tehtävälista / Backlog". Täällä on puhtaasti toimintaohjeita siitä, mitä asioita pitää koodissa korjata tai rakentaa seuraavaksi. Kun Epic on koodattu, se on ikään kuin "tehty".</directory>
        <directory path="scripts/">Cross-functional development utilities. Features `flutter_audit_loop.py` and `backend_audit_loop.py` which unifies CD routines.</directory>
        <file path="AGENTS.md">The Core Root Agent Configuration file ensuring foundational Windows 11 context laws exist natively before anything else.</file>
        <file path="backend_debug.log">Crucial Server Runtime trace logs exposing hidden Python/FastAPI validation faults natively generated during asynchronous events.</file>
        <file path="client_debug.log">Crucial Client Runtime trace logs exposing frontend Freezed parsing failures, Dart mapping errors, and user HTTP interruptions.</file>
    </layer>
</system_map>
