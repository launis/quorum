import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';

import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/shared/widgets/execution_timeline.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/shared/widgets/global_error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/router/router.dart';

import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// **Live Execution SDUI Screen**
///
/// V2 Architecture: Uses `StreamNotifier` for real-time SSE updates.
/// Iterates over `frozen_context['ui_hints_snapshot']` blindly to render
/// the raw backend state.
class ExecutionView extends StatefulHookConsumerWidget {
  final String executionId;
  final bool autoGenerateReport;

  const ExecutionView({
    super.key,
    required this.executionId,
    this.autoGenerateReport = false,
  });

  @override
  ConsumerState<ExecutionView> createState() => _ExecutionViewState();
}

class _ExecutionViewState extends ConsumerState<ExecutionView> {
  bool _reportGenerationTriggered = false;
  bool _reportGenerationLoading = false;
  String? _reportGenerationError;

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

  Future<void> _triggerAutoReportGeneration(ExecutionRecord record) async {
    if (_reportGenerationTriggered) return;
    setState(() {
      _reportGenerationTriggered = true;
      _reportGenerationLoading = true;
      _reportGenerationError = null;
    });

    try {
      final reportsClient = ref.read(reportsClientProvider);
      final profileId =
          record.outputProfileId ?? record.activeProfileId ?? 'default';
      await reportsClient.createReport(
        executionId: widget.executionId,
        profileId: profileId,
      );
      if (!mounted) return;
      setState(() {
        _reportGenerationLoading = false;
      });
      if (context.mounted) {
        ExecutionReportRoute(executionId: widget.executionId).go(context);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _reportGenerationLoading = false;
        _reportGenerationError = e.toString();
      });
    }
  }

  void _retryReportGeneration(ExecutionRecord record) {
    setState(() {
      _reportGenerationTriggered = false;
      _reportGenerationError = null;
    });
    _triggerAutoReportGeneration(record);
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

    // Listen for completion to trigger auto-report generation if enabled
    ref.listen<AsyncValue<ExecutionRecord?>>(executionControllerProvider, (
      previous,
      next,
    ) {
      if (widget.autoGenerateReport && !_reportGenerationTriggered) {
        if (next case AsyncData(value: final record) when record != null) {
          final status = record.status.toLowerCase();
          if (status == 'passed' || status == 'completed') {
            _triggerAutoReportGeneration(record);
          }
        }
      }
    });

    // Check if initial state is already passed
    if (widget.autoGenerateReport && !_reportGenerationTriggered) {
      if (executionState case AsyncData(
        value: final record,
      ) when record != null) {
        final status = record.status.toLowerCase();
        if (status == 'passed' || status == 'completed') {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (mounted && !_reportGenerationTriggered) {
              _triggerAutoReportGeneration(record);
            }
          });
        }
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.liveExecutionTitle),
      ),
      body: AppErrorBoundary(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: switch (executionState) {
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
          ),
        ),
      ),
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

    final versionId = record.frozenContext?.versionId;

    return CustomScrollView(
      slivers: [
        // Sticky Status Header
        SliverToBoxAdapter(
          child: Padding(
            padding: AppSpacing.p16,
            child: Card(
              color: _getStatusColor(context, status),
              child: Padding(
                padding: AppSpacing.p16,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        if (status == 'running' ||
                            status == 'pending' ||
                            status == 'queued' ||
                            resumeMutation.isLoading)
                          SizedBox(
                            width: AppSpacing.s24,
                            height: AppSpacing.s24,
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
                        AppSpacing.w16,
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
                        if (status == 'passed' || status == 'completed')
                          FilledButton.icon(
                            onPressed: () => ExecutionReportRoute(
                              executionId: widget.executionId,
                            ).go(context),
                            icon: const Icon(Icons.article_outlined, size: 18),
                            label: Text(
                              AppLocalizations.of(
                                context,
                              )!.viewReportsButtonLabel,
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
                    if (status == 'running' ||
                        status == 'pending' ||
                        status == 'queued') ...[
                      AppSpacing.h16,
                      LinearProgressIndicator(
                        value: (record.progress ?? 0) / 100.0,
                        backgroundColor: Theme.of(context).colorScheme.surface,
                      ),
                      if (record.statusMessage != null &&
                          record.statusMessage!.isNotEmpty) ...[
                        AppSpacing.h8,
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                record.statusMessage!,
                                style: Theme.of(context).textTheme.bodySmall,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              '${record.progress ?? 0}%',
                              style: Theme.of(context).textTheme.labelMedium
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),

        // Auto-generating report progress banner
        if (_reportGenerationLoading)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s16,
                vertical: AppSpacing.s8,
              ),
              child: Container(
                padding: AppSpacing.p16,
                decoration: BoxDecoration(
                  color: Theme.of(
                    context,
                  ).colorScheme.primaryContainer.withAlpha(120),
                  border: Border.all(
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  borderRadius: BorderRadius.circular(AppSpacing.s8),
                ),
                child: Row(
                  children: [
                    const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    const SizedBox(width: AppSpacing.s16),
                    Expanded(
                      child: Text(
                        AppLocalizations.of(
                          context,
                        )!.autoGeneratingReportNotice,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Theme.of(
                            context,
                          ).colorScheme.onPrimaryContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // Report generation failed actionable inline alert banner
        if (_reportGenerationError != null)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s16,
                vertical: AppSpacing.s8,
              ),
              child: Container(
                padding: AppSpacing.p16,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.errorContainer,
                  border: Border.all(
                    color: Theme.of(context).colorScheme.error,
                  ),
                  borderRadius: BorderRadius.circular(AppSpacing.s8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: Theme.of(context).colorScheme.error,
                    ),
                    const SizedBox(width: AppSpacing.s16),
                    Expanded(
                      child: Text(
                        AppLocalizations.of(
                          context,
                        )!.reportGenerationFailedNotice,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onErrorContainer,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    FilledButton.tonalIcon(
                      onPressed: () => _retryReportGeneration(record),
                      icon: const Icon(Icons.refresh, size: 18),
                      label: Text(
                        AppLocalizations.of(
                          context,
                        )!.retryReportGenerationLabel,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // Version Drift Warning Banner
        if (versionId != null && versionId.isNotEmpty && versionId != 'v2.0.0')
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s16,
                vertical: AppSpacing.s8,
              ),
              child: Container(
                padding: AppSpacing.p12,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  border: Border.all(
                    color: Theme.of(context).colorScheme.outlineVariant,
                  ),
                  borderRadius: BorderRadius.circular(AppSpacing.s8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.warning_amber_rounded,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: AppSpacing.s12),
                    Expanded(
                      child: Text(
                        AppLocalizations.of(
                          context,
                        )!.auditDriftWarning(versionId),
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
                horizontal: AppSpacing.s16,
                vertical: AppSpacing.s8,
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
        if (record.steps.isNotEmpty)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s16,
                vertical: AppSpacing.s8,
              ),
              child: ExecutionTimeline(steps: record.steps, compact: false),
            ),
          ),
      ],
    );
  }
}
