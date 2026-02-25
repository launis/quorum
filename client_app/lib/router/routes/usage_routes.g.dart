// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_routes.dart';

// **************************************************************************
// GoRouterGenerator
// **************************************************************************

List<RouteBase> get $appRoutes => [$usageRoute];

RouteBase get $usageRoute =>
    GoRouteData.$route(path: '/usage/system', factory: $UsageRoute._fromState);

mixin $UsageRoute on GoRouteData {
  static UsageRoute _fromState(GoRouterState state) => const UsageRoute();

  @override
  String get location => GoRouteData.$location('/usage/system');

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
