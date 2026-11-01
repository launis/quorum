import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Reusable dynamic list editor for criteria and anti-patterns with numbered badges,
/// expand-fill text inputs, and trash actions.
class DynamicItemListEditor extends StatefulWidget {
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

  @override
  State<DynamicItemListEditor> createState() => _DynamicItemListEditorState();
}

class _DynamicItemListEditorState extends State<DynamicItemListEditor> {
  late final List<TextEditingController> _controllers;

  @override
  void initState() {
    super.initState();
    _controllers = widget.items
        .map((item) => TextEditingController(text: item))
        .toList();
  }

  @override
  void didUpdateWidget(DynamicItemListEditor oldWidget) {
    super.didUpdateWidget(oldWidget);
    while (_controllers.length > widget.items.length) {
      _controllers.removeLast().dispose();
    }
    while (_controllers.length < widget.items.length) {
      final index = _controllers.length;
      _controllers.add(TextEditingController(text: widget.items[index]));
    }
    for (int i = 0; i < widget.items.length; i++) {
      if (_controllers[i].text != widget.items[i]) {
        _controllers[i].text = widget.items[i];
      }
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  void _addItem() {
    final updated = List<String>.from(widget.items)..add('');
    widget.onChanged(updated);
  }

  void _updateItem(int index, String value) {
    final updated = List<String>.from(widget.items);
    updated[index] = value;
    widget.onChanged(updated);
  }

  void _removeItem(int index) {
    final updated = List<String>.from(widget.items)..removeAt(index);
    widget.onChanged(updated);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int i = 0; i < widget.items.length; i++)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Container(
                  width: AppSpacing.s24,
                  height: AppSpacing.s24,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(AppSpacing.s8),
                  ),
                  child: Text(
                    '${i + 1}',
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.labelMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: TextFormField(
                    controller: _controllers[i],
                    enabled: widget.enabled,
                    decoration: InputDecoration(
                      hintText: widget.placeholder,
                      isDense: true,
                      border: const OutlineInputBorder(),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.s12,
                        vertical: AppSpacing.s8,
                      ),
                    ),
                    onChanged: (val) => _updateItem(i, val),
                  ),
                ),
                AppSpacing.w4,
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: AppSpacing.s16),
                  color: theme.colorScheme.error,
                  tooltip: l10n.delete,
                  onPressed: widget.enabled ? () => _removeItem(i) : null,
                ),
              ],
            ),
          ),
        OutlinedButton.icon(
          onPressed: widget.enabled ? _addItem : null,
          icon: const Icon(Icons.add, size: AppSpacing.s16),
          label: Text(widget.addButtonLabel, overflow: TextOverflow.ellipsis),
        ),
      ],
    );
  }
}
