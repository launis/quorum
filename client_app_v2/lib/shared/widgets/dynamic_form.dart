import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/shared/widgets/schema_mapper.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

export 'package:client_app/shared/widgets/schema_mapper.dart'
    show SchemaFieldDefinition;

@immutable
class DynamicFormSchema {
  final Map<String, SchemaFieldDefinition>? properties;
  final List<String>? requiredFields;
  final bool isCorrupted;

  const DynamicFormSchema({
    this.properties,
    this.requiredFields,
    this.isCorrupted = false,
  });
}

@immutable
class DynamicFormFieldValue {
  final String? stringValue;
  final int? intValue;
  final double? doubleValue;
  final bool? boolValue;

  const DynamicFormFieldValue.string(String this.stringValue)
    : intValue = null,
      doubleValue = null,
      boolValue = null;

  const DynamicFormFieldValue.integer(int this.intValue)
    : stringValue = null,
      doubleValue = null,
      boolValue = null;

  const DynamicFormFieldValue.number(double this.doubleValue)
    : stringValue = null,
      intValue = null,
      boolValue = null;

  const DynamicFormFieldValue.boolean(bool this.boolValue)
    : stringValue = null,
      intValue = null,
      doubleValue = null;

  Object? get rawValue => stringValue ?? intValue ?? doubleValue ?? boolValue;

  static DynamicFormFieldValue? fromObject(Object? value) {
    if (value == null) return null;
    if (value is DynamicFormFieldValue) return value;
    if (value is String) return DynamicFormFieldValue.string(value);
    if (value is int) return DynamicFormFieldValue.integer(value);
    if (value is double) return DynamicFormFieldValue.number(value);
    if (value is bool) return DynamicFormFieldValue.boolean(value);
    throw AppException.validation(
      'Fail-Fast: Unsupported form field value type "${value.runtimeType}".',
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DynamicFormFieldValue &&
          stringValue == other.stringValue &&
          intValue == other.intValue &&
          doubleValue == other.doubleValue &&
          boolValue == other.boolValue;

  @override
  int get hashCode =>
      Object.hash(stringValue, intValue, doubleValue, boolValue);
}

@immutable
class DynamicFormValues {
  final Map<String, DynamicFormFieldValue?> entries;

  const DynamicFormValues({
    this.entries = const <String, DynamicFormFieldValue?>{},
  });

  Object? operator [](String key) => entries[key]?.rawValue;

  DynamicFormValues copyWithField(String key, Object? value) {
    final next = Map<String, DynamicFormFieldValue?>.of(entries);
    next[key] = DynamicFormFieldValue.fromObject(value);
    return DynamicFormValues(
      entries: Map<String, DynamicFormFieldValue?>.unmodifiable(next),
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DynamicFormValues && mapEquals(entries, other.entries);

  @override
  int get hashCode =>
      Object.hashAll(entries.entries.map((e) => Object.hash(e.key, e.value)));
}

/// **Dynamic Form Widget**
///
/// A Server-Driven UI Form that renders inputs based on a JSON Schema.
/// Uses [SchemaMapper] for field generation and enforces Fail-Fast validation.
class DynamicFormWidget extends ConsumerStatefulWidget {
  const DynamicFormWidget({
    super.key,
    required this.schema,
    this.initialData = const DynamicFormValues(),
    required this.onChanged,
  });

  /// The typed schema defining the form structure.
  final DynamicFormSchema schema;

  /// Initial key-value pairs for the form fields.
  final DynamicFormValues initialData;

  /// Callback triggered whenever the form state changes.
  final ValueChanged<DynamicFormValues> onChanged;

  @override
  ConsumerState<DynamicFormWidget> createState() => _DynamicFormWidgetState();
}

class _DynamicFormWidgetState extends ConsumerState<DynamicFormWidget> {
  late DynamicFormValues _formData;
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _formData = widget.initialData;
  }

  @override
  void didUpdateWidget(covariant DynamicFormWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialData != widget.initialData) {
      _formData = widget.initialData;
    }
  }

  void _updateField(String key, Object? value) {
    setState(() {
      _formData = _formData.copyWithField(key, value);
    });
    widget.onChanged(_formData);
  }

  @override
  Widget build(BuildContext context) {
    try {
      if (widget.schema.isCorrupted) {
        throw AppException.validation(
          'Fail-Fast: DynamicFormWidget schema is corrupted.',
        );
      }

      final rawProperties = widget.schema.properties;
      if (rawProperties == null || rawProperties.isEmpty) {
        throw AppException.validation(
          'Fail-Fast: DynamicFormWidget schema must contain non-empty "properties".',
        );
      }

      final requiredFields = <String>{};
      if (widget.schema.requiredFields != null) {
        for (final item in widget.schema.requiredFields!) {
          if (item.trim().isEmpty) {
            throw AppException.validation(
              'Fail-Fast: DynamicFormWidget schema "required" entries must be non-empty Strings.',
            );
          }
          requiredFields.add(item);
        }
      }

      final fieldWidgets = <Widget>[];
      for (final entry in rawProperties.entries) {
        final key = entry.key;
        final fieldSchema = entry.value;
        if (key.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Property "$key" in DynamicFormWidget schema must have a non-empty key.',
          );
        }

        fieldWidgets.add(
          SchemaMapper.mapFieldToWidget(
            context: context,
            key: key,
            schema: fieldSchema,
            value: _formData[key],
            isRequired: requiredFields.contains(key),
            onChanged: (newValue) => _updateField(key, newValue),
          ),
        );
      }

      return Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: fieldWidgets,
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'DynamicFormWidget',
            'VALIDATION_FAILED: Failed to render dynamic form',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
