import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/sdui/widget_factory.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/shared/widgets/execution_timeline.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/router/router.dart';
import 'dart:convert';

/// **Live Execution SDUI Screen**
///
/// V2 Architecture: Uses `StreamNotifier` for real-time SSE updates.
/// Iterates over `frozen_context['ui_hints_snapshot']` blindly to render
/// widget definitions from the backend using the `SDUIWidgetFactory`.
class ExecutionView extends ConsumerStatefulWidget {
  final String executionId;

  const ExecutionView({super.key, required this.executionId});

  @override
  ConsumerState<ExecutionView> createState() => _ExecutionViewState();
}

class _ExecutionViewState extends ConsumerState<ExecutionView> {
  @override
  void initState() {
    super.initState();
    // Fire the stream connection immediately after the layout phase
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref
          .read(executionControllerProvider.notifier)
          .resumeExecution(widget.executionId);
    });
  }

  @override
  Widget build(BuildContext context) {
    // Watch the live stream
    final executionState = ref.watch(executionControllerProvider);

    // Auto-navigate to Report when Completed
    ref.listen<AsyncValue<Map<String, dynamic>?>>(executionControllerProvider, (
      previous,
      next,
    ) {
      if (next is AsyncData && next.value != null) {
        final status = SafeCast.safeString(next.value!['status']).toLowerCase();
        if (status == 'completed') {
          ExecutionReportRoute(executionId: widget.executionId).go(context);
        }
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.liveExecutionTitle),
      ),
      body: executionState.when(
        data: (record) {
          if (record == null) {
            return Center(
              child: Text(AppLocalizations.of(context)!.establishingConnection),
            );
          }

          final status = SafeCast.safeString(record['status']).toLowerCase();
          final frozenContext = SafeCast.safeMap(record['frozen_context']);

          final stepStatesMap = SafeCast.safeMap(record['step_states']);
          final stepStatesList =
              stepStatesMap.values.map((e) => SafeCast.safeMap(e)).toList();

          final results = SafeCast.safeMap(record['results']);

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
                            AppLocalizations.of(
                              context,
                            )!.statusLabel(status.toUpperCase()),
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
                              AppLocalizations.of(context)!.auditDriftWarning(
                                SafeCast.safeString(
                                  frozenContext['version_id'],
                                ),
                              ),
                              style: TextStyle(color: Colors.amber.shade900),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

              // Real-Time Execution Timeline
              if (stepStatesList.isNotEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16.0,
                      vertical: 8.0,
                    ),
                    child: ExecutionTimeline(
                      steps: stepStatesList,
                      compact: false,
                    ),
                  ),
                ),

              // SDUI Grid (Milestone 6: V6.0 Render Blueprint Integration)
              if (record.containsKey('render_blueprints') &&
                  record['render_blueprints'] != null &&
                  record['render_blueprints'].containsKey('default'))
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  sliver: SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final blueprint = SafeCast.safeMap(
                          record['render_blueprints']['default'],
                        );
                        final components = SafeCast.safeList(
                          blueprint['components'],
                        );
                        if (index >= components.length)
                          return const SizedBox.shrink();

                        final componentDef = SafeCast.safeMap(
                          components[index],
                        );
                        final componentType = SafeCast.safeString(
                          componentDef['type'],
                        );
                        // Use data_path as the slug if available, else a generated index slug
                        final slug =
                            SafeCast.safeString(componentDef['data_path'])
                                .replaceAll(r'$results.', '')
                                .replaceAll(r'$results', 'results_root') +
                            '_$index';

                        try {
                          return SDUIWidgetFactory.buildWidget(
                            hint:
                                componentDef, // The V6 component definition acts as the hint
                            slug: slug,
                            results: results,
                            locale:
                                Localizations.localeOf(context).languageCode,
                            logger: ref.read(loggerServiceProvider),
                          );
                        } catch (e, st) {
                          ref
                              .read(loggerServiceProvider)
                              .error(
                                'SDUIBuilder',
                                'VALIDATION_FAILED: Widget render fatal crash for slug "$componentType": $e',
                                e,
                                st,
                              );
                          return const SizedBox.shrink();
                        }
                      },
                      childCount:
                          SafeCast.safeList(
                            SafeCast.safeMap(
                              record['render_blueprints']['default'],
                            )['components'],
                          ).length,
                    ),
                  ),
                ),

              // ALWAYS show Raw Data JSON on completion
              if (status == 'completed' && results.isNotEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          AppLocalizations.of(context)!.rawOutputFallbackTitle,
                          style: Theme.of(
                            context,
                          ).textTheme.titleLarge?.copyWith(
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color:
                                Theme.of(
                                  context,
                                ).colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color:
                                  Theme.of(context).colorScheme.outlineVariant,
                            ),
                          ),
                          child: SelectableText(
                            const JsonEncoder.withIndent('  ').convert(results),
                            style: const TextStyle(fontFamily: 'monospace'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error:
            (error, stackTrace) => ErrorView(
              error: error,
              stackTrace: stackTrace,
              onRetry: () => ref.invalidate(executionControllerProvider),
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
