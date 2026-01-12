import 'package:client_app/features/settings/usage_stats_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class UsageStatsCard extends ConsumerWidget {
  const UsageStatsCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statsAsync = ref.watch(usageStatsProvider);
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.usageCurrentMonth,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
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
                            l10n.tokensUsed(stats.usedTokens),
                            style: theme.textTheme.bodySmall,
                          ),
                          Text(
                            l10n.quotaLimit(stats.tokenLimit),
                            style: theme.textTheme.bodySmall,
                          ),
                        ],
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
                  (err, stack) => Center(
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Text(
                        l10n.failedToLoad(err.toString()),
                        style: TextStyle(color: theme.colorScheme.error),
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
