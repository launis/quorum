import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class _SaveRowIntent extends Intent {
  const _SaveRowIntent();
}

class _DismissRowIntent extends Intent {
  const _DismissRowIntent();
}

class RowEditorModal extends StatefulWidget {
  final MatrixRow? initialMatrixRow;
  final I18nText? initialI18nText;
  final String? title;
  final bool isMatrixRow;

  const RowEditorModal({
    super.key,
    this.initialMatrixRow,
    this.initialI18nText,
    this.title,
    this.isMatrixRow = false,
  }) : assert(
         (isMatrixRow && initialMatrixRow != null) ||
             (!isMatrixRow && initialI18nText != null),
       );

  @override
  State<RowEditorModal> createState() => _RowEditorModalState();
}

class _RowEditorModalState extends State<RowEditorModal> {
  MatrixRow? _editableMatrixRow;
  I18nText? _editableI18nText;
  late final FocusNode _aiDescriptionFocusNode;

  @override
  void initState() {
    super.initState();
    _editableMatrixRow = widget.initialMatrixRow?.copyWith();
    _editableI18nText = widget.initialI18nText?.copyWith();
    _aiDescriptionFocusNode = FocusNode();
  }

  @override
  void dispose() {
    if (_aiDescriptionFocusNode.hasFocus) {
      _aiDescriptionFocusNode.unfocus();
    }
    _aiDescriptionFocusNode.dispose();
    super.dispose();
  }

  void _save() {
    if (widget.isMatrixRow) {
      Navigator.of(context).pop(_editableMatrixRow);
    } else {
      Navigator.of(context).pop(_editableI18nText);
    }
  }

  void _dismiss() {
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Shortcuts(
      shortcuts: const <ShortcutActivator, Intent>{
        SingleActivator(LogicalKeyboardKey.escape): _DismissRowIntent(),
        SingleActivator(LogicalKeyboardKey.enter, control: true):
            _SaveRowIntent(),
      },
      child: Actions(
        actions: <Type, Action<Intent>>{
          _DismissRowIntent: CallbackAction<_DismissRowIntent>(
            onInvoke: (_) {
              _dismiss();
              return null;
            },
          ),
          _SaveRowIntent: CallbackAction<_SaveRowIntent>(
            onInvoke: (_) {
              _save();
              return null;
            },
          ),
        },
        child: Dialog(
          insetPadding: AppSpacing.p16,
          child: Scaffold(
            appBar: AppBar(
              title: Text(
                widget.title ?? l10n.rowEditorDefaultTitle,
                overflow: TextOverflow.ellipsis,
              ),
              leading: IconButton(
                mouseCursor: SystemMouseCursors.click,
                icon: const Icon(Icons.close),
                onPressed: _dismiss,
              ),
              actions: [
                FilledButton.icon(
                  style: FilledButton.styleFrom(
                    enabledMouseCursor: SystemMouseCursors.click,
                  ),
                  onPressed: _save,
                  icon: const Icon(Icons.check),
                  label: Text(l10n.save, overflow: TextOverflow.ellipsis),
                ),
                AppSpacing.w8,
              ],
            ),
            body: SingleChildScrollView(
              padding: AppSpacing.p16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (widget.isMatrixRow && _editableMatrixRow != null) ...[
                    TextFormField(
                      focusNode: _aiDescriptionFocusNode,
                      initialValue: _editableMatrixRow!.aiDescription,
                      decoration: InputDecoration(
                        labelText: l10n.rowAiRuleLabel,
                        helperText: l10n.rowAiRuleHelper,
                        helperStyle: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.error,
                          fontWeight: FontWeight.bold,
                        ),
                        border: const OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                      maxLines: 3,
                      onChanged: (val) {
                        setState(() {
                          _editableMatrixRow = _editableMatrixRow!.copyWith(
                            aiDescription: val,
                          );
                        });
                      },
                    ),
                    AppSpacing.h16,
                    I18nTextField(
                      label: l10n.rowItemContentLabel,
                      initialData: _editableMatrixRow!.label,
                      onChanged: (val) {
                        setState(() {
                          _editableMatrixRow = _editableMatrixRow!.copyWith(
                            label: val,
                          );
                        });
                      },
                    ),
                  ] else if (_editableI18nText != null) ...[
                    I18nTextField(
                      label: l10n.rowItemContentSimpleLabel,
                      initialData: _editableI18nText!,
                      onChanged: (val) {
                        setState(() {
                          _editableI18nText = val;
                        });
                      },
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
