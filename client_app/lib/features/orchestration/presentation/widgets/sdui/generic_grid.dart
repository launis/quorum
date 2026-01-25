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
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2, // Responsive? For now fixed 2
                childAspectRatio: 3.0,
                crossAxisSpacing: 16,
                mainAxisSpacing: 8,
              ),
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index] as Map<String, dynamic>;
                final label = item['label'] ?? '';
                final value = item['value']?.toString() ?? 'N/A';
                final highlight = item['highlight'] == true;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      label,
                      style: Theme.of(
                        context,
                      ).textTheme.labelSmall?.copyWith(color: Colors.grey[600]),
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      value,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight:
                            highlight ? FontWeight.bold : FontWeight.normal,
                        color:
                            highlight
                                ? Theme.of(context).colorScheme.primary
                                : null,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
