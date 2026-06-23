import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';

class ExpectedInputEditorBox extends StatefulWidget {
  final ExpectedInput inputDef;
  final VoidCallback onDelete;
  final Function(ExpectedInput) onChanged;

  const ExpectedInputEditorBox({
    super.key,
    required this.inputDef,
    required this.onDelete,
    required this.onChanged,
  });

  @override
  State<ExpectedInputEditorBox> createState() => _ExpectedInputEditorBoxState();
}

class _ExpectedInputEditorBoxState extends State<ExpectedInputEditorBox> {
  late TextEditingController _keyController;
  late TextEditingController _aiDescController;

  @override
  void initState() {
    super.initState();
    _keyController = TextEditingController(text: widget.inputDef.inputKey);
    _aiDescController = TextEditingController(
      text: widget.inputDef.aiDescription ?? '',
    );
  }

  @override
  void didUpdateWidget(covariant ExpectedInputEditorBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.inputDef.inputKey != widget.inputDef.inputKey) {
      _keyController.text = widget.inputDef.inputKey;
    }
    if (oldWidget.inputDef.aiDescription != widget.inputDef.aiDescription) {
      _aiDescController.text = widget.inputDef.aiDescription ?? '';
    }
  }

  @override
  void dispose() {
    _keyController.dispose();
    _aiDescController.dispose();
    super.dispose();
  }

  void _update(ExpectedInput updated) {
    widget.onChanged(updated);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final def = widget.inputDef;
    final modes = List<String>.from(def.inputModes);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Focus(
                    onFocusChange: (f) {
                      if (!f) {
                        _update(
                          def.copyWith(inputKey: _keyController.text.trim()),
                        );
                      }
                    },
                    child: TextField(
                      controller: _keyController,
                      decoration: InputDecoration(
                        labelText: l10n.workflowInputKeyLabel,
                        border: const OutlineInputBorder(),
                      ),
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(
                    Icons.delete,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  tooltip: l10n.workflowDeleteInputTooltip,
                  onPressed: widget.onDelete,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 16,
              children: [
                FilterChip(
                  label: Text(l10n.workflowInputRequired),
                  selected: def.required,
                  onSelected: (val) {
                    _update(def.copyWith(required: val));
                  },
                ),
                FilterChip(
                  label: Text(l10n.workflowInputIsChatHistory),
                  selected: def.isChatHistory,
                  onSelected: (val) {
                    var newModes = List<String>.from(modes);
                    if (val && newModes.contains('questionnaire')) {
                      newModes.clear();
                      if (!newModes.contains('file')) newModes.add('file');
                    }
                    _update(
                      def.copyWith(isChatHistory: val, inputModes: newModes),
                    );
                  },
                ),
                FilterChip(
                  label: Text(l10n.workflowInputScanPerformative),
                  selected: def.scanForPerformativePatterns,
                  onSelected: (val) {
                    _update(def.copyWith(scanForPerformativePatterns: val));
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              l10n.workflowInputModesLabel,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Wrap(
              spacing: 8,
              children: ['file', 'paste', 'questionnaire'].map((mode) {
                final modeStr = mode == 'file'
                    ? l10n.inputModeFile
                    : mode == 'paste'
                    ? l10n.inputModePaste
                    : l10n.inputModeQuestionnaire;
                return FilterChip(
                  label: Text(modeStr),
                  selected: modes.contains(mode),
                  onSelected: (selected) {
                    var newModes = List<String>.from(modes);
                    bool wasChatHistory = def.isChatHistory;

                    if (selected) {
                      if (mode == 'questionnaire') {
                        newModes.clear();
                        newModes.add(mode);
                        wasChatHistory = false;
                      } else {
                        if (newModes.contains('questionnaire')) {
                          newModes.remove('questionnaire');
                        }
                        if (!newModes.contains(mode)) {
                          newModes.add(mode);
                        }
                      }
                    } else {
                      if (newModes.length > 1) {
                        newModes.remove(mode);
                      }
                    }

                    _update(
                      def.copyWith(
                        inputModes: newModes,
                        isChatHistory: wasChatHistory,
                        questionnaireDefinition:
                            newModes.contains('questionnaire')
                            ? def.questionnaireDefinition
                            : [],
                      ),
                    );
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),
            I18nTextField(
              label: l10n.workflowInputLabelTitle,
              initialData: def.label,
              onChanged: (val) {
                _update(def.copyWith(label: val));
              },
            ),
            const SizedBox(height: 16),
            I18nTextField(
              label: l10n.workflowInputDescriptionTitle,
              initialData: def.description,
              onChanged: (val) {
                _update(def.copyWith(description: val));
              },
            ),
            const SizedBox(height: 16),
            Focus(
              onFocusChange: (f) {
                if (!f) {
                  _update(
                    def.copyWith(aiDescription: _aiDescController.text.trim()),
                  );
                }
              },
              child: TextField(
                controller: _aiDescController,
                maxLines: 3,
                decoration: InputDecoration(
                  labelText: l10n.workflowInputAiDescriptionTitle,
                  border: const OutlineInputBorder(),
                  hintText: 'Always write prompt logic in English',
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(top: 8.0),
              child: Text(
                l10n.adminAiDescriptionHint,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(top: 4.0),
              child: Text(
                l10n.adminPromptBestPracticesHint,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                  fontSize: 12,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),

            if (modes.contains('questionnaire')) ...[
              const SizedBox(height: 24),
              Text(
                l10n.workflowInputQuestionnaireDefTitle,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              _buildQuestionnaireEditor(l10n, def),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionnaireEditor(AppLocalizations l10n, ExpectedInput def) {
    final questions = List<QuestionnaireItem>.from(def.questionnaireDefinition);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (questions.isEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 16.0),
              child: Text(
                l10n.workflowInputNoQuestionsDefined,
                style: const TextStyle(fontStyle: FontStyle.italic),
              ),
            ),
          ...questions.asMap().entries.map((entry) {
            final idx = entry.key;
            final qDef = entry.value;

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            initialValue: qDef.questionId,
                            decoration: InputDecoration(
                              labelText: l10n.workflowInputQuestionIdLabel,
                            ),
                            onChanged: (val) {
                              questions[idx] = qDef.copyWith(
                                questionId: val.trim(),
                              );
                              _update(
                                def.copyWith(
                                  questionnaireDefinition: questions,
                                ),
                              );
                            },
                          ),
                        ),
                        IconButton(
                          icon: Icon(
                            Icons.delete,
                            color: Theme.of(
                              context,
                            ).colorScheme.onSurfaceVariant,
                          ),
                          onPressed: () {
                            questions.removeAt(idx);
                            _update(
                              def.copyWith(questionnaireDefinition: questions),
                            );
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    I18nTextField(
                      label: l10n.workflowInputQuestionTextLabel,
                      initialData: qDef.question,
                      onChanged: (val) {
                        questions[idx] = qDef.copyWith(question: val);
                        _update(
                          def.copyWith(questionnaireDefinition: questions),
                        );
                      },
                    ),
                  ],
                ),
              ),
            );
          }),
          TextButton.icon(
            onPressed: () {
              questions.add(
                QuestionnaireItem(
                  questionId: 'q${questions.length + 1}',
                  question: const I18nText(
                    defaultLocale: 'en',
                    translations: {'en': ''},
                  ),
                  type: 'text',
                ),
              );
              _update(def.copyWith(questionnaireDefinition: questions));
            },
            icon: const Icon(Icons.add),
            label: Text(l10n.workflowInputAddQuestionBtn),
          ),
        ],
      ),
    );
  }
}
