// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'agent_definition.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AgentDefinitionCWProxy {
  AgentDefinition name(String name);

  AgentDefinition class_(String class_);

  AgentDefinition description(String description);

  AgentDefinition model(String model);

  AgentDefinition inputSchema(Map<String, Object>? inputSchema);

  AgentDefinition outputSchema(Map<String, Object>? outputSchema);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentDefinition call({
    String name,
    String class_,
    String description,
    String model,
    Map<String, Object>? inputSchema,
    Map<String, Object>? outputSchema,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAgentDefinition.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAgentDefinition.copyWith.fieldName(...)`
class _$AgentDefinitionCWProxyImpl implements _$AgentDefinitionCWProxy {
  const _$AgentDefinitionCWProxyImpl(this._value);

  final AgentDefinition _value;

  @override
  AgentDefinition name(String name) => this(name: name);

  @override
  AgentDefinition class_(String class_) => this(class_: class_);

  @override
  AgentDefinition description(String description) =>
      this(description: description);

  @override
  AgentDefinition model(String model) => this(model: model);

  @override
  AgentDefinition inputSchema(Map<String, Object>? inputSchema) =>
      this(inputSchema: inputSchema);

  @override
  AgentDefinition outputSchema(Map<String, Object>? outputSchema) =>
      this(outputSchema: outputSchema);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentDefinition call({
    Object? name = const $CopyWithPlaceholder(),
    Object? class_ = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? model = const $CopyWithPlaceholder(),
    Object? inputSchema = const $CopyWithPlaceholder(),
    Object? outputSchema = const $CopyWithPlaceholder(),
  }) {
    return AgentDefinition(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      class_: class_ == const $CopyWithPlaceholder()
          ? _value.class_
          // ignore: cast_nullable_to_non_nullable
          : class_ as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String,
      model: model == const $CopyWithPlaceholder()
          ? _value.model
          // ignore: cast_nullable_to_non_nullable
          : model as String,
      inputSchema: inputSchema == const $CopyWithPlaceholder()
          ? _value.inputSchema
          // ignore: cast_nullable_to_non_nullable
          : inputSchema as Map<String, Object>?,
      outputSchema: outputSchema == const $CopyWithPlaceholder()
          ? _value.outputSchema
          // ignore: cast_nullable_to_non_nullable
          : outputSchema as Map<String, Object>?,
    );
  }
}

extension $AgentDefinitionCopyWith on AgentDefinition {
  /// Returns a callable class that can be used as follows: `instanceOfAgentDefinition.copyWith(...)` or like so:`instanceOfAgentDefinition.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AgentDefinitionCWProxy get copyWith => _$AgentDefinitionCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AgentDefinition _$AgentDefinitionFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'AgentDefinition',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const ['name', 'class', 'description', 'model'],
        );
        final val = AgentDefinition(
          name: $checkedConvert('name', (v) => v as String),
          class_: $checkedConvert('class', (v) => v as String),
          description: $checkedConvert('description', (v) => v as String),
          model: $checkedConvert('model', (v) => v as String),
          inputSchema: $checkedConvert(
            'input_schema',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
          outputSchema: $checkedConvert(
            'output_schema',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'class_': 'class',
        'inputSchema': 'input_schema',
        'outputSchema': 'output_schema',
      },
    );

Map<String, dynamic> _$AgentDefinitionToJson(AgentDefinition instance) =>
    <String, dynamic>{
      'name': instance.name,
      'class': instance.class_,
      'description': instance.description,
      'model': instance.model,
      'input_schema': ?instance.inputSchema,
      'output_schema': ?instance.outputSchema,
    };
