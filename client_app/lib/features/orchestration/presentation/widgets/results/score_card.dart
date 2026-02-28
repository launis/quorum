import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class ScoreCard extends StatelessWidget {
  final String label;
  final double? value;
  final double? maxValue;
  final String? description;
  final double? previousValue; // For dual matrix comparison

  const ScoreCard({
    super.key,
    required this.label,
    required this.value,
    this.maxValue = 5.0,
    this.description,
    this.previousValue,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (value == null) {
      debugPrint("🔴 UI GRACEFUL DEGRADATION: Rendered ScoreCard '\$label' with null value -> fallback 'Data unavailable'");
      return Card(
        elevation: 0,
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              if (description != null && description!.isNotEmpty) ...[
                Text(
                  description!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 8),
              ],
              Text(
                "Tietoja ei saatavilla (Data unavailable)",
                style: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
      );
    }

    // Calculate color based on value/max ratio
    final ratio = value! / (maxValue ?? 5.0);
    final scoreColor =
        Color.lerp(Colors.red, Colors.green, ratio) ?? Colors.grey;

    return Card(
      elevation: 0,
      color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    label,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: scoreColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: scoreColor.withValues(alpha: 0.2),
                    ),
                  ),
                  child: Text(
                    _formatScore(context, value!),
                    style: theme.textTheme.labelLarge?.copyWith(
                      color: scoreColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            if (previousValue != null) ...[
              const SizedBox(height: 4),
              _buildComparison(context, value!, previousValue!),
            ],
            if (description != null && description!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                description!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildComparison(BuildContext context, double current, double prev) {
    final delta = current - prev;
    if (delta == 0) return const SizedBox.shrink();

    final isPositive = delta > 0;
    final color = isPositive ? Colors.green : Colors.red;
    final icon = isPositive ? Icons.arrow_upward : Icons.arrow_downward;

    return Row(
      children: [
        Icon(icon, size: 12, color: color),
        const SizedBox(width: 4),
        Text(
          '\${NumberFormat.decimalPatternDigits(locale: Localizations.localeOf(context).toString(), decimalDigits: 1).format(delta.abs())} (vs prev)',
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(color: color, fontSize: 10),
        ),
      ],
    );
  }

  String _formatScore(BuildContext context, double val) {
    final locale = Localizations.localeOf(context).toString();
    final fmt = NumberFormat.decimalPattern(locale);

    if (val % 1 == 0) {
      return fmt.format(val.toInt());
    }

    final decimalFmt = NumberFormat.decimalPatternDigits(
      locale: locale,
      decimalDigits: 1,
    );
    return decimalFmt.format(val);
  }
}
