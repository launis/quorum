// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_step.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowStepCWProxy {
  WorkflowStep id(String? id);

  WorkflowStep slug(String? slug);

  WorkflowStep name(String name);

  WorkflowStep description(String? description);

  WorkflowStep taskKey(String taskKey);

  WorkflowStep inputs(Map<String, String>? inputs);

  WorkflowStep config(Map<String, Object>? config);

  WorkflowStep isMissingRegistry(bool? isMissingRegistry);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowStep(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowStep(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowStep call({
    String? id,
    String? slug,
    String name,
    String? description,
    String taskKey,
    Map<String, String>? inputs,
    Map<String, Object>? config,
    bool? isMissingRegistry,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowStep.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowStep.copyWith.fieldName(...)`
class _$WorkflowStepCWProxyImpl implements _$WorkflowStepCWProxy {
  const _$WorkflowStepCWProxyImpl(this._value);

  final WorkflowStep _value;

  @override
  WorkflowStep id(String? id) => this(id: id);

  @override
  WorkflowStep slug(String? slug) => this(slug: slug);

  @override
  WorkflowStep name(String name) => this(name: name);

  @override
  WorkflowStep description(String? description) =>
      this(description: description);

  @override
  WorkflowStep taskKey(String taskKey) => this(taskKey: taskKey);

  @override
  WorkflowStep inputs(Map<String, String>? inputs) => this(inputs: inputs);

  @override
  WorkflowStep config(Map<String, Object>? config) => this(config: config);

  @override
  WorkflowStep isMissingRegistry(bool? isMissingRegistry) =>
      this(isMissingRegistry: isMissingRegistry);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowStep(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowStep(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowStep call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? taskKey = const $CopyWithPlaceholder(),
    Object? inputs = const $CopyWithPlaceholder(),
    Object? config = const $CopyWithPlaceholder(),
    Object? isMissingRegistry = const $CopyWithPlaceholder(),
  }) {
    return WorkflowStep(
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
          : taskKey as String,
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as Map<String, String>?,
      config: config == const $CopyWithPlaceholder()
          ? _value.config
          // ignore: cast_nullable_to_non_nullable
          : config as Map<String, Object>?,
      isMissingRegistry: isMissingRegistry == const $CopyWithPlaceholder()
          ? _value.isMissingRegistry
          // ignore: cast_nullable_to_non_nullable
          : isMissingRegistry as bool?,
    );
  }
}

extension $WorkflowStepCopyWith on WorkflowStep {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowStep.copyWith(...)` or like so:`instanceOfWorkflowStep.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowStepCWProxy get copyWith => _$WorkflowStepCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowStep _$WorkflowStepFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'WorkflowStep',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['name', 'task_key']);
        final val = WorkflowStep(
          id: $checkedConvert('id', (v) => v as String?),
          slug: $checkedConvert('slug', (v) => v as String?),
          name: $checkedConvert('name', (v) => v as String),
          description: $checkedConvert('description', (v) => v as String?),
          taskKey: $checkedConvert('task_key', (v) => v as String),
          inputs: $checkedConvert(
            'inputs',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ),
          ),
          config: $checkedConvert(
            'config',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
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

Map<String, dynamic> _$WorkflowStepToJson(WorkflowStep instance) =>
    <String, dynamic>{
      'id': ?instance.id,
      'slug': ?instance.slug,
      'name': instance.name,
      'description': ?instance.description,
      'task_key': instance.taskKey,
      'inputs': ?instance.inputs,
      'config': ?instance.config,
      'is_missing_registry': ?instance.isMissingRegistry,
    };
