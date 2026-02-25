// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_template.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowTemplateCWProxy {
  WorkflowTemplate name(String name);

  WorkflowTemplate description(String description);

  WorkflowTemplate steps(List<String> steps);

  WorkflowTemplate defaultModelMapping(Map<String, String> defaultModelMapping);

  WorkflowTemplate uiSchema(Map<String, Object> uiSchema);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowTemplate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowTemplate(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowTemplate call({
    String name,
    String description,
    List<String> steps,
    Map<String, String> defaultModelMapping,
    Map<String, Object> uiSchema,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowTemplate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowTemplate.copyWith.fieldName(...)`
class _$WorkflowTemplateCWProxyImpl implements _$WorkflowTemplateCWProxy {
  const _$WorkflowTemplateCWProxyImpl(this._value);

  final WorkflowTemplate _value;

  @override
  WorkflowTemplate name(String name) => this(name: name);

  @override
  WorkflowTemplate description(String description) =>
      this(description: description);

  @override
  WorkflowTemplate steps(List<String> steps) => this(steps: steps);

  @override
  WorkflowTemplate defaultModelMapping(
    Map<String, String> defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  WorkflowTemplate uiSchema(Map<String, Object> uiSchema) =>
      this(uiSchema: uiSchema);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowTemplate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowTemplate(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowTemplate call({
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
    Object? uiSchema = const $CopyWithPlaceholder(),
  }) {
    return WorkflowTemplate(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String,
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as List<String>,
      defaultModelMapping: defaultModelMapping == const $CopyWithPlaceholder()
          ? _value.defaultModelMapping
          // ignore: cast_nullable_to_non_nullable
          : defaultModelMapping as Map<String, String>,
      uiSchema: uiSchema == const $CopyWithPlaceholder()
          ? _value.uiSchema
          // ignore: cast_nullable_to_non_nullable
          : uiSchema as Map<String, Object>,
    );
  }
}

extension $WorkflowTemplateCopyWith on WorkflowTemplate {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowTemplate.copyWith(...)` or like so:`instanceOfWorkflowTemplate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowTemplateCWProxy get copyWith => _$WorkflowTemplateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowTemplate _$WorkflowTemplateFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'WorkflowTemplate',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'name',
            'description',
            'steps',
            'default_model_mapping',
            'ui_schema',
          ],
        );
        final val = WorkflowTemplate(
          name: $checkedConvert('name', (v) => v as String),
          description: $checkedConvert('description', (v) => v as String),
          steps: $checkedConvert(
            'steps',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          defaultModelMapping: $checkedConvert(
            'default_model_mapping',
            (v) => Map<String, String>.from(v as Map),
          ),
          uiSchema: $checkedConvert(
            'ui_schema',
            (v) => (v as Map<String, dynamic>).map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'defaultModelMapping': 'default_model_mapping',
        'uiSchema': 'ui_schema',
      },
    );

Map<String, dynamic> _$WorkflowTemplateToJson(WorkflowTemplate instance) =>
    <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'steps': instance.steps,
      'default_model_mapping': instance.defaultModelMapping,
      'ui_schema': instance.uiSchema,
    };
