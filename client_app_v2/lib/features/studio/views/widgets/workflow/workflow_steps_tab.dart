import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:uuid/uuid.dart';
import 'workflow_step_card.dart';

/// **WorkflowStepsTab**
///
/// Componentized UI widget representing Tab 3 of the Workflow Builder.
/// Handles the mapping, ordering, and visualization of execution steps.
class WorkflowStepsTab extends StatelessWidget {
  final Workflow workflow;
  final List<NodeStrategy> blueprints;
  final List<McpGateway> mcpGateways;
  final Function(Workflow) onChanged;

  const WorkflowStepsTab({
    super.key,
    required this.workflow,
    required this.blueprints,
    required this.mcpGateways,
    required this.onChanged,
  });

  int _findFirstZoneCIndex(List<StepRule> steps) {
    for (int i = 1; i < steps.length; i++) {
      final step = steps[i];
      final bp = blueprints
          .where((b) => b.id == step.taskBlueprint)
          .firstOrNull;
      if (bp != null && bp.isSystemCore) {
        return i;
      }
    }
    return -1;
  }

  void _addStep() {
    final steps = List<StepRule>.from(workflow.steps);
    final uuidHex = const Uuid().v4().replaceAll('-', '');
    final newId =
        'sr_${uuidHex.length >= 16 ? uuidHex.substring(0, 16) : uuidHex.padRight(16, '0')}';
    final newStep = StepRule(
      id: newId,
      taskBlueprint: '',
      dependsOn: steps.isNotEmpty ? [steps.first.id] : const <String>[],
      inputMappings: const {},
      isSynthesisSource: true,
    );

    final zoneCIndex = _findFirstZoneCIndex(steps);
    if (zoneCIndex != -1) {
      steps.insert(zoneCIndex, newStep);
      final zoneCStep = steps[zoneCIndex + 1];
      if (!zoneCStep.dependsOn.contains(newId)) {
        final updatedDependsOn = List<String>.from(zoneCStep.dependsOn)
          ..add(newId);
        steps[zoneCIndex + 1] = zoneCStep.copyWith(dependsOn: updatedDependsOn);
      }
    } else {
      steps.add(newStep);
    }
    onChanged(workflow.copyWith(steps: steps));
  }

  void _copyStep(int index) {
    final steps = List<StepRule>.from(workflow.steps);
    if (index < 0 || index >= steps.length) return;

    final original = steps[index];
    final uuidHex = const Uuid().v4().replaceAll('-', '');
    final clonedId =
        'sr_${uuidHex.length >= 16 ? uuidHex.substring(0, 16) : uuidHex.padRight(16, '0')}';
    final clonedStep = original.copyWith(id: clonedId);

    steps.insert(index + 1, clonedStep);

    final zoneCIndex = _findFirstZoneCIndex(steps);
    if (zoneCIndex != -1) {
      final zoneCStep = steps[zoneCIndex];
      if (!zoneCStep.dependsOn.contains(clonedId)) {
        final updatedDependsOn = List<String>.from(zoneCStep.dependsOn)
          ..add(clonedId);
        steps[zoneCIndex] = zoneCStep.copyWith(dependsOn: updatedDependsOn);
      }
    }
    onChanged(workflow.copyWith(steps: steps));
  }

  void _deleteStep(int index) {
    final steps = List<StepRule>.from(workflow.steps);
    if (index < 0 || index >= steps.length) return;

    final deletedId = steps[index].id;
    steps.removeAt(index);

    final stepTargetPrefix = '\$steps.$deletedId';
    final stepTargetSubPrefix = '\$steps.$deletedId.';

    final cleanedSteps = steps.map((step) {
      final newDependsOn = step.dependsOn
          .where((id) => id != deletedId)
          .toList();
      final newMappings = Map<String, String>.fromEntries(
        step.inputMappings.entries.where((e) {
          final val = e.value;
          return val != stepTargetPrefix &&
              !val.startsWith(stepTargetSubPrefix);
        }),
      );
      final newCausalId = step.causalSourceStepId == deletedId
          ? null
          : step.causalSourceStepId;

      return step.copyWith(
        dependsOn: newDependsOn,
        inputMappings: newMappings,
        causalSourceStepId: newCausalId,
      );
    }).toList();

    onChanged(workflow.copyWith(steps: cleanedSteps));
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final allSteps = List<StepRule>.from(workflow.steps);

    return SingleChildScrollView(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.studioWorkflowStepsDependencies,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
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
            AppSpacing.h16,
            if (allSteps.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.s24),
                  child: Text(
                    l10n.studioWorkflowStepsEmpty,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
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
                onCopy: () => _copyStep(entry.key),
                onDelete: () => _deleteStep(entry.key),
              );
            }),
          ],
        ),
      ),
    );
  }
}
