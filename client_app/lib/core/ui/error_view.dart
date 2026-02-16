import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_error.dart';
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
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    // "Red Banner" Style
    final backgroundColor =
        isDark ? theme.colorScheme.errorContainer : Colors.red.shade50;
    final textColor =
        isDark ? theme.colorScheme.onErrorContainer : Colors.red.shade900;
    final iconColor = isDark ? theme.colorScheme.error : Colors.red.shade700;

    final content = Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: iconColor.withOpacity(0.3)),
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
                  backgroundColor: theme.colorScheme.primary, // Distinct from Error Color
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
              child: TextButton.icon( // Downgrade Retry to TextButton if Action is present? Or keep both?
                onPressed: onRetry,
                icon: const Icon(Icons.refresh, size: 16),
                label: Text(retryLabel ?? 'Retry'),
                style: TextButton.styleFrom(
                   foregroundColor: iconColor,
                   visualDensity: VisualDensity.compact,
                ),
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
                title ?? 'Järjestelmävirhe', // Or localized "System Error"
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
    if (error is AppError) {
      return error.maybeMap(
        unknown: (wrapper) {
          final raw =
              wrapper.error?.toString().replaceAll('Exception: ', '') ?? '';
          if (raw.isNotEmpty) return raw;
          return error.message(l10n);
        },
        orElse: () => error.message(l10n),
      );
    }
    // Keep it clean but detailed enough for debugging if needed
    return error.toString().replaceAll('Exception: ', '');
  }
}
