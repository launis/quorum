import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

/// A compact row representing a single execution in a list layout.
class ExecutionListItem extends StatelessWidget {
  const ExecutionListItem({super.key, required this.execution});

  final Execution execution;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).toString();
    final dateFormat = DateFormat.MMMd(locale).add_Hm();
    final statusColor = _getStatusColor(execution.status);

    return ListTile(
      onTap: () {
        if (execution.status == ExecutionStatus.completed) {
          context.go('/dashboard/executions/${execution.id}/report');
        } else {
          context.go('/dashboard/executions/${execution.id}/monitor');
        }
      },
      leading: CircleAvatar(
        backgroundColor: statusColor.withValues(alpha: 0.1),
        child: Icon(
          _getStatusIcon(execution.status),
          color: statusColor,
          size: 20,
        ),
      ),
      title: Text(
        execution.workflowName ??
            l10n.executionIdLabel(execution.id.substring(0, 6)),
        style: theme.textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.w600,
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: _buildSubtitle(context, l10n),
      trailing: Text(
        dateFormat.format(execution.createdAt.toLocal()),
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }

  Widget _buildSubtitle(BuildContext context, AppLocalizations l10n) {
    final stepName = _getCurrentStepName(execution);
    if (stepName != null) {
      return Text(l10n.stepLabel(stepName));
    }
    return Text(
      _getStatusLabel(l10n, execution.status),
      style: const TextStyle(fontSize: 10), // Tiny generic label
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
        return l10n.unknownState; // Using unknown as fallback or add new key
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
