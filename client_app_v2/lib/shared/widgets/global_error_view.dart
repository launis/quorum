import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **V3 Global Error View**
///
/// An isolated widget designed to present RFC 7807 structured errors and Actionable Hints.
/// Inherits graceful degradation (never throws if cast fails) and provides deterministic rendering.
class GlobalErrorView extends StatelessWidget {
  final Object error;
  final StackTrace? stackTrace;
  final VoidCallback? onAction;
  final String? actionLabel;
  final IconData? actionIcon;

  const GlobalErrorView({
    super.key,
    required this.error,
    this.stackTrace,
    this.onAction,
    this.actionLabel,
    this.actionIcon,
  });

  @override
  Widget build(BuildContext context) {
    debugPrint('🔴 V3 GRACEFUL DEGRADATION [GlobalErrorView Rendered]: $error');

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    // Default hints
    String hintText = AppExceptionX.extractLocalizedHint(error, l10n);
    String titleText = l10n.errorUnknown;
    String? rawDetail;

    if (error is AppException) {
      final appEx = error as AppException;
      titleText = '${l10n.sharedSystemError}: ${appEx.errorCode}';
      if (appEx.errorCode == 'TOOL_EXECUTION_FAILED') {
        titleText = l10n.toolExecutionFailed;
      }
      rawDetail = appEx.detail;
    } else if (error is String) {
      hintText = error as String;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s16,
        vertical: AppSpacing.s8,
      ),
      child: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          color: theme.colorScheme.errorContainer.withValues(alpha: 0.5),
          border: Border.all(
            color: theme.colorScheme.error.withValues(alpha: 0.3),
          ),
          borderRadius: BorderRadius.circular(AppSpacing.s12),
        ),
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  color: theme.colorScheme.error,
                  size: AppSpacing.s24,
                ),
                AppSpacing.w12,
                Expanded(
                  child: Text(
                    titleText,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.error,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            AppSpacing.h12,
            Text(
              hintText,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onErrorContainer,
              ),
            ),
            if (rawDetail != null &&
                rawDetail.isNotEmpty &&
                rawDetail != hintText) ...[
              AppSpacing.h12,
              Container(
                width: double.infinity,
                padding: AppSpacing.p12,
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface.withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(AppSpacing.s8),
                  border: Border.all(
                    color: theme.colorScheme.error.withValues(alpha: 0.2),
                  ),
                ),
                child: SelectableText(
                  rawDetail,
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontFamily: 'monospace',
                    color: theme.colorScheme.onErrorContainer.withValues(
                      alpha: 0.8,
                    ),
                    height: 1.4,
                  ),
                ),
              ),
            ],
            if (onAction != null && actionLabel != null) ...[
              AppSpacing.h16,
              Align(
                alignment: Alignment.centerRight,
                child: FilledButton.icon(
                  onPressed: onAction,
                  icon: Icon(actionIcon ?? Icons.refresh, size: AppSpacing.s16),
                  label: Text(actionLabel!, overflow: TextOverflow.ellipsis),
                  style: FilledButton.styleFrom(
                    enabledMouseCursor: SystemMouseCursors.click,
                    backgroundColor: theme.colorScheme.error,
                    foregroundColor: theme.colorScheme.onError,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
