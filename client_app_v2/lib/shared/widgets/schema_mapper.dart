import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

@immutable
class SchemaFieldDefinition {
  final String? type;
  final String? title;
  final String? description;
  final List<String>? enumOptions;

  const SchemaFieldDefinition({
    this.type,
    this.title,
    this.description,
    this.enumOptions,
  });
}

/// **Schema Mapper**
///
/// Utility class to map JSON Schema definitions to Flutter Input Widgets.
/// Implements the Core SDUI Logic for the Cognitive Configuration Studio.
class SchemaMapper {
  const SchemaMapper._();

  static const Set<String> _supportedTypes = {
    'string',
    'integer',
    'number',
    'boolean',
  };

  /// Maps a schema field definition to a specific Input Widget.
  static Widget mapFieldToWidget({
    required BuildContext context,
    required String key,
    required SchemaFieldDefinition schema,
    required Object? value,
    required ValueChanged<Object?> onChanged,
    required bool isRequired,
  }) {
    if (key.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: SchemaMapper key cannot be empty.',
      );
    }

    final type = schema.type;
    if (type != null && !_supportedTypes.contains(type)) {
      throw AppException.validation(
        'Fail-Fast: SchemaMapper property "$key" has unsupported or invalid type "$type".',
      );
    }

    final rawTitle = schema.title;
    if (rawTitle != null && rawTitle.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: SchemaMapper property "$key" title must be a non-empty String.',
      );
    }
    final title = rawTitle ?? key;

    final description = schema.description;

    final enumValues = schema.enumOptions;
    if (enumValues != null && enumValues.isEmpty) {
      throw AppException.validation(
        'Fail-Fast: SchemaMapper property "$key" enum must be a non-empty List.',
      );
    }

    if (type == null && enumValues == null) {
      throw AppException.validation(
        'Fail-Fast: SchemaMapper property "$key" must declare a valid "type" or "enum".',
      );
    }

    final l10n = AppLocalizations.of(context)!;
    final helperText = description != null && description.isNotEmpty
        ? description
        : null;
    final labelText = isRequired ? '$title *' : title;

    // 1. ENUM (Dropdown)
    if (enumValues != null) {
      final optionStrings = <String>[];
      for (final item in enumValues) {
        final strVal = item.trim();
        if (strVal.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: SchemaMapper property "$key" contains an empty enum option.',
          );
        }
        optionStrings.add(strVal);
      }

      final currentSelection = value?.toString();
      if (currentSelection != null &&
          !optionStrings.contains(currentSelection)) {
        throw AppException.validation(
          'Fail-Fast: SchemaMapper property "$key" initial value "$currentSelection" is not in allowed enum options.',
        );
      }

      return Padding(
        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
        child: DropdownButtonFormField<String>(
          key: ValueKey('enum_${key}_$currentSelection'),
          initialValue: currentSelection,
          isExpanded: true,
          decoration: InputDecoration(
            labelText: labelText,
            helperText: helperText,
            border: const OutlineInputBorder(),
          ),
          items: optionStrings.map((val) {
            return DropdownMenuItem<String>(
              value: val,
              child: Text(val, maxLines: 1, overflow: TextOverflow.ellipsis),
            );
          }).toList(),
          onChanged: (val) => onChanged(val),
          validator: isRequired
              ? (val) => val == null || val.isEmpty ? l10n.fieldRequired : null
              : null,
        ),
      );
    }

    // 2. BOOLEAN (Switch)
    if (type == 'boolean') {
      if (value != null && value is! bool) {
        throw AppException.validation(
          'Fail-Fast: SchemaMapper boolean property "$key" received non-bool value "$value".',
        );
      }
      final boolVal = (value as bool?) ?? false;
      return Padding(
        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
        child: SwitchListTile(
          key: ValueKey('bool_${key}_$boolVal'),
          title: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
          subtitle: helperText != null
              ? Text(helperText, maxLines: 2, overflow: TextOverflow.ellipsis)
              : null,
          value: boolVal,
          onChanged: onChanged,
          contentPadding: EdgeInsets.zero,
        ),
      );
    }

    // 3. INTEGER / NUMBER
    if (type == 'integer' || type == 'number') {
      if (value != null && value is! num && value is! String) {
        throw AppException.validation(
          'Fail-Fast: SchemaMapper numeric property "$key" received invalid value "$value".',
        );
      }
      return Padding(
        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
        child: TextFormField(
          key: ValueKey('num_${key}_$value'),
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
            labelText: labelText,
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
          validator: isRequired
              ? (val) => val == null || val.isEmpty ? l10n.fieldRequired : null
              : null,
        ),
      );
    }

    // 4. STRING (Default)
    if (value != null && value is! String) {
      throw AppException.validation(
        'Fail-Fast: SchemaMapper string property "$key" received non-String value "$value".',
      );
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s16),
      child: TextFormField(
        key: ValueKey('str_${key}_$value'),
        initialValue: value as String?,
        decoration: InputDecoration(
          labelText: labelText,
          helperText: helperText,
          border: const OutlineInputBorder(),
        ),
        onChanged: onChanged,
        validator: isRequired
            ? (val) => val == null || val.isEmpty ? l10n.fieldRequired : null
            : null,
      ),
    );
  }
}
