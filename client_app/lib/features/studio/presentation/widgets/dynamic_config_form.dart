import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class DynamicConfigForm extends HookConsumerWidget {
  final Map<String, dynamic> config;
  final Function(String key, dynamic value) onFieldChanged;

  const DynamicConfigForm({
    super.key,
    required this.config,
    required this.onFieldChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // If config is empty, show a message
    if (config.isEmpty) {
      return Center(
        child: Text(
          'No configuration available.',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).colorScheme.outline,
          ),
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16.0),
      children:
          config.entries.map((entry) {
            final key = entry.key;
            final value = entry.value;
            final label = _capitalize(key);

            if (value is bool) {
              return _buildSwitch(context, key, label, value);
            } else if (value is int) {
              return _HookTextField(
                key: ValueKey(
                  key,
                ), // Important for identifying fields if order changes
                fieldKey: key,
                label: label,
                initialValue: value.toString(),
                keyboardType: TextInputType.number,
                onChanged: (val) => onFieldChanged(key, int.tryParse(val) ?? 0),
              );
            } else if (value is double) {
              return _HookTextField(
                key: ValueKey(key),
                fieldKey: key,
                label: label,
                initialValue: value.toString(),
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                onChanged:
                    (val) => onFieldChanged(key, double.tryParse(val) ?? 0.0),
              );
            } else if (value is String) {
              return _HookTextField(
                key: ValueKey(key),
                fieldKey: key,
                label: label,
                initialValue: value,
                onChanged: (val) => onFieldChanged(key, val),
              );
            } else if (value is List) {
              return ListTile(
                title: Text(label),
                subtitle: Text(
                  '${value.length} items (List editing not supported)',
                ),
                leading: const Icon(Icons.list),
              );
            }

            return ListTile(
              title: Text(label),
              subtitle: Text('Unsupported type: ${value.runtimeType}'),
            );
          }).toList(),
    );
  }

  String _capitalize(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }

  Widget _buildSwitch(
    BuildContext context,
    String key,
    String label,
    bool value,
  ) {
    return SwitchListTile(
      title: Text(label),
      value: value,
      onChanged: (newValue) => onFieldChanged(key, newValue),
    );
  }
}

class _HookTextField extends HookWidget {
  final String fieldKey;
  final String label;
  final String initialValue;
  final TextInputType? keyboardType;
  final Function(String) onChanged;

  const _HookTextField({
    super.key,
    required this.fieldKey,
    required this.label,
    required this.initialValue,
    this.keyboardType,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final controller = useTextEditingController(text: initialValue);
    final focusNode = useFocusNode();

    // Sync controller if initialValue changes externally (e.g. undo/redo or remote update)
    // But we need to be careful not to overwrite user typing.
    // Standard pattern: Only update if not focused? Or hook handles it?
    // useTextEditingController does NOT automatically update text if initialValue changes.
    // We explicitly decide NOT to sync efficiently here to avoid fighting the user,
    // assuming this form is the primary editor.
    // However, if we want to support external updates, we might need a useEffect.
    // For now, adhering strictly to "Optimistic UI" implies the local state is the driver.

    useEffect(() {
      void onBlur() {
        if (!focusNode.hasFocus) {
          // Trigger update only on blur
          if (controller.text != initialValue) {
            onChanged(controller.text);
          }
        }
      }

      focusNode.addListener(onBlur);
      return () => focusNode.removeListener(onBlur);
    }, [focusNode, initialValue]);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: TextField(
        controller: controller,
        focusNode: focusNode,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        // Also support "Enter" to submit
        onSubmitted: (val) {
          if (val != initialValue) {
            onChanged(val);
          }
        },
      ),
    );
  }
}
