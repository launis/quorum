import 'package:client_app/shared/widgets/schema_mapper.dart';
import 'package:flutter/material.dart';

/// **Dynamic Form Widget**
///
/// A Server-Driven UI Form that renders inputs based on a JSON Schema.
/// Uses [SchemaMapper] for field generation.
class DynamicFormWidget extends StatefulWidget {
  const DynamicFormWidget({
    super.key,
    required this.schema,
    this.initialData = const {},
    required this.onChanged,
  });

  /// The JSON Schema defining the form structure.
  final Map<String, dynamic> schema;

  /// Initial key-value pairs for the form fields.
  final Map<String, dynamic> initialData;

  /// Callback triggered whenever the form state changes.
  final ValueChanged<Map<String, dynamic>> onChanged;

  @override
  State<DynamicFormWidget> createState() => _DynamicFormWidgetState();
}

class _DynamicFormWidgetState extends State<DynamicFormWidget> {
  late Map<String, dynamic> _formData;
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _formData = Map.of(widget.initialData);
  }

  @override
  void didUpdateWidget(covariant DynamicFormWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    // If schema or initialData fundamentally changes, one might reset.
    // For now, we assume _formData persists unless key changes.
    // Use Key on widget if full reset needed.
  }

  void _updateField(String key, dynamic value) {
    setState(() {
      _formData[key] = value;
    });
    widget.onChanged(_formData);
  }

  @override
  Widget build(BuildContext context) {
    // 2. Parse Schema
    final properties =
        widget.schema['properties'] as Map<String, dynamic>? ?? {};
    final requiredFields =
        (widget.schema['required'] as List<dynamic>?)?.cast<String>() ?? [];

    // 3. Render Form
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children:
            properties.entries.map((entry) {
              final key = entry.key;
              final fieldSchema = entry.value as Map<String, dynamic>;
              final isRequired = requiredFields.contains(key);

              // Render via SchemaMapper
              return SchemaMapper.mapFieldToWidget(
                key: key,
                schema: fieldSchema,
                value: _formData[key],
                isRequired: isRequired,
                onChanged: (newValue) => _updateField(key, newValue),
              );
            }).toList(),
      ),
    );
  }
}
