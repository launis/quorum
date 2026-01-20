import 'package:client_app/features/orchestration/presentation/widgets/file_uploader.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// A Server-Driven Form Widget that renders inputs based on a JSON Schema.
///
/// Supports:
/// - String (TextFormField)
/// - String + format: binary (FileUploader)
/// - Enum (DropdownButton)
class DynamicForm extends StatefulWidget {
  const DynamicForm({
    super.key,
    required this.schema,
    this.initialValues = const {},
    required this.onChanged,
  });

  final Map<String, dynamic> schema;
  final Map<String, dynamic> initialValues;
  final ValueChanged<Map<String, dynamic>> onChanged;

  @override
  State<DynamicForm> createState() => _DynamicFormState();
}

class _DynamicFormState extends State<DynamicForm> {
  late Map<String, dynamic> _formData;
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _formData = Map.of(widget.initialValues);
  }

  void _updateField(String key, dynamic value) {
    setState(() {
      _formData[key] = value;
    });
    widget.onChanged(_formData);
  }

  @override
  Widget build(BuildContext context) {
    final properties =
        widget.schema['properties'] as Map<String, dynamic>? ?? {};
    final requiredFields =
        (widget.schema['required'] as List<dynamic>?)?.cast<String>() ?? [];

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children:
            properties.entries.map((entry) {
              final key = entry.key;
              final fieldSchema = entry.value as Map<String, dynamic>;
              final label = fieldSchema['title'] as String? ?? key;
              final type = fieldSchema['type'] as String?;
              final format = fieldSchema['format'] as String?;
              final enumValues = fieldSchema['enum'] as List<dynamic>?;
              final isRequired = requiredFields.contains(key);

              // 1. File Upload
              if (type == 'string' && format == 'binary') {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: FileUploader(
                    label: isRequired ? '$label *' : label,
                    initialFileName:
                        _formData[key] is PlatformFile
                            ? (_formData[key] as PlatformFile).name
                            : null,
                    onFileSelected: (file) => _updateField(key, file),
                  ),
                );
              }

              // 2. Enum Dropdown
              if (enumValues != null) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: DropdownButtonFormField<String>(
                    // ignore: deprecated_member_use
                    value: _formData[key] as String?,
                    decoration: InputDecoration(
                      labelText: isRequired ? '$label *' : label,
                      border: const OutlineInputBorder(),
                    ),
                    items:
                        enumValues.map((e) {
                          return DropdownMenuItem<String>(
                            value: e.toString(),
                            child: Text(e.toString()),
                          );
                        }).toList(),
                    onChanged: (val) => _updateField(key, val),
                    validator:
                        isRequired
                            ? (val) =>
                                val == null || val.isEmpty
                                    ? AppLocalizations.of(context)!.fieldRequired
                                    : null
                            : null,
                  ),
                );
              }

              // 3. Default Text Field
              if (type == 'string') {
                // Check for multiline
                final isMultiline =
                    format == 'textarea' ||
                    (fieldSchema['maxLength'] as int? ?? 0) > 100;
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: TextFormField(
                    initialValue: _formData[key] as String?,
                    decoration: InputDecoration(
                      labelText: isRequired ? '$label *' : label,
                      border: const OutlineInputBorder(),
                      alignLabelWithHint: isMultiline,
                    ),
                    maxLines: isMultiline ? 5 : 1,
                    onChanged: (val) => _updateField(key, val),
                    validator:
                        isRequired
                            ? (val) =>
                                val == null || val.isEmpty
                                    ? AppLocalizations.of(context)!.fieldRequired
                                    : null
                            : null,
                  ),
                );
              }

              // Fallback
              return const SizedBox.shrink();
            }).toList(),
      ),
    );
  }
}
