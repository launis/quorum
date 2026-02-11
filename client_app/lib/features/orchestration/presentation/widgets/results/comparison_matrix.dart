import 'package:flutter/material.dart';

class ComparisonMatrix extends StatelessWidget {
  final Map<String, dynamic> comparisonData;

  const ComparisonMatrix({super.key, required this.comparisonData});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final leftLabel = comparisonData['left_label'] as String? ?? 'Judge A';
    final rightLabel = comparisonData['right_label'] as String? ?? 'Judge B';
    final rowsRaw = comparisonData['rows'] as List?;
    final rows = rowsRaw?.cast<Map<String, dynamic>>() ?? [];

    if (rows.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No comparison data available.'),
        ),
      );
    }

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Comparative Evaluation',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            // Header
            Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Text(
                    'Dimension',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.secondary,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    leftLabel,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.secondary,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    rightLabel,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.secondary,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    'Delta',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.secondary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
            const Divider(),
            // Rows
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: rows.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                return _buildRow(context, rows[index], leftLabel, rightLabel);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRow(
    BuildContext context,
    Map<String, dynamic> row,
    String leftLabel,
    String rightLabel,
  ) {
    final theme = Theme.of(context);
    final dimension = row['dimension'] as String? ?? 'N/A';
    final left = row['left'] as Map<String, dynamic>?;
    final right = row['right'] as Map<String, dynamic>?;
    final delta = (row['delta'] as num?)?.toDouble() ?? 0.0;

    // Safely extract scores
    final sLeft = left?['score'] as num? ?? 0;
    final sRight = right?['score'] as num? ?? 0;

    // Reasoning
    final rLeft = left?['reasoning'] as String?;
    final rRight = right?['reasoning'] as String?;

    return Semantics(
      excludeSemantics: Platform.isWindows,
      child: ExpansionTile(
        title: Row(
          children: [
            Expanded(
              flex: 3,
              child: Text(
                dimension.toUpperCase(),
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Expanded(
              flex: 2,
              child: Text(
                sLeft.toString(),
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            Expanded(
              flex: 2,
              child: Text(
                sRight.toString(),
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            Expanded(flex: 2, child: _renderDelta(delta)),
          ],
        ),
        shape: const Border(),
        childrenPadding: const EdgeInsets.all(12),
        children: [
          if (rLeft != null) _reasoningBlock(context, leftLabel, rLeft),
          if (rLeft != null && rRight != null) const SizedBox(height: 8),
          if (rRight != null) _reasoningBlock(context, rightLabel, rRight),
        ],
      ),
    );
  }

  Widget _renderDelta(double delta) {
    if (delta == 0) return const Center(child: Text('='));
    final isPos = delta > 0;
    final color = isPos ? Colors.green : Colors.red;
    final icon = isPos ? Icons.arrow_upward : Icons.arrow_downward;

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 12, color: color),
        Text(
          delta.abs().toStringAsFixed(1),
          style: TextStyle(color: color, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _reasoningBlock(BuildContext context, String label, String text) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label:',
          style: Theme.of(
            context,
          ).textTheme.labelSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        Text(text, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}
