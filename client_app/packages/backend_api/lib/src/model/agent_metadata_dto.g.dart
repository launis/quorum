// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'agent_metadata_dto.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AgentMetadataDTOCWProxy {
  AgentMetadataDTO name(String name);

  AgentMetadataDTO description(String description);

  AgentMetadataDTO inputs(List<String> inputs);

  AgentMetadataDTO outputs(List<String>? outputs);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentMetadataDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentMetadataDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentMetadataDTO call({
    String name,
    String description,
    List<String> inputs,
    List<String>? outputs,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAgentMetadataDTO.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAgentMetadataDTO.copyWith.fieldName(...)`
class _$AgentMetadataDTOCWProxyImpl implements _$AgentMetadataDTOCWProxy {
  const _$AgentMetadataDTOCWProxyImpl(this._value);

  final AgentMetadataDTO _value;

  @override
  AgentMetadataDTO name(String name) => this(name: name);

  @override
  AgentMetadataDTO description(String description) =>
      this(description: description);

  @override
  AgentMetadataDTO inputs(List<String> inputs) => this(inputs: inputs);

  @override
  AgentMetadataDTO outputs(List<String>? outputs) => this(outputs: outputs);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentMetadataDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentMetadataDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentMetadataDTO call({
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? inputs = const $CopyWithPlaceholder(),
    Object? outputs = const $CopyWithPlaceholder(),
  }) {
    return AgentMetadataDTO(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String,
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as List<String>,
      outputs: outputs == const $CopyWithPlaceholder()
          ? _value.outputs
          // ignore: cast_nullable_to_non_nullable
          : outputs as List<String>?,
    );
  }
}

extension $AgentMetadataDTOCopyWith on AgentMetadataDTO {
  /// Returns a callable class that can be used as follows: `instanceOfAgentMetadataDTO.copyWith(...)` or like so:`instanceOfAgentMetadataDTO.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AgentMetadataDTOCWProxy get copyWith => _$AgentMetadataDTOCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AgentMetadataDTO _$AgentMetadataDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AgentMetadataDTO', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['name', 'description', 'inputs']);
      final val = AgentMetadataDTO(
        name: $checkedConvert('name', (v) => v as String),
        description: $checkedConvert('description', (v) => v as String),
        inputs: $checkedConvert(
          'inputs',
          (v) => (v as List<dynamic>).map((e) => e as String).toList(),
        ),
        outputs: $checkedConvert(
          'outputs',
          (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
        ),
      );
      return val;
    });

Map<String, dynamic> _$AgentMetadataDTOToJson(AgentMetadataDTO instance) =>
    <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'inputs': instance.inputs,
      'outputs': ?instance.outputs,
    };
