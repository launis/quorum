import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_details_provider.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/result_dashboard.dart';
import 'package:go_router/go_router.dart';

class ExecutionResultScreen extends ConsumerWidget {
  final String executionId;

  const ExecutionResultScreen({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // We assume the user shouldn't be here if it's running,
    // but we can still watch it. Logically we might not need polling here,
    // but executionDetailsProvider handles it.
    final asyncExecution = ref.watch(executionDetailsProvider(executionId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Results'),
        actions: [
          IconButton(
            onPressed:
                () => context.go('/dashboard/executions/$executionId/monitor'),
            icon: const Icon(Icons.history),
            tooltip: 'View Execution Log',
          ),
          IconButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Download PDF not implemented yet'),
                ),
              );
            },
            icon: const Icon(Icons.download),
            tooltip: 'Download Report',
          ),
        ],
      ),
      body: asyncExecution.when(
        data: (execution) {
          if (execution is ExecutionCompleted) {
            return ResultDashboard(execution: execution);
          } else {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Analysis is not complete yet.'),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed:
                        () => context.go(
                          '/dashboard/executions/$executionId/monitor',
                        ),
                    icon: const Icon(Icons.visibility),
                    label: const Text('Go to Monitor'),
                  ),
                ],
              ),
            );
          }
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Error: $err')),
      ),
    );
  }
}
