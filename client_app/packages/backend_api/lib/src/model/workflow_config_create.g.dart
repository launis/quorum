// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_config_create.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowConfigCreateCWProxy {
  WorkflowConfigCreate id(String? id);

  WorkflowConfigCreate slug(String? slug);

  WorkflowConfigCreate name(String name);

  WorkflowConfigCreate sequence(List<String>? sequence);

  WorkflowConfigCreate description(String? description);

  WorkflowConfigCreate defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowConfigCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowConfigCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowConfigCreate call({
    String? id,
    String? slug,
    String name,
    List<String>? sequence,
    String? description,
    Map<String, String>? defaultModelMapping,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowConfigCreate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowConfigCreate.copyWith.fieldName(...)`
class _$WorkflowConfigCreateCWProxyImpl
    implements _$WorkflowConfigCreateCWProxy {
  const _$WorkflowConfigCreateCWProxyImpl(this._value);

  final WorkflowConfigCreate _value;

  @override
  WorkflowConfigCreate id(String? id) => this(id: id);

  @override
  WorkflowConfigCreate slug(String? slug) => this(slug: slug);

  @override
  WorkflowConfigCreate name(String name) => this(name: name);

  @override
  WorkflowConfigCreate sequence(List<String>? sequence) =>
      this(sequence: sequence);

  @override
  WorkflowConfigCreate description(String? description) =>
      this(description: description);

  @override
  WorkflowConfigCreate defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowConfigCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowConfigCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowConfigCreate call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? sequence = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
  }) {
    return WorkflowConfigCreate(
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
      sequence: sequence == const $CopyWithPlaceholder()
          ? _value.sequence
          // ignore: cast_nullable_to_non_nullable
          : sequence as List<String>?,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      defaultModelMapping: defaultModelMapping == const $CopyWithPlaceholder()
          ? _value.defaultModelMapping
          // ignore: cast_nullable_to_non_nullable
          : defaultModelMapping as Map<String, String>?,
    );
  }
}

extension $WorkflowConfigCreateCopyWith on WorkflowConfigCreate {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowConfigCreate.copyWith(...)` or like so:`instanceOfWorkflowConfigCreate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowConfigCreateCWProxy get copyWith =>
      _$WorkflowConfigCreateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowConfigCreate _$WorkflowConfigCreateFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'WorkflowConfigCreate',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['name']);
    final val = WorkflowConfigCreate(
      id: $checkedConvert('id', (v) => v as String?),
      slug: $checkedConvert('slug', (v) => v as String?),
      name: $checkedConvert('name', (v) => v as String),
      sequence: $checkedConvert(
        'sequence',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      ),
      description: $checkedConvert('description', (v) => v as String?),
      defaultModelMapping: $checkedConvert(
        'default_model_mapping',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'defaultModelMapping': 'default_model_mapping'},
);

Map<String, dynamic> _$WorkflowConfigCreateToJson(
  WorkflowConfigCreate instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'slug': ?instance.slug,
  'name': instance.name,
  'sequence': ?instance.sequence,
  'description': ?instance.description,
  'default_model_mapping': ?instance.defaultModelMapping,
};
