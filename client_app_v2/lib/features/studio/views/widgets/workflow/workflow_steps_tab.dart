import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import '../../../../../utils/safe_cast.dart';
import 'workflow_step_card.dart';

/// **WorkflowStepsTab**
///
/// Componentized UI widget representing Tab 3 of the Workflow Builder.
/// Handles the mapping, ordering, and visualization of execution steps.
class WorkflowStepsTab extends StatelessWidget {
  final Map<String, dynamic> workflow;
  final List<Map<String, dynamic>> blueprints;
  final List<Map<String, dynamic>> mcpGateways;
  final VoidCallback onChanged;

  const WorkflowStepsTab({
    super.key,
    required this.workflow,
    required this.blueprints,
    required this.mcpGateways,
    required this.onChanged,
  });

  void _addStep() {
    final steps = SafeCast.safeList(workflow['steps']);
    steps.add({
      'id': 'step_${DateTime.now().millisecondsSinceEpoch}',
      'task_blueprint': '',
      'depends_on': <String>[],
      'input_mappings': <String, dynamic>{'inputs': '\$inputs'},
      'allowed_mcp_tools': <String>[],
    });
    workflow['steps'] = steps;
    onChanged();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final allSteps =
        SafeCast.safeList(
          workflow['steps'],
        ).map((s) => SafeCast.safeMap(s)).toList();

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
            SizedBox(height: 16),
            if (allSteps.isEmpty)
              Center(
                child: Padding(
                  padding: EdgeInsets.all(32.0),
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
                l10n: l10n,
                onChanged: () {
                  allSteps[entry.key] = entry.value;
                  workflow['steps'] = allSteps;
                  onChanged();
                },
                onDelete: () {
                  allSteps.removeAt(entry.key);
                  workflow['steps'] = allSteps;
                  onChanged();
                },
              );
            }),
          ],
        ),
      ),
    );
  }
}
