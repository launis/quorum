import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/features/auth/presentation/providers/auth_provider.dart';
import 'package:client_app/features/auth/presentation/providers/user_role_provider.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'router.g.dart';

// Private keys for navigator state
final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

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
  // Listen to Auth State to trigger rebuilds on login/logout
  final authState = ref.watch(authStateProvider);
  final userProfile = ref.watch(currentUserProfileProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/',
    debugLogDiagnostics: true, // Helpful for debugging redirects
    redirect: (context, state) {
      // 1. Unwrap Auth State
      final isLoggedIn = authState.asData?.value != null;
      final isLoggingIn = state.uri.toString() == '/login';
      final isSplash = state.uri.toString() == '/splash';

      // 2. Not Logged In -> Force Login
      if (!isLoggedIn) {
        return isLoggingIn ? null : '/login';
      }

      // 3. Logged In -> Handle Profile Loading
      // If we are logged in, we MUST have the profile to decide where to go.
      // If profile is loading or error, we show splash to prevent "flash of content"
      // or security leaks.
      if (userProfile.isLoading || userProfile.hasError) {
        return isSplash ? null : '/splash';
      }

      final profile = userProfile.asData?.value;

      // If profile is somehow null (e.g. backend error treated as success null),
      // we might want to stay on splash or show error.
      // For now, assuming hydration works if not loading/error.
      if (profile == null) return '/splash';

      // 4. Already on Login/Splash? -> Go Home
      if (isLoggingIn || isSplash) {
        return targetRouteForUser(profile.isAdmin); // '/admin' or '/dashboard'
      }

      // 5. Role Guarding
      // Example: Member trying to access /admin
      final isAdminRoute = state.uri.toString().startsWith('/admin');
      if (isAdminRoute && !profile.isAdmin) {
        return '/dashboard'; // Access Denied -> Fallback
      }

      return null; // Allow navigation
    },
    routes: [
      GoRoute(
        path: '/login',
        builder:
            (context, state) => const Scaffold(
              body: Center(child: Text('Login Screen Placeholder')),
            ),
      ),
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
                builder:
                    (context, state) =>
                        const Scaffold(body: Center(child: Text('Dashboard'))),
              ),
            ],
          ),
          // Branch 1: Admin (Root/Admin only)
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/admin',
                builder:
                    (context, state) => const Scaffold(
                      body: Center(child: Text('Admin Panel')),
                    ),
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
