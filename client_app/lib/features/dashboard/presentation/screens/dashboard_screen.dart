import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_providers.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/dashboard/presentation/widgets/execution_grid_item.dart';
import 'package:client_app/features/dashboard/presentation/widgets/execution_list_item.dart';
import 'package:client_app/features/dashboard/presentation/widgets/execution_stats_card.dart';
import 'package:client_app/features/settings/theme_provider.dart';
import 'package:client_app/features/settings/locale_provider.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';

/// The main dashboard screen displaying a list of recent executions.
///
/// Features:
/// - **Responsive Layout**: Switches between Grid and List view based on screen width.
/// - **Stats Section**: Displays summary metrics (Total, Failed, In Progress).
/// - **RBAC Readiness**: Prepared for role-based content filtering.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncExecutions = ref.watch(executionListControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.dashboardTitle),
        actions: [
          // Language Selector
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4.0),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<Locale>(
                value:
                    ref.watch(localeProvider).languageCode == 'fi'
                        ? const Locale('fi')
                        : const Locale('en'),
                icon: const Icon(Icons.language),
                onChanged: (Locale? newLocale) {
                  if (newLocale != null) {
                    ref.read(localeProvider.notifier).setLocale(newLocale);
                  }
                },
                items: const [
                  DropdownMenuItem(
                    value: Locale('fi'),
                     child: Text('🇫🇮 FI'),
                  ),
                  DropdownMenuItem(
                    value: Locale('en'),
                    child: Text('🇬🇧 EN'),
                  ),
                ],
              ),
            ),
          ),
          // Theme Selector
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4.0),
            child: IconButton(
              icon: Icon(
                ref.watch(themeModeProvider) == ThemeMode.light
                    ? Icons.light_mode
                    : ref.watch(themeModeProvider) == ThemeMode.dark
                        ? Icons.dark_mode
                        : Icons.brightness_auto,
              ),
              tooltip: l10n.themeMode,
              onPressed: () {
                // Cycle themes: System -> Light -> Dark
                final current = ref.read(themeModeProvider);
                final next =
                    current == ThemeMode.system
                        ? ThemeMode.light
                        : current == ThemeMode.light
                            ? ThemeMode.dark
                            : ThemeMode.system;
                ref.read(themeModeProvider.notifier).setThemeMode(next);
              },
            ),
          ),
          // User Info (Simple Text for now)
          Padding(
             padding: const EdgeInsets.symmetric(horizontal: 8.0),
             child: Center(
               child: Text(
                 ref.watch(authControllerProvider).asData?.value?.displayName ?? "",
                 style: const TextStyle(fontWeight: FontWeight.bold),
               ),
             ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: l10n.retry, // reusing retry or specific refresh key
            onPressed:
                () =>
                    ref
                        .read(executionListControllerProvider.notifier)
                        .refreshList(),
          ),
          const SizedBox(width: 8),
        ],

      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          context.go('/orchestration/new');
        },
        icon: const Icon(Icons.add),
        label: Text(l10n.newAnalysis),
      ),
      body: asyncExecutions.when(
        data: (executions) => _DashboardContent(executions: executions),
        error:
            (error, stack) => Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      size: 48,
                      color: Colors.red,
                    ),
                    const SizedBox(height: 16),
                    Text(l10n.failedToLoad('$error')),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed:
                          () =>
                              ref
                                  .read(
                                    executionListControllerProvider.notifier,
                                  )
                                  .refreshList(),
                      icon: const Icon(Icons.refresh),
                      label: Text(l10n.retry),
                    ),
                  ],
                ),
              ),
            ),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _DashboardContent extends StatelessWidget {
  const _DashboardContent({required this.executions});

  final List<Execution> executions;

  @override
  Widget build(BuildContext context) {
    // Determine breakpoints
    // Mobile < 600, Tablet < 1200, Desktop >= 1200
    // We switch to Grid on Tablet+ (>= 600)
    final l10n = AppLocalizations.of(context)!;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 600;
        final theme = Theme.of(context);

        return Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1000),
            child: CustomScrollView(
              slivers: [
                // 1. Stats Section (Top Padding)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: _buildStatsRow(context, executions, isMobile),
                  ),
                ),

                // 2. Section Header
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16.0,
                      vertical: 8.0,
                    ),
                    child: Text(
                      l10n.dashboardTitle,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),

                // 3. Executions List/Grid
                if (executions.isEmpty)
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.all(32.0),
                      child: Center(child: Text(l10n.noExecutions)),
                    ),
                  )
                else if (isMobile)
                  SliverList(
                    delegate: SliverChildBuilderDelegate((context, index) {
                      final execution = executions[index];
                      return ExecutionListItem(execution: execution);
                    }, childCount: executions.length),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    sliver: SliverGrid(
                      gridDelegate:
                          const SliverGridDelegateWithMaxCrossAxisExtent(
                            maxCrossAxisExtent: 400.0,
                            mainAxisSpacing: 16,
                            crossAxisSpacing: 16,
                            childAspectRatio: 1.5, // Widescreen cards
                          ),
                      delegate: SliverChildBuilderDelegate((context, index) {
                        final execution = executions[index];
                        return ExecutionGridItem(execution: execution);
                      }, childCount: executions.length),
                    ),
                  ),

                // Bottom Padding for FAB
                const SliverToBoxAdapter(child: SizedBox(height: 80)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatsRow(
    BuildContext context,
    List<Execution> list,
    bool isMobile,
  ) {
    if (list.isEmpty) return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;

    // Calculate metrics
    final total = list.length;
    final failed = list.where((e) => e.status == ExecutionStatus.failed).length;
    final running =
        list.where((e) => e.status == ExecutionStatus.running).length;

    // In a real app we'd fetch aggregate stats from API, but for now derive from loaded list
    // or mock deeper stats.

    final cards = [
      ExecutionStatsCard(
        label: l10n.totalRuns,
        value: total.toString(),
        icon: Icons.article,
        color: Colors.blue,
      ),
      ExecutionStatsCard(
        label: l10n.inProgress,
        value: running.toString(),
        icon: Icons.sync,
        color: Colors.orange,
      ),
      ExecutionStatsCard(
        label: l10n.criticalFailures,
        value: failed.toString(),
        icon: Icons.warning,
        color: Colors.red,
      ),
    ];

    if (isMobile) {
      // Horizontal scroll for stats on mobile
      return SizedBox(
        height: 120, // Card height
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          itemCount: cards.length,
          separatorBuilder: (context, index) => const SizedBox(width: 8),
          itemBuilder:
              (context, index) => SizedBox(width: 160, child: cards[index]),
        ),
      );
    } else {
      // Row (or Grid) for stats on larger screens
      return Row(
        children:
            cards
                .map(
                  (c) => Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 8.0),
                      child: c,
                    ),
                  ),
                )
                .toList(),
      );
    }
  }
}
