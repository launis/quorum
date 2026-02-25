// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'schema_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SchemaResponseCWProxy {
  SchemaResponse modelName(String modelName);

  SchemaResponse schemaDef(Map<String, Object> schemaDef);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SchemaResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SchemaResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SchemaResponse call({String modelName, Map<String, Object> schemaDef});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSchemaResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSchemaResponse.copyWith.fieldName(...)`
class _$SchemaResponseCWProxyImpl implements _$SchemaResponseCWProxy {
  const _$SchemaResponseCWProxyImpl(this._value);

  final SchemaResponse _value;

  @override
  SchemaResponse modelName(String modelName) => this(modelName: modelName);

  @override
  SchemaResponse schemaDef(Map<String, Object> schemaDef) =>
      this(schemaDef: schemaDef);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SchemaResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SchemaResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SchemaResponse call({
    Object? modelName = const $CopyWithPlaceholder(),
    Object? schemaDef = const $CopyWithPlaceholder(),
  }) {
    return SchemaResponse(
      modelName: modelName == const $CopyWithPlaceholder()
          ? _value.modelName
          // ignore: cast_nullable_to_non_nullable
          : modelName as String,
      schemaDef: schemaDef == const $CopyWithPlaceholder()
          ? _value.schemaDef
          // ignore: cast_nullable_to_non_nullable
          : schemaDef as Map<String, Object>,
    );
  }
}

extension $SchemaResponseCopyWith on SchemaResponse {
  /// Returns a callable class that can be used as follows: `instanceOfSchemaResponse.copyWith(...)` or like so:`instanceOfSchemaResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SchemaResponseCWProxy get copyWith => _$SchemaResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SchemaResponse _$SchemaResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SchemaResponse',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['model_name', 'schema_def']);
        final val = SchemaResponse(
          modelName: $checkedConvert('model_name', (v) => v as String),
          schemaDef: $checkedConvert(
            'schema_def',
            (v) => (v as Map<String, dynamic>).map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {'modelName': 'model_name', 'schemaDef': 'schema_def'},
    );

Map<String, dynamic> _$SchemaResponseToJson(SchemaResponse instance) =>
    <String, dynamic>{
      'model_name': instance.modelName,
      'schema_def': instance.schemaDef,
    };
