# FRONTEND ARCHITECTURE CONSTRAINTS (V5.2 - FLUTTER)

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR FLUTTER ***

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

    <rule_block id="flexbox_native_engine_standard">
        <banned_pattern>Calculating responsive widths/heights manually using decimal multipliers (e.g., `width: constraints.maxWidth * 0.33`) creating "MediaQuery Thrashing".</banned_pattern>
        <mandatory_pattern>Utilize the Rust-backed Impeller strictly via pure declarative CSS-style Flexbox equivalents (`Row`, `Expanded(flex: N)`, `Flexible`). Let native algorithms handle proportional filling.</mandatory_pattern>
        <catastrophic_reason>Manual multipliers force the Dart UI thread to recalculate the full widget tree pixel-by-pixel upon window drag. Pure Flex constraints allow native GPU offloading, guaranteeing >60fps performance during continuous window scaling.</catastrophic_reason>
    </rule_block>

    <rule_block id="horizontal_overflow_prevention">
        <banned_pattern>Placing unbounded horizontal text (`Text()`) or dropdowns (`DropdownButtonFormField`) inside `Row` or dynamic grid layouts without containment.</banned_pattern>
        <mandatory_pattern>ALWAYS wrap text with long dynamic labels in `Expanded` (or similar flexible constraints) AND strictly set `overflow: TextOverflow.ellipsis`. For Dropdowns, you MUST ALWAYS set `isExpanded: true` to force Impeller to calculate the truncation boundaries before rendering.</mandatory_pattern>
        <catastrophic_reason>Unbounded text inside Flex layouts inevitably breaches maximum rendering dimensions, generating the fatal Yellow/Black Striped 'RenderFlex overflowed' crash, rendering the UI unusable.</catastrophic_reason>
    </rule_block>

    <rule_block id="main_thread_jank_isolate">
        <banned_pattern>Deserializing or parsing heavy JSON DTO structures directly in the Riverpod Future async loop.</banned_pattern>
        <mandatory_pattern>ALWAYS dynamically wrap massive payload processing inside `await Isolate.run(() => jsonDecode(chunk))`.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="mutation_optimistic_ui">
        <banned_pattern>Employing full-screen modal loading spinners or holding manual state flags like `bool _isLoading = true;`. Implementing optimistic updates without a failure rollback handling.</banned_pattern>
        <mandatory_pattern>Use Riverpod 3.0 `Mutation<T>` paradigms paired with Optimistic Updates to instantly render UI changes locally. You MUST ALWAYS implement a state-reversion (rollback) mechanism in the catch/onError block to safely restore the previous state (`ref.invalidate()`) and notify the user (e.g., Toast/Snackbar) if the backend mutation fails.</mandatory_pattern>
    </rule_block>

    <rule_block id="transient_input_state">
        <banned_pattern>Dispatching individual keystrokes immediately to Riverpod providers on every key press event.</banned_pattern>
        <mandatory_pattern>Utilize `flutter_hooks` (`useTextEditingController`) for real-time localized typing state manipulation. Only dispatch variables to Riverpod specifically to `submit()` the mutation.</mandatory_pattern>
    </rule_block>

    <rule_block id="no_magic_strings_l10n">
        <banned_pattern>Hardcoding literal UI text ("Hello", "Save"), pixel padding constants, or simulated local dictionary keys.</banned_pattern>
        <mandatory_pattern>UI strings must be evaluated exclusively via `AppLocalizations` (`.arb` locale runtime logic). Dynamic UI elements map API Backend Enums directly. Utilize App Theme Tokens for layout padding.</mandatory_pattern>
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
        <mandatory_pattern>Upon User/Organization modification, the prior context state MUST be deliberately and safely invalidated (`ref.invalidate()`) protecting cross-tenant privacy leaks instantly.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="documentation_and_hygiene">
        <banned_pattern>Drafting comments depicting WHAT the internal code technically does, or utilizing variables named in Finnish.</banned_pattern>
        <mandatory_pattern>Internal Logic execution operates purely in English. External Chat/Explanations operate in Finnish. Only describe WHY a specific business exception was built inline.</mandatory_pattern>
    </rule_block>

    <rule_block id="graceful_network_degradation">
        <banned_pattern>Crashing the entire UI via AppErrorBoundary into a red error screen due to transient network latency, HTTP 500/503 errors, or SocketExceptions.</banned_pattern>
        <mandatory_pattern>Exception to Fail-Fast: While JSON parsing errors MUST crash visibly, pure network connectivity or timeout errors MUST be caught at the Repository or Notifier level. The UI must degrade gracefully into a 'Reconnecting...' or 'AI is processing...' state without destroying the user's active local workspace (e.g., canvas or input forms).</mandatory_pattern>
    </rule_block>

    <rule_block id="desktop_pro_tool_interaction">
        <banned_pattern>Raw `GestureDetector` without hover states, missing `FocusNode`, or lacking keyboard shortcuts.</banned_pattern>
        <mandatory_pattern>This is a Desktop-Class Pro Tool. ALL interactive elements MUST support mouse hover (`SystemMouseCursors.click`), keyboard traversal (`FocusNode`), and `Shortcuts` actions.</mandatory_pattern>
    </rule_block>

    <rule_block id="design_token_absolute_rule">
        <banned_pattern>Hardcoding magic numbers (`EdgeInsets.all(16)`) or colors (`Colors.blue`).</banned_pattern>
        <mandatory_pattern>Exclusively use global Design Tokens (e.g., `AppSpacing.p16`, `Theme.of(context).textTheme`).</mandatory_pattern>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <frontend_verification>
        <instruction>Execute structural formatting, static layout typing, and test suites natively mapped inside the core `client_app_v2/` workspace routinely.</instruction>
        <command>Execution: `uv run python scripts/flutter_audit_loop.py [tiedosto]`</command>
        <command>Execution (Logic Gen): If Domain Data Models or Freezed structures changed: `uv run python scripts/flutter_audit_loop.py [tiedosto] --build`</command>
        <command>Alternative manual run: `dart run custom_lint ; dart run build_runner build -d`</command>
    </frontend_verification>
    
    <rule_block id="ignore_generated">
        <banned_pattern>Modifying, examining, or referencing `.g.dart` or `.freezed.dart` serialization code files organically.</banned_pattern>
        <mandatory_pattern>The cognitive loop MUST actively ignore `build/` directories and native generated artifact file paths.</mandatory_pattern>
    </rule_block>

    <rule_block id="manual_code_generation_crises">
        <banned_pattern>Getting stuck in loops trying to fix `AppLocalizations isn't defined`, `Couldn't resolve the package 'flutter_gen'`, or missing `.g.dart` / `.freezed.dart` files by changing Dart source code.</banned_pattern>
        <mandatory_pattern>When `.arb` files are modified manually (bypassing normal save-watchers) or generated models throw missing file errors, you MUST forcefully command the user to regenerate them in the client directory:
        1. For localization (l10n) errors: Ask user to run `cd client_app_v2; flutter gen-l10n;`
        2. For Riverpod/Freezed serialization errors: Ask user to run `cd client_app_v2; dart run build_runner build -d;`
        NEVER try to fix these missing files by modifying Dart view logic!</mandatory_pattern>
        <catastrophic_reason>Windows native builds often fail to detect manual changes to non-Dart files (like `.arb` strings) and will break the build with false "missing module" errors.</catastrophic_reason>
    </rule_block>
</universal_quality_gate>