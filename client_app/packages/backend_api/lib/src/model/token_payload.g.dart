// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'token_payload.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TokenPayloadCWProxy {
  TokenPayload token(String token);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TokenPayload(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TokenPayload(...).copyWith(id: 12, name: "My name")
  /// ````
  TokenPayload call({String token});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTokenPayload.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTokenPayload.copyWith.fieldName(...)`
class _$TokenPayloadCWProxyImpl implements _$TokenPayloadCWProxy {
  const _$TokenPayloadCWProxyImpl(this._value);

  final TokenPayload _value;

  @override
  TokenPayload token(String token) => this(token: token);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TokenPayload(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TokenPayload(...).copyWith(id: 12, name: "My name")
  /// ````
  TokenPayload call({Object? token = const $CopyWithPlaceholder()}) {
    return TokenPayload(
      token: token == const $CopyWithPlaceholder()
          ? _value.token
          // ignore: cast_nullable_to_non_nullable
          : token as String,
    );
  }
}

extension $TokenPayloadCopyWith on TokenPayload {
  /// Returns a callable class that can be used as follows: `instanceOfTokenPayload.copyWith(...)` or like so:`instanceOfTokenPayload.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TokenPayloadCWProxy get copyWith => _$TokenPayloadCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TokenPayload _$TokenPayloadFromJson(Map<String, dynamic> json) =>
    $checkedCreate('TokenPayload', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['token']);
      final val = TokenPayload(
        token: $checkedConvert('token', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$TokenPayloadToJson(TokenPayload instance) =>
    <String, dynamic>{'token': instance.token};
