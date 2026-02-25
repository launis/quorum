// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_dto.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StepDTOCWProxy {
  StepDTO id(String id);

  StepDTO name(String? name);

  StepDTO taskKey(String taskKey);

  StepDTO description(String? description);

  StepDTO config(Map<String, Object>? config);

  StepDTO inputs(Map<String, String>? inputs);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  StepDTO call({
    String id,
    String? name,
    String taskKey,
    String? description,
    Map<String, Object>? config,
    Map<String, String>? inputs,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfStepDTO.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfStepDTO.copyWith.fieldName(...)`
class _$StepDTOCWProxyImpl implements _$StepDTOCWProxy {
  const _$StepDTOCWProxyImpl(this._value);

  final StepDTO _value;

  @override
  StepDTO id(String id) => this(id: id);

  @override
  StepDTO name(String? name) => this(name: name);

  @override
  StepDTO taskKey(String taskKey) => this(taskKey: taskKey);

  @override
  StepDTO description(String? description) => this(description: description);

  @override
  StepDTO config(Map<String, Object>? config) => this(config: config);

  @override
  StepDTO inputs(Map<String, String>? inputs) => this(inputs: inputs);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  StepDTO call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? taskKey = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? config = const $CopyWithPlaceholder(),
    Object? inputs = const $CopyWithPlaceholder(),
  }) {
    return StepDTO(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      taskKey: taskKey == const $CopyWithPlaceholder()
          ? _value.taskKey
          // ignore: cast_nullable_to_non_nullable
          : taskKey as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      config: config == const $CopyWithPlaceholder()
          ? _value.config
          // ignore: cast_nullable_to_non_nullable
          : config as Map<String, Object>?,
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as Map<String, String>?,
    );
  }
}

extension $StepDTOCopyWith on StepDTO {
  /// Returns a callable class that can be used as follows: `instanceOfStepDTO.copyWith(...)` or like so:`instanceOfStepDTO.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StepDTOCWProxy get copyWith => _$StepDTOCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StepDTO _$StepDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate('StepDTO', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['id', 'task_key']);
      final val = StepDTO(
        id: $checkedConvert('id', (v) => v as String),
        name: $checkedConvert('name', (v) => v as String?),
        taskKey: $checkedConvert('task_key', (v) => v as String),
        description: $checkedConvert('description', (v) => v as String?),
        config: $checkedConvert(
          'config',
          (v) => (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as Object),
          ),
        ),
        inputs: $checkedConvert(
          'inputs',
          (v) =>
              (v as Map<String, dynamic>?)?.map(
                (k, e) => MapEntry(k, e as String),
              ) ??
              {},
        ),
      );
      return val;
    }, fieldKeyMap: const {'taskKey': 'task_key'});

Map<String, dynamic> _$StepDTOToJson(StepDTO instance) => <String, dynamic>{
  'id': instance.id,
  'name': ?instance.name,
  'task_key': instance.taskKey,
  'description': ?instance.description,
  'config': ?instance.config,
  'inputs': ?instance.inputs,
};
