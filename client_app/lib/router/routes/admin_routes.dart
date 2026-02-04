import 'package:client_app/features/admin/presentation/screens/overview_screen.dart';
import 'package:client_app/features/admin/presentation/screens/system_inspector_screen.dart';
import 'package:client_app/features/shell/presentation/scaffold_with_nav.dart';
import 'package:client_app/features/studio/presentation/screens/workflow_studio_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/admin/presentation/screens/model_registry_screen.dart';

/// **Admin Shell Route (Manual Definition)**
///
/// Implements the Admin Shell using standard [ShellRoute] (or [StatefulShellRoute])
/// due to build generation constraints.
///
/// Wraps:
/// - /studio (Workflows)
/// - /registry (Config)
/// - /analytics (Matrix)
/// - /admin (System)
final adminShellRoute = StatefulShellRoute.indexedStack(
  builder: (context, state, navigationShell) {
    return ScaffoldWithNav(navigationShell: navigationShell);
  },
  branches: [
    // Branch 1: Studio
    StatefulShellBranch(
      routes: [
        GoRoute(
          path: '/studio',
          builder: (context, state) => const WorkflowStudioScreen(),
        ),
      ],
    ),
    // Branch 2: Registry
    StatefulShellBranch(
      routes: [
        GoRoute(
          path: '/registry',
          builder: (context, state) => const ModelRegistryScreen(),
        ),
      ],
    ),
    // Branch 3: Analytics
    StatefulShellBranch(
      routes: [
        GoRoute(
          path: '/analytics',
          builder:
              (context, state) => const _PlaceholderScreen(title: 'Analytics'),
        ),
      ],
    ),
    // Branch 4: Admin
    StatefulShellBranch(
      routes: [
        GoRoute(
          path: '/admin',
          builder:
              (context, state) =>
                  const OverviewScreen(), // Or UserManagement based on sub-routes
          routes: [
            // Keep existing sub-routes if any were critical, or define strictly as per plan
          ],
        ),
      ],
    ),
    // Branch 5: System Inspector
    StatefulShellBranch(
      routes: [
        GoRoute(
          path: '/admin/system',
          builder: (context, state) => const SystemInspectorScreen(),
        ),
      ],
    ),
  ],
);

class _PlaceholderScreen extends StatelessWidget {
  final String title;
  const _PlaceholderScreen({required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.construction,
              size: 64,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 16),
            Text(title, style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            const Text('Feature implementation pending Phase 2 completion.'),
          ],
        ),
      ),
    );
  }
}
