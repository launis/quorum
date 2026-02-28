import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class DynamicStepForm extends HookConsumerWidget {
  final Map<String, dynamic> config;
  final JsonSchema? schema;
  final Function(String key, dynamic value) onChanged;

  const DynamicStepForm({
    super.key,
    required this.config,
    this.schema,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. If Schema provided, drive UI from Schema
    if (schema != null && schema!.properties != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children:
            schema!.properties!.entries.map((entry) {
              final key = entry.key;
              final prop = entry.value;
              final value = config[key]; // No defaultValue in model

              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: _BuildField(
                  keyName: key,
                  value: value,
                  schema: prop,
                  onChanged: onChanged,
                ),
              );
            }).toList(),
      );
    }

    // 2. Fallback: Iterate config keys (Legacy/Schemaless mode)
    if (config.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No configuration properties available for this step.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          config.entries.map((entry) {
            // Skip internal keys
            if (entry.key.startsWith('_')) return const SizedBox.shrink();

            return Padding(
              padding: const EdgeInsets.only(bottom: 16.0),
              child: _BuildField(
                keyName: entry.key,
                value: entry.value,
                onChanged: onChanged,
              ),
            );
          }).toList(),
    );
  }
}

class _BuildField extends HookConsumerWidget {
  final String keyName;
  final dynamic value;
  final JsonSchema? schema;
  final Function(String key, dynamic value) onChanged;

  const _BuildField({
    required this.keyName,
    required this.value,
    this.schema,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. Determine Label
    final label = schema?.title ?? _capitalize(keyName);
    final description = schema?.description;

    // 2. Determine Type & Render
    // Bool / Switch
    if (value is bool || (schema?.type == 'boolean')) {
      return SwitchListTile(
        title: Text(label),
        subtitle: description != null ? Text(description) : null,
        value: value == true,
        onChanged: (newValue) => onChanged(keyName, newValue),
      );
    }

    // Number
    final isNumber =
        (value is num) ||
        (schema?.type == 'number') ||
        (schema?.type == 'integer');

    // Text Controller
    final controller = useTextEditingController(text: value?.toString() ?? '');
    final focusNode = useFocusNode();

    // Sync external changes
    useEffect(() {
      if (!focusNode.hasFocus && controller.text != (value?.toString() ?? '')) {
        controller.text = value?.toString() ?? '';
      }
      return null;
    }, [value]);

    // Handle Blur
    useEffect(() {
      void listener() {
        if (!focusNode.hasFocus) {
          // Blur detected
          _submit(controller.text, isNumber);
        }
      }

      focusNode.addListener(listener);
      return () => focusNode.removeListener(listener);
    }, [focusNode]);

    return TextField(
      controller: controller,
      focusNode: focusNode,
      keyboardType: isNumber ? TextInputType.number : TextInputType.text,
      decoration: InputDecoration(
        labelText: label,
        helperText: description,
        border: const OutlineInputBorder(),
      ),
      onSubmitted: (text) => _submit(text, isNumber),
    );
  }

  void _submit(String text, bool isNumber) {
    if (isNumber) {
      final numVal = num.tryParse(text);
      if (numVal != null && numVal != value) {
        onChanged(keyName, numVal);
      }
    } else {
      if (text != (value?.toString() ?? '')) {
        onChanged(keyName, text);
      }
    }
  }

  String _capitalize(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }
}
