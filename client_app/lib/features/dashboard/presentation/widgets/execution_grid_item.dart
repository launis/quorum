import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_providers.dart';

/// A card representing a single execution in a grid layout.
class ExecutionGridItem extends ConsumerStatefulWidget {
  const ExecutionGridItem({super.key, required this.execution});

  final Execution execution;

  @override
  ConsumerState<ExecutionGridItem> createState() => _ExecutionGridItemState();
}

class _ExecutionGridItemState extends ConsumerState<ExecutionGridItem> {
  // Cache progress to prevent backward jumps (jitter)
  double _cachedProgress = 0.0;
  String? _lastStepName;

  @override
  void initState() {
    super.initState();
    _updateProgress();
  }

  @override
  void didUpdateWidget(ExecutionGridItem oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.execution != widget.execution) {
      _updateProgress();
    }
  }

  void _updateProgress() {
    final newProgress = _calculateMonotonicProgress(widget.execution);

    // Check for ID change or status reset (e.g. Restart)
    // If status is 'started' or 'pending', we should always be able to reset.
    bool shouldReset =
        widget.execution.status == ExecutionStatus.started ||
        widget.execution.status == ExecutionStatus.pending;

    // If we are Running, but cached was Completed (1.0), we must reset.
    if (widget.execution.status == ExecutionStatus.running &&
        _cachedProgress >= 0.99) {
      // This handles the "Run Again" case where the widget state persists.
      shouldReset = true;
    }

    if (shouldReset) {
      _cachedProgress = newProgress;
      return;
    }

    // Normal monotonic update
    if (widget.execution.status == ExecutionStatus.completed) {
      _cachedProgress = 1.0;
    } else if (newProgress >= _cachedProgress) {
      _cachedProgress = newProgress;
    }
    // Allow slight corrections if we switched branches or steps reordered,
    // but prevent massive jumps unless it's a reset.
    else {
      final currentStep = _getCurrentStepName(widget.execution);
      if (currentStep != _lastStepName) {
        _lastStepName = currentStep;
        if (currentStep != null) {
          // If we have a valid step, trust it, even if it resets progress slightly (e.g. parallel branches)
          // But don't drop to 0.1 default if we were further ahead.
          if (newProgress > 0.15) {
            _cachedProgress = newProgress;
          }
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).toString();
    final dateFormat = DateFormat.yMMMd(locale).add_Hm();
    final statusColor = _getStatusColor(widget.execution.status);

    return Card(
      clipBehavior: Clip.antiAlias,
      elevation: 2,
      child: InkWell(
        onTap: () {
          if (widget.execution.status == ExecutionStatus.completed) {
            context.go('/dashboard/executions/${widget.execution.id}/report');
          } else {
            context.go('/dashboard/executions/${widget.execution.id}/monitor');
          }
        },
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: statusColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: statusColor.withValues(alpha: 0.2),
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _getStatusIcon(widget.execution.status),
                          size: 14,
                          color: statusColor,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _getStatusLabel(l10n, widget.execution.status),
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: statusColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Action Buttons: Cancel (Active) vs Delete (Terminal)
                  if (widget.execution.status == ExecutionStatus.running ||
                      widget.execution.status == ExecutionStatus.pending)
                    Container(
                      margin: const EdgeInsets.only(left: 8),
                      child: IconButton(
                        onPressed: () {
                          ref
                              .read(executionControllerProvider.notifier)
                              .cancelExecution(widget.execution.id);
                        },
                        icon: const Icon(Icons.cancel, color: Colors.orange), // Orange for 'Stop'
                        iconSize: 20,
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        tooltip: l10n.cancel,
                      ),
                    )
                  else if (widget.execution.status == ExecutionStatus.completed ||
                           widget.execution.status == ExecutionStatus.failed ||
                           widget.execution.status == ExecutionStatus.rejected ||
                           widget.execution.status == ExecutionStatus.interrupted ||
                           widget.execution.status == ExecutionStatus.cancelling ||
                           widget.execution.status == ExecutionStatus.unknown)
                     Container(
                      margin: const EdgeInsets.only(left: 8),
                      child: IconButton(
                        onPressed: () {
                          // Confirm delete logic could be added here, but for now direct action like Cancel
                          ref
                              .read(executionListControllerProvider.notifier)
                              .deleteExecution(widget.execution.id);
                        },
                        icon: const Icon(Icons.delete_outline, color: Colors.grey), // Grey/Red for Delete
                        iconSize: 20,
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        tooltip: 'Poista', // Fallback until L10n updated
                      ),
                    ),
                  // Could add context menu icon here
                ],
              ),
              const Spacer(),
              Text(
                widget.execution.workflowName ?? l10n.defaultWorkflowTitle,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                widget.execution.id.substring(0, 8),
                style: theme.textTheme.bodySmall?.copyWith(
                  fontFamily: 'monospace',
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              const SizedBox(height: 8),
              if (_getCurrentStepName(widget.execution) != null ||
                  widget.execution.status == ExecutionStatus.running) ...[
                TweenAnimationBuilder<double>(
                  key: ValueKey(
                    widget.execution.id,
                  ), // Force reset animation on new execution
                  tween: Tween<double>(begin: 0, end: _cachedProgress),
                  duration: const Duration(milliseconds: 500),
                  builder:
                      (context, value, _) => LinearProgressIndicator(
                        value: value,
                        backgroundColor:
                            theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(2),
                        minHeight: 4,
                      ),
                ),
              ],
              const SizedBox(height: 8),
              Text(
                dateFormat.format(widget.execution.createdAt.toLocal()),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.outline,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getStatusLabel(AppLocalizations l10n, ExecutionStatus status) {
    switch (status) {
      case ExecutionStatus.completed:
        return l10n.statusCompleted;
      case ExecutionStatus.running:
        return l10n.statusRunning;
      case ExecutionStatus.failed:
        return l10n.statusFailed;
      case ExecutionStatus.rejected:
        return l10n.statusRejected;
      case ExecutionStatus.pending:
        return l10n.statusPending;
      case ExecutionStatus.started:
        return l10n.statusStarted;
      case ExecutionStatus.cancelling:
        return l10n.cancelling;
      case ExecutionStatus.interrupted:
        return l10n.unknownState;
      case ExecutionStatus.unknown:
        return l10n.unknownState;
    }
  }

  Color _getStatusColor(ExecutionStatus status) {
    switch (status) {
      case ExecutionStatus.running:
      case ExecutionStatus.started:
        return Colors.blue;
      case ExecutionStatus.completed:
        return Colors.green;
      case ExecutionStatus.failed:
      case ExecutionStatus.rejected:
        return Colors.red;
      case ExecutionStatus.cancelling:
      case ExecutionStatus.interrupted:
        return Colors.orange;
      case ExecutionStatus.pending:
      case ExecutionStatus.unknown:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(ExecutionStatus status) {
    switch (status) {
      case ExecutionStatus.running:
        return Icons.sync;
      case ExecutionStatus.started:
        return Icons.play_circle_outline;
      case ExecutionStatus.completed:
        return Icons.check_circle_outline;
      case ExecutionStatus.failed:
      case ExecutionStatus.rejected:
        return Icons.error_outline;
      case ExecutionStatus.cancelling:
      case ExecutionStatus.interrupted:
        return Icons.pause_circle_outline;
      case ExecutionStatus.pending:
        return Icons.hourglass_empty;
      case ExecutionStatus.unknown:
        return Icons.help_outline;
    }
  }

  String? _getCurrentStepName(Execution execution) {
    return execution.map(
      pending: (_) => null,
      started: (_) => null,
      running: (e) => e.currentStepName,
      completed: (e) => e.currentStepName,
      failed: (e) => e.currentStepName,
      rejected: (e) => e.currentStepName,
      interrupted: (e) => e.currentStepName,
      cancelling: (e) => e.currentStepName,
      unknown: (_) => null,
    );
  }

  double _calculateMonotonicProgress(Execution execution) {
    if (execution.status == ExecutionStatus.completed) return 1.0;
    if (execution.status == ExecutionStatus.pending) return 0.0;
    if (execution.status == ExecutionStatus.started) return 0.05;

    final currentStep = _getCurrentStepName(execution);
    if (currentStep == null) return 0.0; // Transient state

    // Approximate progress based on standard steps
    const steps = [
      'step_guard',
      'step_analyst',
      'step_interaction',
      'step_profiler',
      'step_panel',
      'step_archivist',
      'step_judge',
      'step_coach',
      'step_xai',
    ];

    int index = -1;
    // Try exact match
    index = steps.indexOf(currentStep);

    // Try fuzzy match
    if (index == -1) {
      final lower = currentStep.toLowerCase();
      for (int i = 0; i < steps.length; i++) {
        if (lower.contains(steps[i].replaceAll('step_', ''))) {
          index = i;
          break;
        }
      }
    }

    if (index != -1) {
      return (index + 1) / steps.length;
    }

    return 0.1; // Default running state for unknown steps
  }
}
