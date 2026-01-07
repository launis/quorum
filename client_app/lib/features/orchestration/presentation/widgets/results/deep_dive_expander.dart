import 'package:flutter/material.dart';

class DeepDiveExpander extends StatelessWidget {
  final String title;
  final Widget child;
  final IconData icon;
  final bool initiallyExpanded;

  const DeepDiveExpander({
    super.key,
    required this.title,
    required this.child,
    this.icon = Icons.analytics_outlined,
    this.initiallyExpanded = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Using ExpansionTile inside a Card with custom styling
    return Card(
      elevation: 0,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
      ),
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        shape: const Border(), // Remove internal border
        collapsedShape: const Border(),
        leading: Icon(icon, color: theme.colorScheme.primary),
        title: Text(
          title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        childrenPadding: const EdgeInsets.all(16),
        children: [child],
      ),
    );
  }
}
