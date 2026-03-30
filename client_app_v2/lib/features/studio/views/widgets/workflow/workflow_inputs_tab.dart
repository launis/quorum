import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import '../expected_input_editor_box.dart';

/// **WorkflowInputsTab**
///
/// Componentized UI widget representing Tab 2 of the Workflow Builder.
/// Handles listing and adding expected inputs.
class WorkflowInputsTab extends StatelessWidget {
  final Workflow workflow;
  final Function(Workflow) onChanged;

  const WorkflowInputsTab({
    super.key,
    required this.workflow,
    required this.onChanged,
  });

  void _addExpectedInput() {
    final inputs = List<ExpectedInput>.from(workflow.expectedInputs);
    inputs.add(
      ExpectedInput(
        inputKey: 'new_input_key_${inputs.length}',
        label: const I18nText(defaultLocale: 'en', translations: {'en': ''}),
        description: const I18nText(
          defaultLocale: 'en',
          translations: {'en': ''},
        ),
        required: false,
        isChatHistory: false,
        inputModes: ['file'],
      ),
    );
    onChanged(workflow.copyWith(expectedInputs: inputs));
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final inputsList = List<ExpectedInput>.from(workflow.expectedInputs);

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
                  l10n.workflowInputsTitle,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: _addExpectedInput,
                  icon: const Icon(Icons.add),
                  label: Text(l10n.workflowAddInputBtn),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (inputsList.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(32.0),
                  child: Text(
                    l10n.studioWorkflowInputsEmpty,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ),
            ...inputsList.asMap().entries.map((entry) {
              final index = entry.key;
              final inputDef = entry.value;

              return ExpectedInputEditorBox(
                inputDef: inputDef,
                onDelete: () {
                  final newInputs = List<ExpectedInput>.from(inputsList);
                  newInputs.removeAt(index);
                  onChanged(workflow.copyWith(expectedInputs: newInputs));
                },
                onChanged: (updatedInput) {
                  final newInputs = List<ExpectedInput>.from(inputsList);
                  newInputs[index] = updatedInput;
                  onChanged(workflow.copyWith(expectedInputs: newInputs));
                },
              );
            }),
          ],
        ),
      ),
    );
  }
}
