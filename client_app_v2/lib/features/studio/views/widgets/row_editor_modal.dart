import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class RowEditorModal extends StatefulWidget {
  final MatrixRow? initialMatrixRow;
  final I18nText? initialI18nText;
  final String title;
  final bool isMatrixRow;

  const RowEditorModal({
    super.key,
    this.initialMatrixRow,
    this.initialI18nText,
    this.title = 'Edit Row/Column',
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
      insetPadding: const EdgeInsets.all(16),
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.title),
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
            const SizedBox(width: 8),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              // If isMatrixRow is true, 'initialRow' is actually a full MatrixRow object containing 'label' and 'ai_description'.
              // Otherwise, it's just the translation map directly.
              if (widget.isMatrixRow && _editableMatrixRow != null) ...[
                TextFormField(
                  initialValue: _editableMatrixRow!.aiDescription,
                  decoration: InputDecoration(
                    labelText: 'Row AI Rule (MANDATORY ENGLISH)',
                    helperText:
                        "MUST be in English. Use strict commanding language.",
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
                const SizedBox(height: 16),
                I18nTextField(
                  label: 'Item Content (UI/PDF)',
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
                  label: 'Item Content',
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
