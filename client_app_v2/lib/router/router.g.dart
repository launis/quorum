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
      path: 'workflow/edit',
      factory: $WorkflowEditRoute._fromState,
    ),
    GoRouteData.$route(path: 'matrix/new', factory: $MatrixNewRoute._fromState),
    GoRouteData.$route(
      path: 'matrix/edit',
      factory: $MatrixEditRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'task-blueprint/new',
      factory: $TaskBlueprintNewRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'task-blueprint/edit',
      factory: $TaskBlueprintEditRoute._fromState,
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
  static WorkflowEditRoute _fromState(GoRouterState state) =>
      WorkflowEditRoute($extra: state.extra as Map<String, dynamic>?);

  WorkflowEditRoute get _self => this as WorkflowEditRoute;

  @override
  String get location => GoRouteData.$location('/admin/workflow/edit');

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
  static MatrixEditRoute _fromState(GoRouterState state) =>
      MatrixEditRoute($extra: state.extra as Map<String, dynamic>?);

  MatrixEditRoute get _self => this as MatrixEditRoute;

  @override
  String get location => GoRouteData.$location('/admin/matrix/edit');

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

mixin $TaskBlueprintNewRoute on GoRouteData {
  static TaskBlueprintNewRoute _fromState(GoRouterState state) =>
      const TaskBlueprintNewRoute();

  @override
  String get location => GoRouteData.$location('/admin/task-blueprint/new');

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

mixin $TaskBlueprintEditRoute on GoRouteData {
  static TaskBlueprintEditRoute _fromState(GoRouterState state) =>
      TaskBlueprintEditRoute($extra: state.extra as Map<String, dynamic>?);

  TaskBlueprintEditRoute get _self => this as TaskBlueprintEditRoute;

  @override
  String get location => GoRouteData.$location('/admin/task-blueprint/edit');

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
