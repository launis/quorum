import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/features/auth/presentation/login_screen.dart';

import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
import 'package:client_app/features/studio/views/studio_dashboard_view.dart';
import 'package:client_app/features/studio/views/workflow_builder_view.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';
import 'package:client_app/features/studio/views/step_builder_view.dart';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/execution/views/dashboard_view.dart';
import 'package:client_app/features/execution/views/execution_view.dart';
import 'package:client_app/features/execution/views/execution_report_view.dart';

part 'router.g.dart';

// Private keys for navigator state
final _rootNavigatorKey = GlobalKey<NavigatorState>();

// Global route observer for RouteAware logic (e.g. Dashboard cache invalidation)
final RouteObserver<ModalRoute<void>> routeObserver =
    RouteObserver<ModalRoute<void>>();

// Private keys for navigator state

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
final routerProvider = Provider<GoRouter>((ref) {
  // Listen to Auth State (User Profile)
  final authState = ref.watch(authControllerProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/',
    debugLogDiagnostics: true,
    observers: [routeObserver],
    errorBuilder:
        (context, state) => ErrorView(
          title: 'Navigation Error',
          error: AppException.notFound(
            'Route ${state.uri.toString()} not found or broken. ${state.error?.message ?? ""}',
          ),
          onAction: () => context.go('/dashboard'),
          actionLabel: 'Return Home',
        ),
    redirect: (context, state) {
      final isLoggingIn = state.uri.toString() == '/login';
      final isSplash = state.uri.toString() == '/splash';

      // 1. Loading State -> Splash
      if (authState.isLoading) {
        return isSplash ? null : '/splash';
      }

      // 2. Error State -> Login (Assume session lost or network error preventing auth)
      if (authState.hasError) {
        return isLoggingIn ? null : '/login';
      }

      final user = authState.asData?.value;

      // 3. Unauthenticated -> Login
      if (user == null) {
        return isLoggingIn ? null : '/login';
      }

      // 4. Authenticated -> Redirect from Guest routes (Login/Splash)
      if (isLoggingIn || isSplash) {
        return targetRouteForUser(user.role);
      }

      // 5. Role Guard
      final isAdminRoute = state.uri.toString().startsWith('/admin');
      final isStudioRoute = state.uri.toString().startsWith('/studio');

      // Strict RBAC: Only ROOT and ADMIN can access /admin or /studio routes
      if (isAdminRoute || isStudioRoute) {
        if (user.role != UserRole.root && user.role != UserRole.admin) {
          // Unauthorized access attempt -> Redirect to dashboard
          return '/dashboard';
        }
      }

      return null;
    },
    routes: $appRoutes,
  );
});

@TypedGoRoute<LoginRoute>(path: '/login')
class LoginRoute extends GoRouteData with $LoginRoute {
  const LoginRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const LoginScreen();
}

@TypedGoRoute<SplashRoute>(path: '/splash')
class SplashRoute extends GoRouteData with $SplashRoute {
  const SplashRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const SplashScreen();
}

@TypedStatefulShellRoute<AppShellRoute>(
  branches: <TypedStatefulShellBranch<StatefulShellBranchData>>[
    TypedStatefulShellBranch<DashboardBranch>(
      routes: <TypedRoute<RouteData>>[
        TypedGoRoute<DashboardRoute>(
          path: '/dashboard',
          routes: [
            TypedGoRoute<ExecutionRoute>(path: 'executions/:executionId'),
            TypedGoRoute<ExecutionReportRoute>(
              path: 'executions/:executionId/report',
            ),
          ],
        ),
      ],
    ),
    TypedStatefulShellBranch<NewAnalysisBranch>(
      routes: <TypedRoute<RouteData>>[
        TypedGoRoute<NewExecutionRoute>(path: '/orchestration/new'),
      ],
    ),
    TypedStatefulShellBranch<SettingsBranch>(
      routes: <TypedRoute<RouteData>>[
        TypedGoRoute<SettingsRoute>(path: '/settings'),
      ],
    ),
  ],
)
class AppShellRoute extends StatefulShellRouteData {
  const AppShellRoute();

