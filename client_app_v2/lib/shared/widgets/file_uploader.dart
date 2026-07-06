import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class FileUploader extends StatefulWidget {
  final String label;
  final ValueChanged<PlatformFile>? onFileSelected;
  final String? initialFileName;
  final bool isLoading;
  final String? errorText;

  const FileUploader({
    super.key,
    required this.label,
    this.onFileSelected,
    this.initialFileName,
    this.isLoading = false,
    this.errorText,
  });

  @override
  State<FileUploader> createState() => _FileUploaderState();
}

class _FileUploaderState extends State<FileUploader> {
  String? _fileName;

  @override
  void initState() {
    super.initState();
    _fileName = widget.initialFileName;
  }

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.pickFiles();

      if (result != null) {
        final file = result.files.single;
        setState(() {
          _fileName = file.name;
        });
        widget.onFileSelected?.call(file);
      }
    } catch (e) {
      if (mounted) {
        ProviderScope.containerOf(context)
            .read(loggerServiceProvider)
            .error('Shared', 'File Uploader Error: $e', e);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              AppLocalizations.of(context)?.errorReadingFile('$e') ??
                  'Error reading file ($e)',
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(widget.label, style: Theme.of(context).textTheme.labelMedium),
        const SizedBox(height: 8),
        InkWell(
          onTap: widget.isLoading ? null : _pickFile,
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              border: Border.all(
                color: widget.errorText != null
                    ? Theme.of(context).colorScheme.error
                    : Theme.of(context).colorScheme.outline,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                if (widget.isLoading)
                  const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                else
                  Icon(
                    Icons.attach_file,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    widget.isLoading
                        ? (AppLocalizations.of(context)?.sharedUploading ??
                              'Uploading...')
                        : (_fileName ??
                              AppLocalizations.of(context)?.sharedSelectFile ??
                              'Select file...'),
                    style: TextStyle(
                      color: (widget.isLoading || _fileName != null)
                          ? Theme.of(context).colorScheme.onSurface
                          : Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (!widget.isLoading && _fileName != null)
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () {
                      setState(() {
                        _fileName = null;
                      });
                      // If we are just clearing UI, we might not trigger onFileSelected
                      // but usually we want to notify parent.
                      // PlatformFile not nullable in ValueChanged, so we skip callback or need architectural change if clear needed.
                      // For now, consistent with previous behavior (UI clear only).
                    },
                  ),
              ],
            ),
          ),
        ),
        if (widget.errorText != null)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              widget.errorText!,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
                fontSize: 12,
              ),
            ),
          ),
      ],
    );
  }
}
