import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'workflow_step_card.dart';

/// **WorkflowStepsTab**
///
/// Componentized UI widget representing Tab 3 of the Workflow Builder.
/// Handles the mapping, ordering, and visualization of execution steps.
class WorkflowStepsTab extends StatelessWidget {
  final Workflow workflow;
  final List<NodeStrategy> blueprints;
  final List<Map<String, dynamic>> mcpGateways;
  final Function(Workflow) onChanged;

  const WorkflowStepsTab({
    super.key,
    required this.workflow,
    required this.blueprints,
    required this.mcpGateways,
    required this.onChanged,
  });

  void _addStep() {
    final steps = List<StepRule>.from(workflow.steps);
    steps.add(
      StepRule(
        id: 'step_${DateTime.now().millisecondsSinceEpoch}',
        taskBlueprint: '',
        dependsOn: const [],
        inputMappings: const {'inputs': r'$inputs'},
      ),
    );
    onChanged(workflow.copyWith(steps: steps));
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final allSteps = List<StepRule>.from(workflow.steps);

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.studioWorkflowStepsDependencies,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: _addStep,
                  icon: const Icon(Icons.add),
                  label: Text(l10n.studioWorkflowAddStepNodeBtn),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (allSteps.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(32.0),
                  child: Text(
                    l10n.studioWorkflowStepsEmpty,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ),
            ...allSteps.asMap().entries.map((entry) {
              return WorkflowStepCard(
                index: entry.key,
                stepDef: entry.value,
                blueprints: blueprints,
                allSteps: allSteps,
                mcpGateways: mcpGateways,
                globalWorkflowInputs: workflow.expectedInputs,
                l10n: l10n,
                onChanged: (updatedStep) {
                  final newSteps = List<StepRule>.from(allSteps);
                  newSteps[entry.key] = updatedStep;
                  onChanged(workflow.copyWith(steps: newSteps));
                },
                onDelete: () {
                  final newSteps = List<StepRule>.from(allSteps);
                  newSteps.removeAt(entry.key);
                  onChanged(workflow.copyWith(steps: newSteps));
                },
              );
            }),
          ],
        ),
      ),
    );
  }
}
