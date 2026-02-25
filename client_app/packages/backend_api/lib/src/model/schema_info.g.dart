// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'schema_info.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SchemaInfoCWProxy {
  SchemaInfo schema(Map<String, Object> schema);

  SchemaInfo example(dynamic example);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SchemaInfo(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SchemaInfo(...).copyWith(id: 12, name: "My name")
  /// ````
  SchemaInfo call({Map<String, Object> schema, dynamic example});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSchemaInfo.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSchemaInfo.copyWith.fieldName(...)`
class _$SchemaInfoCWProxyImpl implements _$SchemaInfoCWProxy {
  const _$SchemaInfoCWProxyImpl(this._value);

  final SchemaInfo _value;

  @override
  SchemaInfo schema(Map<String, Object> schema) => this(schema: schema);

  @override
  SchemaInfo example(dynamic example) => this(example: example);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SchemaInfo(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SchemaInfo(...).copyWith(id: 12, name: "My name")
  /// ````
  SchemaInfo call({
    Object? schema = const $CopyWithPlaceholder(),
    Object? example = const $CopyWithPlaceholder(),
  }) {
    return SchemaInfo(
      schema: schema == const $CopyWithPlaceholder()
          ? _value.schema
          // ignore: cast_nullable_to_non_nullable
          : schema as Map<String, Object>,
      example: example == const $CopyWithPlaceholder()
          ? _value.example
          // ignore: cast_nullable_to_non_nullable
          : example as dynamic,
    );
  }
}

extension $SchemaInfoCopyWith on SchemaInfo {
  /// Returns a callable class that can be used as follows: `instanceOfSchemaInfo.copyWith(...)` or like so:`instanceOfSchemaInfo.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SchemaInfoCWProxy get copyWith => _$SchemaInfoCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SchemaInfo _$SchemaInfoFromJson(Map<String, dynamic> json) => $checkedCreate(
  'SchemaInfo',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['schema']);
    final val = SchemaInfo(
      schema: $checkedConvert(
        'schema',
        (v) =>
            (v as Map<String, dynamic>).map((k, e) => MapEntry(k, e as Object)),
      ),
      example: $checkedConvert('example', (v) => v),
    );
    return val;
  },
);

Map<String, dynamic> _$SchemaInfoToJson(SchemaInfo instance) =>
    <String, dynamic>{'schema': instance.schema, 'example': ?instance.example};
