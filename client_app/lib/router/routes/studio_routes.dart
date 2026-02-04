import 'package:client_app/features/studio/presentation/screens/studio_dashboard_screen.dart';
import 'package:client_app/features/studio/presentation/screens/workflow_studio_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class StudioRoute extends GoRouteData {
  const StudioRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    // Check sub-routes manually if using GoRouteData like this with nested routes?
    // GoRouteData usually maps 1:1.
    // However, here we are at /studio.
    // If I want sub-routes, I should define them in the Router configuration or use `routes` property of GoRouteData.
    // But since `StudioRoute` is a leaf in `router.dart`, I should change how it works or replace it in `router.dart`.
    // Wait, `router.dart` uses `const StudioRoute().build(...)`.
    // If I want sub-paths like `/studio/workflows`, I must define them in `router.dart` OR here IF this was a ShellRoute.
    // But it's defined as a GoRoute in `router.dart`.

    // Changing strategy: Since I cannot easily change `router.dart` structure from here without editing `router.dart` extensively,
    // I will assume `router.dart` is the place to make structural changes.
    // BUT I am editing `studio_routes.dart` which presumably is just the TypedRoute definition?
    // Actually `router.dart` imports it.

    // Let's look at `router.dart` again.
    // It creates `GoRoute(path: '/studio', builder: (context, state) => const StudioRoute().build(context, state))`.
    // This handles ONLY `/studio`.
    // It does NOT handle `/studio/workflows`.

    // To support `/studio/workflows`, I must ADD sub-routes in `router.dart`.
    // Modifying `StudioRoute` class alone won't add routes to the router configuration unless using Typed GoRoute generation which I see `router.g.dart` part.
    // Ah, `StudioRoute` extends `GoRouteData`. This implies code generation! `part 'router.g.dart';` in `router.dart`.
    // If `StudioRoute` is part of the generation, I should see annotations like `@TypedGoRoute`.
    // I don't see `@TypedGoRoute` in `studio_routes.dart`.
    // I see `admin_routes.dart` imported in `router.dart`.

    // Let's modify `router.dart` to manually define the routes for Studio instead of relying on this `StudioRoute` class being a builder if it's not generated.
    // Or I can just update `StudioRoute` to return the Dashboard, and add new routes in `router.dart`.

    // Reverting to simplistic return for `StudioRoute`.
    return const StudioDashboardScreen();
  }
}
