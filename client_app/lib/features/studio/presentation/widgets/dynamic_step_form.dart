import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class DynamicStepForm extends HookConsumerWidget {
  final Map<String, dynamic> config;
  final Function(String key, dynamic value) onChanged;

  const DynamicStepForm({
    super.key,
    required this.config,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
  final Function(String key, dynamic value) onChanged;

  const _BuildField({
    required this.keyName,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (value is bool) {
      return SwitchListTile(
        title: Text(keyName),
        value: value as bool,
        onChanged: (newValue) => onChanged(keyName, newValue),
      );
    }

    final controller = useTextEditingController(text: value.toString());
    final focusNode = useFocusNode();

    // Sync external changes
    useEffect(() {
      if (!focusNode.hasFocus && controller.text != value.toString()) {
        controller.text = value.toString();
      }
      return null;
    }, [value]);

    // Handle Blur
    useEffect(() {
      void listener() {
        if (!focusNode.hasFocus) {
          // Blur detected
          onChanged(keyName, controller.text);
        }
      }

      focusNode.addListener(listener);
      return () => focusNode.removeListener(listener);
    }, [focusNode]);

    return TextField(
      controller: controller,
      focusNode: focusNode,
      decoration: InputDecoration(
        labelText: keyName,
        border: const OutlineInputBorder(),
      ),
      onSubmitted: (text) {
        onChanged(keyName, text);
      },
    );
  }
}
