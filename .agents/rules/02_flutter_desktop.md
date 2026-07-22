# FRONTEND ARCHITECTURE CONSTRAINTS (V5.2 - FLUTTER)

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR FLUTTER ***

<domain_boundary>
    <role>FRONTEND FLUTTER & UI LOGIC ONLY</role>
    <instruction>These rules apply STRICTLY to Flutter (Dart) UI layout, Riverpod state management, and desktop interaction logic. If you are modifying Python APIs or Database seed JSONs, you MUST halt and read their respective rule files instead.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="the_no_pass_rule">
        <banned_pattern>Using empty catch blocks (`try { ... } catch (e) {}`).</banned_pattern>
        <mandatory_pattern>Catch exceptions, display an `ErrorView`, log it via `LoggerServiceProvider`, and `rethrow`.</mandatory_pattern>
        <catastrophic_reason>Silent exception swallowing hides catastrophic parsing and network state failures.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="sized_box_shrink_ban">
        <banned_pattern>Using `SizedBox.shrink()` to intentionally hide broken UI components or trap rendering crashes.</banned_pattern>
        <mandatory_pattern>Invalid components MUST crash natively and be caught audibly by the higher-level `AppErrorBoundary`.</mandatory_pattern>
        <catastrophic_reason>Hiding UI flaws creates phantom states where users click invisible interactive dead zones.</catastrophic_reason>
    </rule_block>

    <rule_block id="silent_json_fallbacks">
        <banned_pattern>Using fallback defaults for missing server data (e.g., `text ?? "Unknown"` or `text = ""`).</banned_pattern>
        <mandatory_pattern>Ensure 100% strict JSON conformity (`disallow_unrecognized_keys: true`). Missing data MUST crash the Freezed parser immediately.</mandatory_pattern>
        <catastrophic_reason>The Fail-Fast Client Firewall requires proactive UI crashes on bad server DTOs to protect memory integrity from data pollution.</catastrophic_reason>
    </rule_block>

    <rule_block id="monolithic_god_widgets">
        <banned_pattern>Combining UI rendering logic, heavy JSON string parsing, HTTP network calls, or manual state management directly in a Widget's `build()`.</banned_pattern>
        <mandatory_pattern>Enforce strict Riverpod SRP boundaries. Widgets ONLY render. Riverpod Notifiers ONLY hold state. Repositories ONLY handle HTTP/Network calls.</mandatory_pattern>
        <catastrophic_reason>Simultaneous layout and state parsing destroys widget lifecycle determinism, generating massive UI jank.</catastrophic_reason>
    </rule_block>

    <rule_block id="go_router_extra_ban">
        <banned_pattern>Passing entire Objects or ViewModels through the GoRouter `$extra` parameter.</banned_pattern>
        <mandatory_pattern>Routing must pass ONLY string IDs (e.g. `blk_123`). Target views re-pull full object states cleanly via Riverpod using the ID.</mandatory_pattern>
        <catastrophic_reason>Object passing violates Deep Linking specifications, resulting in a broken URL refresh experience and stale logic models.</catastrophic_reason>
    </rule_block>

    <rule_block id="freezed_when_ban">
        <banned_pattern>Using Freezed `.when()`, `.map()`, or manual `if-else` chains.</banned_pattern>
        <mandatory_pattern>ALWAYS use Dart 3 native `switch` expressions (pattern matching destructuring).</mandatory_pattern>
        <code_example>
            <anti_pattern>return state.when(data: (v) => Text(v), loading: () => Spinner());</anti_pattern>
            <pro_pattern>return switch (state) { AsyncData(:final value) => Text(value), AsyncLoading() => const Spinner() };</pro_pattern>
        </code_example>
    </rule_block>
    
    <rule_block id="manual_riverpod_providers">
        <banned_pattern>Writing `ChangeNotifier`, `StateProvider`, or manual un-annotated legacy `Provider` declaration logic.</banned_pattern>
        <mandatory_pattern>Riverpod Code Generation `@riverpod` is ABSOLUTELY MANDATORY for all state providers.</mandatory_pattern>
        <catastrophic_reason>Legacy providers leak memory aggressively and lack reliable AsyncValue tracking capabilities.</catastrophic_reason>
    </rule_block>

    <rule_block id="o1_lists">
        <banned_pattern>Using immutable collections packages for list state or deeply checking massive arrays manually.</banned_pattern>
        <mandatory_pattern>Use native Dart `List<T>` combined explicitly with `@Freezed(equal: false)` to bypass O(N^2) deep equality performance hits on Master Views.</mandatory_pattern>
        <catastrophic_reason>Deeply comparing 10,000 DAG nodes continuously freezes the main loop.</catastrophic_reason>
    </rule_block>

    <rule_block id="riverpod_read_vs_watch_ban">
        <banned_pattern>Using `ref.read` inside `build()`, or `ref.watch` inside callbacks.</banned_pattern>
        <mandatory_pattern>Inside `build()`, use ONLY `ref.watch(provider)`. `ref.read` is strictly reserved for one-time execution inside event callbacks (`onPressed`).</mandatory_pattern>
        <code_example>
            <anti_pattern>Widget build() { final x = ref.read(prov); onPressed: () => ref.watch(prov); }</anti_pattern>
            <pro_pattern>Widget build() { final x = ref.watch(prov); onPressed: () => ref.read(prov); }</pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="deprecated_commands_ban">
        <banned_pattern>Calling or proposing `flutter pub run`.</banned_pattern>
        <mandatory_pattern>ALWAYS use `dart run` instead.</mandatory_pattern>
        <catastrophic_reason>Deprecated tooling breaks the modern Flutter 3 pipeline and Quality Gate logic.</catastrophic_reason>
    </rule_block>

    <rule_block id="internal_language_and_epic_ban">
        <banned_pattern>Using the term "Epic" (or "EPIC") in any description, docstring, or comment. Using Finnish or any non-English language in comments, variable names, or internal descriptions.</banned_pattern>
        <mandatory_pattern>All internal codebase documentation, inline comments, and description fields MUST be written exclusively in English. The word "Epic" MUST NOT be used anywhere in the codebase to describe tasks or fields.</mandatory_pattern>
        <catastrophic_reason>Hardcoding non-English terminology or agile tracking terms like 'Epic' pollutes the codebase with ephemeral/localized metadata that degrades over time and confuses cross-functional developers.</catastrophic_reason>
    </rule_block>
    <rule_block id="dio_duration_zero_ban">
        <banned_pattern>Setting Dio network timeouts (e.g., `receiveTimeout`, `connectTimeout`) to `Duration.zero` to disable them.</banned_pattern>
        <mandatory_pattern>If you need to disable a timeout in Dio 5.0+, you MUST set it to `null`. Setting it to `Duration.zero` causes an immediate 0-millisecond timeout that silently aborts the socket without throwing an exception.</mandatory_pattern>
        <catastrophic_reason>A 0ms timeout creates a "Fail-Silent" bug where long-running streams (like SSE) drop instantly but trigger `onDone` instead of `onError`, permanently freezing the UI.</catastrophic_reason>
    </rule_block>

    <rule_block id="riverpod_autodispose_read_ban">
        <banned_pattern>Using `ref.read` on an `autoDispose` provider (the default `@riverpod` without keepAlive) inside a method where no active UI component is `watch`ing it.</banned_pattern>
        <mandatory_pattern>If a stateless service or client (e.g. `SseClient`) is instantiated via a Provider and needs to be imperatively accessed via `ref.read` in a controller method, its Provider MUST be explicitly marked with `@Riverpod(keepAlive: true)`. Otherwise, you must pass the injected dependency explicitly or use `ref.watch` inside the Provider's build method.</mandatory_pattern>
        <catastrophic_reason>In Riverpod 3.3, reading an `autoDispose` provider that has no active listeners creates the instance and immediately destroys it on the same millisecond, causing catastrophic state loss and silent connection failures.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="rigid_macro_breakpoint_standard">
        <banned_pattern>Using `bool isMobile = MediaQuery.of(context).size.width < 600` at the root, or applying global screen size checks for component-level responsivness.</banned_pattern>
        <mandatory_pattern>Enforce the 'Macro-Breakpoint' standard locally using `LayoutBuilder(builder: (context, constraints))`. Components must be agnostic of the global UI window and adapt strictly via:
        1. Large/Desktop (maxWidth >= 1200): Three-Pane parallel Row `[ P1 | P2 | P3 ]`
        2. Medium/Tablet (maxWidth >= 800): Two-Pane Split-Screen Row `[ Column(P1, P2) | P3 ]`
        3. Small/Mobile (maxWidth < 800): Single-column linear layout (ListView/Column)</mandatory_pattern>
        <catastrophic_reason>Global `MediaQuery` checks break component isolation in Multi-Window desktop deployments. LayoutBuilder guarantees pure component-level boundary constraints.</catastrophic_reason>
    </rule_block>

    <rule_block id="sdui_native_schizophrenia_prevention">
        <banned_pattern>Embedding new business logic, adding complex state flows, or building new UI components directly into hardcoded native views (e.g., inside `features/studio/views/`).</banned_pattern>
        <mandatory_pattern>Enforce strict Server-Driven UI (SDUI) boundaries. While legacy hardcoded views still exist in the codebase (pending a future removal epic), you MUST treat them as strictly deprecated dead-ends. ALL new UI logic, rendering flows, and component updates MUST be driven by the backend (`sdui_mapper_service.py`) and rendered dynamically via the frontend's SDUI renderer (`sdui_node_renderer.dart`). Do NOT leak business logic back into the Flutter frontend.</mandatory_pattern>
        <catastrophic_reason>Frontend-side business logic violates the core SDUI architecture. It creates "Architectural Schizophrenia" where half the app is driven by the server and half is hardcoded in Flutter, making multi-platform updates impossible and creating untraceable state bugs.</catastrophic_reason>
    </rule_block>

    <rule_block id="strict_sdui_rendering_mandate">
        <banned_pattern>Hardcoding fallback UI strings for errors or layout states (e.g. hardcoding "Export failed" if the backend returns an HTTP 400 without reading the RFC-7807 detail).</banned_pattern>
        <mandatory_pattern>The frontend MUST NOT contain any hardcoded business logic, layout states, or fallback UI strings for dynamic views (like output profiles). All dynamic content, including layout configurations, section titles, and RFC-7807 error messages, MUST be strictly driven by backend DTOs and localization dictionaries. The Flutter UI only renders what the backend provides.</mandatory_pattern>
        <catastrophic_reason>Hardcoding fallback strings for dynamic features creates unlocalized "ghost texts" and bypasses the backend's Single Source of Truth for business rules, making errors untraceable and preventing seamless multi-platform updates.</catastrophic_reason>
    </rule_block>

    <rule_block id="flexbox_native_engine_standard">
        <banned_pattern>Calculating responsive widths/heights manually using decimal multipliers (e.g., `width: constraints.maxWidth * 0.33`) creating "MediaQuery Thrashing".</banned_pattern>
        <mandatory_pattern>Utilize the Rust-backed Impeller strictly via pure declarative CSS-style Flexbox equivalents (`Row`, `Expanded(flex: N)`, `Flexible`). Let native algorithms handle proportional filling.</mandatory_pattern>
        <catastrophic_reason>Manual multipliers force the Dart UI thread to recalculate the full widget tree pixel-by-pixel upon window drag. Pure Flex constraints allow native GPU offloading, guaranteeing >60fps performance during continuous window scaling.</catastrophic_reason>
    </rule_block>

    <rule_block id="horizontal_overflow_prevention">
        <banned_pattern>Placing unbounded text (`Text()`) or dropdowns (`DropdownButtonFormField`) inside `Row` or dynamic grid layouts without containment.</banned_pattern>
        <mandatory_pattern>ALWAYS wrap ALL dynamic UI text in `Expanded` or `Flexible` AND strictly set `overflow: TextOverflow.ellipsis`. For Dropdowns, you MUST ALWAYS set `isExpanded: true`.</mandatory_pattern>
        <catastrophic_reason>Unbounded text inside Flex layouts inevitably breaches maximum rendering dimensions, generating the fatal Yellow/Black Striped 'RenderFlex overflowed' crash, rendering the UI unusable.</catastrophic_reason>
    </rule_block>

    <rule_block id="main_thread_jank_isolate">
        <banned_pattern>Deserializing or parsing JSON DTO structures directly in the Riverpod Future async loop without Thread isolation.</banned_pattern>
        <mandatory_pattern>ALWAYS dynamically wrap payload processing inside `await Isolate.run(() => jsonDecode(chunk))` if the JSON array exceeds 100 elements or the payload string exceeds 100KB.</mandatory_pattern>
        <catastrophic_reason>Parsing JSON blocks the UI Dart Isolate continuously, causing the 60fps/120fps render loop to freeze ("Jank"), making the Desktop app feel completely unresponsive.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="mutation_optimistic_ui">
        <banned_pattern>Employing full-screen modal loading spinners or holding manual state flags like `bool _isLoading = true;`. Implementing optimistic updates without a failure rollback handling.</banned_pattern>
        <mandatory_pattern>Use Riverpod 3.0 `Mutation<T>` paradigms paired with Optimistic Updates to instantly render UI changes locally. You MUST ALWAYS implement a state-reversion (rollback) mechanism in the catch/onError block to safely restore the previous state (`ref.invalidate()`) and notify the user (e.g., Toast/Snackbar) if the backend mutation fails.</mandatory_pattern>
        <catastrophic_reason>Without rollback handling on optimistic mutations, a silent network failure leaves the user staring at a false positive state, leading to critical workflow corruption.</catastrophic_reason>
    </rule_block>

    <rule_block id="transient_input_state">
        <banned_pattern>Dispatching individual keystrokes immediately to Riverpod providers on every key press event.</banned_pattern>
        <mandatory_pattern>Utilize `flutter_hooks` (`useTextEditingController`) for real-time localized typing state manipulation. Only dispatch variables to Riverpod specifically to `submit()` the mutation.</mandatory_pattern>
        <catastrophic_reason>Rebuilding the entire Riverpod provider tree on every single keystroke causes immediate 100% CPU lockup and severe typing latency on Desktop.</catastrophic_reason>
    </rule_block>

    <rule_block id="no_magic_strings_l10n">
        <banned_pattern>Hardcoding literal UI text ("Hello", "Save"), pixel padding constants, or simulated local dictionary keys.</banned_pattern>
        <mandatory_pattern>UI strings MUST be evaluated exclusively via `AppLocalizations` (`.arb` locale runtime logic). Dynamic UI elements map API Backend Enums directly. Utilize App Theme Tokens for layout padding.</mandatory_pattern>
        <catastrophic_reason>Hardcoded strings bypass the `.arb` compilation step entirely, instantly breaking Internationalization (i18n) and resulting in untranslatable ghost texts in production.</catastrophic_reason>
    </rule_block>

    <rule_block id="strict_translation_fallback_mandate">
        <banned_pattern>Using generic fallbacks like IDs or empty strings if a translation is missing, or hardcoding `fi` as a fallback when `en` is missing.</banned_pattern>
        <mandatory_pattern>All dynamic translations (e.g. `m.label.translations`) MUST follow the strict Fail-Fast resolution chain:
        1. Attempt `Localizations.localeOf(context).languageCode`.
        2. Attempt `en` (Lingua Franca fallback).
        3. If BOTH are empty/null, `throw AppException.validation('Fail-Fast: Missing required translation.');`. NEVER fallback to `fi` or model IDs.</mandatory_pattern>
        <catastrophic_reason>Masking translation failures with generic IDs or forcing Finnish fallbacks violates internationalization integrity and prevents the Fail-Fast mechanism from catching data corruption at the UI Boundary.</catastrophic_reason>
    </rule_block>

    <rule_block id="centralized_frontend_enums">
        <banned_pattern>Scattering systemic frontend Enum definitions (like API polling timeouts, maximum attempts, or concurrency limits) randomly across individual feature controllers or files.</banned_pattern>
        <mandatory_pattern>All systemic or global Client constraints MUST be centralized in `client_app_v2/lib/core/models/enums.dart` (e.g., `SystemConcurrency`). This ensures 1-to-1 architectural parity with the backend's strict enum definitions.</mandatory_pattern>
        <catastrophic_reason>Scattered magic timeouts and loosely typed enums create unmaintainable fail-fast regressions and duplicate logic when the backend architecture evolves.</catastrophic_reason>
    </rule_block>

    <rule_block id="no_raw_string_enum_mappings">
        <banned_pattern>Using `if (!['a', 'b'].contains(val))` or `switch (val) { case 'a': }` to render UI logic based on a backend string value. Dropping invalid strings into a default fallback without warning.</banned_pattern>
        <mandatory_pattern>All backend Pydantic Literals and Enums that control UI structures MUST be defined as strict `@JsonEnum()` elements in `enums.dart` and assigned to Freezed model fields. Any unsupported string sent by the server MUST crash the JSON parser natively before the UI attempts to render a broken state.</mandatory_pattern>
        <catastrophic_reason>Failing to parse the exact backend Enum causes the Dart UI to silently fall back to defaults, hiding elements off-screen and subsequently wiping those fields from the live Database upon the next User Save.</catastrophic_reason>
    </rule_block>

    <rule_block id="dropdown_database_alignment">
        <banned_pattern>Filtering dropdown items with hardcoded UI-only string filters (e.g. `categoryId == 'matrix'`) that do not match the database, or using UI fallbacks to mask schema mismatches.</banned_pattern>
        <mandatory_pattern>All dropdown items filter conditions depending on database categories MUST be strictly aligned with the database schema. Define these allowed categories explicitly as grouped lists inside `PromptBlockCategoryGroups` in `enums.dart` and use them to filter items.</mandatory_pattern>
        <catastrophic_reason>Hardcoded string filters that mismatch backend seed data categories cause fatal Flutter 'DropdownButton' assertion crashes during reactive mid-flight rebuilds.</catastrophic_reason>
    </rule_block>

    <rule_block id="frontend_zero_db_hardcoding_mandate">
        <banned_pattern>Hardcoding database IDs, specific node names, or fixed array indices in Flutter UI logic (e.g. `if (node.id == 'main_node')` or `final first = data.blocks[0]`).</banned_pattern>
        <mandatory_pattern>Flutter UI MUST NOT know about or rely on specific database record identifiers. Rendering and logic must be driven entirely by the generic schema types (e.g. `block.type == BlockType.matrix`) or explicitly provided configuration lists. The layout must be purely SDUI (Server-Driven UI) compliant.</mandatory_pattern>
        <catastrophic_reason>Coupling frontend rendering logic to specific database IDs permanently breaks the application when moving from Staging to Production, or when a user modifies their workflow configuration in the Admin Studio.</catastrophic_reason>
    </rule_block>

    <rule_block id="tenant_data_isolation">
        <banned_pattern>Leaving old cached Master Data arrays visually intact memory-resident when switching tenant organization context.</banned_pattern>
        <mandatory_pattern>Upon User/Organization modification, the prior context state MUST be deliberately and safely invalidated by targeting the root providers (e.g., `ref.invalidate(masterDataProvider);`) to protect cross-tenant privacy leaks instantly. Note: `ref.invalidate` requires the provider argument.</mandatory_pattern>
        <catastrophic_reason>Failing to flush the Riverpod cache on tenant boundary switches causes catastrophic Cross-Tenant Data Leaks, where User A sees User B's highly confidential data rendered on the screen.</catastrophic_reason>
    </rule_block>

    <rule_block id="desktop_memory_leak_prevention">
        <banned_pattern>Declaring `@Riverpod(keepAlive: true)` for transient feature views or complex editors.</banned_pattern>
        <mandatory_pattern>All UI-bound Providers MUST use standard `@riverpod` (which defaults to `autoDispose` in V3) or explicitly `@Riverpod(keepAlive: false)`. Only global Core Services (Auth, DB) may be kept alive permanently.</mandatory_pattern>
        <catastrophic_reason>Desktop apps run for weeks. Keeping transient DOM trees or huge DTO arrays alive in memory after the user navigates away causes catastrophic RAM leaks.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="documentation_and_hygiene">
        <banned_pattern>Drafting comments depicting WHAT the internal code technically does, or utilizing variables named in Finnish.</banned_pattern>
        <mandatory_pattern>Internal Logic execution operates purely in English. External Chat/Explanations operate in Finnish. Only describe WHY a specific business exception was built inline.</mandatory_pattern>
        <catastrophic_reason>Writing logic comments in Finnish forces non-Finnish engineering tools and subsequent English LLM models to hallucinate the meaning of complex Domain algorithms.</catastrophic_reason>
    </rule_block>

    <rule_block id="graceful_network_degradation">
        <banned_pattern>Crashing the entire UI via AppErrorBoundary into a red error screen due to transient network latency, HTTP 500/503 errors, or SocketExceptions.</banned_pattern>
        <mandatory_pattern>Exception to Fail-Fast: While JSON parsing errors MUST crash visibly, pure network connectivity or timeout errors MUST be caught at the Repository or Notifier level. The UI must degrade gracefully into a 'Reconnecting...' or 'AI is processing...' state without destroying the user's active local workspace (e.g., canvas or input forms).</mandatory_pattern>
        <catastrophic_reason>Transient socket errors happen constantly. Crashing the entire app and wiping the local DOM state for a 2-second WiFi drop destroys the Desktop User Experience.</catastrophic_reason>
    </rule_block>

    <rule_block id="desktop_pro_tool_interaction">
        <banned_pattern>Raw `GestureDetector` without hover states, missing `FocusNode`, or lacking keyboard shortcuts.</banned_pattern>
        <mandatory_pattern>This is a Desktop-Class Pro Tool. ALL interactive elements MUST support mouse hover (`SystemMouseCursors.click`), keyboard traversal (`FocusNode`), and `Shortcuts` actions.</mandatory_pattern>
        <catastrophic_reason>Desktop Pro Tools require pointer accuracy. Without hover states and focus nodes, users cannot navigate complex dense data grids efficiently, destroying productivity.</catastrophic_reason>
    </rule_block>

    <rule_block id="design_token_absolute_rule">
        <banned_pattern>Hardcoding magic numbers (`EdgeInsets.all(16)`) or colors (`Colors.blue`).</banned_pattern>
        <mandatory_pattern>Exclusively use global Design Tokens (e.g., `AppSpacing.p16`, `Theme.of(context).textTheme`). ANY use of hardcoded numeric doubles for heights, widths, or padding (e.g., `SizedBox(height: 15)`) is STRICTLY PROHIBITED.</mandatory_pattern>
        <catastrophic_reason>Magic numbers destroy structural rhythm, making global resizing for different monitor densities impossible.</catastrophic_reason>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <rule_block id="frontend_quality_gate_delegation">
        <mandatory_pattern>Run the quality gate as defined in `AGENTS.md`.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="ignore_generated">
        <banned_pattern>Modifying, examining, or referencing `.g.dart` or `.freezed.dart` serialization code files organically.</banned_pattern>
        <mandatory_pattern>The cognitive loop MUST actively ignore `build/` directories and native generated artifact file paths.</mandatory_pattern>
    </rule_block>

    <rule_block id="automated_code_generation_mandate">
        <banned_pattern>Getting stuck in loops trying to fix missing `.g.dart` or `.freezed.dart` files by changing Dart source code, OR asking the human user to run build commands manually.</banned_pattern>
        <mandatory_pattern>When `.arb` files or Freezed models are modified, you MUST autonomously execute the generation using the `run_command` tool (with appropriate `WaitMsBeforeAsync`):
        1. For localization (l10n) errors: Run `cd client_app_v2; flutter gen-l10n`
        2. For Riverpod/Freezed errors: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
        NEVER try to fix these missing files by modifying Dart view logic, and NEVER wait for the human to run the commands for you.</mandatory_pattern>
        <catastrophic_reason>Asking the human to run standard build commands violates the autonomous agent mandate and stalls the CI/CD pipeline.</catastrophic_reason>
    </rule_block>
</universal_quality_gate>