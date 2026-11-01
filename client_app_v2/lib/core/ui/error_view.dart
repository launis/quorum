import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// A consistent full-screen or sectional error view that mimics the backend's "Critical Failure" style.
///
/// Use this instead of ad-hoc `Center(child: Text(...))` for `AsyncValue.error` states.
class ErrorView extends StatelessWidget {
  final Object error;
  final StackTrace? stackTrace;
  final VoidCallback? onRetry;
  final String? retryLabel;
  final VoidCallback? onAction;
  final String? actionLabel;
  final String? title;
  final bool compact;

  const ErrorView({
    super.key,
    required this.error,
    this.stackTrace,
    this.title,
    this.onRetry,
    this.retryLabel,
    this.onAction,
    this.actionLabel,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    // DEVELOPER VISIBILITY MANDATE: Ensure no UI degradation is completely silent
    debugPrint('🔴 UI DIAGNOSTIC NODE [ErrorView rendered]: $error');

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final backgroundColor = theme.colorScheme.errorContainer;
    final textColor = theme.colorScheme.onErrorContainer;
    final iconColor = theme.colorScheme.error;
    final currentActionLabel = actionLabel;
    final technicalDetails = _getTechnicalDetails(error);

    final content = Container(
      padding: AppSpacing.p16,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(AppSpacing.s12),
        border: Border.all(color: iconColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(Icons.error_outline, color: iconColor, size: AppSpacing.s24),
              AppSpacing.w12,
              Expanded(
                child: Text(
                  _formatError(error, l10n),
                  maxLines: 6,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: textColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          if (onAction != null && currentActionLabel != null) ...[
            AppSpacing.h12,
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.arrow_forward, size: AppSpacing.s16),
                label: Text(
                  currentActionLabel,
                  overflow: TextOverflow.ellipsis,
                ),
                style: FilledButton.styleFrom(
                  backgroundColor: theme.colorScheme.primary,
                  foregroundColor: theme.colorScheme.onPrimary,
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ),
          ],
          if (onRetry != null) ...[
            AppSpacing.h12,
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh, size: AppSpacing.s16),
                label: Text(
                  retryLabel ?? l10n.retry,
                  overflow: TextOverflow.ellipsis,
                ),
                style: TextButton.styleFrom(
                  foregroundColor: iconColor,
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ),
          ],
          if (kDebugMode && technicalDetails != null) ...[
            AppSpacing.h16,
            Theme(
              data: theme.copyWith(
                dividerColor: theme.colorScheme.surface.withValues(alpha: 0.0),
              ),
              child: ExpansionTile(
                title: Text(
                  l10n.technicalDetails,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: iconColor,
                  ),
                ),
                tilePadding: EdgeInsets.zero,
                childrenPadding: AppSpacing.p8,
                children: [
                  Container(
                    width: double.infinity,
                    padding: AppSpacing.p8,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(AppSpacing.s4),
                    ),
                    child: SelectableText(
                      technicalDetails,
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontFamily: 'monospace',
                        color: textColor,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );

    if (compact) {
      return content;
    }

    return Center(
      child: SingleChildScrollView(
        child: Padding(
          padding: AppSpacing.p24,
          child: ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: AppSpacing.s300 + AppSpacing.s300,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  title ?? l10n.systemError,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: iconColor,
                  ),
                ),
                AppSpacing.h24,
                content,
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _formatError(Object error, AppLocalizations l10n) {
    // FAIL-FAST MANDATE / NO-STRING MANDATE:
    // Raw exceptions (DioException, FormatException) must never leak their toString to the UI.
    // Always map through the centralized localized extractor.
    return AppExceptionX.extractLocalizedHint(error, l10n);
  }

  String? _getTechnicalDetails(Object error) {
    if (error is DioException && error.error is AppException) {
      return _getTechnicalDetails(error.error!);
    }
    if (error is AppException) {
      return 'Code: ${error.errorCode}\nStatus: ${error.status}\nType: ${error.type}\nInstance: ${error.instance}\nDetail: ${error.detail}';
    }
    return null;
  }
}
