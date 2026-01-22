import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

class ExecutionMonitorScreen extends ConsumerWidget {
  final String executionId;

  const ExecutionMonitorScreen({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncExecution = ref.watch(executionStreamProvider(executionId));
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.monitorTitle(executionId.substring(0, 8))),
      ),
      body: asyncExecution.when(
        data: (execution) {
          // Auto-redirect if completed
          if (execution.status == ExecutionStatus.completed) {
            // We use a post-frame callback or simple logic to show a prominent button.
            // Direct navigation might be jarring if user is reading logs.
            // Let's show a FAB or banner.
          }
          return _MonitorView(execution: execution);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error:
            (err, stack) =>
                Center(child: Text(l10n.failedToLoad(err.toString()))),
      ),
      floatingActionButton:
          asyncExecution.asData?.value.status == ExecutionStatus.completed
              ? FloatingActionButton.extended(
                onPressed:
                    () =>
                        context.go('/dashboard/executions/$executionId/report'),
                label: Text(l10n.viewResults),
                icon: const Icon(Icons.arrow_forward),
                backgroundColor: Colors.green,
              )
              : null,
    );
  }
}

class _MonitorView extends StatelessWidget {
  final Execution execution;

  const _MonitorView({required this.execution});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    final isRunning = execution.status == ExecutionStatus.running;
    final isCompleted = execution.status == ExecutionStatus.completed;

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1000),
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            // Status Card
            Card(
              color: _getStatusColor(execution.status).withValues(alpha: 0.1),
              child: ListTile(
                leading:
                    isRunning
                        ? SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 3,
                            color: _getStatusColor(execution.status),
                          ),
                        )
                        : Icon(
                          _getStatusIcon(execution.status),
                          color: _getStatusColor(execution.status),
                          size: 32,
                        ),
                title: Text(
                  execution.status.name
                      .toUpperCase(), // Enum names remain tech-focused, or could map too
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle:
                    execution.currentStepName != null
                        ? Text(l10n.stepLabel(execution.currentStepName!))
                        : null,
              ),
            ),
            if (isCompleted) ...[
              const SizedBox(height: 16),
              _CompletionBanner(executionId: execution.id),
            ],
            const SizedBox(height: 16),

            // Timeline
            Text(l10n.timeline, style: theme.textTheme.titleMedium),
            const Divider(),
            _infoRow(
              l10n.created,
              DateFormat('yyyy-MM-dd HH:mm:ss').format(execution.createdAt.toLocal()),
            ),
            const SizedBox(height: 24),

            // Steps Progress
            Text(l10n.workflowProgress, style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            _StepProgressList(
              currentStep: execution.currentStepName,
              workflowId: execution.workflowName,
              status: execution.status,
            ),

            // Hint for raw data
            const SizedBox(height: 32),
            Center(
              child: TextButton.icon(
                icon: const Icon(Icons.code),
                label: Text(l10n.viewRawDataComingSoon),
                onPressed: () {
                  // Placeholder for raw data modal or route
                },
              ),
            ),
          ],
        ),
      ),
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

class _CompletionBanner extends StatelessWidget {
  final String executionId;

  const _CompletionBanner({required this.executionId});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.withValues(alpha: 0.5)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.green),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  l10n.analysisCompletedSuccess,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Colors.green,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed:
                  () => context.go('/dashboard/executions/$executionId/report'),
              icon: const Icon(Icons.visibility),
              label: Text(l10n.viewFullReport),
              style: FilledButton.styleFrom(backgroundColor: Colors.green),
            ),
          ),
        ],
      ),
    );
  }
}

class _StepProgressList extends StatelessWidget {
  final String? currentStep;
  final String? workflowId;
  final ExecutionStatus status;

  const _StepProgressList({
    this.currentStep,
    this.workflowId,
    required this.status,
  });



  static const _stepsSequential = [
    'step_guard',
    'step_analyst',
    'step_interaction',
    'step_profiler',
    'step_logician',
    'step_falsifier',
    'step_causal',
    'step_detector',
    'step_overseer',
    'step_archivist',
    'step_judge',
    'step_judge_cognitive',
    'step_coach',
    'step_context',
    'step_xai',
  ];

