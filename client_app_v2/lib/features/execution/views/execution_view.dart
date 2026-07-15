import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';

import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/shared/widgets/execution_timeline.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/shared/widgets/global_error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_v2_widget.dart';
import 'package:client_app/features/execution/models/execution_record.dart';

import 'dart:convert';

/// **Live Execution SDUI Screen**
///
/// V2 Architecture: Uses `StreamNotifier` for real-time SSE updates.
/// Iterates over `frozen_context['ui_hints_snapshot']` blindly to render
/// the raw backend state.
class ExecutionView extends StatefulHookConsumerWidget {
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
    // Setup pessimistic Rehydration mutation
    final resumeMutation = useMutation<void>(
      onError: (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(AppLocalizations.of(context)!.failedToResume),
            ),
          );
        }
      },
    );

    // Watch the live stream
    final executionState = ref.watch(executionControllerProvider);

    // Auto-navigation disabled to preserve timeline visibility (tulostus osa)

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.liveExecutionTitle),
      ),
      body: switch (executionState) {
        AsyncData(:final value) => _buildExecutionContent(
          value,
          resumeMutation,
        ),
        AsyncError(:final error, :final stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
          onRetry: () => ref
              .read(executionControllerProvider.notifier)
              .resumeExecution(widget.executionId),
        ),
        _ => const Center(child: CircularProgressIndicator()),
      },
    );
  }

  Color _getStatusColor(BuildContext context, String status) {
    if (status == 'failed') return Theme.of(context).colorScheme.error;
    if (status == 'passed' || status == 'completed') {
      return Theme.of(context).colorScheme.primaryContainer;
    }
    return Theme.of(context).colorScheme.surfaceContainerHighest;
  }

  Widget _buildExecutionContent(
    ExecutionRecord? record,
    MutationState<void> resumeMutation,
  ) {
    if (record == null) {
      return Center(
        child: Text(AppLocalizations.of(context)!.establishingConnection),
      );
    }

    final status = record.status.toLowerCase();

    final isRecoverable = record.isResumable == true;

    final frozenContext = record.frozenContext ?? {};

    final stepStatesMap = record.stepStates ?? {};
    final stepStatesList = stepStatesMap.values
        .map((e) => e is Map ? e as Map<String, dynamic> : <String, dynamic>{})
        .toList();

    final results = record.results ?? <String, dynamic>{};

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
                    if (status == 'running' ||
                        status == 'pending' ||
                        status == 'queued' ||
                        resumeMutation.isLoading)
                      SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: status == 'failed'
                              ? Theme.of(context).colorScheme.onError
                              : null,
                        ),
                      )
                    else if (status == 'passed' || status == 'completed')
                      Icon(
                        Icons.check_circle,
                        color: Theme.of(context).colorScheme.primary,
                      )
                    else if (status == 'failed')
                      Icon(
                        Icons.error,
                        color: Theme.of(context).colorScheme.onError,
                      ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(
                        AppLocalizations.of(
                          context,
                        )!.statusLabel(status.toUpperCase()),
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(
                              color: status == 'failed'
                                  ? Theme.of(context).colorScheme.onError
                                  : null,
                            ),
                      ),
                    ),
                    if (status == 'failed' && isRecoverable)
                      MutationButton<void>(
                        mutation: resumeMutation,
                        label: AppLocalizations.of(
                          context,
                        )!.resumeActionableHint,
                        icon: Icons.refresh,
                        action: () => ref
                            .read(executionControllerProvider.notifier)
                            .submitRehydration(widget.executionId),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),

        // Version Drift Warning Banner
        if (frozenContext.containsKey('version_id') &&
            (frozenContext['version_id']?.toString() ?? '') != 'v2.0.0')
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16.0,
                vertical: 8.0,
              ),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  border: Border.all(
                    color: Theme.of(context).colorScheme.outlineVariant,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.warning_amber_rounded,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        AppLocalizations.of(context)!.auditDriftWarning(
                          (frozenContext['version_id']?.toString() ?? ''),
                        ),
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // V3 Global Error View for Actionable Hints
        if (status == 'failed' && record.error != null)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16.0,
                vertical: 8.0,
              ),
              child: GlobalErrorView(
                error: AppException(
                  title: AppLocalizations.of(
                    context,
                  )!.errWorkflowExecutionFailed,
                  detail: record.error.toString(),
                  extensions: {'error_code': record.error.toString()},
                ),
                actionLabel: isRecoverable
                    ? AppLocalizations.of(context)!.resumeActionableHint
                    : null,
                onAction: isRecoverable
                    ? () => ref
                          .read(executionControllerProvider.notifier)
                          .submitRehydration(widget.executionId)
                    : null,
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
                results: results,
                compact: false,
              ),
            ),
          ),

        // V3 Flat MVC Report Rendering
        if (record.reportData != null) ...[
          SliverToBoxAdapter(
            child: ReportRendererV2Widget(
              payload: record.reportData!,
              executionId: widget.executionId,
            ),
          ),
        ] else if ((status == 'passed' || status == 'completed') &&
            results.isNotEmpty)
          // ALWAYS show Raw Data JSON on completion if Heavy Fetch failed
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    AppLocalizations.of(context)!.rawOutputFallbackTitle,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(
                        context,
                      ).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: Theme.of(context).colorScheme.outlineVariant,
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
  }
}
