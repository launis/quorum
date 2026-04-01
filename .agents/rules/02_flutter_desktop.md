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
        <banned_pattern>Using Freezed `.when()`, `.map()`, or manual `if-else` chains on State objects or nested Union types.</banned_pattern>
        <mandatory_pattern>ALWAYS use Dart 3 native `switch` expressions (pattern matching destructuring: `return switch(state) { AsyncData(:final value) => Text(value) };`).</mandatory_pattern>
        <catastrophic_reason>Older syntax mapping defeats modern compiler exhaustiveness checks and severely inflates line count.</catastrophic_reason>
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
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="desktop_first_layout">
        <banned_pattern>Displaying full-screen list mobile routing layouts on a PC environment natively.</banned_pattern>
        <mandatory_pattern>Enforce `VisualDensity.compact`. PC breakpoints (>1200dp) strictly utilize Three-Pane layout. Tablet (600dp-1199dp) uses TwoPane Split-Screen arrays.</mandatory_pattern>
    </rule_block>

    <rule_block id="mediaquery_thrashing_ban">
        <banned_pattern>Using `MediaQuery.of(context).size` formulas (e.g., `width * 0.05`) to dynamically stretch paddings, fonts, or fixed widget dimensions representing "responsive flow".</banned_pattern>
        <mandatory_pattern>Quorum relies on Desktop Rigid Pane architecture. Use relative Flexbox (`Expanded`, `Flexible`) inside Macro-Breakpoints (`LayoutBuilder`). Bind spacing purely to static Theme padding tokens to prevent massive >60fps render cycle rebuilds upon window resizes.</mandatory_pattern>
    </rule_block>

    <rule_block id="main_thread_jank_isolate">
        <banned_pattern>Deserializing or parsing heavy JSON DTO structures directly in the Riverpod Future async loop.</banned_pattern>
        <mandatory_pattern>ALWAYS dynamically wrap massive payload processing inside `await Isolate.run(() => jsonDecode(chunk))`.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="mutation_optimistic_ui">
        <banned_pattern>Employing full-screen modal loading spinners or holding manual state flags like `bool _isLoading = true;`.</banned_pattern>
        <mandatory_pattern>Use Riverpod 3.0 `Mutation<T>` paradigms paired with Optimistic Updates to instantly render UI changes locally while syncing softly.</mandatory_pattern>
    </rule_block>

    <rule_block id="transient_input_state">
        <banned_pattern>Dispatching individual keystrokes immediately to Riverpod providers on every key press event.</banned_pattern>
        <mandatory_pattern>Utilize `flutter_hooks` (`useTextEditingController`) for real-time localized typing state manipulation. Only dispatch variables to Riverpod specifically to `submit()` the mutation.</mandatory_pattern>
    </rule_block>

    <rule_block id="no_magic_strings_l10n">
        <banned_pattern>Hardcoding literal UI text ("Hello", "Save"), pixel padding constants, or simulated local dictionary keys.</banned_pattern>
        <mandatory_pattern>UI strings must be evaluated exclusively via `AppLocalizations` (`.arb` locale runtime logic). Dynamic UI elements map API Backend Enums directly. Utilize App Theme Tokens for layout padding.</mandatory_pattern>
    </rule_block>

    <rule_block id="tenant_data_isolation">
        <banned_pattern>Leaving old cached Master Data arrays visually intact memory-resident when switching tenant organization context.</banned_pattern>
        <mandatory_pattern>Upon User/Organization modification, the prior context state MUST be deliberately and safely invalidated (`ref.invalidate()`) protecting cross-tenant privacy leaks instantly.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="documentation_and_hygiene">
        <banned_pattern>Drafting comments depicting WHAT the internal code technically does, or utilizing variables named in Finnish.</banned_pattern>
        <mandatory_pattern>Internal Logic execution operates purely in English. External Chat/Explanations operate in Finnish. Only describe WHY a specific business exception was built inline.</mandatory_pattern>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <frontend_verification>
        <instruction>Execute structural formatting, static layout typing, and test suites natively mapped inside the core `client_app_v2/` workspace routinely.</instruction>
        <command>Execution: `uv run python docs\koodit\flutter_audit_loop.py [tiedosto]`</command>
        <command>Execution (Logic Gen): If Domain Data Models or Freezed structures changed: `uv run python docs\koodit\flutter_audit_loop.py [tiedosto] --build`</command>
        <command>Alternative manual run: `dart run custom_lint ; dart run build_runner build -d`</command>
    </frontend_verification>
    
    <rule_block id="ignore_generated">
        <banned_pattern>Modifying, examining, or referencing `.g.dart` or `.freezed.dart` serialization code files organically.</banned_pattern>
        <mandatory_pattern>The cognitive loop MUST actively ignore `build/` directories and native generated artifact file paths.</mandatory_pattern>
    </rule_block>
</universal_quality_gate>