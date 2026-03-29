import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
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

    // "Red Banner" Style (Now fully dynamic via FlexColorScheme)
    final backgroundColor = theme.colorScheme.errorContainer;
    final textColor = theme.colorScheme.onErrorContainer;
    final iconColor = theme.colorScheme.error;

    final content = Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: iconColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(Icons.error_outline, color: iconColor, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  _formatError(error, AppLocalizations.of(context)!),
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: textColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          if (onAction != null && actionLabel != null) ...[
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.arrow_forward, size: 16),
                label: Text(actionLabel!),
                style: FilledButton.styleFrom(
                  backgroundColor:
                      theme.colorScheme.primary, // Distinct from Error Color
                  foregroundColor: theme.colorScheme.onPrimary,
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ),
          ],
          if (onRetry != null) ...[
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                // Downgrade Retry to TextButton if Action is present? Or keep both?
                onPressed: onRetry,
                icon: const Icon(Icons.refresh, size: 16),
                label: Text(retryLabel ?? l10n.retry),
                style: TextButton.styleFrom(
                  foregroundColor: iconColor,
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ),
          ],
          if (kDebugMode && _getTechnicalDetails(error) != null) ...[
            const SizedBox(height: 16),
            Theme(
              data: Theme.of(
                context,
              ).copyWith(dividerColor: Colors.transparent),
              child: ExpansionTile(
                title: Text(
                  l10n.technicalDetails,
                  style: TextStyle(color: iconColor, fontSize: 12),
                ),
                tilePadding: EdgeInsets.zero,
                childrenPadding: const EdgeInsets.all(8),
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: SelectableText(
                      _getTechnicalDetails(error)!,
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 10,
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
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                title ?? l10n.systemError, // Or localized "System Error"
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: iconColor,
                ),
              ),
              const SizedBox(height: 24),
              content,
            ],
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
