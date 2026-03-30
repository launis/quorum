import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/logging/logger_service.dart';

class FileInputField extends StatefulWidget {
  final String label;
  final IconData? icon;
  final PlatformFile? value; // Current value (file object)
  final ValueChanged<PlatformFile> onFileSelected;
  final VoidCallback onClear;
  final String? Function(PlatformFile?)? validator;

  const FileInputField({
    super.key,
    required this.label,
    required this.onFileSelected,
    required this.onClear,
    this.icon,
    this.value,
    this.validator,
  });

  @override
  State<FileInputField> createState() => _FileInputFieldState();
}

class _FileInputFieldState extends State<FileInputField> {
  bool _isLoading = false;

  Future<void> _pickFile() async {
    final l10n = AppLocalizations.of(context)!;
    setState(() => _isLoading = true);
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: [
          'pdf',
          'docx',
          'txt',
          'md',
          'json',
          'log',
          'csv',
          'xml',
          'yaml',
          'yml',
        ],
        withData:
            true, // Always load bytes to ensure reliability across platforms
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.single;
        widget.onFileSelected(file);
      }
    } catch (e) {
      if (mounted) {
        ProviderScope.containerOf(
          context,
        ).read(loggerServiceProvider).error('Shared', 'File Error: $e', e);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(l10n.errorReadingFile('$e'))));
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final fileName = widget.value?.name;
    final hasFile = fileName != null;

    return FormField<PlatformFile>(
      validator: widget.validator,
      initialValue: widget.value,
      builder: (state) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            InkWell(
              onTap: _pickFile,
              borderRadius: BorderRadius.circular(4),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: widget.label,
                  border: const OutlineInputBorder(),
                  prefixIcon: widget.icon != null ? Icon(widget.icon) : null,
                  errorText: state.errorText,
                  suffixIcon: _isLoading
                      ? const Padding(
                          padding: EdgeInsets.all(12.0),
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : hasFile
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: widget.onClear,
                        )
                      : Icon(Icons.attach_file),
                ),
                child: Text(
                  fileName ?? AppLocalizations.of(context)!.selectFile,
                  style: TextStyle(
                    color: hasFile
                        ? Theme.of(context).textTheme.bodyMedium?.color
                        : Theme.of(context).hintColor,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
            if (hasFile)
              Padding(
                padding: EdgeInsets.only(top: 4, left: 12),
                child: Text(
                  AppLocalizations.of(
                    context,
                  )!.fileInputLabel(widget.value!.name, widget.value!.size),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
          ],
        );
      },
    );
  }
}
