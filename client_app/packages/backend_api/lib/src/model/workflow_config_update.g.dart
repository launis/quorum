// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_config_update.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowConfigUpdateCWProxy {
  WorkflowConfigUpdate steps(List<Map<String, Object>>? steps);

  WorkflowConfigUpdate sequence(List<String>? sequence);

  WorkflowConfigUpdate description(String? description);

  WorkflowConfigUpdate defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowConfigUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowConfigUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowConfigUpdate call({
    List<Map<String, Object>>? steps,
    List<String>? sequence,
    String? description,
    Map<String, String>? defaultModelMapping,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowConfigUpdate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowConfigUpdate.copyWith.fieldName(...)`
class _$WorkflowConfigUpdateCWProxyImpl
    implements _$WorkflowConfigUpdateCWProxy {
  const _$WorkflowConfigUpdateCWProxyImpl(this._value);

  final WorkflowConfigUpdate _value;

  @override
  WorkflowConfigUpdate steps(List<Map<String, Object>>? steps) =>
      this(steps: steps);

  @override
  WorkflowConfigUpdate sequence(List<String>? sequence) =>
      this(sequence: sequence);

  @override
  WorkflowConfigUpdate description(String? description) =>
      this(description: description);

  @override
  WorkflowConfigUpdate defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowConfigUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowConfigUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowConfigUpdate call({
    Object? steps = const $CopyWithPlaceholder(),
    Object? sequence = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
  }) {
    return WorkflowConfigUpdate(
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as List<Map<String, Object>>?,
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

extension $WorkflowConfigUpdateCopyWith on WorkflowConfigUpdate {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowConfigUpdate.copyWith(...)` or like so:`instanceOfWorkflowConfigUpdate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowConfigUpdateCWProxy get copyWith =>
      _$WorkflowConfigUpdateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowConfigUpdate _$WorkflowConfigUpdateFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'WorkflowConfigUpdate',
  json,
  ($checkedConvert) {
    final val = WorkflowConfigUpdate(
      steps: $checkedConvert(
        'steps',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) => (e as Map<String, dynamic>).map(
                (k, e) => MapEntry(k, e as Object),
              ),
            )
            .toList(),
      ),
      sequence: $checkedConvert(
        'sequence',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
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

Map<String, dynamic> _$WorkflowConfigUpdateToJson(
  WorkflowConfigUpdate instance,
) => <String, dynamic>{
  'steps': ?instance.steps,
  'sequence': ?instance.sequence,
  'description': ?instance.description,
  'default_model_mapping': ?instance.defaultModelMapping,
};
