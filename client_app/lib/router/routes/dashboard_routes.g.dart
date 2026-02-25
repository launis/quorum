// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dashboard_routes.dart';

// **************************************************************************
// GoRouterGenerator
// **************************************************************************

List<RouteBase> get $appRoutes => [$dashboardHomeRoute];

RouteBase get $dashboardHomeRoute => GoRouteData.$route(
  path: '/dashboard',
  factory: $DashboardHomeRoute._fromState,
  routes: [
    GoRouteData.$route(
      path: 'executions/:executionId/monitor',
      factory: $ExecutionMonitorRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'executions/:executionId/report',
      factory: $ExecutionResultRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'executions/:executionId/details',
      factory: $ExecutionDetailsRoute._fromState,
    ),
  ],
);

mixin $DashboardHomeRoute on GoRouteData {
  static DashboardHomeRoute _fromState(GoRouterState state) =>
      const DashboardHomeRoute();

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

mixin $ExecutionMonitorRoute on GoRouteData {
  static ExecutionMonitorRoute _fromState(GoRouterState state) =>
      ExecutionMonitorRoute(state.pathParameters['executionId']!);

  ExecutionMonitorRoute get _self => this as ExecutionMonitorRoute;

  @override
  String get location => GoRouteData.$location(
    '/dashboard/executions/${Uri.encodeComponent(_self.executionId)}/monitor',
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

mixin $ExecutionResultRoute on GoRouteData {
  static ExecutionResultRoute _fromState(GoRouterState state) =>
      ExecutionResultRoute(state.pathParameters['executionId']!);

  ExecutionResultRoute get _self => this as ExecutionResultRoute;

  @override
  String get location => GoRouteData.$location(
    '/dashboard/executions/${Uri.encodeComponent(_self.executionId)}/report',
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

mixin $ExecutionDetailsRoute on GoRouteData {
  static ExecutionDetailsRoute _fromState(GoRouterState state) =>
      ExecutionDetailsRoute(state.pathParameters['executionId']!);

  ExecutionDetailsRoute get _self => this as ExecutionDetailsRoute;

  @override
  String get location => GoRouteData.$location(
    '/dashboard/executions/${Uri.encodeComponent(_self.executionId)}/details',
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
