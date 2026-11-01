import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

const List<String> _kSupportedInputModes = <String>[
  'file',
  'paste',
  'questionnaire',
  'assignment',
];

class ExpectedInputEditorBox extends StatefulWidget {
  final ExpectedInput inputDef;
  final VoidCallback onDelete;
  final ValueChanged<ExpectedInput> onChanged;

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
  late FocusNode _keyFocusNode;
  late FocusNode _aiDescFocusNode;
  final List<TextEditingController> _questionIdControllers =
      <TextEditingController>[];
  final List<FocusNode> _questionIdFocusNodes = <FocusNode>[];
  final List<VoidCallback> _questionIdFocusListeners = <VoidCallback>[];

  @override
  void initState() {
    super.initState();
    _keyController = TextEditingController(text: widget.inputDef.inputKey);
    _aiDescController = TextEditingController(
      text: widget.inputDef.aiDescription ?? '',
    );
    _keyFocusNode = FocusNode()..addListener(_onKeyFocusChange);
    _aiDescFocusNode = FocusNode()..addListener(_onAiDescFocusChange);
    _syncQuestionControllers(widget.inputDef.questionnaireDefinition);
  }

  void _syncQuestionControllers(List<QuestionnaireItem> items) {
    while (_questionIdControllers.length > items.length) {
      final int lastIndex = _questionIdControllers.length - 1;
      final FocusNode fn = _questionIdFocusNodes.removeLast();
      final VoidCallback listener = _questionIdFocusListeners.removeLast();
      fn.removeListener(listener);
      if (fn.hasFocus) {
        fn.unfocus();
      }
      fn.dispose();
      _questionIdControllers.removeAt(lastIndex).dispose();
    }

    while (_questionIdControllers.length < items.length) {
      final int idx = _questionIdControllers.length;
      final TextEditingController ctrl = TextEditingController(
        text: items[idx].questionId,
      );
      final FocusNode fn = FocusNode();
      void listener() {
        if (!fn.hasFocus) {
          _commitQuestionIdAt(idx);
        }
      }

      fn.addListener(listener);
      _questionIdControllers.add(ctrl);
      _questionIdFocusNodes.add(fn);
      _questionIdFocusListeners.add(listener);
    }

    for (int i = 0; i < items.length; i++) {
      if (_questionIdControllers[i].text != items[i].questionId) {
        _questionIdControllers[i].text = items[i].questionId;
      }
    }
  }

  void _commitQuestionIdAt(int idx) {
    final List<QuestionnaireItem> currentQuestions =
        List<QuestionnaireItem>.from(widget.inputDef.questionnaireDefinition);
    if (idx < 0 || idx >= currentQuestions.length) {
      return;
    }
    final String trimmed = _questionIdControllers[idx].text.trim();
    if (trimmed.isEmpty) {
      _questionIdControllers[idx].text = currentQuestions[idx].questionId;
      return;
    }
    if (trimmed != currentQuestions[idx].questionId) {
      currentQuestions[idx] = currentQuestions[idx].copyWith(
        questionId: trimmed,
      );
      _update(
        widget.inputDef.copyWith(questionnaireDefinition: currentQuestions),
      );
    }
  }

  void _onKeyFocusChange() {
    if (!_keyFocusNode.hasFocus) {
      _commitInputKey();
    }
  }

  void _commitInputKey() {
    final String trimmed = _keyController.text.trim();
    if (trimmed.isEmpty) {
      _keyController.text = widget.inputDef.inputKey;
      return;
    }
    if (trimmed != widget.inputDef.inputKey) {
      _update(widget.inputDef.copyWith(inputKey: trimmed));
    }
  }

  void _onAiDescFocusChange() {
    if (!_aiDescFocusNode.hasFocus) {
      _commitAiDescription();
    }
  }

  void _commitAiDescription() {
    final String trimmed = _aiDescController.text.trim();
    if (trimmed != (widget.inputDef.aiDescription ?? '')) {
      _update(widget.inputDef.copyWith(aiDescription: trimmed));
    }
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
    _syncQuestionControllers(widget.inputDef.questionnaireDefinition);
  }

