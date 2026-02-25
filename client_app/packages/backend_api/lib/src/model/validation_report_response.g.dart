// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'validation_report_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ValidationReportResponseCWProxy {
  ValidationReportResponse valid(bool valid);

  ValidationReportResponse errors(List<String> errors);

  ValidationReportResponse trace(List<String> trace);

  ValidationReportResponse finalStateKeys(List<String> finalStateKeys);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ValidationReportResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ValidationReportResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ValidationReportResponse call({
    bool valid,
    List<String> errors,
    List<String> trace,
    List<String> finalStateKeys,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfValidationReportResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfValidationReportResponse.copyWith.fieldName(...)`
class _$ValidationReportResponseCWProxyImpl
    implements _$ValidationReportResponseCWProxy {
  const _$ValidationReportResponseCWProxyImpl(this._value);

  final ValidationReportResponse _value;

  @override
  ValidationReportResponse valid(bool valid) => this(valid: valid);

  @override
  ValidationReportResponse errors(List<String> errors) => this(errors: errors);

  @override
  ValidationReportResponse trace(List<String> trace) => this(trace: trace);

  @override
  ValidationReportResponse finalStateKeys(List<String> finalStateKeys) =>
      this(finalStateKeys: finalStateKeys);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ValidationReportResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ValidationReportResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ValidationReportResponse call({
    Object? valid = const $CopyWithPlaceholder(),
    Object? errors = const $CopyWithPlaceholder(),
    Object? trace = const $CopyWithPlaceholder(),
    Object? finalStateKeys = const $CopyWithPlaceholder(),
  }) {
    return ValidationReportResponse(
      valid: valid == const $CopyWithPlaceholder()
          ? _value.valid
          // ignore: cast_nullable_to_non_nullable
          : valid as bool,
      errors: errors == const $CopyWithPlaceholder()
          ? _value.errors
          // ignore: cast_nullable_to_non_nullable
          : errors as List<String>,
      trace: trace == const $CopyWithPlaceholder()
          ? _value.trace
          // ignore: cast_nullable_to_non_nullable
          : trace as List<String>,
      finalStateKeys: finalStateKeys == const $CopyWithPlaceholder()
          ? _value.finalStateKeys
          // ignore: cast_nullable_to_non_nullable
          : finalStateKeys as List<String>,
    );
  }
}

extension $ValidationReportResponseCopyWith on ValidationReportResponse {
  /// Returns a callable class that can be used as follows: `instanceOfValidationReportResponse.copyWith(...)` or like so:`instanceOfValidationReportResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ValidationReportResponseCWProxy get copyWith =>
      _$ValidationReportResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ValidationReportResponse _$ValidationReportResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ValidationReportResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['valid', 'errors', 'trace', 'final_state_keys'],
    );
    final val = ValidationReportResponse(
      valid: $checkedConvert('valid', (v) => v as bool),
      errors: $checkedConvert(
        'errors',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
      trace: $checkedConvert(
        'trace',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
      finalStateKeys: $checkedConvert(
        'final_state_keys',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'finalStateKeys': 'final_state_keys'},
);

Map<String, dynamic> _$ValidationReportResponseToJson(
  ValidationReportResponse instance,
) => <String, dynamic>{
  'valid': instance.valid,
  'errors': instance.errors,
  'trace': instance.trace,
  'final_state_keys': instance.finalStateKeys,
};
