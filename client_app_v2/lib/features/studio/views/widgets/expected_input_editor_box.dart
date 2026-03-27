import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';

class ExpectedInputEditorBox extends StatefulWidget {
  final Map<String, dynamic> inputDef;
  final VoidCallback onDelete;
  final VoidCallback onChanged;

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
  late bool _isRequired;
  late bool _isChatHistory;

  @override
  void initState() {
    super.initState();
    _keyController = TextEditingController(
      text: SafeCast.safeString(widget.inputDef['input_key']),
    );
    _isRequired = SafeCast.safeBool(widget.inputDef['required'], false);
    _isChatHistory = SafeCast.safeBool(
      widget.inputDef['is_chat_history'],
      false,
    );
    _aiDescController = TextEditingController(
      text: SafeCast.safeString(widget.inputDef['ai_description']),
    );
  }

  @override
  void didUpdateWidget(covariant ExpectedInputEditorBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.inputDef['input_key'] != widget.inputDef['input_key']) {
      _keyController.text = SafeCast.safeString(widget.inputDef['input_key']);
    }
    _isRequired = SafeCast.safeBool(widget.inputDef['required'], false);
    _isChatHistory = SafeCast.safeBool(
      widget.inputDef['is_chat_history'],
      false,
    );
    if (oldWidget.inputDef['ai_description'] !=
        widget.inputDef['ai_description']) {
      _aiDescController.text = SafeCast.safeString(
        widget.inputDef['ai_description'],
      );
    }
  }

  @override
  void dispose() {
    _keyController.dispose();
    _aiDescController.dispose();
    super.dispose();
  }

  void _notifyChange() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        widget.onChanged();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final List<String> modes =
        SafeCast.safeList(
          widget.inputDef['input_modes'],
        ).map((e) => e.toString()).toList();

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
                        widget.inputDef['input_key'] =
                            _keyController.text.trim();
                        _notifyChange();
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
                  icon: const Icon(Icons.delete, color: Colors.red),
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
                  selected: _isRequired,
                  onSelected: (val) {
                    setState(() {
                      _isRequired = val;
                      widget.inputDef['required'] = val;
                      _notifyChange();
                    });
                  },
                ),
                FilterChip(
                  label: Text(l10n.workflowInputIsChatHistory),
                  selected: _isChatHistory,
                  onSelected: (val) {
                    setState(() {
                      _isChatHistory = val;
                      widget.inputDef['is_chat_history'] = val;

                      // Enforce rule: Chat history cannot be a questionnaire
                      if (val && modes.contains('questionnaire')) {
                        modes.clear();
                        if (!modes.contains('file')) modes.add('file');
                        widget.inputDef['input_modes'] = modes;
                      }

                      _notifyChange();
                    });
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
              children:
                  ['file', 'paste', 'questionnaire'].map((mode) {
                    final modeStr =
                        mode == 'file'
                            ? l10n.inputModeFile
                            : mode == 'paste'
                            ? l10n.inputModePaste
                            : l10n.inputModeQuestionnaire;
                    return FilterChip(
                      label: Text(modeStr),
                      selected: modes.contains(mode),
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            if (mode == 'questionnaire') {
                              modes.clear();
                              modes.add(mode);
                              // Enforce rule: Questionnaire cannot be chat history
                              if (_isChatHistory) {
                                _isChatHistory = false;
                                widget.inputDef['is_chat_history'] = false;
                              }
                            } else {
                              if (modes.contains('questionnaire')) {
                                modes.remove('questionnaire');
                                widget.inputDef['questionnaire_definition'] =
                                    [];
                              }
                              if (!modes.contains(mode)) {
                                modes.add(mode);
                              }
                            }
                          } else {
                            // Prevent deselection if it would leave the list empty
                            if (modes.length > 1) {
                              modes.remove(mode);
                            } else if (modes.length == 1 &&
                                modes.first != mode) {
                              modes.remove(
                                mode,
                              ); // theoretically impossible but safe
                            }
                          }
                          widget.inputDef['input_modes'] = modes;
                          _notifyChange();
                        });
                      },
                    );
                  }).toList(),
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),
            I18nTextField(
              label: l10n.workflowInputLabelTitle,
              initialData: SafeCast.safeMap(widget.inputDef['label']),
              onChanged: (val) {
                widget.inputDef['label'] = val;
                _notifyChange();
              },
            ),
            const SizedBox(height: 16),
            I18nTextField(
              label: l10n.workflowInputDescriptionTitle,
              initialData: SafeCast.safeMap(widget.inputDef['description']),
              onChanged: (val) {
                widget.inputDef['description'] = val;
                _notifyChange();
              },
            ),
            const SizedBox(height: 16),
            Focus(
              onFocusChange: (f) {
                if (!f) {
                  widget.inputDef['ai_description'] =
                      _aiDescController.text.trim();
                  _notifyChange();
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
                style: const TextStyle(
                  color: Colors.blueGrey,
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
              _buildQuestionnaireEditor(l10n),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionnaireEditor(AppLocalizations l10n) {
    final questions = SafeCast.safeList(
      widget.inputDef['questionnaire_definition'],
    );

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
            final qDef = SafeCast.safeMap(entry.value);
            final idCtrl = TextEditingController(
              text: SafeCast.safeString(qDef['question_id']),
            );

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Focus(
                            onFocusChange: (f) {
                              if (!f) {
                                qDef['question_id'] = idCtrl.text.trim();
                                _notifyChange();
                              }
                            },
                            child: TextField(
                              controller: idCtrl,
                              decoration: InputDecoration(
                                labelText: l10n.workflowInputQuestionIdLabel,
                              ),
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete, color: Colors.grey),
                          onPressed: () {
                            setState(() {
                              questions.removeAt(idx);
                              widget.inputDef['questionnaire_definition'] =
                                  questions;
                              _notifyChange();
                            });
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    I18nTextField(
                      label: l10n.workflowInputQuestionTextLabel,
                      initialData: SafeCast.safeMap(qDef['question']),
                      onChanged: (val) {
                        qDef['question'] = val;
                        _notifyChange();
                      },
                    ),
                  ],
                ),
              ),
            );
          }),
          TextButton.icon(
            onPressed: () {
              setState(() {
                questions.add({
                  'question_id': 'q${questions.length + 1}',
                  'question': {
                    'default_locale': 'en',
                    'translations': {'en': ''},
                  },
                  'type': 'text',
                });
                widget.inputDef['questionnaire_definition'] = questions;
                _notifyChange();
              });
            },
            icon: const Icon(Icons.add),
            label: Text(l10n.workflowInputAddQuestionBtn),
          ),
        ],
      ),
    );
  }
}
