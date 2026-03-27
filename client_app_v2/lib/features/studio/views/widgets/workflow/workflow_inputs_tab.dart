import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import '../../../../../utils/safe_cast.dart';
import '../expected_input_editor_box.dart';

/// **WorkflowInputsTab**
///
/// Componentized UI widget representing Tab 2 of the Workflow Builder.
/// Handles listing and adding expected inputs.
class WorkflowInputsTab extends StatelessWidget {
  final Map<String, dynamic> workflow;
  final VoidCallback onChanged;

  const WorkflowInputsTab({
    super.key,
    required this.workflow,
    required this.onChanged,
  });

  void _addExpectedInput() {
    final inputs = SafeCast.safeList(workflow['expected_inputs']);
    inputs.add({
      'input_key': 'new_input_key_${inputs.length}',
      'label': {
        'default_locale': 'en',
        'translations': {'en': ''},
      },
      'description': {
        'default_locale': 'en',
        'translations': {'en': ''},
      },
      'ai_description': {
        'default_locale': 'en',
        'translations': {'en': ''},
      },
      'required': false,
      'is_chat_history': false,
      'input_modes': ['file'],
      'questionnaire_definition': [],
    });
    workflow['expected_inputs'] = inputs;
    onChanged();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final inputsList = SafeCast.safeList(workflow['expected_inputs']);

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
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32.0),
                  child: Text(
                    'No expected inputs defined.',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
              ),
            ...inputsList.asMap().entries.map((entry) {
              final index = entry.key;
              final inputDef = SafeCast.safeMap(entry.value);

              return ExpectedInputEditorBox(
                inputDef: inputDef,
                onDelete: () {
                  inputsList.removeAt(index);
                  workflow['expected_inputs'] = inputsList;
                  onChanged();
                },
                onChanged: onChanged,
              );
            }),
          ],
        ),
      ),
    );
  }
}
