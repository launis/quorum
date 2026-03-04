import 'package:flutter/material.dart';

class GenericGrid extends StatelessWidget {
  final String title;
  final Map<String, dynamic> data;

  const GenericGrid({super.key, required this.title, required this.data});

  @override
  Widget build(BuildContext context) {
    final items = data['items'] as List<dynamic>? ?? [];

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      clipBehavior: Clip.antiAlias,
      child: Container(
        decoration: const BoxDecoration(
          border: Border(left: BorderSide(color: Colors.blueGrey, width: 4)),
        ),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: Colors.blueGrey[800]),
            ),
            const SizedBox(height: 16),
            LayoutBuilder(
              builder: (context, constraints) {
                final double itemWidth = (constraints.maxWidth - 16) / 2;
                return Wrap(
                  spacing: 16,
                  runSpacing: 12,
                  children: items.map((item) {
                    final itemMap = item as Map<String, dynamic>;
                    final label = itemMap['label'] ?? '';
                    final value = itemMap['value']?.toString() ?? 'N/A';
                    final highlight = itemMap['highlight'] == true;

                    return SizedBox(
                      width: itemWidth,
                      child: Container(
                        padding: const EdgeInsets.all(8.0),
                        decoration: BoxDecoration(
                          color: highlight ? Colors.deepPurple.withOpacity(0.05) : Colors.grey.shade50,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: highlight ? Colors.deepPurple.shade100 : Colors.grey.shade200),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              label,
                              style: Theme.of(
                                context,
                              ).textTheme.labelSmall?.copyWith(color: Colors.grey[600], fontSize: 10, fontWeight: FontWeight.bold),
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 2),
                            Text(
                              value,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontSize: 14,
                                fontWeight:
                                    highlight ? FontWeight.bold : FontWeight.w600,
                                color:
                                    highlight
                                        ? Colors.deepPurple[700]
                                        : Colors.grey[800],
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                );
              }
            ),
          ],
        ),
      ),
    );
  }
}
