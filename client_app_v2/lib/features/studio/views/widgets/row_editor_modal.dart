import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';

class RowEditorModal extends StatefulWidget {
  final Map<String, dynamic> initialRow;
  final String title;

  const RowEditorModal({
    super.key,
    required this.initialRow,
    this.title = 'Edit Row/Column',
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
              I18nTextField(
                label: 'Item Content',
                initialData: SafeCast.safeMap(_editableRow),
                onChanged: (val) {
                  _editableRow = val;
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
