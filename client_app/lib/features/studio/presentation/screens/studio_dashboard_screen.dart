import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class StudioDashboardScreen extends StatelessWidget {
  const StudioDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
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
            crossAxisCount: 4,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            shrinkWrap: true,
            children: [
              _buildCard(
                context,
                title: l10n.studioDashboardWorkflowsTitle,
                icon: Icons.schema,
                description: l10n.studioDashboardWorkflowsDesc,
                onTap: () => context.go('/studio/workflows'),
              ),
              _buildCard(
                context,
                title: l10n.studioDashboardStepsTitle,
                icon: Icons.checklist,
                description: l10n.studioDashboardStepsDesc,
                onTap: () => context.go('/studio/steps'),
              ),
              _buildCard(
                context,
                title: l10n.studioDashboardMatricesTitle,
                icon: Icons.grid_on,
                description: l10n.studioDashboardMatricesDesc,
                onTap: () => context.go('/studio/matrices'),
              ),
              _buildCard(
                context,
                title: l10n.studioDashboardComponentsTitle,
                icon: Icons.extension,
                description: l10n.studioDashboardComponentsDesc,
                onTap: () => context.go('/studio/components'),
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
          padding: const EdgeInsets.all(16.0),
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
