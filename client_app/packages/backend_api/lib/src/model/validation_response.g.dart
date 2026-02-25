// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'validation_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ValidationResponseCWProxy {
  ValidationResponse valid(bool valid);

  ValidationResponse reason(String? reason);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ValidationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ValidationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ValidationResponse call({bool valid, String? reason});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfValidationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfValidationResponse.copyWith.fieldName(...)`
class _$ValidationResponseCWProxyImpl implements _$ValidationResponseCWProxy {
  const _$ValidationResponseCWProxyImpl(this._value);

  final ValidationResponse _value;

  @override
  ValidationResponse valid(bool valid) => this(valid: valid);

  @override
  ValidationResponse reason(String? reason) => this(reason: reason);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ValidationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ValidationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ValidationResponse call({
    Object? valid = const $CopyWithPlaceholder(),
    Object? reason = const $CopyWithPlaceholder(),
  }) {
    return ValidationResponse(
      valid: valid == const $CopyWithPlaceholder()
          ? _value.valid
          // ignore: cast_nullable_to_non_nullable
          : valid as bool,
      reason: reason == const $CopyWithPlaceholder()
          ? _value.reason
          // ignore: cast_nullable_to_non_nullable
          : reason as String?,
    );
  }
}

extension $ValidationResponseCopyWith on ValidationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfValidationResponse.copyWith(...)` or like so:`instanceOfValidationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ValidationResponseCWProxy get copyWith =>
      _$ValidationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ValidationResponse _$ValidationResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('ValidationResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['valid']);
      final val = ValidationResponse(
        valid: $checkedConvert('valid', (v) => v as bool),
        reason: $checkedConvert('reason', (v) => v as String?),
      );
      return val;
    });

Map<String, dynamic> _$ValidationResponseToJson(ValidationResponse instance) =>
    <String, dynamic>{'valid': instance.valid, 'reason': ?instance.reason};
