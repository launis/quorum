import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/shared/widgets/schema_mapper.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **Dynamic Form Widget**
///
/// A Server-Driven UI Form that renders inputs based on a JSON Schema.
/// Uses [SchemaMapper] for field generation and enforces Fail-Fast validation.
class DynamicFormWidget extends ConsumerStatefulWidget {
  const DynamicFormWidget({
    super.key,
    required this.schema,
    this.initialData = const {},
    required this.onChanged,
  });

  /// The JSON Schema defining the form structure.
  final Map<String, Object?> schema;

  /// Initial key-value pairs for the form fields.
  final Map<String, Object?> initialData;

  /// Callback triggered whenever the form state changes.
  final ValueChanged<Map<String, Object?>> onChanged;

  @override
  ConsumerState<DynamicFormWidget> createState() => _DynamicFormWidgetState();
}

class _DynamicFormWidgetState extends ConsumerState<DynamicFormWidget> {
  late Map<String, Object?> _formData;
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _formData = Map<String, Object?>.of(widget.initialData);
  }

  @override
  void didUpdateWidget(covariant DynamicFormWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!mapEquals(oldWidget.initialData, widget.initialData)) {
      _formData = Map<String, Object?>.of(widget.initialData);
    }
  }

  void _updateField(String key, Object? value) {
    setState(() {
      _formData[key] = value;
    });
    widget.onChanged(Map<String, Object?>.unmodifiable(_formData));
  }

  @override
  Widget build(BuildContext context) {
    try {
      final rawProperties = widget.schema['properties'];
      if (rawProperties is! Map<String, Object?> || rawProperties.isEmpty) {
        throw AppException.validation(
          'Fail-Fast: DynamicFormWidget schema must contain a non-empty "properties" Map<String, Object?>.',
        );
      }

      final requiredFields = <String>{};
      if (widget.schema.containsKey('required') &&
          widget.schema['required'] != null) {
        final rawRequired = widget.schema['required'];
        if (rawRequired is! List<Object?>) {
          throw AppException.validation(
            'Fail-Fast: DynamicFormWidget schema "required" field must be a List<String>.',
          );
        }
        for (final item in rawRequired) {
          if (item is! String || item.trim().isEmpty) {
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
        if (key.trim().isEmpty || fieldSchema is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Property "$key" in DynamicFormWidget schema must be a valid Map<String, Object?>.',
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
