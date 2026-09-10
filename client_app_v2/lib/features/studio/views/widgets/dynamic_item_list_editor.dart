import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Reusable dynamic list editor for criteria and anti-patterns with numbered badges,
/// expand-fill text inputs, and trash actions.
class DynamicItemListEditor extends StatelessWidget {
  final List<String> items;
  final ValueChanged<List<String>> onChanged;
  final String addButtonLabel;
  final String? placeholder;
  final bool enabled;

  const DynamicItemListEditor({
    super.key,
    required this.items,
    required this.onChanged,
    required this.addButtonLabel,
    this.placeholder,
    this.enabled = true,
  });

  void _addItem() {
    final updated = List<String>.from(items)..add('');
    onChanged(updated);
  }

  void _updateItem(int index, String value) {
    final updated = List<String>.from(items);
    updated[index] = value;
    onChanged(updated);
  }

  void _removeItem(int index) {
    final updated = List<String>.from(items)..removeAt(index);
    onChanged(updated);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int i = 0; i < items.length; i++)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Container(
                  width: 28,
                  height: 28,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${i + 1}',
                    style: theme.textTheme.labelMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: TextFormField(
                    initialValue: items[i],
                    enabled: enabled,
                    decoration: InputDecoration(
                      hintText: placeholder,
                      isDense: true,
                      border: const OutlineInputBorder(),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 8,
                      ),
                    ),
                    onChanged: (val) => _updateItem(i, val),
                  ),
                ),
                AppSpacing.w4,
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  color: theme.colorScheme.error,
                  tooltip: 'Delete item',
                  onPressed: enabled ? () => _removeItem(i) : null,
                ),
              ],
            ),
          ),
        OutlinedButton.icon(
          onPressed: enabled ? _addItem : null,
          icon: const Icon(Icons.add, size: 18),
          label: Text(addButtonLabel),
        ),
      ],
    );
  }
}
