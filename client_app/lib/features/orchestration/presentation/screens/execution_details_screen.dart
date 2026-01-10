import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/result_dashboard.dart';
import 'package:intl/intl.dart';

class ExecutionDetailsScreen extends ConsumerWidget {
  final String executionId;

  const ExecutionDetailsScreen({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncExecution = ref.watch(executionStreamProvider(executionId));
    final l10n = AppLocalizations.of(context)!;

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            '${l10n.executionDetails}: ${executionId.substring(0, 8)}...',
          ),
          bottom: TabBar(
            tabs: [
              Tab(text: l10n.overview),
              Tab(text: l10n.report),
              Tab(text: l10n.rawData),
            ],
          ),
          actions: [
            // Download Action (Mock/Future)
            IconButton(
              icon: const Icon(Icons.download),
              tooltip: 'Download PDF',
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(l10n.downloadNotImplemented)),
                );
              },
            ),
          ],
        ),
        body: asyncExecution.when(
          data:
              (execution) => TabBarView(
                children: [
                  _OverviewTab(execution: execution),
                  _ReportTab(execution: execution),
                  _RawDataTab(execution: execution),
                ],
              ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error:
              (err, stack) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error, color: Colors.red, size: 48),
                    const SizedBox(height: 16),
                    Text(l10n.failedToLoad('$err')),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed:
                          () => ref.invalidate(
                            executionStreamProvider(executionId),
                          ),
                      child: Text(l10n.retry),
                    ),
                  ],
                ),
              ),
        ),
      ),
    );
  }
}

class _OverviewTab extends StatelessWidget {
  final Execution execution;

  const _OverviewTab({required this.execution});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    String statusText = execution.status.name.toUpperCase();
    // Optional: map to localized status if needed, or keep technical uppercase
    if (execution.status == ExecutionStatus.completed) {
      statusText = l10n.statusCompleted;
    }
    if (execution.status == ExecutionStatus.running) {
      statusText = l10n.statusRunning;
    }
    if (execution.status == ExecutionStatus.failed) {
      statusText = l10n.statusFailed;
    }
    if (execution.status == ExecutionStatus.rejected) {
      statusText = l10n.statusRejected;
    }
    if (execution.status == ExecutionStatus.pending) {
      statusText = l10n.statusPending;
    }
    if (execution.status == ExecutionStatus.started) {
      statusText = l10n.statusStarted;
    }

    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        // Status Card
        Card(
          color: _getStatusColor(execution.status).withValues(alpha: 0.1),
          child: ListTile(
            leading: Icon(
              _getStatusIcon(execution.status),
              color: _getStatusColor(execution.status),
              size: 32,
            ),
            title: Text(
              statusText,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle:
                execution.currentStepName != null
                    ? Text(l10n.currentStep(execution.currentStepName!))
                    : null,
          ),
        ),
        const SizedBox(height: 16),

        // Timeline
        Text(l10n.timeline, style: theme.textTheme.titleMedium),
        const Divider(),
        _infoRow(
          l10n.created,
          DateFormat.yMMMd(
            Localizations.localeOf(context).toString(),
          ).add_jms().format(execution.createdAt),
        ),

        // Assuming we default to None for missing times in MVP
        // If Model had startedAt/finishedAt we'd show them.
        const SizedBox(height: 24),

        // Steps Progress
        Text(l10n.workflowProgress, style: theme.textTheme.titleMedium),
        const SizedBox(height: 8),
        _StepProgressList(currentStep: execution.currentStepName),
      ],
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value),
        ],
      ),
    );
  }

  Color _getStatusColor(ExecutionStatus status) {
    return switch (status) {
      ExecutionStatus.completed => Colors.green,
      ExecutionStatus.running => Colors.blue,
      ExecutionStatus.failed || ExecutionStatus.rejected => Colors.red,
      _ => Colors.grey,
    };
  }

  IconData _getStatusIcon(ExecutionStatus status) {
    return switch (status) {
      ExecutionStatus.completed => Icons.check_circle,
      ExecutionStatus.running => Icons.sync,
      ExecutionStatus.failed || ExecutionStatus.rejected => Icons.error,
      _ => Icons.hourglass_empty,
    };
  }
}

class _StepProgressList extends StatelessWidget {
  final String? currentStep;

  const _StepProgressList({this.currentStep});

