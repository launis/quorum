// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'login_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$LoginResponseCWProxy {
  LoginResponse user(User user);

  LoginResponse tokenValid(bool tokenValid);

  LoginResponse debugMsg(String? debugMsg);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LoginResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LoginResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  LoginResponse call({User user, bool tokenValid, String? debugMsg});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfLoginResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfLoginResponse.copyWith.fieldName(...)`
class _$LoginResponseCWProxyImpl implements _$LoginResponseCWProxy {
  const _$LoginResponseCWProxyImpl(this._value);

  final LoginResponse _value;

  @override
  LoginResponse user(User user) => this(user: user);

  @override
  LoginResponse tokenValid(bool tokenValid) => this(tokenValid: tokenValid);

  @override
  LoginResponse debugMsg(String? debugMsg) => this(debugMsg: debugMsg);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LoginResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LoginResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  LoginResponse call({
    Object? user = const $CopyWithPlaceholder(),
    Object? tokenValid = const $CopyWithPlaceholder(),
    Object? debugMsg = const $CopyWithPlaceholder(),
  }) {
    return LoginResponse(
      user: user == const $CopyWithPlaceholder()
          ? _value.user
          // ignore: cast_nullable_to_non_nullable
          : user as User,
      tokenValid: tokenValid == const $CopyWithPlaceholder()
          ? _value.tokenValid
          // ignore: cast_nullable_to_non_nullable
          : tokenValid as bool,
      debugMsg: debugMsg == const $CopyWithPlaceholder()
          ? _value.debugMsg
          // ignore: cast_nullable_to_non_nullable
          : debugMsg as String?,
    );
  }
}

extension $LoginResponseCopyWith on LoginResponse {
  /// Returns a callable class that can be used as follows: `instanceOfLoginResponse.copyWith(...)` or like so:`instanceOfLoginResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$LoginResponseCWProxy get copyWith => _$LoginResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LoginResponse _$LoginResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'LoginResponse',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['user', 'token_valid']);
        final val = LoginResponse(
          user: $checkedConvert(
            'user',
            (v) => User.fromJson(v as Map<String, dynamic>),
          ),
          tokenValid: $checkedConvert('token_valid', (v) => v as bool),
          debugMsg: $checkedConvert('debug_msg', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {'tokenValid': 'token_valid', 'debugMsg': 'debug_msg'},
    );

Map<String, dynamic> _$LoginResponseToJson(LoginResponse instance) =>
    <String, dynamic>{
      'user': instance.user.toJson(),
      'token_valid': instance.tokenValid,
      'debug_msg': ?instance.debugMsg,
    };
