// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'body_run_agent_agents_agent_name_run_post.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BodyRunAgentAgentsAgentNameRunPostCWProxy {
  BodyRunAgentAgentsAgentNameRunPost inputs(Map<String, Object> inputs);

  BodyRunAgentAgentsAgentNameRunPost systemInstruction(
    String? systemInstruction,
  );

  BodyRunAgentAgentsAgentNameRunPost model(String? model);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyRunAgentAgentsAgentNameRunPost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyRunAgentAgentsAgentNameRunPost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyRunAgentAgentsAgentNameRunPost call({
    Map<String, Object> inputs,
    String? systemInstruction,
    String? model,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBodyRunAgentAgentsAgentNameRunPost.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBodyRunAgentAgentsAgentNameRunPost.copyWith.fieldName(...)`
class _$BodyRunAgentAgentsAgentNameRunPostCWProxyImpl
    implements _$BodyRunAgentAgentsAgentNameRunPostCWProxy {
  const _$BodyRunAgentAgentsAgentNameRunPostCWProxyImpl(this._value);

  final BodyRunAgentAgentsAgentNameRunPost _value;

  @override
  BodyRunAgentAgentsAgentNameRunPost inputs(Map<String, Object> inputs) =>
      this(inputs: inputs);

  @override
  BodyRunAgentAgentsAgentNameRunPost systemInstruction(
    String? systemInstruction,
  ) => this(systemInstruction: systemInstruction);

  @override
  BodyRunAgentAgentsAgentNameRunPost model(String? model) => this(model: model);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyRunAgentAgentsAgentNameRunPost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyRunAgentAgentsAgentNameRunPost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyRunAgentAgentsAgentNameRunPost call({
    Object? inputs = const $CopyWithPlaceholder(),
    Object? systemInstruction = const $CopyWithPlaceholder(),
    Object? model = const $CopyWithPlaceholder(),
  }) {
    return BodyRunAgentAgentsAgentNameRunPost(
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as Map<String, Object>,
      systemInstruction: systemInstruction == const $CopyWithPlaceholder()
          ? _value.systemInstruction
          // ignore: cast_nullable_to_non_nullable
          : systemInstruction as String?,
      model: model == const $CopyWithPlaceholder()
          ? _value.model
          // ignore: cast_nullable_to_non_nullable
          : model as String?,
    );
  }
}

extension $BodyRunAgentAgentsAgentNameRunPostCopyWith
    on BodyRunAgentAgentsAgentNameRunPost {
  /// Returns a callable class that can be used as follows: `instanceOfBodyRunAgentAgentsAgentNameRunPost.copyWith(...)` or like so:`instanceOfBodyRunAgentAgentsAgentNameRunPost.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BodyRunAgentAgentsAgentNameRunPostCWProxy get copyWith =>
      _$BodyRunAgentAgentsAgentNameRunPostCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BodyRunAgentAgentsAgentNameRunPost _$BodyRunAgentAgentsAgentNameRunPostFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'BodyRunAgentAgentsAgentNameRunPost',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['inputs']);
    final val = BodyRunAgentAgentsAgentNameRunPost(
      inputs: $checkedConvert(
        'inputs',
        (v) =>
            (v as Map<String, dynamic>).map((k, e) => MapEntry(k, e as Object)),
      ),
      systemInstruction: $checkedConvert(
        'system_instruction',
        (v) => v as String?,
      ),
      model: $checkedConvert('model', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'systemInstruction': 'system_instruction'},
);

Map<String, dynamic> _$BodyRunAgentAgentsAgentNameRunPostToJson(
  BodyRunAgentAgentsAgentNameRunPost instance,
) => <String, dynamic>{
  'inputs': instance.inputs,
  'system_instruction': ?instance.systemInstruction,
  'model': ?instance.model,
};
