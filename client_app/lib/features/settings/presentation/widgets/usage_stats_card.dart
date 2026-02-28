import 'package:client_app/features/settings/usage_stats_provider.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'usage_stats_card.g.dart';

@riverpod
class UsageScope extends _$UsageScope {
  @override
  String build() {
    final userAsync = ref.watch(authControllerProvider);
    final user = userAsync.asData?.value;
    if (user?.role == UserRole.member || user?.role == UserRole.viewer) {
      return 'user';
    }
    return 'org';
  }

  void setScope(String scope) {
    state = scope;
  }
}

class UsageStatsCard extends ConsumerWidget {
  const UsageStatsCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedScope = ref.watch(usageScopeProvider);
    final statsAsync = ref.watch(usageStatsProvider(scope: selectedScope));

    final userAsync = ref.watch(authControllerProvider);
    final user = userAsync.asData?.value;

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    // Determine available scopes based on role
    final List<ButtonSegment<String>> segments = [];

    if (user != null) {
      segments.add(
        const ButtonSegment<String>(
          value: 'user',
          label: Text('My Usage'),
          icon: Icon(Icons.person),
        ),
      );

      if (user.role == UserRole.root ||
          user.role == UserRole.admin ||
          user.role == UserRole.manager) {
        segments.add(
          const ButtonSegment<String>(
            value: 'org',
            label: Text('Organization'),
            icon: Icon(Icons.business),
          ),
        );
      }

      if (user.role == UserRole.root) {
        segments.add(
          const ButtonSegment<String>(
            value: 'system',
            label: Text('System'),
            icon: Icon(Icons.admin_panel_settings),
          ),
        );
      }
    }

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.usageCurrentMonth,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (segments.length > 1)
                  SegmentedButton<String>(
                    segments: segments,
                    selected: {selectedScope},
                    onSelectionChanged: (Set<String> newSelection) {
                      ref
                          .read(usageScopeProvider.notifier)
                          .setScope(newSelection.first);
                    },
                    style: const ButtonStyle(
                      visualDensity: VisualDensity.compact,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            statsAsync.when(
              data:
                  (stats) => Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(l10n.usageQuota),
                          Text(
                            '${(stats.percentage * 100).toStringAsFixed(1)}%',
                            style: TextStyle(
                              color:
                                  stats.percentage > 0.9
                                      ? theme.colorScheme.error
                                      : theme.colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      LinearProgressIndicator(
                        value: stats.percentage,
                        backgroundColor:
                            theme.colorScheme.surfaceContainerHighest,
                        color:
                            stats.percentage > 0.9
                                ? theme.colorScheme.error
                                : theme.colorScheme.primary,
                        minHeight: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Used: \$${stats.usedCost.toStringAsFixed(6)}',
                            style: theme.textTheme.bodySmall,
                          ),
                          Text(
                            'Limit: \$${stats.costLimit.toStringAsFixed(2)}',
                            style: theme.textTheme.bodySmall,
                          ),
                        ],
                      ),
                      const Divider(height: 16),

                      // NEW METRICS GRID
                      Row(
                        children: [
                          Expanded(
                            child: _MetricTile(
                              title: 'Total Runs',
                              value: '${stats.totalRuns}',
                              icon: Icons.play_arrow,
                            ),
                          ),
                          Expanded(
                            child: _MetricTile(
                              title: 'Processing Time',
                              value:
                                  '${(stats.totalProcessingTimeMs / 1000).toStringAsFixed(1)}s',
                              icon: Icons.timer,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: _MetricTile(
                              title: 'Total Tokens',
                              value: '${stats.totalTokens}',
                              icon: Icons.data_usage,
                            ),
                          ),
                          Expanded(
                            child: _MetricTile(
                              title: 'Reasoning',
                              value: '${stats.reasoningTokens}',
                              icon: Icons.psychology,
                            ),
                          ),
                          Expanded(
                            child: _MetricTile(
                              title: 'Cached',
                              value: '${stats.cachedTokens}',
                              icon: Icons.memory,
                            ),
                          ),
                        ],
                      ),

                      if (stats.modelsUsed.isNotEmpty) ...[
                        const Divider(height: 24),
                        Text('Models Used', style: theme.textTheme.labelMedium),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 8.0,
                          runSpacing: 4.0,
                          children:
                              stats.modelsUsed.entries
                                  .map(
                                    (e) => Chip(
                                      label: Text('${e.key}: ${e.value}'),
                                      visualDensity: VisualDensity.compact,
                                      labelStyle: theme.textTheme.bodySmall,
                                    ),
                                  )
                                  .toList(),
                        ),
                      ],

                      if (stats.workflowsUsed.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        Text(
                          'Workflows Used',
                          style: theme.textTheme.labelMedium,
                        ),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 8.0,
                          runSpacing: 4.0,
                          children:
                              stats.workflowsUsed.entries
                                  .map(
                                    (e) => Chip(
                                      label: Text('${e.key}: ${e.value}'),
                                      visualDensity: VisualDensity.compact,
                                      labelStyle: theme.textTheme.bodySmall,
                                      backgroundColor:
                                          theme.colorScheme.secondaryContainer,
                                    ),
                                  )
                                  .toList(),
                        ),
                      ],

                      const Divider(height: 24),
                      Text('Rate Limits', style: theme.textTheme.labelMedium),
                      const SizedBox(height: 4),
                      Text(
                        'TPM: ${stats.tpmLimit} tokens / min',
                        style: theme.textTheme.bodySmall,
                      ),
                      Text(
                        'RPM: ${stats.rpmLimit} requests / min',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
              loading:
                  () => const Center(
                    child: Padding(
                      padding: EdgeInsets.all(16.0),
                      child: CircularProgressIndicator(),
                    ),
                  ),
              error:
                  (err, stack) => Padding(
                    padding: const EdgeInsets.only(top: 16.0),
                    child: ErrorView(
                      error: err,
                      stackTrace: stack,
                      compact: true,
                      onRetry:
                          () => ref.refresh(
                            usageStatsProvider(scope: selectedScope).future,
                          ),
                    ),
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _MetricTile({
    required this.title,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      elevation: 0,
      color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 8.0),
        child: Column(
          children: [
            Icon(icon, size: 20, color: theme.colorScheme.primary),
            const SizedBox(height: 4),
            Text(title, style: theme.textTheme.labelSmall),
            const SizedBox(height: 2),
            Text(
              value,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
