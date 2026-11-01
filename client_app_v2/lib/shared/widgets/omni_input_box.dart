import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/file_input_field.dart';
import 'package:client_app/shared/widgets/pdf_export_guide_dialog.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class OmniInputBox extends ConsumerStatefulWidget {
  final String label;
  final String keyName;
  final Object? currentValue;
  final IconData? icon;
  final int minLines;
  final ValueChanged<Object?> onChanged;
  final Future<FilePickerResult?> Function()? pickFiles;

  const OmniInputBox({
    super.key,
    required this.label,
    required this.keyName,
    this.currentValue,
    this.icon,
    this.minLines = 1,
    required this.onChanged,
    this.pickFiles,
  });

  @override
  ConsumerState<OmniInputBox> createState() => _OmniInputBoxState();
}

class _OmniInputBoxState extends ConsumerState<OmniInputBox> {
  late bool _isFileMode;

  @override
  void initState() {
    super.initState();
    _isFileMode = widget.currentValue is PlatformFile;
  }

  @override
  void didUpdateWidget(covariant OmniInputBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.currentValue != oldWidget.currentValue &&
        widget.currentValue != null) {
      if (widget.currentValue is PlatformFile && !_isFileMode) {
        _isFileMode = true;
      } else if (widget.currentValue is String && _isFileMode) {
        _isFileMode = false;
      }
    }
  }

  Widget _buildModeSelector(AppLocalizations l10n) {
    return SegmentedButton<bool>(
      showSelectedIcon: false,
      segments: [
        ButtonSegment<bool>(
          value: false,
          icon: const Icon(Icons.text_fields, size: AppSpacing.s16),
          label: Text(
            l10n.pasteText,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        ButtonSegment<bool>(
          value: true,
          icon: const Icon(Icons.upload_file, size: AppSpacing.s16),
          label: Text(
            l10n.uploadFile,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
      selected: {_isFileMode},
      onSelectionChanged: (Set<bool> newSelection) {
        setState(() {
          _isFileMode = newSelection.first;
        });
        // Clear the state when switching modes to avoid sending stale text in file mode.
        widget.onChanged(null);
      },
    );
  }

  Widget _buildTitleAndHelpRow(
    BuildContext context,
    ThemeData theme,
    AppLocalizations l10n,
  ) {
    return Row(
      children: [
        if (widget.icon != null) ...[
          Icon(
            widget.icon,
            size: AppSpacing.s24,
            color: theme.colorScheme.primary,
          ),
          AppSpacing.w8,
        ],
        Expanded(
          child: Text(
            widget.label,
            style: theme.textTheme.titleMedium,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        IconButton(
          icon: const Icon(Icons.help_outline, size: AppSpacing.s24),
          tooltip: l10n.chatIngressGuideTooltip,
          mouseCursor: SystemMouseCursors.click,
          onPressed: () {
            showDialog<void>(
              context: context,
              builder: (context) => const PdfExportGuideDialog(),
            );
          },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    try {
      if (widget.label.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: OmniInputBox label cannot be empty.',
        );
      }
      if (widget.keyName.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: OmniInputBox keyName cannot be empty.',
        );
      }
      if (widget.minLines < 1) {
        throw AppException.validation(
          'Fail-Fast: OmniInputBox minLines must be at least 1.',
        );
      }

      final currentVal = widget.currentValue;
      if (currentVal != null &&
          currentVal is! String &&
          currentVal is! PlatformFile) {
        throw AppException.validation(
          'Fail-Fast: OmniInputBox currentValue must be a String, PlatformFile, or null.',
        );
      }

      if (currentVal is PlatformFile) {
        if (currentVal.name.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Selected PlatformFile name cannot be empty.',
          );
        }
        if (currentVal.size < 0) {
          throw AppException.validation(
            'Fail-Fast: Selected PlatformFile size cannot be negative.',
          );
        }
      }

      final PlatformFile? fileValue = switch (currentVal) {
        final PlatformFile file => file,
        _ => null,
      };
      final String textValue = switch (currentVal) {
        final String text => text,
        _ => '',
      };

      return Card(
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
          side: BorderSide(color: theme.colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              LayoutBuilder(
                builder: (context, constraints) {
                  if (constraints.maxWidth < 460) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _buildTitleAndHelpRow(context, theme, l10n),
                        AppSpacing.h8,
                        Align(
                          alignment: Alignment.centerLeft,
                          child: FittedBox(
                            fit: BoxFit.scaleDown,
                            child: _buildModeSelector(l10n),
                          ),
                        ),
                      ],
                    );
                  }
                  return Row(
                    children: [
                      Expanded(
                        child: _buildTitleAndHelpRow(context, theme, l10n),
                      ),
                      AppSpacing.w8,
                      Flexible(
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          child: _buildModeSelector(l10n),
                        ),
                      ),
                    ],
                  );
                },
              ),
              AppSpacing.h16,
              if (_isFileMode && widget.keyName == 'chat_log') ...[
                Container(
                  padding: AppSpacing.p12,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.errorContainer.withValues(
                      alpha: 0.2,
                    ),
                    borderRadius: BorderRadius.circular(AppSpacing.s8),
                    border: Border.all(
                      color: theme.colorScheme.error.withValues(alpha: 0.5),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.warning_amber_rounded,
                        color: theme.colorScheme.error,
                        size: AppSpacing.s24,
                      ),
                      AppSpacing.w8,
                      Expanded(
                        child: Text(
                          l10n.chatGptPdfTruncationWarning,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.error,
                          ),
                          maxLines: 4,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                AppSpacing.h12,
              ],
              if (_isFileMode)
                FileInputField(
                  label: widget.label,
                  icon: widget.icon,
                  value: fileValue,
                  pickFiles: widget.pickFiles,
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
                  initialValue: textValue,
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
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'OmniInputBox',
            'VALIDATION_FAILED: Failed to render OmniInputBox',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
