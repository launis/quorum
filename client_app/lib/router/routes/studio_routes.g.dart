// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_routes.dart';

// **************************************************************************
// GoRouterGenerator
// **************************************************************************

List<RouteBase> get $appRoutes => [$studioDashboardRoute];

RouteBase get $studioDashboardRoute => GoRouteData.$route(
  path: '/studio',
  factory: $StudioDashboardRoute._fromState,
  routes: [
    GoRouteData.$route(
      path: 'workflows',
      factory: $StudioWorkflowsRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'matrices',
      factory: $StudioMatricesRoute._fromState,
    ),
    GoRouteData.$route(path: 'steps', factory: $StudioStepsRoute._fromState),
    GoRouteData.$route(
      path: 'components',
      factory: $StudioComponentsRoute._fromState,
    ),
    GoRouteData.$route(
      path: 'knowledge',
      factory: $StudioKnowledgeRoute._fromState,
    ),
  ],
);

mixin $StudioDashboardRoute on GoRouteData {
  static StudioDashboardRoute _fromState(GoRouterState state) =>
      const StudioDashboardRoute();

  @override
  String get location => GoRouteData.$location('/studio');

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

mixin $StudioWorkflowsRoute on GoRouteData {
  static StudioWorkflowsRoute _fromState(GoRouterState state) =>
      const StudioWorkflowsRoute();

  @override
  String get location => GoRouteData.$location('/studio/workflows');

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

mixin $StudioMatricesRoute on GoRouteData {
  static StudioMatricesRoute _fromState(GoRouterState state) =>
      const StudioMatricesRoute();

  @override
  String get location => GoRouteData.$location('/studio/matrices');

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

mixin $StudioStepsRoute on GoRouteData {
  static StudioStepsRoute _fromState(GoRouterState state) =>
      const StudioStepsRoute();

  @override
  String get location => GoRouteData.$location('/studio/steps');

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

mixin $StudioComponentsRoute on GoRouteData {
  static StudioComponentsRoute _fromState(GoRouterState state) =>
      const StudioComponentsRoute();

  @override
  String get location => GoRouteData.$location('/studio/components');

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

mixin $StudioKnowledgeRoute on GoRouteData {
  static StudioKnowledgeRoute _fromState(GoRouterState state) =>
      const StudioKnowledgeRoute();

  @override
  String get location => GoRouteData.$location('/studio/knowledge');

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
