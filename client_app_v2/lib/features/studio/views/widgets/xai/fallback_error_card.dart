import 'package:client_app/core/theme/app_spacing.dart';
import 'package:flutter/material.dart';

/// Renders a graceful degradation card when an XAI extension is missing or malformed.
/// Strictly mimics the PDF System Notification Banner (border-left: 4px solid).
class FallbackErrorCard extends StatelessWidget {
  final String title;
  final String message;

  const FallbackErrorCard({
    super.key,
    required this.title,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: theme.colorScheme.errorContainer.withValues(alpha: 0.5),
        border: Border(
          left: BorderSide(
            color: theme.colorScheme.error,
            width: AppSpacing.s4,
          ),
          top: BorderSide(color: theme.dividerColor),
          right: BorderSide(color: theme.dividerColor),
          bottom: BorderSide(color: theme.dividerColor),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.warning_amber_rounded,
                color: theme.colorScheme.error,
                size: AppSpacing.s16,
              ),
              AppSpacing.w8,
              Expanded(
                child: Text(
                  title,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.error,
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          AppSpacing.h4,
          Text(
            message,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onErrorContainer,
            ),
          ),
        ],
      ),
    );
  }
}
