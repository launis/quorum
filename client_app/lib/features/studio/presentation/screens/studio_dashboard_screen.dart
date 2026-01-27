import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class StudioDashboardScreen extends StatelessWidget {
  const StudioDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cognitive Studio'),
        leading: BackButton(
          onPressed: () => context.go('/dashboard'),
        ),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 900),
          child: GridView.count(
            crossAxisCount: 3,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            shrinkWrap: true,
            children: [
              _buildCard(
                context,
                title: 'Workflows',
                icon: Icons.schema,
                description: 'Design and manage audit workflows.',
                onTap: () => context.go('/studio/workflows'),
              ),
              _buildCard(
                context,
                title: 'Matrices',
                icon: Icons.grid_on,
                description: 'Configure evaluation criteria and matrices.',
                onTap: () => context.go('/studio/matrices'),
              ),
              _buildCard(
                context,
                title: 'Components',
                icon: Icons.extension,
                description: 'Manage re-usable prompts and rules.',
                // For now, Components maps to matrices or custom generic component view?
                // User asked for "Components" menu.
                // Assuming it might share the Matrix/Sidebar view or be separate.
                // Reusing WorkflowStudioScreen with specific tab or new screen.
                // Since we don't have a component editor yet, maybe just point to matrices for now or show "Coming soon"?
                // Or maybe the Sidebar will have a "Components" tab?
                // The current Sidebar has "Workflows" and "Matrices".
                // I'll point to /studio/components and handle it in router.
                onTap: () => context.go('/studio/matrices'), // Temporarily mapping to matrices as that's the closest "Component" type we have editor for.
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required String description,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 48, color: theme.colorScheme.primary),
              const SizedBox(height: 16),
              Text(
                title,
                style: theme.textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: theme.textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