  @override
  Widget builder(
    BuildContext context,
    GoRouterState state,
    StatefulNavigationShell navigationShell,
  ) {
    return ScaffoldWithNav(navigationShell: navigationShell);
  }
}

class DashboardBranch extends StatefulShellBranchData {
  const DashboardBranch();
}

class DashboardRoute extends GoRouteData with $DashboardRoute {
  const DashboardRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const DashboardView();
}

class ExecutionRoute extends GoRouteData with $ExecutionRoute {
  const ExecutionRoute({required this.executionId});
  final String executionId;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      ExecutionView(executionId: executionId);
}

class ExecutionReportRoute extends GoRouteData with $ExecutionReportRoute {
  const ExecutionReportRoute({required this.executionId});
  final String executionId;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      ExecutionReportView(executionId: executionId);
}

class NewAnalysisBranch extends StatefulShellBranchData {
  const NewAnalysisBranch();
}

class NewExecutionRoute extends GoRouteData with $NewExecutionRoute {
  const NewExecutionRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const NewExecutionView();
}

class SettingsBranch extends StatefulShellBranchData {
  const SettingsBranch();
}

class SettingsRoute extends GoRouteData with $SettingsRoute {
  const SettingsRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const Scaffold(body: Center(child: Text("Asetukset (V2 WIP)")));
}

@TypedGoRoute<AdminShellRoute>(
  path: '/admin',
  routes: <TypedRoute<RouteData>>[
    TypedGoRoute<WorkflowNewRoute>(path: 'workflow/new'),
    TypedGoRoute<WorkflowEditRoute>(path: 'workflow/edit/:slug'),
    TypedGoRoute<PromptBlockNewRoute>(path: 'prompt-block/new'),
    TypedGoRoute<PromptBlockEditRoute>(path: 'prompt-block/edit/:slug'),
    TypedGoRoute<StepNewRoute>(path: 'step/new'),
    TypedGoRoute<StepEditRoute>(path: 'step/edit'),
  ],
)
class AdminShellRoute extends GoRouteData with $AdminShellRoute {
  const AdminShellRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const StudioDashboardView();
}

class WorkflowNewRoute extends GoRouteData with $WorkflowNewRoute {
  const WorkflowNewRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const WorkflowBuilderView(slug: 'new');
}

class WorkflowEditRoute extends GoRouteData with $WorkflowEditRoute {
  const WorkflowEditRoute({required this.slug, this.$extra});
  final String slug;
  final Map<String, dynamic>? $extra;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      WorkflowBuilderView(slug: slug, initialData: $extra);
}

class PromptBlockNewRoute extends GoRouteData with $PromptBlockNewRoute {
  const PromptBlockNewRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const PromptBlockBuilderView(slug: 'new');
}

class PromptBlockEditRoute extends GoRouteData with $PromptBlockEditRoute {
  const PromptBlockEditRoute({required this.slug, this.$extra});
  final String slug;
  final Map<String, dynamic>? $extra;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      PromptBlockBuilderView(slug: slug, initialData: $extra);
}

class StepNewRoute extends GoRouteData with $StepNewRoute {
  const StepNewRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const StepBuilderView(step: {});
}

class StepEditRoute extends GoRouteData with $StepEditRoute {
  const StepEditRoute({this.$extra});
  final Map<String, dynamic>? $extra;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      StepBuilderView(step: $extra ?? const {});
}

@TypedGoRoute<RootRoute>(path: '/')
class RootRoute extends GoRouteData with $RootRoute {
  const RootRoute();
  @override
  String? redirect(BuildContext context, GoRouterState state) =>
      const DashboardRoute().location;
}

/// Helper to determine the default landing page based on role.
String targetRouteForUser(UserRole role) {
  switch (role) {
    case UserRole.root:
    case UserRole.admin:
      return '/admin';
    default:
      return '/dashboard';
  }
}
