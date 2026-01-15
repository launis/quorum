import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/result_dashboard.dart';
import 'package:go_router/go_router.dart';

class ExecutionResultScreen extends ConsumerWidget {
  final String executionId;

  const ExecutionResultScreen({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // We assume the user shouldn't be here if it's running,
    // but we can still watch it. Logically we might not need polling here,
    // but executionStreamProvider handles it.
    final asyncExecution = ref.watch(executionStreamProvider(executionId));
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.resultsTitle),
        actions: [
          IconButton(
            onPressed:
                () => context.go('/dashboard/executions/$executionId/monitor'),
            icon: const Icon(Icons.history),
            tooltip: l10n.viewLogTooltip,
          ),
          IconButton(
            onPressed:
                () => context.go('/dashboard/executions/$executionId/details'),
            icon: const Icon(Icons.code),
            tooltip: l10n.rawData,
          ),
          IconButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(l10n.downloadNotImplementedPdf)),
              );
            },
            icon: const Icon(Icons.download),
            tooltip: l10n.downloadReportTooltip,
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: asyncExecution.when(
            data: (execution) {
              if (execution is ExecutionCompleted) {
                return ResultDashboard(execution: execution);
              } else {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(l10n.analysisNotComplete),
                      const SizedBox(height: 16),
                      FilledButton.icon(
                        onPressed:
                            () => context.go(
                              '/dashboard/executions/$executionId/monitor',
                            ),
                        icon: const Icon(Icons.visibility),
                        label: Text(l10n.goToMonitor),
                      ),
                    ],
                  ),
                );
              }
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error:
                (err, stack) => Center(child: Text(l10n.failedToLoad('$err'))),
          ),
        ),
      ),
    );
  }
}
