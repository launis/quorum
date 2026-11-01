import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FileInputField extends ConsumerStatefulWidget {
  final String label;
  final IconData? icon;
  final PlatformFile? value;
  final ValueChanged<PlatformFile> onFileSelected;
  final VoidCallback onClear;
  final String? Function(PlatformFile?)? validator;
  final Future<FilePickerResult?> Function()? pickFiles;

  const FileInputField({
    super.key,
    required this.label,
    required this.onFileSelected,
    required this.onClear,
    this.icon,
    this.value,
    this.validator,
    this.pickFiles,
  });

  @override
  ConsumerState<FileInputField> createState() => _FileInputFieldState();
}

class _FileInputFieldState extends ConsumerState<FileInputField> {
  bool _isLoading = false;

  Future<void> _pickFile() async {
    final l10n = AppLocalizations.of(context)!;
    setState(() => _isLoading = true);
    try {
      final picker = widget.pickFiles;
      final result = picker != null
          ? await picker()
          : await FilePicker.pickFiles(
              type: FileType.custom,
              allowedExtensions: const [
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
              withData: true,
            );

      if (!mounted) return;

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.single;
        widget.onFileSelected(file);
      }
    } catch (e, st) {
      if (!mounted) return;
      ref
          .read(loggerServiceProvider)
          .error('FileInputField', 'File Error: $e', e, st);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            l10n.errorReadingFile(AppExceptionX.extractLocalizedHint(e, l10n)),
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    try {
      if (widget.label.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: FileInputField label cannot be empty.',
        );
      }

      final currentFile = widget.value;
      if (currentFile != null) {
        if (currentFile.name.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Selected PlatformFile name cannot be empty.',
          );
        }
        if (currentFile.size < 0) {
          throw AppException.validation(
            'Fail-Fast: Selected PlatformFile size cannot be negative.',
          );
        }
      }

      final fileName = currentFile?.name;
      final hasFile = fileName != null;

      return FormField<PlatformFile>(
        key: ValueKey(currentFile),
        validator: widget.validator,
        initialValue: currentFile,
        builder: (state) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              InkWell(
                onTap: _pickFile,
                mouseCursor: SystemMouseCursors.click,
                borderRadius: BorderRadius.circular(AppSpacing.s4),
                child: InputDecorator(
                  decoration: InputDecoration(
                    labelText: widget.label,
                    border: const OutlineInputBorder(),
                    prefixIcon: widget.icon != null ? Icon(widget.icon) : null,
                    errorText: state.errorText,
                    suffixIcon: _isLoading
                        ? const Padding(
                            padding: AppSpacing.p12,
                            child: CircularProgressIndicator(
                              strokeWidth: AppSpacing.s2,
                            ),
                          )
                        : hasFile
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            mouseCursor: SystemMouseCursors.click,
                            onPressed: widget.onClear,
                          )
                        : const Icon(Icons.attach_file),
                  ),
                  child: Text(
                    fileName ?? l10n.selectFile,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: hasFile
                          ? theme.textTheme.bodyMedium?.color
                          : theme.hintColor,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
              if (hasFile)
                Padding(
                  padding: const EdgeInsets.only(
                    top: AppSpacing.s4,
                    left: AppSpacing.s12,
                  ),
                  child: Text(
                    l10n.fileInputLabel(currentFile!.name, currentFile.size),
                    style: theme.textTheme.bodySmall,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
            ],
          );
        },
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'FileInputField',
            'VALIDATION_FAILED: Failed to render FileInputField',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
