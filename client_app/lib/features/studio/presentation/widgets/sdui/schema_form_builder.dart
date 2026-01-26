import 'package:client_app/features/studio/domain/logic/schema_validator.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/code_editor_field.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/file_upload_field.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **SchemaFormBuilder**
///
/// Renders a dynamic form based on a [JsonSchema].
/// Uses standard Flutter [Form] and [TextFormField] widgets.
class SchemaFormBuilder extends ConsumerStatefulWidget {
  final JsonSchema schema;
  final Map<String, dynamic> initialData;
  final ValueChanged<Map<String, dynamic>> onChanged;

  const SchemaFormBuilder({
    super.key,
    required this.schema,
    this.initialData = const {},
    required this.onChanged,
  });

  @override
  ConsumerState<SchemaFormBuilder> createState() => _SchemaFormBuilderState();
}

class _SchemaFormBuilderState extends ConsumerState<SchemaFormBuilder> {
  late Map<String, dynamic> _formData;
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _formData = Map.of(widget.initialData);
  }

  void _updateField(String key, dynamic value) {
    setState(() {
      _formData[key] = value;
    });
    widget.onChanged(_formData);
  }

  @override
  Widget build(BuildContext context) {
    final properties = widget.schema.properties ?? {};

    return Form(
      key: _formKey,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 600;
          final gap = 16.0;
          // Calculate item width: full width if narrow, half width minus gap if wide
          final halfWidth = (constraints.maxWidth - gap) / 2;

          return Wrap(
            spacing: gap,
            runSpacing: gap,
            children:
                properties.entries.map((entry) {
                  final key = entry.key;
                  final fieldSchema = entry.value;

                  // Determine if this specific field should be full width
                  // e.g. textareas or complex objects, or just default behavior
                  final isTextArea = fieldSchema.uiWidget == 'textarea';
                  // Force full width for textarea or on narrow screens
                  final useFullWidth = !isWide || isTextArea;

                  return SizedBox(
                    width: useFullWidth ? constraints.maxWidth : halfWidth,
                    child: _buildField(key, fieldSchema),
                  );
                }).toList(),
          );
        },
      ),
    );
  }

  Widget _buildField(String key, JsonSchema fieldSchema) {
    final label = fieldSchema.title ?? key;
    final type = fieldSchema.type;

    // 1. Enum (Dropdown)
    if (fieldSchema.enumValues != null && fieldSchema.enumValues!.isNotEmpty) {
      return DropdownButtonFormField<dynamic>(
        initialValue: _formData[key] ?? fieldSchema.enumValues!.first,
        decoration: InputDecoration(
          labelText: label,
          helperText: fieldSchema.description,
          border: const OutlineInputBorder(),
        ),
        items:
            fieldSchema.enumValues!.map((e) {
              return DropdownMenuItem<dynamic>(
                value: e,
                child: Text(e.toString()),
              );
            }).toList(),
        onChanged: (val) => _updateField(key, val),
        validator: (val) => SchemaValidator.validate(fieldSchema, val),
      );
    }

    // 2. Boolean (Switch)
    if (type == 'boolean') {
      return SwitchListTile(
        title: Text(label),
        subtitle:
            fieldSchema.description != null
                ? Text(fieldSchema.description!)
                : null,
        value: _formData[key] == true,
        onChanged: (val) => _updateField(key, val),
      );
    }

    // 3. Integer/Number
    if (type == 'integer' || type == 'number') {
      return TextFormField(
        initialValue: _formData[key]?.toString(),
        decoration: InputDecoration(
          labelText: label,
          helperText: fieldSchema.description,
          border: const OutlineInputBorder(),
        ),
        keyboardType: TextInputType.numberWithOptions(
          decimal: type == 'number',
        ),
        inputFormatters: [
          if (type == 'integer') FilteringTextInputFormatter.digitsOnly,
          if (type == 'number')
            FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
        ],
        onChanged: (val) {
          if (type == 'integer') {
            _updateField(key, int.tryParse(val));
          } else {
            _updateField(key, double.tryParse(val));
          }
        },
        validator: (val) {
          final numVal =
              type == 'integer'
                  ? int.tryParse(val ?? '')
                  : double.tryParse(val ?? '');
          return SchemaValidator.validate(fieldSchema, numVal);
        },
      );
    }

    // 4. String (Default + Specialized Widgets)
    if (fieldSchema.uiWidget == 'code-editor') {
      return CodeEditorField(
        label: label,
        initialValue: _formData[key] as String?,
        onChanged: (val) => _updateField(key, val),
      );
    }

    if (fieldSchema.uiWidget == 'file-upload') {
      return FileUploadField(
        label: label,
        initialValue: _formData[key] as String?,
        onChanged: (val) => _updateField(key, val),
      );
    }
    
    final isTextArea = fieldSchema.uiWidget == 'textarea';
    var initialValue = _formData[key];
    if (initialValue is List) {
       // Simple join for list display if we don't have a specialized array widget yet
       initialValue = initialValue.join(', ');
    }

    return TextFormField(
      initialValue: initialValue?.toString(),
      decoration: InputDecoration(
        labelText: label,
        helperText: fieldSchema.description,
        border: const OutlineInputBorder(),
        alignLabelWithHint: isTextArea,
      ),
      minLines: isTextArea ? 3 : 1,
      maxLines: isTextArea ? 5 : 1,
      onChanged: (val) {
          // If the schema expects an array, split the string back into a list
          if (type == 'array') {
             _updateField(key, val.split(',').map((e) => e.trim()).toList());
          } else {
             _updateField(key, val);
          }
      },
      validator: (val) => SchemaValidator.validate(fieldSchema, val),
    );
  }
}
