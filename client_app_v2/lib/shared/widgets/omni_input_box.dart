import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/file_input_field.dart';

class OmniInputBox extends StatefulWidget {
  final String label;
  final String keyName;
  final dynamic currentValue;
  final IconData? icon;
  final int minLines;
  final Function(dynamic) onChanged;

  const OmniInputBox({
    super.key,
    required this.label,
    required this.keyName,
    this.currentValue,
    this.icon,
    this.minLines = 1,
    required this.onChanged,
  });

  @override
  State<OmniInputBox> createState() => _OmniInputBoxState();
}

class _OmniInputBoxState extends State<OmniInputBox> {
  late bool _isFileMode;

  @override
  void initState() {
    super.initState();
    // Default to file mode if it's currently a file, otherwise defaulting to text
    _isFileMode = widget.currentValue is PlatformFile;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Card(
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Theme.of(context).dividerColor),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                if (widget.icon != null) ...[
                  Icon(
                    widget.icon,
                    size: 20,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                ],
                Expanded(
                  child: Text(
                    widget.label,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                SegmentedButton<bool>(
                  showSelectedIcon: false,
                  segments: [
                    ButtonSegment<bool>(
                      value: false,
                      icon: const Icon(Icons.text_fields, size: 18),
                      label: Text(l10n.pasteText),
                    ),
                    ButtonSegment<bool>(
                      value: true,
                      icon: const Icon(Icons.upload_file, size: 18),
                      label: Text(l10n.uploadFile),
                    ),
                  ],
                  selected: {_isFileMode},
                  onSelectionChanged: (Set<bool> newSelection) {
                    setState(() {
                      _isFileMode = newSelection.first;
                    });
                    // Clear the state when switching modes, this avoids accidentally sending text when file mode is selected
                    widget.onChanged(null);
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_isFileMode)
              FileInputField(
                label: widget.label,
                icon: widget.icon,
                value:
                    widget.currentValue is PlatformFile
                        ? widget.currentValue
                        : null,
                validator: (value) {
                  if (value == null) {
                    return l10n.fileRequired;
                  }
                  return null;
                },
                onFileSelected: (file) => widget.onChanged(file),
                onClear: () => widget.onChanged(null),
              )
            else
              TextFormField(
                key: ValueKey('${widget.keyName}_text'),
                initialValue:
                    widget.currentValue is String ? widget.currentValue : '',
                decoration: InputDecoration(
                  labelText: l10n.pasteTextLabel,
                  border: const OutlineInputBorder(),
                  alignLabelWithHint: widget.minLines > 1,
                ),
                minLines: widget.minLines,
                maxLines: widget.minLines + 10,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return l10n.fieldRequired;
                  }
                  return null;
                },
                onChanged: (value) => widget.onChanged(value),
              ),
          ],
        ),
      ),
    );
  }
}
