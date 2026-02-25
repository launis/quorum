// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_config_definition.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowConfigDefinitionCWProxy {
  WorkflowConfigDefinition id(String? id);

  WorkflowConfigDefinition slug(String? slug);

  WorkflowConfigDefinition name(String name);

  WorkflowConfigDefinition description(String? description);

  WorkflowConfigDefinition sequence(List<String>? sequence);

  WorkflowConfigDefinition steps(Steps? steps);

  WorkflowConfigDefinition uiSchema(Map<String, Object>? uiSchema);

  WorkflowConfigDefinition defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowConfigDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowConfigDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowConfigDefinition call({
    String? id,
    String? slug,
    String name,
    String? description,
    List<String>? sequence,
    Steps? steps,
    Map<String, Object>? uiSchema,
    Map<String, String>? defaultModelMapping,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowConfigDefinition.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowConfigDefinition.copyWith.fieldName(...)`
class _$WorkflowConfigDefinitionCWProxyImpl
    implements _$WorkflowConfigDefinitionCWProxy {
  const _$WorkflowConfigDefinitionCWProxyImpl(this._value);

  final WorkflowConfigDefinition _value;

  @override
  WorkflowConfigDefinition id(String? id) => this(id: id);

  @override
  WorkflowConfigDefinition slug(String? slug) => this(slug: slug);

  @override
  WorkflowConfigDefinition name(String name) => this(name: name);

  @override
  WorkflowConfigDefinition description(String? description) =>
      this(description: description);

  @override
  WorkflowConfigDefinition sequence(List<String>? sequence) =>
      this(sequence: sequence);

  @override
  WorkflowConfigDefinition steps(Steps? steps) => this(steps: steps);

  @override
  WorkflowConfigDefinition uiSchema(Map<String, Object>? uiSchema) =>
      this(uiSchema: uiSchema);

  @override
  WorkflowConfigDefinition defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowConfigDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowConfigDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowConfigDefinition call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? sequence = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
    Object? uiSchema = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
  }) {
    return WorkflowConfigDefinition(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
      slug: slug == const $CopyWithPlaceholder()
          ? _value.slug
          // ignore: cast_nullable_to_non_nullable
          : slug as String?,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      sequence: sequence == const $CopyWithPlaceholder()
          ? _value.sequence
          // ignore: cast_nullable_to_non_nullable
          : sequence as List<String>?,
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as Steps?,
      uiSchema: uiSchema == const $CopyWithPlaceholder()
          ? _value.uiSchema
          // ignore: cast_nullable_to_non_nullable
          : uiSchema as Map<String, Object>?,
      defaultModelMapping: defaultModelMapping == const $CopyWithPlaceholder()
          ? _value.defaultModelMapping
          // ignore: cast_nullable_to_non_nullable
          : defaultModelMapping as Map<String, String>?,
    );
  }
}

extension $WorkflowConfigDefinitionCopyWith on WorkflowConfigDefinition {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowConfigDefinition.copyWith(...)` or like so:`instanceOfWorkflowConfigDefinition.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowConfigDefinitionCWProxy get copyWith =>
      _$WorkflowConfigDefinitionCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowConfigDefinition _$WorkflowConfigDefinitionFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'WorkflowConfigDefinition',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['name']);
    final val = WorkflowConfigDefinition(
      id: $checkedConvert('id', (v) => v as String?),
      slug: $checkedConvert('slug', (v) => v as String?),
      name: $checkedConvert('name', (v) => v as String),
      description: $checkedConvert('description', (v) => v as String?),
      sequence: $checkedConvert(
        'sequence',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      ),
      steps: $checkedConvert(
        'steps',
        (v) => v == null ? null : Steps.fromJson(v as Map<String, dynamic>),
      ),
      uiSchema: $checkedConvert(
        'ui_schema',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      defaultModelMapping: $checkedConvert(
        'default_model_mapping',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'uiSchema': 'ui_schema',
    'defaultModelMapping': 'default_model_mapping',
  },
);

Map<String, dynamic> _$WorkflowConfigDefinitionToJson(
  WorkflowConfigDefinition instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'slug': ?instance.slug,
  'name': instance.name,
  'description': ?instance.description,
  'sequence': ?instance.sequence,
  'steps': ?instance.steps?.toJson(),
  'ui_schema': ?instance.uiSchema,
  'default_model_mapping': ?instance.defaultModelMapping,
};
