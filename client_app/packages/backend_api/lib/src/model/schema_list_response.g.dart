// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'schema_list_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SchemaListResponseCWProxy {
  SchemaListResponse items(Map<String, SchemaInfo> items);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SchemaListResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SchemaListResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SchemaListResponse call({Map<String, SchemaInfo> items});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSchemaListResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSchemaListResponse.copyWith.fieldName(...)`
class _$SchemaListResponseCWProxyImpl implements _$SchemaListResponseCWProxy {
  const _$SchemaListResponseCWProxyImpl(this._value);

  final SchemaListResponse _value;

  @override
  SchemaListResponse items(Map<String, SchemaInfo> items) => this(items: items);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SchemaListResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SchemaListResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SchemaListResponse call({Object? items = const $CopyWithPlaceholder()}) {
    return SchemaListResponse(
      items: items == const $CopyWithPlaceholder()
          ? _value.items
          // ignore: cast_nullable_to_non_nullable
          : items as Map<String, SchemaInfo>,
    );
  }
}

extension $SchemaListResponseCopyWith on SchemaListResponse {
  /// Returns a callable class that can be used as follows: `instanceOfSchemaListResponse.copyWith(...)` or like so:`instanceOfSchemaListResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SchemaListResponseCWProxy get copyWith =>
      _$SchemaListResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SchemaListResponse _$SchemaListResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SchemaListResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['items']);
      final val = SchemaListResponse(
        items: $checkedConvert(
          'items',
          (v) => (v as Map<String, dynamic>).map(
            (k, e) =>
                MapEntry(k, SchemaInfo.fromJson(e as Map<String, dynamic>)),
          ),
        ),
      );
      return val;
    });

Map<String, dynamic> _$SchemaListResponseToJson(SchemaListResponse instance) =>
    <String, dynamic>{
      'items': instance.items.map((k, e) => MapEntry(k, e.toJson())),
    };
