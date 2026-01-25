import 'package:client_app/features/studio/presentation/screens/studio_shell_screen.dart';
import 'package:client_app/features/studio/presentation/screens/workflow_editor_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// **Studio Routes**
///
/// Defines the sub-routes for the Cognitive Studio (Admin Workspace).
/// Root path: `/studio`
final studioRoutes = ShellRoute(
  builder: (context, state, child) {
    return StudioShellScreen(child: child);
  },
  routes: [
    GoRoute(
      path: '/studio',
      redirect: (_, __) => '/studio/workflows',
    ),
    // 1. Workflows
    GoRoute(
      path: '/studio/workflows',
      builder: (context, state) => const WorkflowEditorScreen(),
    ),
    // 2. Prompts
    GoRoute(
      path: '/studio/prompts',
      builder: (context, state) => const _StudioPlaceholderScreen(title: 'Prompt Studio'),
    ),
    // 3. Ontology
    GoRoute(
      path: '/studio/ontology',
      builder: (context, state) => const _StudioPlaceholderScreen(title: 'Ontology Studio'),
    ),
  ],
);

/// Temporary Placeholder for Studio Screens
class _StudioPlaceholderScreen extends StatelessWidget {
  final String title;
  const _StudioPlaceholderScreen({required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent, // Inherit from Shell
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.construction, size: 48, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 16),
            Text(title, style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            const Text('Under Construction'),
          ],
        ),
      ),
    );
  }
}
