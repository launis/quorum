import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LogViewer extends ConsumerWidget {
  final List<String> logs;

  const LogViewer({super.key, required this.logs});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final semanticColors = context.semanticColors;
    final l10n = AppLocalizations.of(context)!;

    try {
      for (final logEntry in logs) {
        if (logEntry.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: LogViewer entry cannot be empty or whitespace-only.',
          );
        }
      }

      return Container(
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(AppSpacing.s8),
          border: Border.all(color: theme.colorScheme.onSurfaceVariant),
        ),
        width: double.infinity,
        padding: AppSpacing.p12,
        child: logs.isEmpty
            ? Center(
                child: Text(
                  l10n.sharedNoLogsAvailable,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontFamily: 'monospace',
                  ),
                ),
              )
            : ListView.builder(
                itemCount: logs.length,
                itemBuilder: (context, index) {
                  return Text(
                    logs[index],
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: semanticColors.success,
                      fontFamily: 'monospace',
                    ),
                  );
                },
              ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'LogViewer',
            'VALIDATION_FAILED: Failed to render log entries',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
