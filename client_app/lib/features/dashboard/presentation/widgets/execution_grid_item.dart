import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

/// A card representing a single execution in a grid layout.
class ExecutionGridItem extends StatelessWidget {
  const ExecutionGridItem({super.key, required this.execution});

  final Execution execution;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).toString();
    final dateFormat = DateFormat.yMMMd(locale).add_Hm();
    final statusColor = _getStatusColor(execution.status);

    return Card(
      clipBehavior: Clip.antiAlias,
      elevation: 2,
      child: InkWell(
        onTap: () {
          if (execution.status == ExecutionStatus.completed) {
            context.go('/dashboard/executions/${execution.id}/report');
          } else {
            context.go('/dashboard/executions/${execution.id}/monitor');
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
                          _getStatusIcon(execution.status),
                          size: 14,
                          color: statusColor,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _getStatusLabel(l10n, execution.status),
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: statusColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Could add context menu icon here
                ],
              ),
              const Spacer(),
              Text(
                execution.workflowName ?? l10n.defaultWorkflowTitle,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                execution.id.substring(0, 8),
                style: theme.textTheme.bodySmall?.copyWith(
                  fontFamily: 'monospace',
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              if (_getCurrentStepName(execution) != null) ...[
                Text(
                  l10n.stepLabel(_getCurrentStepName(execution)!),
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              const SizedBox(height: 8),
              Text(
                dateFormat.format(execution.createdAt),
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
      unknown: (_) => null,
    );
  }
}