  @override
  void dispose() {
    _keyFocusNode.removeListener(_onKeyFocusChange);
    _aiDescFocusNode.removeListener(_onAiDescFocusChange);

    if (_keyFocusNode.hasFocus) {
      _keyFocusNode.unfocus();
    }
    if (_aiDescFocusNode.hasFocus) {
      _aiDescFocusNode.unfocus();
    }

    _keyFocusNode.dispose();
    _aiDescFocusNode.dispose();
    _keyController.dispose();
    _aiDescController.dispose();

    for (int i = 0; i < _questionIdFocusNodes.length; i++) {
      final FocusNode fn = _questionIdFocusNodes[i];
      fn.removeListener(_questionIdFocusListeners[i]);
      if (fn.hasFocus) {
        fn.unfocus();
      }
      fn.dispose();
      _questionIdControllers[i].dispose();
    }
    _questionIdFocusNodes.clear();
    _questionIdFocusListeners.clear();
    _questionIdControllers.clear();

    super.dispose();
  }

  void _validateInputInvariants(ExpectedInput def) {
    if (def.inputKey.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: ExpectedInput inputKey cannot be empty in ExpectedInputEditorBox.',
      );
    }
    for (final String mode in def.inputModes) {
      if (!_kSupportedInputModes.contains(mode)) {
        throw AppException.validation(
          'Fail-Fast: Unsupported input mode "$mode" in ExpectedInputEditorBox.',
        );
      }
    }
    for (final QuestionnaireItem item in def.questionnaireDefinition) {
      if (item.questionId.trim().isEmpty || item.type.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: QuestionnaireItem questionId and type cannot be empty in ExpectedInputEditorBox.',
        );
      }
    }
  }

  void _update(ExpectedInput updated) {
    widget.onChanged(updated);
  }

  String _resolveModeLabel(AppLocalizations l10n, String mode) {
    return switch (mode) {
      'file' => l10n.inputModeFile,
      'paste' => l10n.inputModePaste,
      'questionnaire' => l10n.inputModeQuestionnaire,
      'assignment' => l10n.inputModeAssignment,
      _ => throw AppException.validation(
        'Fail-Fast: Unsupported input mode "$mode" in ExpectedInputEditorBox.',
      ),
    };
  }

  @override
  Widget build(BuildContext context) {
    final ExpectedInput def = widget.inputDef;
    _validateInputInvariants(def);

    final ThemeData theme = Theme.of(context);
    final AppLocalizations l10n = AppLocalizations.of(context)!;
    final List<String> modes = List<String>.from(def.inputModes);

    return Card(
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      elevation: AppSpacing.s2,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Expanded(
                  child: TextField(
                    key: const ValueKey<String>('expected_input_key_field'),
                    controller: _keyController,
                    focusNode: _keyFocusNode,
                    onSubmitted: (_) => _commitInputKey(),
                    decoration: InputDecoration(
                      labelText: l10n.workflowInputKeyLabel,
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
                IconButton(
                  key: const ValueKey<String>('expected_input_delete_button'),
                  mouseCursor: SystemMouseCursors.click,
                  icon: Icon(Icons.delete, color: theme.colorScheme.error),
                  tooltip: l10n.workflowDeleteInputTooltip,
                  onPressed: widget.onDelete,
                ),
              ],
            ),
            AppSpacing.h16,
            Wrap(
              spacing: AppSpacing.s16,
              runSpacing: AppSpacing.s8,
              children: <Widget>[
                FilterChip(
                  key: const ValueKey<String>('expected_input_required_chip'),
                  mouseCursor: SystemMouseCursors.click,
                  label: Text(
                    l10n.workflowInputRequired,
                    overflow: TextOverflow.ellipsis,
                  ),
                  selected: def.required,
                  onSelected: (bool val) {
                    _update(def.copyWith(required: val));
                  },
                ),
                FilterChip(
                  key: const ValueKey<String>(
                    'expected_input_chat_history_chip',
                  ),
                  mouseCursor: SystemMouseCursors.click,
                  label: Text(
                    l10n.workflowInputIsChatHistory,
                    overflow: TextOverflow.ellipsis,
                  ),
                  selected: def.isChatHistory,
                  onSelected: (bool val) {
                    final List<String> newModes = List<String>.from(modes);
                    bool wasEndorsed = def.isEndorsedDeliverable;
                    if (val) {
                      newModes.remove('questionnaire');
                      newModes.remove('assignment');
                      wasEndorsed = false;
                      if (newModes.isEmpty) {
                        newModes.add('file');
                      }
                    }
                    _update(
                      def.copyWith(
                        isChatHistory: val,
                        isEndorsedDeliverable: wasEndorsed,
                        inputModes: newModes,
                      ),
                    );
                  },
                ),
                FilterChip(
                  key: const ValueKey<String>('expected_input_endorsed_chip'),
                  mouseCursor: SystemMouseCursors.click,
                  label: Text(
                    l10n.workflowInputEndorsedDeliverable,
                    overflow: TextOverflow.ellipsis,
                  ),
                  selected: def.isEndorsedDeliverable,
                  onSelected: (bool val) {
                    final List<String> newModes = List<String>.from(modes);
                    bool wasChat = def.isChatHistory;
                    if (val) {
                      wasChat = false;
                      newModes.remove('questionnaire');
                      newModes.remove('assignment');
                      if (newModes.isEmpty) {
                        newModes.add('file');
                      }
                    }
                    _update(
                      def.copyWith(
                        isEndorsedDeliverable: val,
                        isChatHistory: wasChat,
                        inputModes: newModes,
                      ),
                    );
                  },
                ),
                FilterChip(
                  key: const ValueKey<String>(
                    'expected_input_scan_performative_chip',
                  ),
                  mouseCursor: SystemMouseCursors.click,
                  label: Text(
                    l10n.workflowInputScanPerformative,
                    overflow: TextOverflow.ellipsis,
                  ),
                  selected: def.scanForPerformativePatterns,
                  onSelected: (bool val) {
                    _update(def.copyWith(scanForPerformativePatterns: val));
                  },
                ),
              ],
            ),
            AppSpacing.h16,
            Text(
              l10n.workflowInputModesLabel,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              overflow: TextOverflow.ellipsis,
            ),
            AppSpacing.h8,
            Wrap(
              spacing: AppSpacing.s8,
              runSpacing: AppSpacing.s8,
              children: _kSupportedInputModes.map((String mode) {
                final String modeStr = _resolveModeLabel(l10n, mode);
                return FilterChip(
                  key: ValueKey<String>('expected_input_mode_chip_$mode'),
                  mouseCursor: SystemMouseCursors.click,
                  label: Text(modeStr, overflow: TextOverflow.ellipsis),
                  selected: modes.contains(mode),
                  onSelected: (bool selected) {
                    final List<String> newModes = List<String>.from(modes);
                    bool wasChatHistory = def.isChatHistory;
                    bool wasEndorsed = def.isEndorsedDeliverable;

                    if (selected) {
                      if (mode == 'questionnaire') {
                        newModes
                          ..clear()
                          ..add(mode);
                        wasChatHistory = false;
                        wasEndorsed = false;
                      } else if (mode == 'assignment') {
                        newModes.remove('questionnaire');
                        wasChatHistory = false;
                        wasEndorsed = false;
                        if (!newModes.contains('assignment')) {
                          newModes.add('assignment');
                        }
                      } else {
                        newModes.remove('questionnaire');
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
                        isEndorsedDeliverable: wasEndorsed,
                        questionnaireDefinition:
                            newModes.contains('questionnaire')
                            ? def.questionnaireDefinition
                            : <QuestionnaireItem>[],
                      ),
                    );
                  },
                );
              }).toList(),
            ),
            AppSpacing.h16,
            const Divider(),
            AppSpacing.h16,
            I18nTextField(
              label: l10n.workflowInputLabelTitle,
              initialData: def.label,
              onChanged: (I18nText val) {
                _update(def.copyWith(label: val));
              },
            ),
            AppSpacing.h16,
            I18nTextField(
              label: l10n.workflowInputDescriptionTitle,
              initialData: def.description,
              onChanged: (I18nText val) {
                _update(def.copyWith(description: val));
              },
            ),
            AppSpacing.h16,
            TextField(
              key: const ValueKey<String>('expected_input_ai_desc_field'),
              controller: _aiDescController,
              focusNode: _aiDescFocusNode,
              maxLines: 3,
              onSubmitted: (_) => _commitAiDescription(),
              decoration: InputDecoration(
                labelText: l10n.workflowInputAiDescriptionTitle,
                border: const OutlineInputBorder(),
                hintText: l10n.rowAiRuleHelper,
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(top: AppSpacing.s8),
              child: Text(
                l10n.adminAiDescriptionHint,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.error,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(top: AppSpacing.s4),
              child: Text(
                l10n.adminPromptBestPracticesHint,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
            if (modes.contains('questionnaire')) ...<Widget>[
              AppSpacing.h24,
              Text(
                l10n.workflowInputQuestionnaireDefTitle,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
              AppSpacing.h8,
              _buildQuestionnaireEditor(theme, l10n, def),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionnaireEditor(
    ThemeData theme,
    AppLocalizations l10n,
    ExpectedInput def,
  ) {
    final List<QuestionnaireItem> questions = List<QuestionnaireItem>.from(
      def.questionnaireDefinition,
    );

    return Container(
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(AppSpacing.s8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          if (questions.isEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.s16),
              child: Text(
                l10n.workflowInputNoQuestionsDefined,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontStyle: FontStyle.italic,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ...questions.asMap().entries.map((
            MapEntry<int, QuestionnaireItem> entry,
          ) {
            final int idx = entry.key;
            final QuestionnaireItem qDef = entry.value;

            return Card(
              key: ValueKey<String>('questionnaire_card_$idx'),
              margin: const EdgeInsets.only(bottom: AppSpacing.s12),
              child: Padding(
                padding: AppSpacing.p12,
                child: Column(
                  children: <Widget>[
                    Row(
                      children: <Widget>[
                        Expanded(
                          child: TextField(
                            key: ValueKey<String>('question_id_field_$idx'),
                            controller: _questionIdControllers[idx],
                            focusNode: _questionIdFocusNodes[idx],
                            decoration: InputDecoration(
                              labelText: l10n.workflowInputQuestionIdLabel,
                            ),
                            onSubmitted: (_) => _commitQuestionIdAt(idx),
                          ),
                        ),
                        IconButton(
                          key: ValueKey<String>('question_delete_btn_$idx'),
                          mouseCursor: SystemMouseCursors.click,
                          tooltip: l10n.delete,
                          icon: Icon(
                            Icons.delete,
                            color: theme.colorScheme.error,
                          ),
                          onPressed: () {
                            final List<QuestionnaireItem> updatedQuestions =
                                List<QuestionnaireItem>.from(questions)
                                  ..removeAt(idx);
                            _update(
                              def.copyWith(
                                questionnaireDefinition: updatedQuestions,
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                    AppSpacing.h12,
                    I18nTextField(
                      label: l10n.workflowInputQuestionTextLabel,
                      initialData: qDef.question,
                      onChanged: (I18nText val) {
                        final List<QuestionnaireItem> updatedQuestions =
                            List<QuestionnaireItem>.from(questions);
                        updatedQuestions[idx] = qDef.copyWith(question: val);
                        _update(
                          def.copyWith(
                            questionnaireDefinition: updatedQuestions,
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            );
          }),
          TextButton.icon(
            key: const ValueKey<String>('questionnaire_add_btn'),
            style: TextButton.styleFrom(
              enabledMouseCursor: SystemMouseCursors.click,
            ),
            onPressed: () {
              final List<QuestionnaireItem> updatedQuestions =
                  List<QuestionnaireItem>.from(questions)..add(
                    QuestionnaireItem(
                      questionId: 'q${questions.length + 1}',
                      question: const I18nText(
                        translations: <String, String>{'en': ''},
                      ),
                      type: 'text',
                    ),
                  );
              _update(def.copyWith(questionnaireDefinition: updatedQuestions));
            },
            icon: const Icon(Icons.add),
            label: Text(
              l10n.workflowInputAddQuestionBtn,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
