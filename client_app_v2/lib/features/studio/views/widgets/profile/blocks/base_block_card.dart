import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Canonical container widget wrapping every block card with header icon,
/// localized title, drag handle, and Universal Baseline Switch.
class BaseBlockCard extends StatelessWidget {
  final TargetBlockType blockType;
  final String title;
  final String? subtitle;
  final IconData icon;
  final bool isIncluded;
  final ValueChanged<bool> onToggle;
  final Widget? body;
  final Widget? dragHandle;

  const BaseBlockCard({
    super.key,
    required this.blockType,
    required this.title,
    this.subtitle,
    required this.icon,
    required this.isIncluded,
    required this.onToggle,
    this.body,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(
          color: isIncluded
              ? colorScheme.outlineVariant
              : colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
      ),
      color: isIncluded
          ? colorScheme.surfaceContainer
          : colorScheme.surfaceContainerLow.withValues(alpha: 0.6),
      child: Padding(
        padding: AppSpacing.p12,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  size: 20,
                  color: isIncluded
                      ? colorScheme.primary
                      : colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: AppSpacing.s12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: isIncluded
                              ? colorScheme.onSurface
                              : colorScheme.onSurfaceVariant,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (subtitle != null && subtitle!.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          subtitle!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
                Switch(value: isIncluded, onChanged: onToggle),
                if (dragHandle != null) ...[
                  const SizedBox(width: AppSpacing.s8),
                  dragHandle!,
                ],
              ],
            ),
            if (isIncluded && body != null) ...[
              const SizedBox(height: AppSpacing.s8),
              const Divider(),
              const SizedBox(height: AppSpacing.s8),
              body!,
            ],
          ],
        ),
      ),
    );
  }
}