  static const _stepsFused = [
    'step_guard',
    'step_analyst',
    'step_interaction',
    'step_profiler',
    'step_panel',
    'step_archivist',
    'step_judge',
    'step_coach',
    'step_context',
    'step_xai',
  ];

  // Specific mappings for known workflows
  static const Map<String, List<String>> _workflowSteps = {
    'sequential_audit_chain_dual': _stepsSequential,
    'fused_audit_chain_dual': _stepsFused,
    'fused_audit_chain_cognitive': _stepsFused, // Uses same structure
    'simple_audit': ['step_guard', 'step_analyst', 'step_judge', 'step_xai'],
  };

  String _getStepLabel(BuildContext context, String stepKey) {
    final l10n = AppLocalizations.of(context)!;
    return switch (stepKey) {
      'step_guard' => l10n.stepGuard,
      'step_analyst' => l10n.stepAnalyst,
      'step_interaction' => l10n.stepInteraction,
      'step_profiler' => l10n.stepProfiler,
      'step_panel' => l10n.stepPanel,
      'step_archivist' => l10n.stepArchivist,
      'step_judge' => l10n.stepJudge,
      'step_coach' => l10n.stepCoach,
      'step_xai' => l10n.stepXai,
      'step_logician' => l10n.stepLogician,
      'step_falsifier' => l10n.stepFalsifier,
      'step_causal' => l10n.stepCausal,
      'step_detector' => l10n.stepDetector,
      'step_overseer' => l10n.stepOverseer,
      'step_judge_cognitive' => l10n.stepJudgeCognitive,
      'step_context' => l10n.stepContext,
      'init' => l10n.stepInitializing,
      _ => stepKey,
    };
  }

  @override
  Widget build(BuildContext context) {
    // Determine which list to use
    List<String> steps;
    if (workflowId != null && _workflowSteps.containsKey(workflowId)) {
        steps = _workflowSteps[workflowId]!;
    } else {
        // Fallback heuristics
        final lowerId = workflowId?.toLowerCase() ?? '';
        final isFused = lowerId.contains('fused') || lowerId.contains('panel') || lowerId.contains('courtroom');
        steps = isFused ? _stepsFused : _stepsSequential;
    }
    
    int currentIndex = -1;
    if (currentStep != null) {
      // 1. Try exact match
      currentIndex = steps.indexOf(currentStep!);

      // 2. Try fuzzy / value match if exact failed
      if (currentIndex == -1) {
        // Reverse lookup: check if currentStep matches any of the values in stepNames
        // or partial contains - now using backend keys
        final lowerStep = currentStep!.toLowerCase();
        
        // MAPPING FOR FUSED VIEW:
        // If we are in Fused mode, map "integrated" steps to 'step_panel'
        // (Only if step_panel is actually in the list!)
        if (steps.contains('step_panel')) {
           if (lowerStep.contains('logician') || // Logician is fused into Panel in Fused workflow
               lowerStep.contains('falsifier') || 
               lowerStep.contains('causal') ||
               lowerStep.contains('detector')) {
               currentIndex = steps.indexOf('step_panel');
           }
        }


        if (currentIndex == -1) {
            for (int i = 0; i < steps.length; i++) {
              final key = steps[i];
              // Check normalized key
              if (key == lowerStep || 'step_$lowerStep' == key) {
                currentIndex = i;
                break;
              }
    
              // Specific backend mappings (common ones)
              if (lowerStep.contains('guard') && key == 'step_guard') {
                currentIndex = i;
              }
              // Skip Analyst/Interaction/Profiler checks here if they were already mapped above for Fused
              
              if (lowerStep.contains('panel') && key == 'step_panel') {
                currentIndex = i;
              }
              if (lowerStep.contains('judge') && key == 'step_judge') {
                currentIndex = i;
              }
              if (lowerStep.contains('xai') && key == 'step_xai') {
                currentIndex = i;
              }
    
              if (currentIndex != -1) break;
            }
        }
      }
    }

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: steps.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final stepKey = steps[index];
          final stepLabel = _getStepLabel(context, stepKey);

          // Steps before current index are completed
          bool isCompleted = index < currentIndex;
          // Current step is the one matching index (if running/pending)
          bool isCurrent =
              index == currentIndex && status != ExecutionStatus.completed;

          // Visually, if completed, ALL are completed
          if (status == ExecutionStatus.completed) {
            isCompleted = true;
            isCurrent = false;
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
