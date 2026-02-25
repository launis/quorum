// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_definition.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StepDefinitionCWProxy {
  StepDefinition id(String? id);

  StepDefinition slug(String? slug);

  StepDefinition name(String name);

  StepDefinition description(String? description);

  StepDefinition taskKey(String? taskKey);

  StepDefinition config(Map<String, Object>? config);

  StepDefinition inputs(Map<String, String>? inputs);

  StepDefinition isMissingRegistry(bool? isMissingRegistry);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  StepDefinition call({
    String? id,
    String? slug,
    String name,
    String? description,
    String? taskKey,
    Map<String, Object>? config,
    Map<String, String>? inputs,
    bool? isMissingRegistry,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfStepDefinition.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfStepDefinition.copyWith.fieldName(...)`
class _$StepDefinitionCWProxyImpl implements _$StepDefinitionCWProxy {
  const _$StepDefinitionCWProxyImpl(this._value);

  final StepDefinition _value;

  @override
  StepDefinition id(String? id) => this(id: id);

  @override
  StepDefinition slug(String? slug) => this(slug: slug);

  @override
  StepDefinition name(String name) => this(name: name);

  @override
  StepDefinition description(String? description) =>
      this(description: description);

  @override
  StepDefinition taskKey(String? taskKey) => this(taskKey: taskKey);

  @override
  StepDefinition config(Map<String, Object>? config) => this(config: config);

  @override
  StepDefinition inputs(Map<String, String>? inputs) => this(inputs: inputs);

  @override
  StepDefinition isMissingRegistry(bool? isMissingRegistry) =>
      this(isMissingRegistry: isMissingRegistry);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  StepDefinition call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? taskKey = const $CopyWithPlaceholder(),
    Object? config = const $CopyWithPlaceholder(),
    Object? inputs = const $CopyWithPlaceholder(),
    Object? isMissingRegistry = const $CopyWithPlaceholder(),
  }) {
    return StepDefinition(
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
      taskKey: taskKey == const $CopyWithPlaceholder()
          ? _value.taskKey
          // ignore: cast_nullable_to_non_nullable
          : taskKey as String?,
      config: config == const $CopyWithPlaceholder()
          ? _value.config
          // ignore: cast_nullable_to_non_nullable
          : config as Map<String, Object>?,
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as Map<String, String>?,
      isMissingRegistry: isMissingRegistry == const $CopyWithPlaceholder()
          ? _value.isMissingRegistry
          // ignore: cast_nullable_to_non_nullable
          : isMissingRegistry as bool?,
    );
  }
}

extension $StepDefinitionCopyWith on StepDefinition {
  /// Returns a callable class that can be used as follows: `instanceOfStepDefinition.copyWith(...)` or like so:`instanceOfStepDefinition.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StepDefinitionCWProxy get copyWith => _$StepDefinitionCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StepDefinition _$StepDefinitionFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'StepDefinition',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['name']);
        final val = StepDefinition(
          id: $checkedConvert('id', (v) => v as String?),
          slug: $checkedConvert('slug', (v) => v as String?),
          name: $checkedConvert('name', (v) => v as String),
          description: $checkedConvert('description', (v) => v as String?),
          taskKey: $checkedConvert(
            'task_key',
            (v) => v as String? ?? 'analyst',
          ),
          config: $checkedConvert(
            'config',
            (v) =>
                (v as Map<String, dynamic>?)?.map(
                  (k, e) => MapEntry(k, e as Object),
                ) ??
                {},
          ),
          inputs: $checkedConvert(
            'inputs',
            (v) =>
                (v as Map<String, dynamic>?)?.map(
                  (k, e) => MapEntry(k, e as String),
                ) ??
                {},
          ),
          isMissingRegistry: $checkedConvert(
            'is_missing_registry',
            (v) => v as bool? ?? false,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'taskKey': 'task_key',
        'isMissingRegistry': 'is_missing_registry',
      },
    );

Map<String, dynamic> _$StepDefinitionToJson(StepDefinition instance) =>
    <String, dynamic>{
      'id': ?instance.id,
      'slug': ?instance.slug,
      'name': instance.name,
      'description': ?instance.description,
      'task_key': ?instance.taskKey,
      'config': ?instance.config,
      'inputs': ?instance.inputs,
      'is_missing_registry': ?instance.isMissingRegistry,
    };
