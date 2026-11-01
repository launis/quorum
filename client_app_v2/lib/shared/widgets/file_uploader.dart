import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FileUploader extends ConsumerStatefulWidget {
  final String label;
  final ValueChanged<PlatformFile>? onFileSelected;
  final VoidCallback? onClear;
  final String? initialFileName;
  final bool isLoading;
  final String? errorText;
  final Future<FilePickerResult?> Function()? pickFiles;

  const FileUploader({
    super.key,
    required this.label,
    this.onFileSelected,
    this.onClear,
    this.initialFileName,
    this.isLoading = false,
    this.errorText,
    this.pickFiles,
  });

  @override
  ConsumerState<FileUploader> createState() => _FileUploaderState();
}

class _FileUploaderState extends ConsumerState<FileUploader> {
  String? _fileName;

  @override
  void initState() {
    super.initState();
    _fileName = widget.initialFileName;
  }

  @override
  void didUpdateWidget(covariant FileUploader oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialFileName != oldWidget.initialFileName) {
      _fileName = widget.initialFileName;
    }
  }

  Future<void> _pickFile() async {
    final l10n = AppLocalizations.of(context)!;
    try {
      final picker = widget.pickFiles;
      final result = picker != null
          ? await picker()
          : await FilePicker.pickFiles();

      if (!mounted) return;

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.single;
        if (file.name.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Selected PlatformFile name cannot be empty.',
          );
        }
        if (file.size < 0) {
          throw AppException.validation(
            'Fail-Fast: Selected PlatformFile size cannot be negative.',
          );
        }
        setState(() {
          _fileName = file.name;
        });
        widget.onFileSelected?.call(file);
      }
    } catch (e, st) {
      if (!mounted) return;
      ref
          .read(loggerServiceProvider)
          .error('FileUploader', 'File Uploader Error: $e', e, st);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(l10n.errorReadingFile('$e'))));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    try {
      if (widget.label.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: FileUploader label cannot be empty.',
        );
      }
      if (widget.initialFileName != null &&
          widget.initialFileName!.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: FileUploader initialFileName cannot be blank.',
        );
      }
      if (widget.errorText != null && widget.errorText!.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: FileUploader errorText cannot be blank.',
        );
      }

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  widget.label,
                  style: theme.textTheme.labelMedium,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          AppSpacing.h8,
          InkWell(
            onTap: widget.isLoading ? null : _pickFile,
            mouseCursor: widget.isLoading
                ? SystemMouseCursors.basic
                : SystemMouseCursors.click,
            borderRadius: BorderRadius.circular(AppSpacing.s8),
            child: Container(
              padding: AppSpacing.p12,
              decoration: BoxDecoration(
                border: Border.all(
                  color: widget.errorText != null
                      ? theme.colorScheme.error
                      : theme.colorScheme.outline,
                ),
                borderRadius: BorderRadius.circular(AppSpacing.s8),
              ),
              child: Row(
                children: [
                  if (widget.isLoading)
                    const SizedBox(
                      width: AppSpacing.s24,
                      height: AppSpacing.s24,
                      child: CircularProgressIndicator(
                        strokeWidth: AppSpacing.s2,
                      ),
                    )
                  else
                    Icon(Icons.attach_file, color: theme.colorScheme.primary),
                  AppSpacing.w12,
                  Expanded(
                    child: Text(
                      widget.isLoading
                          ? l10n.sharedUploading
                          : (_fileName ?? l10n.sharedSelectFile),
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: (widget.isLoading || _fileName != null)
                            ? theme.colorScheme.onSurface
                            : theme.colorScheme.onSurfaceVariant,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (!widget.isLoading && _fileName != null)
                    IconButton(
                      icon: const Icon(Icons.close),
                      mouseCursor: SystemMouseCursors.click,
                      onPressed: () {
                        setState(() {
                          _fileName = null;
                        });
                        widget.onClear?.call();
                      },
                    ),
                ],
              ),
            ),
          ),
          if (widget.errorText != null)
            Padding(
              padding: const EdgeInsets.only(top: AppSpacing.s4),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      widget.errorText!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.error,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
        ],
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'FileUploader',
            'VALIDATION_FAILED: Failed to render FileUploader',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
