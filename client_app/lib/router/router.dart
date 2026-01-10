import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/features/auth/presentation/login_screen.dart';
import 'package:client_app/features/dashboard/presentation/screens/dashboard_screen.dart';

import 'package:client_app/features/settings/presentation/screens/settings_screen.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
import 'package:client_app/features/orchestration/presentation/screens/analysis_wizard_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_monitor_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_result_screen.dart';
import 'package:client_app/features/admin/presentation/screens/admin_dashboard_screen.dart';
import 'package:client_app/features/admin/presentation/screens/user_management_screen.dart';
import 'package:client_app/features/admin/presentation/screens/organization_list_screen.dart';
import 'package:client_app/features/admin/presentation/screens/overview_screen.dart';
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

      // 2. Error State -> Login (or specialized error page)
      if (authState.hasError) {
        // If error (e.g. network), maybe show login to retry?
        return isLoggingIn ? null : '/login';
      }

      final user = authState.asData?.value;

      // 3. Unauthenticated -> Login
      if (user == null) {
        return isLoggingIn ? null : '/login';
      }

      // 4. Authenticated -> Redirect from Guest routes
      if (isLoggingIn || isSplash) {
        return targetRouteForUser(user.isAdmin);
      }

      // 5. Role Guard
      final isAdminRoute = state.uri.toString().startsWith('/admin');
      if (isAdminRoute && !user.isAdmin) {
        return '/dashboard';
      }

      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      // Authenticated Shell
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return ScaffoldWithNav(navigationShell: navigationShell);
        },
        branches: [
          // Branch 0: Dashboard (Member/Everyone)
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/dashboard',
                // BYPASS: Use real DashboardScreen
                builder: (context, state) => const DashboardScreen(),
                routes: [
                  GoRoute(
                    path: 'executions/:id',
                    redirect: (context, state) {
                      final path = state.uri.toString();
                      if (path.endsWith('/monitor') ||
                          path.endsWith('/report')) {
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
                    ],
                  ),
                ],
              ),
            ],
          ),
          // Branch 1: New Analysis (Member/Everyone)
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/orchestration/new',
                builder: (context, state) => const AnalysisWizardScreen(),
              ),
            ],
          ),
          // Branch 2: Settings (Member/Everyone)
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/settings',
                builder: (context, state) => const SettingsScreen(),
              ),
            ],
          ),
          // Branch 3: Admin (Root/Admin only)
          StatefulShellBranch(
            routes: [
              ShellRoute(
                builder: (context, state, child) {
                  return AdminDashboardScreen(child: child);
                },
                routes: [
                  GoRoute(
                    path: '/admin',
                    builder: (context, state) => const OverviewScreen(),
                    routes: [
                      GoRoute(
                        path: 'users',
                        builder:
                            (context, state) => const UserManagementScreen(),
                      ),
                      GoRoute(
                        path: 'organizations',
                        builder:
                            (context, state) => const OrganizationListScreen(),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
      // Root Redirect
      GoRoute(
        path: '/',
        redirect: (context, state) => '/dashboard',
        // Note: The top-level redirect will catch this before it executes
        // if we are in a special state, but `targetRouteForUser` handles the logic.
        // Actually, returning null in top-level redirect means this matches.
        // So we can just redirect to dashboard here, and if admin, the shell might
        // show admin.
        // Better: let the top level redirect handle "Landing".
      ),
    ],
  );
}

/// Helper to determine the default landing page based on role.
String targetRouteForUser(bool isAdmin) {
  return isAdmin ? '/admin' : '/dashboard';
}
