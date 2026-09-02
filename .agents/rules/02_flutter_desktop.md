# FRONTEND ARCHITECTURE CONSTRAINTS (V5.2 - FLUTTER)

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR FLUTTER ***

<domain_boundary>
    <role>FRONTEND FLUTTER & UI LOGIC ONLY</role>
    <instruction>These rules apply STRICTLY to Flutter (Dart) UI layout, Riverpod state management, and desktop interaction logic. If you are modifying Python APIs or Database seed JSONs, you MUST halt and read their respective rule files instead.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="the_no_pass_rule">
        <mandate>NEVER use empty catch blocks (`try { ... } catch (e) {}`). ALWAYS catch exceptions, display an `ErrorView`, log via `LoggerServiceProvider`, and `rethrow`.</mandate>
    </rule_block>
    
    <rule_block id="sized_box_shrink_ban">
        <mandate>NEVER use `SizedBox.shrink()` to intentionally hide broken UI components or trap rendering crashes. Invalid components MUST crash natively and be caught audibly by the higher-level `AppErrorBoundary`.</mandate>
    </rule_block>

    <rule_block id="silent_json_fallbacks">
        <mandate>NEVER use fallback defaults for missing server data (e.g., `text ?? "Unknown"` or `text = ""`). ALWAYS ensure 100% strict JSON conformity (`disallowUnrecognizedKeys: true`); missing data MUST crash the Freezed parser immediately.</mandate>
    </rule_block>

    <rule_block id="monolithic_god_widgets">
        <mandate>NEVER combine UI rendering, heavy JSON string parsing, HTTP calls, or manual state management in a Widget's `build()`. ALWAYS enforce strict Riverpod SRP boundaries: Widgets ONLY render, Riverpod Notifiers ONLY hold state, Repositories ONLY handle HTTP/Network calls.</mandate>
    </rule_block>

    <rule_block id="go_router_extra_ban">
        <mandate>NEVER pass entire Objects or ViewModels through GoRouter `$extra`. Routing MUST pass ONLY string IDs (e.g. `blk_123`); target views re-fetch full object states cleanly via Riverpod using the ID.</mandate>
    </rule_block>

    <rule_block id="freezed_when_ban">
        <mandate>NEVER use Freezed `.when()`, `.map()`, or manual `if-else` chains. ALWAYS use Dart 3 native `switch` expressions with pattern matching destructuring (e.g., `switch (state) { AsyncData(:final value) => ..., AsyncLoading() => ... }`).</mandate>
    </rule_block>
    
    <rule_block id="manual_riverpod_providers">
        <mandate>NEVER write `ChangeNotifier`, `StateProvider`, or manual un-annotated legacy `Provider` declarations. Riverpod Code Generation (`@riverpod`) is ABSOLUTELY MANDATORY for all state providers.</mandate>
    </rule_block>

    <rule_block id="id_backend_authority_and_frontend_read_only_mandate">
        <mandate>NEVER allow entity IDs (`workflow.id`, `step.id`, `prompt_block.id`, `profile.id`) to be editable in frontend, generate IDs client-side without randomized crypto generators, or send custom user-crafted ID strings. All canonical entity IDs MUST be issued and generated exclusively by backend using randomized Opaque Stripe IDs (`uuid.uuid4().hex[:16]`). In Flutter, all ID fields MUST be strictly read-only (`readOnly: true` or un-editable display chips).</mandate>
    </rule_block>

    <rule_block id="3rd_party_semantic_sandboxing">
        <mandate>NEVER allow 3rd-party visual libraries (like `fl_chart`) to synthesize English accessibility texts or feed localized backend strings to chart components. ALL complex 3rd-party visual decorations (e.g., Radar/Scatter charts) MUST be wrapped in `ExcludeSemantics()`. Render accessibility content separately as standard text widgets adjacent to charts, purely driven by backend SDUI payload.</mandate>
    </rule_block>

    <rule_block id="o1_lists">
        <mandate>NEVER use immutable collections packages for list state or deeply check massive arrays manually. ALWAYS use native Dart `List<T>` combined explicitly with `@Freezed(equal: false)` to bypass O(N^2) deep equality hits on Master Views.</mandate>
    </rule_block>

    <rule_block id="riverpod_read_vs_watch_ban">
        <mandate>NEVER use `ref.read` inside `build()`, and NEVER use `ref.watch` inside callbacks. Inside `build()`, use ONLY `ref.watch(provider)`. `ref.read` is strictly reserved for one-time execution inside event callbacks (`onPressed`).</mandate>
    </rule_block>

    <rule_block id="deprecated_commands_ban">
        <mandate>NEVER call or propose `flutter pub run`. ALWAYS use `dart run` instead.</mandate>
    </rule_block>

    <rule_block id="internal_language_and_epic_ban">
        <mandate>NEVER use the term "Epic" (or "EPIC") in any description, docstring, or comment, and NEVER use Finnish or non-English in comments, variable names, or internal descriptions. ALL internal codebase documentation, inline comments, and description fields MUST be written exclusively in English.</mandate>
    </rule_block>

    <rule_block id="dio_duration_zero_ban">
        <mandate>NEVER set Dio network timeouts (`receiveTimeout`, `connectTimeout`) to `Duration.zero` to disable them (causes immediate 0ms silent abort). In Dio 5.0+, ALWAYS set timeout to `null` to disable.</mandate>
    </rule_block>

    <rule_block id="riverpod_autodispose_read_ban">
        <mandate>NEVER use `ref.read` on an `autoDispose` provider inside a method where no active UI component is watching it. If a stateless service or client (e.g. `SseClient`) is instantiated via Provider and accessed imperatively via `ref.read` in controller methods, mark its Provider explicitly with `@Riverpod(keepAlive: true)`.</mandate>
    </rule_block>

    <rule_block id="async_build_context_mounted_ban">
        <mandate>NEVER use `BuildContext` (`ScaffoldMessenger.of(context)`, `GoRouter.of(context)`, `Theme.of(context)`) after an asynchronous gap (`await`) without verifying widget mounting. ALWAYS check `if (!context.mounted) return;` immediately after ANY `await` call before interacting with `BuildContext`.</mandate>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="rigid_macro_breakpoint_standard">
        <mandate>NEVER use root `MediaQuery.of(context).size.width < 600` or global screen checks for component responsiveness. Enforce the Macro-Breakpoint standard locally using `LayoutBuilder(builder: (context, constraints))`: 1) Large/Desktop (`maxWidth >= 1200`): Three-Pane parallel Row `[ P1 | P2 | P3 ]`, 2) Medium/Tablet (`maxWidth >= 800`): Two-Pane Split-Screen Row `[ Column(P1, P2) | P3 ]`, 3) Small/Mobile (`maxWidth < 800`): Single-column linear layout (`ListView`/`Column`).</mandate>
    </rule_block>

    <rule_block id="sdui_native_schizophrenia_prevention">
        <mandate>NEVER embed new business logic, complex state flows, or new UI components into hardcoded native views (`features/studio/views/`). ALL new UI logic, rendering flows, and component updates MUST be driven by the backend (`sdui_mapper_service.py`) and rendered dynamically via the SDUI renderer (`sdui_node_renderer.dart`).</mandate>
    </rule_block>

    <rule_block id="strict_sdui_rendering_mandate">
        <mandate>NEVER hardcode fallback UI strings, layout states, or business logic for dynamic views. All dynamic content, layout configurations, section titles, and RFC-7807 error messages MUST be strictly driven by backend DTOs and localization dictionaries. Flutter UI only renders what backend provides. Modifying Flutter SDUI widgets or renderers requires verifying 1:1 semantic parity against PDF via `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` and `sdui_semantic_parity_test.dart`.</mandate>
    </rule_block>

    <rule_block id="flexbox_native_engine_standard">
        <mandate>NEVER calculate responsive widths/heights manually using decimal multipliers (`width: constraints.maxWidth * 0.33`). ALWAYS utilize Impeller via declarative Flexbox equivalents (`Row`, `Expanded(flex: N)`, `Flexible`).</mandate>
    </rule_block>

    <rule_block id="horizontal_overflow_prevention">
        <mandate>NEVER place unbounded text (`Text()`) or dropdowns (`DropdownButtonFormField`) inside `Row` or dynamic grid layouts without containment. ALWAYS wrap dynamic UI text in `Expanded` or `Flexible` with `overflow: TextOverflow.ellipsis`. For Dropdowns, ALWAYS set `isExpanded: true`.</mandate>
    </rule_block>

    <rule_block id="main_thread_jank_isolate">
        <mandate>NEVER deserialize massive JSON DTOs on the main thread, and NEVER spam `Isolate.run()` per event in high-frequency streams (SSE/WebSockets). For one-off REST API calls exceeding 100 elements or 100KB, wrap processing in `await Isolate.run(() => jsonDecode(chunk))`. For high-frequency streams, batch events before parsing or spawn a single persistent Background Worker Isolate.</mandate>
    </rule_block>
    
    <rule_block id="mutation_optimistic_ui">
        <mandate>NEVER employ full-screen modal loading spinners, hold manual flags (`bool _isLoading = true`), implement optimistic updates without rollback, or use destructive rollbacks like `ref.invalidate()`. Use Riverpod 3.0 `Mutation<T>` with Optimistic Updates. Cache prior `AsyncData` before mutation and re-assign explicitly in catch/onError block.</mandate>
    </rule_block>

    <rule_block id="transient_input_state">
        <mandate>NEVER dispatch individual keystrokes immediately to Riverpod providers on every keypress. Utilize `flutter_hooks` (`useTextEditingController`) for localized typing state and dispatch to Riverpod only to `submit()` the mutation.</mandate>
    </rule_block>

    <rule_block id="no_magic_strings_l10n">
        <mandate>NEVER hardcode literal UI text, pixel padding constants, or simulated dictionary keys. UI strings MUST be evaluated exclusively via `AppLocalizations` (`.arb` runtime logic). Dynamic elements map API Backend Enums directly. Layout padding MUST use App Theme Tokens.</mandate>
    </rule_block>

    <rule_block id="strict_translation_fallback_mandate">
        <mandate>NEVER use IDs/empty strings as translation fallbacks, hardcode `fi` when `en` is missing, or pass `BuildContext` into Riverpod Notifiers/Repositories. Dynamic translations (`m.label.translations`) MUST follow strict Fail-Fast chain: 1) Active language code (in Widgets: `Localizations.localeOf(context).languageCode`; in Notifiers/Repositories: read from `localeProvider`), 2) Lingua Franca `en`, 3) If both empty/null, `throw AppException.validation('Fail-Fast: Missing required translation.');`.</mandate>
    </rule_block>

    <rule_block id="centralized_frontend_enums">
        <mandate>NEVER scatter systemic frontend Enum definitions (API timeouts, max attempts, concurrency limits) across feature files. Centralize all systemic client constraints in `client_app_v2/lib/core/models/enums.dart` (e.g. `SystemConcurrency`) for 1:1 parity with backend enums.</mandate>
    </rule_block>

    <rule_block id="no_raw_string_enum_mappings">
        <mandate>NEVER use `if (!['a', 'b'].contains(val))` or `switch (val) { case 'a': }` to render UI logic based on raw strings, and NEVER drop invalid strings into silent default fallbacks. All backend Pydantic Literals and Enums controlling UI MUST be defined as strict `@JsonEnum()` in `enums.dart` and assigned to Freezed model fields.</mandate>
    </rule_block>

    <rule_block id="dropdown_database_alignment">
        <mandate>NEVER filter dropdown items with hardcoded UI-only string filters (`categoryId == 'matrix'`) that mismatch the database. Define allowed categories explicitly as grouped lists inside `PromptBlockCategoryGroups` in `enums.dart` and use them to filter items.</mandate>
    </rule_block>

    <rule_block id="frontend_zero_db_hardcoding_mandate">
        <mandate>NEVER hardcode database IDs, specific node names, or fixed array indices in Flutter UI logic (`if (node.id == 'main_node')`, `data.blocks[0]`). Flutter UI rendering and logic must be driven entirely by generic schema types (`block.type == BlockType.matrix`) and SDUI configuration.</mandate>
    </rule_block>

    <rule_block id="tenant_data_isolation">
        <mandate>NEVER leave cached Master Data arrays memory-resident when switching tenant/organization context. Upon User/Organization modification, prior context state MUST be invalidated targeting root providers (e.g., `ref.invalidate(masterDataProvider)`).</mandate>
    </rule_block>

    <rule_block id="desktop_memory_leak_prevention">
        <mandate>NEVER declare `@Riverpod(keepAlive: true)` for transient feature views or complex editors. All UI-bound Providers MUST use standard `@riverpod` (defaults to `autoDispose` in V3) or explicitly `@Riverpod(keepAlive: false)`. Only global Core Services (Auth, DB) may be kept alive permanently.</mandate>
    </rule_block>
    
    <rule_block id="documentation_and_hygiene">
        <mandate>NEVER draft comments depicting mechanical WHAT code does, and NEVER use Finnish in variable names or comments. Internal logic execution operates purely in English; external chat/explanations operate in Finnish. Only describe WHY a specific business exception was built inline.</mandate>
    </rule_block>

    <rule_block id="graceful_network_degradation">
        <mandate>NEVER crash the entire UI into a red screen via AppErrorBoundary due to transient network latency, HTTP 500/503 errors, or SocketExceptions. Catch pure network/timeout errors at Repository/Notifier level and degrade gracefully into a 'Reconnecting...' or 'AI is processing...' state without wiping active local workspace state.</mandate>
    </rule_block>

    <rule_block id="desktop_pro_tool_interaction">
        <mandate>NEVER use raw `GestureDetector` without hover states, omit `FocusNode`, or lack keyboard shortcuts. Desktop-Class Pro Tool: ALL interactive elements MUST support mouse hover (`SystemMouseCursors.click`), keyboard traversal (`FocusNode`), and `Shortcuts` actions.</mandate>
    </rule_block>

    <rule_block id="design_token_absolute_rule">
        <mandate>NEVER hardcode magic numbers (`EdgeInsets.all(16)`) or colors (`Colors.blue`). Exclusively use global Design Tokens (`AppSpacing.p16`, `Theme.of(context).textTheme`). Hardcoded numeric doubles for heights, widths, or padding (`SizedBox(height: 15)`) are STRICTLY PROHIBITED.</mandate>
    </rule_block>

    <rule_block id="studio_unified_visual_design_system">
        <mandate>All Quorum Studio CRUD views and profile tabs (including OutputProfileCrudView tabs 1-4) MUST strictly adhere to the Studio Unified Visual & UX Design System: 1) Consistent Card containers (`elevation: 2`, `BorderRadius.circular(12)`, `margin: bottom 16`, `padding: 16`), 2) Interactive `FilterChip`/`ChoiceChip` widgets for multi-select groups instead of small checkboxes, 3) Pill-shaped status badges (`Container` with `colorScheme.primaryContainer` and rounded borders), 4) `fontSize: 20, bold` headers with `OutlinedButton.icon` action triggers and red `IconButton` delete triggers, 5) 100% Theme.of(context) color adherence.</mandate>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <rule_block id="frontend_quality_gate_delegation">
        <mandate>ALWAYS run the quality gate as defined in `AGENTS.md`: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`.</mandate>
    </rule_block>
    
    <rule_block id="ignore_generated">
        <mandate>NEVER modify, examine, or reference `.g.dart` or `.freezed.dart` serialization code files organically. Actively ignore `build/` directories and native generated artifact file paths.</mandate>
    </rule_block>

    <rule_block id="automated_code_generation_mandate">
        <mandate>NEVER get stuck in loops modifying Dart view logic to fix missing `.g.dart`/`.freezed.dart` files, and NEVER ask the user to run build commands manually. Autonomously execute generation via `run_command`: 1) For localization (l10n): `cd client_app_v2; flutter gen-l10n`, 2) For Riverpod/Freezed: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`.</mandate>
    </rule_block>
</universal_quality_gate>