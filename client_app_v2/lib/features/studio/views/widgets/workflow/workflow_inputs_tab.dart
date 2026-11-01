import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
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
  final ValueChanged<Workflow> onChanged;

  const WorkflowInputsTab({
    super.key,
    required this.workflow,
    required this.onChanged,
  });

  void _validateWorkflowInputs(Workflow target) {
    if (target.id.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Workflow id cannot be empty in WorkflowInputsTab.',
      );
    }
    for (final ExpectedInput input in target.expectedInputs) {
      if (input.inputKey.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: ExpectedInput inputKey cannot be empty in WorkflowInputsTab.',
        );
      }
    }
  }

  void _addExpectedInput() {
    final List<ExpectedInput> inputs = List<ExpectedInput>.from(
      workflow.expectedInputs,
    );
    final Set<String> existingKeys = inputs
        .map((ExpectedInput e) => e.inputKey)
        .toSet();
    int candidateIndex = inputs.length;
    String nextKey = 'new_input_key_$candidateIndex';
    while (existingKeys.contains(nextKey)) {
      candidateIndex++;
      nextKey = 'new_input_key_$candidateIndex';
    }

    inputs.add(
      ExpectedInput(
        inputKey: nextKey,
        label: const I18nText(translations: <String, String>{'en': ''}),
        description: const I18nText(translations: <String, String>{'en': ''}),
        required: false,
        isChatHistory: false,
        inputModes: const <String>['file'],
      ),
    );
    onChanged(workflow.copyWith(expectedInputs: inputs));
  }

  @override
  Widget build(BuildContext context) {
    _validateWorkflowInputs(workflow);

    final AppLocalizations l10n = AppLocalizations.of(context)!;
    final ThemeData theme = Theme.of(context);
    final List<ExpectedInput> inputsList = List<ExpectedInput>.from(
      workflow.expectedInputs,
    );

    return SingleChildScrollView(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Expanded(
                  child: Text(
                    l10n.workflowInputsTitle,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                AppSpacing.w16,
                OutlinedButton.icon(
                  key: const ValueKey<String>(
                    'workflow_add_expected_input_btn',
                  ),
                  style: OutlinedButton.styleFrom(
                    enabledMouseCursor: SystemMouseCursors.click,
                  ),
                  onPressed: _addExpectedInput,
                  icon: const Icon(Icons.add),
                  label: Text(
                    l10n.workflowAddInputBtn,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            AppSpacing.h16,
            if (inputsList.isEmpty)
              Center(
                child: Padding(
                  padding: AppSpacing.p24,
                  child: Text(
                    l10n.studioWorkflowInputsEmpty,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ),
            ...inputsList.asMap().entries.map((
              MapEntry<int, ExpectedInput> entry,
            ) {
              final int index = entry.key;
              final ExpectedInput inputDef = entry.value;

              return ExpectedInputEditorBox(
                key: ValueKey<String>(
                  'expected_input_box_${index}_${inputDef.inputKey}',
                ),
                inputDef: inputDef,
                onDelete: () {
                  final List<ExpectedInput> newInputs =
                      List<ExpectedInput>.from(inputsList)..removeAt(index);
                  onChanged(workflow.copyWith(expectedInputs: newInputs));
                },
                onChanged: (ExpectedInput updatedInput) {
                  final List<ExpectedInput> newInputs =
                      List<ExpectedInput>.from(inputsList);
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
