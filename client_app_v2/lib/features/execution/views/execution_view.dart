import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/sdui/widget_factory.dart';
import 'package:client_app/utils/safe_cast.dart';

/// **Live Execution SDUI Screen**
///
/// V2 Architecture: Uses `StreamNotifier` for real-time SSE updates.
/// Iterates over `frozen_context['ui_hints_snapshot']` blindly to render
/// widget definitions from the backend using the `SDUIWidgetFactory`.
class ExecutionView extends ConsumerWidget {
  final String executionId;

  const ExecutionView({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch the live stream
    final executionState = ref.watch(executionControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Live Execution')),
      body: executionState.when(
        data: (record) {
          if (record == null) {
            return const Center(child: Text('Establishing connection...'));
          }

          final status = SafeCast.safeString(record['status']).toLowerCase();
          final frozenContext = SafeCast.safeMap(record['frozen_context']);
          final uiHints = SafeCast.safeList(frozenContext['ui_hints_snapshot']);

          return CustomScrollView(
            slivers: [
              // Sticky Status Header
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Card(
                    color: _getStatusColor(context, status),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Row(
                        children: [
                          if (status == 'running' || status == 'pending')
                            const CircularProgressIndicator()
                          else if (status == 'completed')
                            const Icon(Icons.check_circle, color: Colors.green)
                          else if (status == 'failed')
                            const Icon(Icons.error, color: Colors.white),
                          const SizedBox(width: 16),
                          Text(
                            'Status: ${status.toUpperCase()}',
                            style: Theme.of(
                              context,
                            ).textTheme.titleMedium?.copyWith(
                              color: status == 'failed' ? Colors.white : null,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),

              // Version Drift Warning Banner
              if (frozenContext.containsKey('version_id') &&
                  SafeCast.safeString(frozenContext['version_id']) != 'v2.0.0')
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16.0,
                      vertical: 8.0,
                    ),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade100,
                        border: Border.all(color: Colors.amber.shade700),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.warning_amber_rounded,
                            color: Colors.amber.shade900,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Audit Drift Warning: This execution was completed with system parameters (${SafeCast.safeString(frozenContext['version_id'])}) '
                              'that differ from the current active ruleset (v2.0.0). Results should be interpreted with caution.',
                              style: TextStyle(color: Colors.amber.shade900),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

              // SDUI Grid
              if (uiHints.isNotEmpty)
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  sliver: SliverGrid(
                    gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                      maxCrossAxisExtent:
                          800, // Breakpoint for Desktop/Tablet responsivity
                      mainAxisSpacing: 16,
                      crossAxisSpacing: 16,
                      childAspectRatio:
                          1.5, // General ratio for charts, can be overridden per widget if needed in a more advanced grid
                    ),
                    delegate: SliverChildBuilderDelegate((context, index) {
                      final hint = SafeCast.safeMap(uiHints[index]);
                      final componentType = SafeCast.safeString(
                        hint['component'],
                      );
                      final results = SafeCast.safeMap(record['results']);

                      // Generate component
                      return SDUIWidgetFactory.buildWidget(
                        hint: hint,
                        slug: componentType, // Map component type to slug
                        results: results,
                        locale: 'fi', // Default until locale context is added
                      );
                    }, childCount: uiHints.length),
                  ),
                )
              else
                const SliverFillRemaining(
                  child: Center(
                    child: Text(
                      'No UI hints available yet. Waiting for stream...',
                    ),
                  ),
                ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error:
            (error, stackTrace) => Center(
              child: Text(
                'Error: $error',
                style: const TextStyle(color: Colors.red),
              ),
            ),
      ),
    );
  }

  Color _getStatusColor(BuildContext context, String status) {
    if (status == 'failed') return Theme.of(context).colorScheme.error;
    if (status == 'completed')
      return Theme.of(context).colorScheme.primaryContainer;
    return Theme.of(context).colorScheme.surfaceContainerHighest;
  }
}
