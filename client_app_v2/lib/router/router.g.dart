// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'router.dart';

// **************************************************************************
// GoRouterGenerator
// **************************************************************************

List<RouteBase> get $appRoutes => [
  $loginRoute,
  $splashRoute,
  $appShellRoute,
  $adminShellRoute,
  $rootRoute,
];

RouteBase get $loginRoute =>
    GoRouteData.$route(path: '/login', factory: $LoginRoute._fromState);

mixin $LoginRoute on GoRouteData {
  static LoginRoute _fromState(GoRouterState state) => const LoginRoute();

  @override
  String get location => GoRouteData.$location('/login');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

RouteBase get $splashRoute =>
    GoRouteData.$route(path: '/splash', factory: $SplashRoute._fromState);

mixin $SplashRoute on GoRouteData {
  static SplashRoute _fromState(GoRouterState state) => const SplashRoute();

  @override
  String get location => GoRouteData.$location('/splash');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

RouteBase get $appShellRoute => StatefulShellRouteData.$route(
  factory: $AppShellRouteExtension._fromState,
  branches: [
    StatefulShellBranchData.$branch(
      routes: [
        GoRouteData.$route(
          path: '/dashboard',
          factory: $DashboardRoute._fromState,
          routes: [
            GoRouteData.$route(
              path: 'executions/:executionId',
              factory: $ExecutionRoute._fromState,
            ),
            GoRouteData.$route(
              path: 'executions/:executionId/report',
              factory: $ExecutionReportRoute._fromState,
            ),
          ],
        ),
      ],
    ),
    StatefulShellBranchData.$branch(
      routes: [
        GoRouteData.$route(
          path: '/orchestration/new',
          factory: $NewExecutionRoute._fromState,
        ),
      ],
    ),
    StatefulShellBranchData.$branch(
      routes: [
        GoRouteData.$route(
          path: '/settings',
          factory: $SettingsRoute._fromState,
        ),
      ],
    ),
  ],
);

extension $AppShellRouteExtension on AppShellRoute {
  static AppShellRoute _fromState(GoRouterState state) => const AppShellRoute();
}

mixin $DashboardRoute on GoRouteData {
  static DashboardRoute _fromState(GoRouterState state) =>
      const DashboardRoute();

  @override
  String get location => GoRouteData.$location('/dashboard');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $ExecutionRoute on GoRouteData {
  static ExecutionRoute _fromState(GoRouterState state) =>
      ExecutionRoute(executionId: state.pathParameters['executionId']!);

  ExecutionRoute get _self => this as ExecutionRoute;

  @override
  String get location => GoRouteData.$location(
    '/dashboard/executions/${Uri.encodeComponent(_self.executionId)}',
  );

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $ExecutionReportRoute on GoRouteData {
  static ExecutionReportRoute _fromState(GoRouterState state) =>
      ExecutionReportRoute(
        executionId: state.pathParameters['executionId']!,
        variant: state.uri.queryParameters['variant'] ?? 'default',
      );

  ExecutionReportRoute get _self => this as ExecutionReportRoute;

  @override
  String get location => GoRouteData.$location(
    '/dashboard/executions/${Uri.encodeComponent(_self.executionId)}/report',
    queryParams: {if (_self.variant != 'default') 'variant': _self.variant},
  );

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $NewExecutionRoute on GoRouteData {
  static NewExecutionRoute _fromState(GoRouterState state) =>
      const NewExecutionRoute();

  @override
  String get location => GoRouteData.$location('/orchestration/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $SettingsRoute on GoRouteData {
  static SettingsRoute _fromState(GoRouterState state) => const SettingsRoute();

  @override
  String get location => GoRouteData.$location('/settings');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

RouteBase get $adminShellRoute => GoRouteData.$route(
  path: '/admin',
  factory: $AdminShellRoute._fromState,
  routes: [
    GoRouteData.$route(
      path: 'workflow/new',
      factory: $WorkflowNewRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'workflow/edit/:id/:slug',
      factory: $WorkflowEditRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'prompt-block/new',
      factory: $PromptBlockNewRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'prompt-block/edit/:id/:slug',
      factory: $PromptBlockEditRoute._fromState,
    ),
    GoRouteData.$route(path: 'step/new', factory: $StepNewRoute._fromState),
    GoRouteData.$route(path: 'step/edit', factory: $StepEditRoute._fromState),
    GoRouteData.$route(
      path: 'profiles/:workflowSlug',
      factory: $ProfileEditorRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'output-profile/new',
      factory: $OutputProfileNewRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'output-profile/edit/:id',
      factory: $OutputProfileEditRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'model-registry/new',
      factory: $ModelRegistryNewRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'model-registry/edit/:id',
      factory: $ModelRegistryEditRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'mcp-gateway/new',
      factory: $McpGatewayNewRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'mcp-gateway/edit/:id',
      factory: $McpGatewayEditRoute._fromState,
    ),
    GoRouteData.$route(path: 'matrix/new', factory: $MatrixNewRoute._fromState),
    GoRouteData.$route(
      path: 'matrix/edit/:id',
      factory: $MatrixEditRoute._fromState,
    ),
  ],
);

mixin $AdminShellRoute on GoRouteData {
  static AdminShellRoute _fromState(GoRouterState state) =>
      const AdminShellRoute();

  @override
  String get location => GoRouteData.$location('/admin');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $WorkflowNewRoute on GoRouteData {
  static WorkflowNewRoute _fromState(GoRouterState state) =>
      const WorkflowNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/workflow/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $WorkflowEditRoute on GoRouteData {
  static WorkflowEditRoute _fromState(GoRouterState state) => WorkflowEditRoute(
    id: state.pathParameters['id']!,
    slug: state.pathParameters['slug']!,
  );

  WorkflowEditRoute get _self => this as WorkflowEditRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/workflow/edit/${Uri.encodeComponent(_self.id)}/${Uri.encodeComponent(_self.slug)}',
  );

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $PromptBlockNewRoute on GoRouteData {
  static PromptBlockNewRoute _fromState(GoRouterState state) =>
      const PromptBlockNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/prompt-block/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $PromptBlockEditRoute on GoRouteData {
  static PromptBlockEditRoute _fromState(GoRouterState state) =>
      PromptBlockEditRoute(
        id: state.pathParameters['id']!,
        slug: state.pathParameters['slug']!,
      );

  PromptBlockEditRoute get _self => this as PromptBlockEditRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/prompt-block/edit/${Uri.encodeComponent(_self.id)}/${Uri.encodeComponent(_self.slug)}',
  );

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $StepNewRoute on GoRouteData {
  static StepNewRoute _fromState(GoRouterState state) => const StepNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/step/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $StepEditRoute on GoRouteData {
  static StepEditRoute _fromState(GoRouterState state) =>
      StepEditRoute($extra: state.extra as Map<String, dynamic>?);

  StepEditRoute get _self => this as StepEditRoute;

  @override
  String get location => GoRouteData.$location('/admin/step/edit');

  @override
  void go(BuildContext context) => context.go(location, extra: _self.$extra);

  @override
  Future<T?> push<T>(BuildContext context) =>
      context.push<T>(location, extra: _self.$extra);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location, extra: _self.$extra);

  @override
  void replace(BuildContext context) =>
      context.replace(location, extra: _self.$extra);
}

mixin $ProfileEditorRoute on GoRouteData {
  static ProfileEditorRoute _fromState(GoRouterState state) =>
      ProfileEditorRoute(
        workflowSlug: state.pathParameters['workflowSlug']!,
        $extra: state.extra as Map<String, dynamic>?,
      );

  ProfileEditorRoute get _self => this as ProfileEditorRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/profiles/${Uri.encodeComponent(_self.workflowSlug)}',
  );

  @override
  void go(BuildContext context) => context.go(location, extra: _self.$extra);

  @override
  Future<T?> push<T>(BuildContext context) =>
      context.push<T>(location, extra: _self.$extra);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location, extra: _self.$extra);

  @override
  void replace(BuildContext context) =>
      context.replace(location, extra: _self.$extra);
}

mixin $OutputProfileNewRoute on GoRouteData {
  static OutputProfileNewRoute _fromState(GoRouterState state) =>
      const OutputProfileNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/output-profile/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $OutputProfileEditRoute on GoRouteData {
  static OutputProfileEditRoute _fromState(GoRouterState state) =>
      OutputProfileEditRoute(
        id: state.pathParameters['id']!,
        $extra: state.extra as Map<String, dynamic>?,
      );

  OutputProfileEditRoute get _self => this as OutputProfileEditRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/output-profile/edit/${Uri.encodeComponent(_self.id)}',
  );

  @override
  void go(BuildContext context) => context.go(location, extra: _self.$extra);

  @override
  Future<T?> push<T>(BuildContext context) =>
      context.push<T>(location, extra: _self.$extra);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location, extra: _self.$extra);

  @override
  void replace(BuildContext context) =>
      context.replace(location, extra: _self.$extra);
}

mixin $ModelRegistryNewRoute on GoRouteData {
  static ModelRegistryNewRoute _fromState(GoRouterState state) =>
      const ModelRegistryNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/model-registry/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $ModelRegistryEditRoute on GoRouteData {
  static ModelRegistryEditRoute _fromState(GoRouterState state) =>
      ModelRegistryEditRoute(
        id: state.pathParameters['id']!,
        $extra: state.extra as Map<String, dynamic>?,
      );

  ModelRegistryEditRoute get _self => this as ModelRegistryEditRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/model-registry/edit/${Uri.encodeComponent(_self.id)}',
  );

  @override
  void go(BuildContext context) => context.go(location, extra: _self.$extra);

  @override
  Future<T?> push<T>(BuildContext context) =>
      context.push<T>(location, extra: _self.$extra);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location, extra: _self.$extra);

  @override
  void replace(BuildContext context) =>
      context.replace(location, extra: _self.$extra);
}

mixin $McpGatewayNewRoute on GoRouteData {
  static McpGatewayNewRoute _fromState(GoRouterState state) =>
      const McpGatewayNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/mcp-gateway/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $McpGatewayEditRoute on GoRouteData {
  static McpGatewayEditRoute _fromState(GoRouterState state) =>
      McpGatewayEditRoute(
        id: state.pathParameters['id']!,
        $extra: state.extra as Map<String, dynamic>?,
      );

  McpGatewayEditRoute get _self => this as McpGatewayEditRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/mcp-gateway/edit/${Uri.encodeComponent(_self.id)}',
  );

  @override
  void go(BuildContext context) => context.go(location, extra: _self.$extra);

  @override
  Future<T?> push<T>(BuildContext context) =>
      context.push<T>(location, extra: _self.$extra);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location, extra: _self.$extra);

  @override
  void replace(BuildContext context) =>
      context.replace(location, extra: _self.$extra);
}

mixin $MatrixNewRoute on GoRouteData {
  static MatrixNewRoute _fromState(GoRouterState state) =>
      const MatrixNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/matrix/new');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

mixin $MatrixEditRoute on GoRouteData {
  static MatrixEditRoute _fromState(GoRouterState state) => MatrixEditRoute(
    id: state.pathParameters['id']!,
    $extra: state.extra as Map<String, dynamic>?,
  );

  MatrixEditRoute get _self => this as MatrixEditRoute;

  @override
  String get location => GoRouteData.$location(
    '/admin/matrix/edit/${Uri.encodeComponent(_self.id)}',
  );

  @override
  void go(BuildContext context) => context.go(location, extra: _self.$extra);

  @override
  Future<T?> push<T>(BuildContext context) =>
      context.push<T>(location, extra: _self.$extra);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location, extra: _self.$extra);

  @override
  void replace(BuildContext context) =>
      context.replace(location, extra: _self.$extra);
}

RouteBase get $rootRoute =>
    GoRouteData.$route(path: '/', factory: $RootRoute._fromState);

mixin $RootRoute on GoRouteData {
  static RootRoute _fromState(GoRouterState state) => const RootRoute();

  @override
  String get location => GoRouteData.$location('/');

  @override
  void go(BuildContext context) => context.go(location);

  @override
  Future<T?> push<T>(BuildContext context) => context.push<T>(location);

  @override
  void pushReplacement(BuildContext context) =>
      context.pushReplacement(location);

  @override
  void replace(BuildContext context) => context.replace(location);
}

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Router Provider**
///
/// The central nervous system of the application's navigation.
///
/// **Responsibility**:
/// - Manages the routing table.
/// - Handles authentication guarding (Redirects).
/// - Implements the Adaptive Shell (NavRail vs BottomBar).
///
/// **Redirect Logic**:
/// 1.  **Checking Auth**: If not logged in -> Redirect to `/login`.
/// 2.  **Hydrating Profile**: If logged in but profile loading -> Show Splash.
/// 3.  **Role Guarding**:
///     - Admin routes are protected.
///     - Unknown roles are sent to `/dashboard`.
/// 4.  **Bootstrapping**:
///     - `/` redirects to `/dashboard` or `/admin` based on role.

@ProviderFor(router)
final routerProvider = RouterProvider._();

/// **Router Provider**
///
/// The central nervous system of the application's navigation.
///
/// **Responsibility**:
/// - Manages the routing table.
/// - Handles authentication guarding (Redirects).
/// - Implements the Adaptive Shell (NavRail vs BottomBar).
///
/// **Redirect Logic**:
/// 1.  **Checking Auth**: If not logged in -> Redirect to `/login`.
/// 2.  **Hydrating Profile**: If logged in but profile loading -> Show Splash.
/// 3.  **Role Guarding**:
///     - Admin routes are protected.
///     - Unknown roles are sent to `/dashboard`.
/// 4.  **Bootstrapping**:
///     - `/` redirects to `/dashboard` or `/admin` based on role.

final class RouterProvider
    extends $FunctionalProvider<GoRouter, GoRouter, GoRouter>
    with $Provider<GoRouter> {
  /// **Router Provider**
  ///
  /// The central nervous system of the application's navigation.
  ///
  /// **Responsibility**:
  /// - Manages the routing table.
  /// - Handles authentication guarding (Redirects).
  /// - Implements the Adaptive Shell (NavRail vs BottomBar).
  ///
  /// **Redirect Logic**:
  /// 1.  **Checking Auth**: If not logged in -> Redirect to `/login`.
  /// 2.  **Hydrating Profile**: If logged in but profile loading -> Show Splash.
  /// 3.  **Role Guarding**:
  ///     - Admin routes are protected.
  ///     - Unknown roles are sent to `/dashboard`.
  /// 4.  **Bootstrapping**:
  ///     - `/` redirects to `/dashboard` or `/admin` based on role.
  RouterProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'routerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$routerHash();

  @$internal
  @override
  $ProviderElement<GoRouter> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  GoRouter create(Ref ref) {
    return router(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(GoRouter value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<GoRouter>(value),
    );
  }
}

String _$routerHash() => r'6ac56870262d8a4fc47224768b3f214c14378491';
