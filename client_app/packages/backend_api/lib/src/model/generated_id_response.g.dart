// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generated_id_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$GeneratedIdResponseCWProxy {
  GeneratedIdResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GeneratedIdResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GeneratedIdResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  GeneratedIdResponse call({String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfGeneratedIdResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfGeneratedIdResponse.copyWith.fieldName(...)`
class _$GeneratedIdResponseCWProxyImpl implements _$GeneratedIdResponseCWProxy {
  const _$GeneratedIdResponseCWProxyImpl(this._value);

  final GeneratedIdResponse _value;

  @override
  GeneratedIdResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GeneratedIdResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GeneratedIdResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  GeneratedIdResponse call({Object? id = const $CopyWithPlaceholder()}) {
    return GeneratedIdResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
    );
  }
}

extension $GeneratedIdResponseCopyWith on GeneratedIdResponse {
  /// Returns a callable class that can be used as follows: `instanceOfGeneratedIdResponse.copyWith(...)` or like so:`instanceOfGeneratedIdResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$GeneratedIdResponseCWProxy get copyWith =>
      _$GeneratedIdResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GeneratedIdResponse _$GeneratedIdResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('GeneratedIdResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['id']);
      final val = GeneratedIdResponse(
        id: $checkedConvert('id', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$GeneratedIdResponseToJson(
  GeneratedIdResponse instance,
) => <String, dynamic>{'id': instance.id};
