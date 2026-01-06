import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_providers.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

/// The main dashboard screen displaying a list of recent executions.
///
/// This screen strictly follows the System Mandate (2026):
/// - Uses [ConsumerWidget] for Riverpod integration.
/// - Watches [dashboardControllerProvider] for state.
/// - Handles [AsyncValue] states (loading, error, data).
/// - Implements Material 3 design via [Scaffold] and [Card].
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncExecutions = ref.watch(dashboardControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Orchestration Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed:
                () =>
                    ref
                        .read(dashboardControllerProvider.notifier)
                        .refreshList(),
          ),
        ],
      ),
      body: asyncExecutions.when(
        data: (executions) {
          if (executions.isEmpty) {
            return const Center(child: Text('No executions found.'));
          }
          return ListView.separated(
            itemCount: executions.length,
            separatorBuilder: (context, index) => const SizedBox(height: 8),
            padding: const EdgeInsets.all(16),
            itemBuilder: (context, index) {
              final execution = executions[index];
              return _ExecutionCard(execution: execution);
            },
          );
        },
        error:
            (error, stack) => Center(
              child: Card(
                margin: const EdgeInsets.all(16),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        color: Colors.red,
                        size: 48,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Failed to load executions',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(error.toString(), textAlign: TextAlign.center),
                      const SizedBox(height: 16),
                      FilledButton.icon(
                        onPressed:
                            () =>
                                ref
                                    .read(dashboardControllerProvider.notifier)
                                    .refreshList(),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

/// A Material 3 Card representing a single [Execution].
///
/// Displays:
/// - Status indicator (color-coded).
/// - Execution ID/Title.
/// - Current Step Name (if running) or Status text.
/// - Created timestamp.
class _ExecutionCard extends StatelessWidget {
  const _ExecutionCard({required this.execution});

  final Execution execution;

  Color _getStatusColor(ExecutionStatus status) {
    switch (status) {
      case ExecutionStatus.running:
        return Colors.blue;
      case ExecutionStatus.completed:
        return Colors.green;
      case ExecutionStatus.failed:
        return Colors.red;
      case ExecutionStatus.pending:
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final statusColor = _getStatusColor(execution.status);
    final dateFormat = DateFormat.yMMMd().add_Hm();

    return Card(
      clipBehavior: Clip.antiAlias,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: statusColor.withValues(alpha: 0.2),
          child: Icon(
            _getStatusIcon(execution.status),
            color: statusColor,
            size: 20,
          ),
        ),
        title: Text(
          execution.id, // Using ID as title for now, maybe inputs['name'] later
          style: theme.textTheme.titleSmall?.copyWith(
            fontFamily:
                'Inter', // Enforcing Inter as per mandate (handled by theme globally usually but good to know)
            fontWeight: FontWeight.bold,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_getCurrentStepName(execution) != null)
              Text(
                'Step: ${_getCurrentStepName(execution)}',
                style: theme.textTheme.bodySmall,
              )
            else
              Text(
                execution.status.name.toUpperCase(),
                style: theme.textTheme.labelSmall?.copyWith(letterSpacing: 0.5),
              ),
          ],
        ),
        trailing: Text(
          dateFormat.format(execution.createdAt),
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        onTap: () {
          context.go('/dashboard/executions/${execution.id}');
        },
      ),
    );
  }

  IconData _getStatusIcon(ExecutionStatus status) {
    switch (status) {
      case ExecutionStatus.running:
        return Icons.sync;
      case ExecutionStatus.completed:
        return Icons.check;
      case ExecutionStatus.failed:
        return Icons.error_outline;
      case ExecutionStatus.pending:
        return Icons.hourglass_empty;
      case ExecutionStatus.unknown:
        return Icons.help_outline;
    }
  }

  String? _getCurrentStepName(Execution execution) {
    return execution.map(
      pending: (_) => null,
      running: (e) => e.currentStepName,
      completed: (e) => e.currentStepName,
      failed: (e) => e.currentStepName,
      unknown: (_) => null,
    );
  }
}
