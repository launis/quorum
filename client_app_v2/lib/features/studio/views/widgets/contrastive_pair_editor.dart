import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Semantic contrastive calibration pair editor with live character counters,
/// duplicate detection, and responsive <520px layout stacking.
class ContrastivePairEditor extends StatefulWidget {
  final ContrastivePairDTO? initialValue;
  final ValueChanged<ContrastivePairDTO?> onChanged;
  final bool enabled;

  const ContrastivePairEditor({
    super.key,
    this.initialValue,
    required this.onChanged,
    this.enabled = true,
  });

  @override
  State<ContrastivePairEditor> createState() => _ContrastivePairEditorState();
}

class _ContrastivePairEditorState extends State<ContrastivePairEditor> {
  late final TextEditingController _acceptableController;
  late final TextEditingController _rejectedController;

  @override
  void initState() {
    super.initState();
    _acceptableController = TextEditingController(
      text: widget.initialValue?.acceptable ?? '',
    );
    _rejectedController = TextEditingController(
      text: widget.initialValue?.rejected ?? '',
    );
  }

  @override
  void didUpdateWidget(ContrastivePairEditor oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialValue != widget.initialValue) {
      final newAcc = widget.initialValue?.acceptable ?? '';
      final newRej = widget.initialValue?.rejected ?? '';
      if (_acceptableController.text != newAcc ||
          _rejectedController.text != newRej) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) {
            if (_acceptableController.text != newAcc) {
              _acceptableController.text = newAcc;
            }
            if (_rejectedController.text != newRej) {
              _rejectedController.text = newRej;
            }
          }
        });
      }
    }
  }

  @override
  void dispose() {
    _acceptableController.dispose();
    _rejectedController.dispose();
    super.dispose();
  }

  void _notifyChanged() {
    final acc = _acceptableController.text;
    final rej = _rejectedController.text;
    if (acc.trim().isEmpty && rej.trim().isEmpty) {
      widget.onChanged(null);
    } else {
      widget.onChanged(ContrastivePairDTO(acceptable: acc, rejected: rej));
    }
    setState(() {});
  }

  Widget _buildField({
    required BuildContext context,
    required TextEditingController controller,
    required String label,
    required String helper,
    required bool isAcceptable,
  }) {
    final theme = Theme.of(context);
    final count = controller.text.length;
    final isMinMet = count >= 10;
    final counterColor = count == 0
        ? theme.colorScheme.onSurfaceVariant
        : (isMinMet ? theme.colorScheme.primary : theme.colorScheme.error);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        TextFormField(
          controller: controller,
          enabled: widget.enabled,
          maxLines: 3,
          minLines: 2,
          onChanged: (_) => _notifyChanged(),
          decoration: InputDecoration(
            labelText: label,
            helperText: helper,
            helperMaxLines: 2,
            alignLabelWithHint: true,
            border: const OutlineInputBorder(),
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: isAcceptable
                    ? theme.colorScheme.primary.withValues(alpha: 0.5)
                    : theme.colorScheme.error.withValues(alpha: 0.5),
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: isAcceptable
                    ? theme.colorScheme.primary
                    : theme.colorScheme.error,
                width: 2,
              ),
            ),
          ),
        ),
        AppSpacing.h4,
        Align(
          alignment: Alignment.centerRight,
          child: Text(
            '$count/10 chars',
            style: theme.textTheme.labelSmall?.copyWith(
              color: counterColor,
              fontWeight: isMinMet ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context);
    final accText = _acceptableController.text.trim();
    final rejText = _rejectedController.text.trim();
    final isIdentical =
        accText.isNotEmpty &&
        rejText.isNotEmpty &&
        accText.toLowerCase() == rejText.toLowerCase();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (isIdentical)
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: AppSpacing.p8,
            decoration: BoxDecoration(
              color: theme.colorScheme.errorContainer,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.error_outline,
                  size: 18,
                  color: theme.colorScheme.onErrorContainer,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n?.scaleContrastiveIdenticalError ??
                        'Examples cannot be identical.',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onErrorContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        LayoutBuilder(
          builder: (context, constraints) {
            final acceptableWidget = _buildField(
              context: context,
              controller: _acceptableController,
              label:
                  l10n?.scaleAcceptableExampleLabel ??
                  'Approved Example (Acceptable)',
              helper:
                  l10n?.scaleAcceptableExampleHelper ??
                  'Example satisfying this requirement.',
              isAcceptable: true,
            );
            final rejectedWidget = _buildField(
              context: context,
              controller: _rejectedController,
              label:
                  l10n?.scaleRejectedExampleLabel ??
                  'Rejected Counterpart (Rejected)',
              helper:
                  l10n?.scaleRejectedExampleHelper ??
                  'Example rejected from this level.',
              isAcceptable: false,
            );

            if (constraints.maxWidth >= 520) {
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: acceptableWidget),
                  AppSpacing.w16,
                  Expanded(child: rejectedWidget),
                ],
              );
            } else {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [acceptableWidget, AppSpacing.h12, rejectedWidget],
              );
            }
          },
        ),
      ],
    );
  }
}