  static const steps = [
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

  static const stepNames = {
    'step_guard': 'Guard Agent (Safety)',
    'step_analyst': 'Analyst Agent (Research)',
    'step_interaction': 'Interaction Analyst',
    'step_profiler': 'Profiler Agent',
    'step_panel': 'Panel Audit (Parallel)',
    'step_archivist': 'Archivist (History)',
    'step_judge': 'Judge (Verdict)',
    'step_coach': 'Coach (Feedback)',
    'step_xai': 'Reporter (Final Report)',
    'init': 'Initializing...',
  };

  @override
  Widget build(BuildContext context) {
    // Determine current index
    int currentIndex = -1;
    if (currentStep != null) {
      currentIndex = steps.indexOf(currentStep!);
    }
    // If completed/unknown or not in list
    if (currentIndex == -1 && currentStep == 'completed') {
      currentIndex = steps.length;
    }

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: steps.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final stepKey = steps[index];
          final stepLabel = stepNames[stepKey] ?? stepKey;

          bool isCompleted = index < currentIndex;
          bool isCurrent = index == currentIndex;

          // If we receive 'completed' step, everything is done
          if (currentStep == null) {
            // Maybe completed? depend on parent status.
            // But here we rely on name.
          }

          return ListTile(
            dense: true,
            leading: _buildStepIcon(isCompleted, isCurrent),
            title: Text(
              stepLabel,
              style: TextStyle(
                fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                color: isCurrent ? Theme.of(context).primaryColor : null,
              ),
            ),
            trailing:
                isCurrent
                    ? const SizedBox(
                      width: 12,
                      height: 12,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                    : null,
          );
        },
      ),
    );
  }

  Widget _buildStepIcon(bool isCompleted, bool isCurrent) {
    if (isCompleted) {
      return const Icon(Icons.check_circle, color: Colors.green, size: 20);
    }
    if (isCurrent) {
      return const Icon(Icons.play_circle_fill, color: Colors.blue, size: 20);
    }
    return const Icon(
      Icons.radio_button_unchecked,
      color: Colors.grey,
      size: 20,
    );
  }
}

class _ReportTab extends StatelessWidget {
  final Execution execution;

  const _ReportTab({required this.execution});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    if (execution.status == ExecutionStatus.running ||
        execution.status == ExecutionStatus.pending ||
        execution.status == ExecutionStatus.started) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              l10n.analysisInProgress,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(l10n.currentStep(execution.currentStepName ?? 'Initializing')),
          ],
        ),
      );
    }

    return execution.map(
      pending: (_) => Center(child: Text(l10n.waitingToStart)),
      started: (_) => Center(child: Text(l10n.executionStarted)),
      running: (_) => const SizedBox.shrink(),
      completed:
          (data) => ResultDashboard(execution: data), // Use new Dashboard
      failed:
          (data) => Center(
            child: Text(
              l10n.executionFailed('${data.error}'),
              style: const TextStyle(color: Colors.red),
            ),
          ),
      unknown: (_) => Center(child: Text(l10n.unknownState)),
    );
  }
}

class _RawDataTab extends StatelessWidget {
  final Execution execution;

  const _RawDataTab({required this.execution});

  @override
  Widget build(BuildContext context) {
    // Sanitize inputs and results to avoid dumping massive text files
    final safeInputs = _sanitizeMap(execution.inputs);
    final safeResult = execution.mapOrNull(
      completed: (c) => _sanitizeMap(c.result),
      failed: (f) => {'error': f.error},
    );

    final content = {
      'id': execution.id,
      'status': execution.status.name,
      'inputs': safeInputs,
      'result': safeResult,
    };

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: SelectableText(
        _prettyPrint(content),
        style: const TextStyle(fontFamily: 'monospace'),
      ),
    );
  }

  Map<String, dynamic> _sanitizeMap(Map<String, dynamic> map) {
    if (map.isEmpty) return map;
    return map.map((key, value) {
      if (value is String && value.length > 200) {
        return MapEntry(key, '<Content truncated: ${value.length} chars>');
      }
      return MapEntry(key, value);
    });
  }

  String _prettyPrint(Map<String, dynamic> json) {
    var str = json.toString();
    // Simple naive formatting for MVP
    str = str.replaceAll(',', ',\n  ');
    str = str.replaceAll('{', '{\n  ');
    str = str.replaceAll('}', '\n}');
    return str;
  }
}
