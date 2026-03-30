import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/workflow.dart';

class InspectorPane extends StatelessWidget {
  final String? selectedStepId;
  final Workflow workflow;
  final List<NodeStrategy> availableBlueprints;
  final Function(String stepId, StepRule updatedStep) onStepUpdated;
  final VoidCallback onAddStep;
  final Function(String stepId) onDeleteStep;

  const InspectorPane({
    super.key,
    required this.selectedStepId,
    required this.workflow,
    required this.availableBlueprints,
    required this.onStepUpdated,
    required this.onAddStep,
    required this.onDeleteStep,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    if (selectedStepId == null) {
      return Container(
        width: 350,
        color: Theme.of(context).cardColor,
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'Inspector',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            Spacer(),
            Text(
              'Select a node to inspect',
              style: TextStyle(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: FilledButton.icon(
                onPressed: onAddStep,
                icon: const Icon(Icons.add),
                label: Text(l10n.studioWorkflowAddStepNodeBtn),
              ),
            ),
          ],
        ),
      );
    }

    final steps = workflow.steps;
    final stepDef = steps.firstWhere(
      (s) => s.id == selectedStepId,
      orElse: () => const StepRule(id: '', taskBlueprint: ''),
    );

    if (stepDef.id.isEmpty) {
      throw AppException.validation(
        'Selected step definition not found: $selectedStepId. Data is corrupted.',
      );
    }

    return Container(
      width: 350,
      color: Theme.of(context).cardColor,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Node Inspector',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: Icon(
                    Icons.delete,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  onPressed: () => onDeleteStep(selectedStepId!),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: _buildInspectorForm(context, stepDef, l10n),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInspectorForm(
    BuildContext context,
    StepRule stepDef,
    AppLocalizations l10n,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (stepDef.id.isNotEmpty) ...[
          Text(
            'Node ID',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          SelectableText(
            stepDef.id,
            style: const TextStyle(fontFamily: 'monospace'),
          ),
          const SizedBox(height: 16),
        ],
        DropdownButtonFormField<String>(
          decoration: const InputDecoration(
            labelText: 'Task Blueprint',
            isDense: true,
          ),
          isExpanded: true,
          initialValue:
              availableBlueprints.any((bp) => bp.id == stepDef.taskBlueprint)
              ? stepDef.taskBlueprint
              : null,
          items: availableBlueprints.map((bp) {
            final id = bp.id;

            // Nomenclature Resolution: Fetch based on locale, fallback to 'en', then id.
            final currentLocale = Localizations.localeOf(context).languageCode;
            final label =
                bp.name.translations[currentLocale] ??
                bp.name.translations['en'] ??
                id;

            return DropdownMenuItem(
              value: id,
              child: Text(label, overflow: TextOverflow.ellipsis),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null) {
              onStepUpdated(
                selectedStepId!,
                stepDef.copyWith(taskBlueprint: val),
              );
            }
          },
        ),
        const SizedBox(height: 16),
        const Text(
          'Depends On (Comma separated IDs)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        ),
        const SizedBox(height: 4),
        TextFormField(
          initialValue: stepDef.dependsOn.join(', '),
          decoration: const InputDecoration(
            isDense: true,
            border: OutlineInputBorder(),
          ),
          onFieldSubmitted: (val) {
            final newDependsOn = val
                .split(',')
                .map((e) => e.trim())
                .where((e) => e.isNotEmpty)
                .toList();
            onStepUpdated(
              selectedStepId!,
              stepDef.copyWith(dependsOn: newDependsOn),
            );
          },
        ),
        const SizedBox(height: 16),
        const Text(
          'Input Mappings (Press Enter to apply)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        ),
        ...stepDef.inputMappings.entries.map((e) {
          return Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Row(
              children: [
                Expanded(
                  flex: 1,
                  child: TextFormField(
                    initialValue: e.key,
                    decoration: const InputDecoration(
                      isDense: true,
                      border: OutlineInputBorder(),
                      hintText: 'Key',
                    ),
                    onFieldSubmitted: (newKey) {
                      newKey = newKey.trim();
                      if (newKey.isNotEmpty && newKey != e.key) {
                        final newMappings = Map<String, String>.from(
                          stepDef.inputMappings,
                        );
                        final val = newMappings.remove(e.key);
                        newMappings[newKey] = val ?? '';
                        onStepUpdated(
                          selectedStepId!,
                          stepDef.copyWith(inputMappings: newMappings),
                        );
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    initialValue: e.value,
                    decoration: const InputDecoration(
                      isDense: true,
                      border: OutlineInputBorder(),
                      hintText: '\$inputs.value',
                    ),
                    onFieldSubmitted: (newVal) {
                      final newMappings = Map<String, String>.from(
                        stepDef.inputMappings,
                      );
                      newMappings[e.key] = newVal.trim();
                      onStepUpdated(
                        selectedStepId!,
                        stepDef.copyWith(inputMappings: newMappings),
                      );
                    },
                  ),
                ),
                IconButton(
                  icon: Icon(
                    Icons.remove_circle,
                    color: Theme.of(context).colorScheme.error,
                    size: 20,
                  ),
                  onPressed: () {
                    final newMappings = Map<String, String>.from(
                      stepDef.inputMappings,
                    );
                    newMappings.remove(e.key);
                    onStepUpdated(
                      selectedStepId!,
                      stepDef.copyWith(inputMappings: newMappings),
                    );
                  },
                ),
              ],
            ),
          );
        }),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton.icon(
            onPressed: () {
              final newMappings = Map<String, String>.from(
                stepDef.inputMappings,
              );
              newMappings['new_param_${newMappings.length}'] = '\$inputs.';
              onStepUpdated(
                selectedStepId!,
                stepDef.copyWith(inputMappings: newMappings),
              );
            },
            icon: const Icon(Icons.add, size: 16),
            label: Text(l10n.workflowAddMappingBtn),
          ),
        ),
      ],
    );
  }
}
