import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class OutputRenderer extends ConsumerWidget {
  final String markdownContent;

  const OutputRenderer({super.key, required this.markdownContent});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    try {
      if (markdownContent.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: OutputRenderer markdownContent cannot be empty or whitespace-only.',
        );
      }

      // Normalize HTML <br> tags from raw extractions into single spaces.
      final renderedContent = markdownContent.replaceAll(
        RegExp(r'<br\s*\/?>', caseSensitive: false),
        ' ',
      );

      if (renderedContent.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: OutputRenderer renderedContent cannot be empty after HTML <br> sanitization.',
        );
      }

      return MarkdownBody(
        data: renderedContent,
        selectable: true,
        styleSheet: MarkdownStyleSheet(
          h1: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          h2: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          p: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
          code: theme.textTheme.bodySmall?.copyWith(
            backgroundColor: theme.colorScheme.surfaceContainerHighest,
            color: theme.colorScheme.onSurfaceVariant,
            fontFamily: 'monospace',
          ),
          codeblockDecoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(AppSpacing.s4),
          ),
          blockquote: theme.textTheme.bodyMedium?.copyWith(
            fontStyle: FontStyle.italic,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          blockquoteDecoration: BoxDecoration(
            border: Border(
              left: BorderSide(
                color: theme.colorScheme.primary,
                width: AppSpacing.s4,
              ),
            ),
            color: theme.colorScheme.surfaceContainerLowest,
          ),
          blockquotePadding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s16,
            vertical: AppSpacing.s8,
          ),
          listBullet: theme.textTheme.bodyMedium,
          listIndent: AppSpacing.s24,
          tableBorder: TableBorder.all(color: theme.colorScheme.outlineVariant),
          tableHead: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          tableBody: theme.textTheme.bodyMedium,
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'OutputRenderer',
            'VALIDATION_FAILED: Failed to render markdown output',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
