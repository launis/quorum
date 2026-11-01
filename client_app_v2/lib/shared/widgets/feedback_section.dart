import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FeedbackSection extends ConsumerWidget {
  final String title;
  final List<String> items;
  final IconData icon;
  final Color? color;

  const FeedbackSection({
    super.key,
    required this.title,
    required this.items,
    this.icon = Icons.lightbulb_outline,
    this.color,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (items.isEmpty) {
      return const SizedBox();
    }

    final theme = Theme.of(context);

    try {
      if (title.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: FeedbackSection title cannot be empty.',
        );
      }
      for (final item in items) {
        if (item.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: FeedbackSection item cannot be empty.',
          );
        }
      }

      final baseColor = color ?? theme.colorScheme.primary;

      return Card(
        elevation: 0,
        color: theme.colorScheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
          side: BorderSide(color: theme.colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, color: baseColor, size: 20),
                  AppSpacing.w8,
                  Expanded(
                    child: Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ),
                ],
              ),
              AppSpacing.h12,
              ...items.map(
                (item) => Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(top: AppSpacing.s6),
                        child: Icon(
                          Icons.circle,
                          size: AppSpacing.s6,
                          color: baseColor.withValues(alpha: 0.6),
                        ),
                      ),
                      AppSpacing.w12,
                      Expanded(
                        child: Text(
                          item,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            height: 1.5,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'FeedbackSection',
            'VALIDATION_FAILED: Failed to render feedback section',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
