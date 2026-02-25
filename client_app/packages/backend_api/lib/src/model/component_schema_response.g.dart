// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'component_schema_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ComponentSchemaResponseCWProxy {
  ComponentSchemaResponse schema(Map<String, Object> schema);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentSchemaResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentSchemaResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentSchemaResponse call({Map<String, Object> schema});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfComponentSchemaResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfComponentSchemaResponse.copyWith.fieldName(...)`
class _$ComponentSchemaResponseCWProxyImpl
    implements _$ComponentSchemaResponseCWProxy {
  const _$ComponentSchemaResponseCWProxyImpl(this._value);

  final ComponentSchemaResponse _value;

  @override
  ComponentSchemaResponse schema(Map<String, Object> schema) =>
      this(schema: schema);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentSchemaResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentSchemaResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentSchemaResponse call({
    Object? schema = const $CopyWithPlaceholder(),
  }) {
    return ComponentSchemaResponse(
      schema: schema == const $CopyWithPlaceholder()
          ? _value.schema
          // ignore: cast_nullable_to_non_nullable
          : schema as Map<String, Object>,
    );
  }
}

extension $ComponentSchemaResponseCopyWith on ComponentSchemaResponse {
  /// Returns a callable class that can be used as follows: `instanceOfComponentSchemaResponse.copyWith(...)` or like so:`instanceOfComponentSchemaResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ComponentSchemaResponseCWProxy get copyWith =>
      _$ComponentSchemaResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ComponentSchemaResponse _$ComponentSchemaResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ComponentSchemaResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['schema']);
  final val = ComponentSchemaResponse(
    schema: $checkedConvert(
      'schema',
      (v) =>
          (v as Map<String, dynamic>).map((k, e) => MapEntry(k, e as Object)),
    ),
  );
  return val;
});

Map<String, dynamic> _$ComponentSchemaResponseToJson(
  ComponentSchemaResponse instance,
) => <String, dynamic>{'schema': instance.schema};
