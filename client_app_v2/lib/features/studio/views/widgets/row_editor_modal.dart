import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

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
  }) : assert(initialMatrixRow != null || initialI18nText != null);

  @override
  State<RowEditorModal> createState() => _RowEditorModalState();
}

class _RowEditorModalState extends State<RowEditorModal> {
  MatrixRow? _editableMatrixRow;
  I18nText? _editableI18nText;

  @override
  void initState() {
    super.initState();
    _editableMatrixRow = widget.initialMatrixRow?.copyWith();
    _editableI18nText = widget.initialI18nText?.copyWith();
  }

  void _save() {
    if (widget.isMatrixRow) {
      Navigator.of(context).pop(_editableMatrixRow);
    } else {
      Navigator.of(context).pop(_editableI18nText);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Dialog(
      insetPadding: AppSpacing.p16,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.title ?? l10n.rowEditorDefaultTitle),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Navigator.of(context).pop(),
          ),
          actions: [
            FilledButton.icon(
              onPressed: _save,
              icon: const Icon(Icons.check),
              label: Text(l10n.save),
            ),
            AppSpacing.w8,
          ],
        ),
        body: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (widget.isMatrixRow && _editableMatrixRow != null) ...[
                TextFormField(
                  initialValue: _editableMatrixRow!.aiDescription,
                  decoration: InputDecoration(
                    labelText: l10n.rowAiRuleLabel,
                    helperText: l10n.rowAiRuleHelper,
                    helperStyle: TextStyle(
                      color: Theme.of(context).colorScheme.error,
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
    );
  }
}
