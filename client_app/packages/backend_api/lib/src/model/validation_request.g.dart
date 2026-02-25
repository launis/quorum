// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'validation_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ValidationRequestCWProxy {
  ValidationRequest sourceStep(String sourceStep);

  ValidationRequest targetStep(String targetStep);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ValidationRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ValidationRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ValidationRequest call({String sourceStep, String targetStep});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfValidationRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfValidationRequest.copyWith.fieldName(...)`
class _$ValidationRequestCWProxyImpl implements _$ValidationRequestCWProxy {
  const _$ValidationRequestCWProxyImpl(this._value);

  final ValidationRequest _value;

  @override
  ValidationRequest sourceStep(String sourceStep) =>
      this(sourceStep: sourceStep);

  @override
  ValidationRequest targetStep(String targetStep) =>
      this(targetStep: targetStep);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ValidationRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ValidationRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ValidationRequest call({
    Object? sourceStep = const $CopyWithPlaceholder(),
    Object? targetStep = const $CopyWithPlaceholder(),
  }) {
    return ValidationRequest(
      sourceStep: sourceStep == const $CopyWithPlaceholder()
          ? _value.sourceStep
          // ignore: cast_nullable_to_non_nullable
          : sourceStep as String,
      targetStep: targetStep == const $CopyWithPlaceholder()
          ? _value.targetStep
          // ignore: cast_nullable_to_non_nullable
          : targetStep as String,
    );
  }
}

extension $ValidationRequestCopyWith on ValidationRequest {
  /// Returns a callable class that can be used as follows: `instanceOfValidationRequest.copyWith(...)` or like so:`instanceOfValidationRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ValidationRequestCWProxy get copyWith =>
      _$ValidationRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ValidationRequest _$ValidationRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'ValidationRequest',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['source_step', 'target_step']);
        final val = ValidationRequest(
          sourceStep: $checkedConvert('source_step', (v) => v as String),
          targetStep: $checkedConvert('target_step', (v) => v as String),
        );
        return val;
      },
      fieldKeyMap: const {
        'sourceStep': 'source_step',
        'targetStep': 'target_step',
      },
    );

Map<String, dynamic> _$ValidationRequestToJson(ValidationRequest instance) =>
    <String, dynamic>{
      'source_step': instance.sourceStep,
      'target_step': instance.targetStep,
    };
