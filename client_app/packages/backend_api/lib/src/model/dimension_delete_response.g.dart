// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dimension_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$DimensionDeleteResponseCWProxy {
  DimensionDeleteResponse status(String status);

  DimensionDeleteResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `DimensionDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// DimensionDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  DimensionDeleteResponse call({String status, String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfDimensionDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfDimensionDeleteResponse.copyWith.fieldName(...)`
class _$DimensionDeleteResponseCWProxyImpl
    implements _$DimensionDeleteResponseCWProxy {
  const _$DimensionDeleteResponseCWProxyImpl(this._value);

  final DimensionDeleteResponse _value;

  @override
  DimensionDeleteResponse status(String status) => this(status: status);

  @override
  DimensionDeleteResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `DimensionDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// DimensionDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  DimensionDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return DimensionDeleteResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
    );
  }
}

extension $DimensionDeleteResponseCopyWith on DimensionDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfDimensionDeleteResponse.copyWith(...)` or like so:`instanceOfDimensionDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$DimensionDeleteResponseCWProxy get copyWith =>
      _$DimensionDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DimensionDeleteResponse _$DimensionDeleteResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('DimensionDeleteResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'id']);
  final val = DimensionDeleteResponse(
    status: $checkedConvert('status', (v) => v as String),
    id: $checkedConvert('id', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$DimensionDeleteResponseToJson(
  DimensionDeleteResponse instance,
) => <String, dynamic>{'status': instance.status, 'id': instance.id};
