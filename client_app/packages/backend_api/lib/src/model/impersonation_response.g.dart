// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'impersonation_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ImpersonationResponseCWProxy {
  ImpersonationResponse accessToken(String accessToken);

  ImpersonationResponse tokenType(String? tokenType);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ImpersonationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ImpersonationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ImpersonationResponse call({String accessToken, String? tokenType});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfImpersonationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfImpersonationResponse.copyWith.fieldName(...)`
class _$ImpersonationResponseCWProxyImpl
    implements _$ImpersonationResponseCWProxy {
  const _$ImpersonationResponseCWProxyImpl(this._value);

  final ImpersonationResponse _value;

  @override
  ImpersonationResponse accessToken(String accessToken) =>
      this(accessToken: accessToken);

  @override
  ImpersonationResponse tokenType(String? tokenType) =>
      this(tokenType: tokenType);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ImpersonationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ImpersonationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ImpersonationResponse call({
    Object? accessToken = const $CopyWithPlaceholder(),
    Object? tokenType = const $CopyWithPlaceholder(),
  }) {
    return ImpersonationResponse(
      accessToken: accessToken == const $CopyWithPlaceholder()
          ? _value.accessToken
          // ignore: cast_nullable_to_non_nullable
          : accessToken as String,
      tokenType: tokenType == const $CopyWithPlaceholder()
          ? _value.tokenType
          // ignore: cast_nullable_to_non_nullable
          : tokenType as String?,
    );
  }
}

extension $ImpersonationResponseCopyWith on ImpersonationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfImpersonationResponse.copyWith(...)` or like so:`instanceOfImpersonationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ImpersonationResponseCWProxy get copyWith =>
      _$ImpersonationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ImpersonationResponse _$ImpersonationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ImpersonationResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['access_token']);
    final val = ImpersonationResponse(
      accessToken: $checkedConvert('access_token', (v) => v as String),
      tokenType: $checkedConvert('token_type', (v) => v as String? ?? 'bearer'),
    );
    return val;
  },
  fieldKeyMap: const {'accessToken': 'access_token', 'tokenType': 'token_type'},
);

Map<String, dynamic> _$ImpersonationResponseToJson(
  ImpersonationResponse instance,
) => <String, dynamic>{
  'access_token': instance.accessToken,
  'token_type': ?instance.tokenType,
};
