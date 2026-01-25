import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// **Schema Mapper**
///
/// Utility class to map JSON Schema definitions to Flutter Input Widgets.
/// Implements the Core SDUI Logic for the Cognitive Configuration Studio.
class SchemaMapper {
  const SchemaMapper._();

  /// Maps a schema field definition to a specific Input Widget.
  static Widget mapFieldToWidget({
    required String key,
    required Map<String, dynamic> schema,
    required dynamic value,
    required ValueChanged<dynamic> onChanged,
    required bool isRequired,
  }) {
    final type = schema['type'] as String?;
    final title = schema['title'] as String? ?? key;
    final description = schema['description'] as String?;
    final enumValues = schema['enum'] as List<dynamic>?;

    // Helper Text (Description)
    final helperText =
        description != null && description.isNotEmpty ? description : null;

    // 1. ENUM (Dropdown)
    if (enumValues != null) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 16.0),
        child: DropdownButtonFormField<String>(
          // ignore: deprecated_member_use
          value: value?.toString(),
          decoration: InputDecoration(
            labelText: isRequired ? '$title *' : title,
            helperText: helperText,
            border: const OutlineInputBorder(),
          ),
          items:
              enumValues.map((e) {
                final val = e.toString();
                return DropdownMenuItem<String>(value: val, child: Text(val));
              }).toList(),
          onChanged: (val) => onChanged(val),
          validator:
              isRequired
                  ? (val) =>
                      val == null || val.isEmpty ? 'Field required' : null
                  : null,
        ),
      );
    }

    // 2. BOOLEAN (Switch)
    if (type == 'boolean') {
      final boolVal = value as bool? ?? false;
      return Padding(
        padding: const EdgeInsets.only(bottom: 16.0),
        child: SwitchListTile(
          title: Text(title),
          subtitle: helperText != null ? Text(helperText) : null,
          value: boolVal,
          onChanged: onChanged,
          contentPadding: EdgeInsets.zero,
        ),
      );
    }

    // 3. INTEGER / NUMBER
    if (type == 'integer' || type == 'number') {
      return Padding(
        padding: const EdgeInsets.only(bottom: 16.0),
        child: TextFormField(
          initialValue: value?.toString(),
          keyboardType: TextInputType.numberWithOptions(
            decimal: type == 'number',
            signed: true,
          ),
          inputFormatters: [
            type == 'integer'
                ? FilteringTextInputFormatter.digitsOnly
                : FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
          ],
          decoration: InputDecoration(
            labelText: isRequired ? '$title *' : title,
            helperText: helperText,
            border: const OutlineInputBorder(),
          ),
          onChanged: (val) {
            if (val.isEmpty) {
              onChanged(null);
              return;
            }
            if (type == 'integer') {
              onChanged(int.tryParse(val));
            } else {
              onChanged(double.tryParse(val));
            }
          },
          validator:
              isRequired
                  ? (val) =>
                      val == null || val.isEmpty ? 'Field required' : null
                  : null,
        ),
      );
    }

    // 4. STRING (Default)
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: TextFormField(
        initialValue: value as String?,
        decoration: InputDecoration(
          labelText: isRequired ? '$title *' : title,
          helperText: helperText,
          border: const OutlineInputBorder(),
        ),
        onChanged: onChanged,
        validator:
            isRequired
                ? (val) => val == null || val.isEmpty ? 'Field required' : null
                : null,
      ),
    );
  }
}
