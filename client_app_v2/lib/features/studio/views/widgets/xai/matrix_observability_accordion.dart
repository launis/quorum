import 'package:flutter/material.dart';

/// Visualizes the internal scoring mechanics (true/false atoms) of a Matrix.
/// Uses pure Flexbox constraints (Row, Expanded) to guarantee 60fps responsiveness.
class MatrixObservabilityAccordion extends StatelessWidget {
  final int trueAtomsCount;
  final int falseAtomsCount;
  final String titleLabel;
  final String subtitleLabel;
  final String trueAtomsLabel;
  final String falseAtomsLabel;

  const MatrixObservabilityAccordion({
    super.key,
    required this.trueAtomsCount,
    required this.falseAtomsCount,
    required this.titleLabel,
    required this.subtitleLabel,
    required this.trueAtomsLabel,
    required this.falseAtomsLabel,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      elevation: 0,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.dividerColor),
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.analytics_outlined,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8.0),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        titleLabel,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        subtitleLabel,
                        style: theme.textTheme.bodySmall,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12.0),
            Row(
              children: [
                Expanded(
                  child: _buildGridItem(
                    context,
                    label: trueAtomsLabel,
                    value: trueAtomsCount.toString(),
                    isPositive: true,
                  ),
                ),
                const SizedBox(width: 8.0),
                Expanded(
                  child: _buildGridItem(
                    context,
                    label: falseAtomsLabel,
                    value: falseAtomsCount.toString(),
                    isPositive: false,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGridItem(
    BuildContext context, {
    required String label,
    required String value,
    required bool isPositive,
  }) {
    final theme = Theme.of(context);

    // Fallback to surfaceContainerHighest per new Material 3 standards
    final bgColor = theme.colorScheme.surfaceContainerHighest;

    final valueColor = isPositive
        ? Colors.green.shade700
        : theme.colorScheme.error;

    return Container(
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(6.0),
        border: Border.all(color: theme.dividerColor.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4.0),
          Text(
            value,
            style: theme.textTheme.titleMedium?.copyWith(
              color: valueColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
