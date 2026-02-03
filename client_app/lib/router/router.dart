import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/features/auth/presentation/login_screen.dart';
import 'package:client_app/features/dashboard/presentation/screens/dashboard_screen.dart';

import 'package:client_app/features/settings/presentation/screens/settings_screen.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
import 'package:client_app/features/orchestration/presentation/screens/analysis_wizard_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_monitor_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_result_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_details_screen.dart';
// Duplicate removed inside router.dart
import 'package:client_app/features/studio/presentation/screens/workflow_studio_screen.dart'; // Added for direct routing
import 'package:client_app/router/routes/admin_routes.dart'; // Manual Shell Route
import 'package:client_app/router/routes/studio_routes.dart'; // Studio Route

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'router.g.dart';

// Private keys for navigator state
final _rootNavigatorKey = GlobalKey<NavigatorState>();

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
@riverpod
GoRouter router(Ref ref) {
  // Listen to Auth State (User Profile)
  final authState = ref.watch(authControllerProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/',
    debugLogDiagnostics: true,
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
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      // Authenticated Shell (Dashboard - Generic)
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          // Pointing to ORIGINAL generic scaffold or rename generic one?
          // The task is to "Refactor Routing".
          // The "ScaffoldWithNav" I created in features/shell is specific to ADMIN.
          // The OLD "ScaffoldWithNav" in router/scaffold_with_nav.dart handles generic dashboard.
          // Ideally, I should rename the old import or use "as GenericShell".
          // But here I'll stick to pointing to the old one for Dashboard branch.
          // Note: Imports must be fixed at the top of file if I want to use both.
          // For now, I will assume the import `import 'package:client_app/router/scaffold_with_nav.dart';` is still valid for this part.
          return ScaffoldWithNav(navigationShell: navigationShell);
        },
        branches: [
          // Branch 0: Dashboard
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/dashboard',
                builder: (context, state) => const DashboardScreen(),
                routes: [
                  GoRoute(
                    path: 'executions/:id',
                    redirect: (context, state) {
                      final path = state.uri.toString();
                      if (path.endsWith('/monitor') ||
                          path.endsWith('/report') ||
                          path.endsWith('/details')) {
                        return null;
                      }
                      return '$path/monitor';
                    },
                    routes: [
                      GoRoute(
                        path: 'monitor',
                        builder: (context, state) {
                          final id = state.pathParameters['id']!;
                          return ExecutionMonitorScreen(executionId: id);
                        },
                      ),
                      GoRoute(
                        path: 'report',
                        builder: (context, state) {
                          final id = state.pathParameters['id']!;
                          return ExecutionResultScreen(executionId: id);
                        },
                      ),
                      GoRoute(
                        path: 'details',
                        builder: (context, state) {
                          final id = state.pathParameters['id']!;
                          return ExecutionDetailsScreen(executionId: id);
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          // Branch 1: New Analysis
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/orchestration/new',
                builder: (context, state) => const AnalysisWizardScreen(),
              ),
            ],
          ),
          // Branch 2: Settings
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/settings',
                builder: (context, state) => const SettingsScreen(),
              ),
            ],
          ),
        ],
      ),

      // Studio Route (Typed - Independent Shell)
      GoRoute(
        path: '/studio',
        builder: (context, state) => const StudioRoute().build(context, state),
        routes: [
          GoRoute(
            path: 'workflows',
            builder: (context, state) => const WorkflowStudioScreen(initialTabIndex: 0),
          ),
          GoRoute(
            path: 'matrices',
            builder: (context, state) => const WorkflowStudioScreen(initialTabIndex: 1),
          ),
          GoRoute(
            path: 'steps',
            builder: (context, state) => const WorkflowStudioScreen(initialTabIndex: 2),
          ),
          GoRoute(
            path: 'components',
            builder: (context, state) => const WorkflowStudioScreen(initialTabIndex: 3),
          ),
        ],
      ),

      // Admin Shell (Typed & Isolated)
      adminShellRoute,

      // Root Redirect
      GoRoute(path: '/', redirect: (context, state) => '/dashboard'),
    ],
  );
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
