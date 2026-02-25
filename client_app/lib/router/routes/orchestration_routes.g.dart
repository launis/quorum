// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'orchestration_routes.dart';

// **************************************************************************
// GoRouterGenerator
// **************************************************************************

List<RouteBase> get $appRoutes => [$newAnalysisRoute];

RouteBase get $newAnalysisRoute => GoRouteData.$route(
  path: '/orchestration/new',
  factory: $NewAnalysisRoute._fromState,
);

mixin $NewAnalysisRoute on GoRouteData {
  static NewAnalysisRoute _fromState(GoRouterState state) =>
      const NewAnalysisRoute();

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
