import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// A card widget that displays the current status of a DAG workflow execution.
/// It observes the [executionControllerProvider] to reactively update its UI
/// when polling the backend.
class ExecutionStatusCard extends ConsumerWidget {
  final String workflowId;
  final Map<String, dynamic> initialInputs;

  const ExecutionStatusCard({
    super.key,
    required this.workflowId,
    this.initialInputs = const {},
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final executionState = ref.watch(executionControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              l10n.defaultWorkflowTitle,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              l10n.executionTargetLabel(workflowId),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const Divider(),
            const SizedBox(height: 8),
            _buildStateContent(context, ref, executionState, l10n),
            const SizedBox(height: 16),
            _buildActionButtons(context, ref, executionState, l10n),
          ],
        ),
      ),
    );
  }

  Widget _buildStateContent(
    BuildContext context,
    WidgetRef ref,
    AsyncValue<Map<String, dynamic>?> state,
    AppLocalizations l10n,
  ) {
    return state.when(
      data: (record) {
        if (record == null) {
          return Text(l10n.waitingToStart);
        }

        final status = record['status'] as String? ?? 'UNKNOWN';
        final executionId = record['id'] as String? ?? 'N/A';

        // Assuming results exist if there are any
        final results = record['results'] as Map<String, dynamic>? ?? {};

        // Extract Metrics
        final cost = (record['cost_estimate'] as num?)?.toDouble() ?? 0.0;
        final totalT = record['total_tokens'] as int? ?? 0;
        final promptT = record['prompt_tokens'] as int? ?? 0;
        final completionT = record['completion_tokens'] as int? ?? 0;
        final cachedT = record['cached_tokens'] as int? ?? 0;
        final reasoningT = record['reasoning_tokens'] as int? ?? 0;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                _buildStatusIcon(status),
                const SizedBox(width: 8),
                Text(
                  status.toUpperCase(),
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: _getStatusColor(status),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              l10n.executionIdLabel(executionId),
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            if (totalT > 0 || cost > 0) ...[
              Text(
                l10n.executionMetricsTitle,
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 4),
              Text(l10n.executionTokensBreakdown(totalT, promptT, completionT)),
              if (cachedT > 0)
                Text(
                  l10n.executionTokensCached(cachedT),
                  style: const TextStyle(color: Colors.green),
                ),
              if (reasoningT > 0)
                Text(
                  l10n.executionTokensReasoning(reasoningT),
                  style: const TextStyle(color: Colors.deepPurple),
                ),
              Text(l10n.executionCostEstimate(cost.toStringAsFixed(6))),
              const SizedBox(height: 16),
            ],
            const SizedBox(height: 8),
            if (status == 'completed' || status == 'failed') ...[
              Text(
                l10n.resultsTitle,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  results.toString(),
                  style: Theme.of(
                    context,
                  ).textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
                ),
              ),
            ],
          ],
        );
      },
      loading:
          () => const Center(
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: CircularProgressIndicator(),
            ),
          ),
      error:
          (error, stackTrace) =>
              ErrorView(error: error, stackTrace: stackTrace, compact: true),
    );
  }

  Widget _buildActionButtons(
    BuildContext context,
    WidgetRef ref,
    AsyncValue<Map<String, dynamic>?> state,
    AppLocalizations l10n,
  ) {
    final isRunning =
        state.isLoading ||
        (state.hasValue &&
            state.value != null &&
            (state.value!['status'] == 'pending' ||
                state.value!['status'] == 'running'));

    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        if (state.hasValue && state.value != null)
          TextButton.icon(
            onPressed:
                isRunning
                    ? null
                    : () =>
                        ref
                            .read(executionControllerProvider.notifier)
                            .refreshStatus(),
            icon: const Icon(Icons.refresh),
            label: Text(l10n.refresh),
          ),
        const SizedBox(width: 8),
        FilledButton.icon(
          onPressed:
              isRunning
                  ? null
                  : () => ref
                      .read(executionControllerProvider.notifier)
                      .startExecution(workflowId, initialInputs),
          icon: const Icon(Icons.play_arrow),
          label: Text(l10n.startAiExecution),
        ),
      ],
    );
  }

  Widget _buildStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return const Icon(Icons.check_circle, color: Colors.green);
      case 'failed':
        return const Icon(Icons.error, color: Colors.red);
      case 'running':
      case 'pending':
        return const SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      default:
        return const Icon(Icons.help_outline, color: Colors.grey);
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'running':
      case 'pending':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }
}
