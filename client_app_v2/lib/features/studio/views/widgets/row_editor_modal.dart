import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_exception.dart';

class RowEditorModal extends StatefulWidget {
  final Map<String, dynamic> initialRow;
  final String title;
  final bool isMatrixRow;

  const RowEditorModal({
    super.key,
    required this.initialRow,
    this.title = 'Edit Row/Column',
    this.isMatrixRow = false,
  });

  @override
  State<RowEditorModal> createState() => _RowEditorModalState();
}

class _RowEditorModalState extends State<RowEditorModal> {
  late Map<String, dynamic> _editableRow;

  @override
  void initState() {
    super.initState();
    _editableRow = Map<String, dynamic>.from(widget.initialRow);
  }

  void _save() {
    Navigator.of(context).pop(_editableRow);
  }

  @override
  Widget build(BuildContext context) {
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
              label: const Text('Apply'),
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
              if (widget.isMatrixRow) ...[
                TextFormField(
                  initialValue: SafeCast.safeString(
                    _editableRow['ai_description'],
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Row AI Rule (MANDATORY ENGLISH)',
                    helperText:
                        "MUST be in English. Use strict commanding language.",
                    helperStyle: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                    border: OutlineInputBorder(),
                    alignLabelWithHint: true,
                  ),
                  maxLines: 3,
                  onChanged: (val) {
                    _editableRow['ai_description'] = val;
                  },
                ),
                const SizedBox(height: 16),
                I18nTextField(
                  label: 'Item Content (UI/PDF)',
                  initialData: SafeCast.safeMap(
                    _editableRow['label'] ?? (throw AppException.validation('Matrix row data corrupted: missing localized label.'))
                  ),
                  onChanged: (val) {
                    _editableRow['label'] = val;
                  },
                ),
              ] else ...[
                I18nTextField(
                  label: 'Item Content',
                  initialData: SafeCast.safeMap(_editableRow),
                  onChanged: (val) {
                    _editableRow = val;
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
