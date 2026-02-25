import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/usage/presentation/screens/usage_screen.dart';

part 'usage_routes.g.dart';

@TypedGoRoute<UsageRoute>(path: '/usage/system')
class UsageRoute extends GoRouteData with $UsageRoute {
  const UsageRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const UsageScreen();
  }
}
