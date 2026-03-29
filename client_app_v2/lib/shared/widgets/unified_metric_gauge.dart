import 'package:client_app/theme/app_durations.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class UnifiedMetricGauge extends StatelessWidget {
  final String label;
  final double value;
  final double max;
  final String description; // Primary localized description
  final String?
  descriptionSecondary; // Optional secondary (e.g. English fallback)
  final String displayValue; // e.g. "4/6" or "High"
  final Color? color;
  final List<String>? axisLabels;
  final bool
  isOrdinal; // If true, only highlights the current segment instead of all segments up to it.

  const UnifiedMetricGauge({
    super.key,
    required this.label,
    required this.value,
    required this.max,
    required this.description,
    this.descriptionSecondary,
    required this.displayValue,
    this.color,
    this.axisLabels,
    this.isOrdinal = false,
  });

  @override
  Widget build(BuildContext context) {
    if (label.trim().isEmpty) {
      throw FormatException("UnifiedMetricGauge requires a non-empty label.");
    }
    if (displayValue.trim().isEmpty) {
      throw FormatException(
        "UnifiedMetricGauge requires a non-empty displayValue for '$label'.",
      );
    }

    if (max <= 0) {
      throw FormatException(
        "UnifiedMetricGauge '$label' requires max > 0, got $max.",
      );
    }
    if (value < 0 || value > max) {
      throw FormatException(
        "UnifiedMetricGauge '$label' value $value is out of bounds [0, $max].",
      );
    }

    final theme = Theme.of(context);
    final effectiveColor = color ?? theme.primaryColor;

    // Segment logic
    final int totalSegments = max.toInt();
    final int filledSegments = value.toInt();

    final mainRow = Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          // 1. Label
          SizedBox(
            width: 140,
            child: Tooltip(
              message: description,
              waitDuration: AppDurations.medium,
              showDuration: AppDurations.display,
              child: Text(
                label,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ),

          // 2. Segmented Bar
          Expanded(
            child: SizedBox(
              height: 12, // Compact height
              child: Row(
                children: List.generate(totalSegments, (index) {
                  final isFilled =
                      isOrdinal
                          ? (index == filledSegments - 1)
                          : (index < filledSegments);
                  return Expanded(
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 1.0),
                      decoration: BoxDecoration(
                        color:
                            isFilled
                                ? effectiveColor
                                : Theme.of(
                                  context,
                                ).colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),
          const SizedBox(width: 12),

          // 3. Display Value
          SizedBox(
            width: 60,
            child: Text(
              displayValue,
              textAlign: TextAlign.end,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ),

          // 4. Mandatory Bilingual Help Trigger
          const SizedBox(width: 8),
          _buildHelpTrigger(context),
        ],
      ),
    );

    if (axisLabels == null || axisLabels!.isEmpty) {
      return mainRow;
    }

    // Render labels under the bar
    // We need to align them with the bar, so we use the same flex ratio or padding
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        mainRow,
        Row(
          children: [
            // Spacer for Label (width 140)
            const SizedBox(width: 140),
            // Labels
            Expanded(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: _buildAlignedLabels(
                  context,
                  axisLabels!,
                  totalSegments,
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Spacer for DisplayValue (width 60)
            const SizedBox(width: 60),
            const SizedBox(width: 8),
            // Spacer for Icon (approx 24)
            const SizedBox(width: 24),
          ],
        ),
      ],
    );
  }

  Widget _buildHelpTrigger(BuildContext context) {
    return GestureDetector(
      onTap: () => _showHelpDialog(context),
      child: Icon(
        Icons.help_outline,
        size: 16,
        color: Theme.of(context).colorScheme.onSurfaceVariant,
      ),
    );
  }

  void _showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  size: 20,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(description, style: const TextStyle(fontSize: 14)),
                if (descriptionSecondary != null) ...[
                  const SizedBox(height: 12),
                  const Divider(),
                  const SizedBox(height: 8),
                  Text(
                    descriptionSecondary!,
                    style: TextStyle(
                      fontSize: 13,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: Text(AppLocalizations.of(context)?.sharedOk ?? "OK"),
              ),
            ],
          ),
    );
  }

  List<Widget> _buildAlignedLabels(
    BuildContext context,
    List<String> labels,
    int segmentCount,
  ) {
    if (labels.length == segmentCount) {
      return labels
          .map(
            (l) => Expanded(
              child: Text(
                l,
                textAlign: TextAlign.center,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 8,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          )
          .toList();
    }

    return labels
        .map(
          (l) => Text(
            l,
            style: TextStyle(
              fontSize: 9,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        )
        .toList();
  }
}
