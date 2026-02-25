// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_update_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StepUpdateRequestCWProxy {
  StepUpdateRequest name(String? name);

  StepUpdateRequest config(Map<String, Object>? config);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepUpdateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepUpdateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  StepUpdateRequest call({String? name, Map<String, Object>? config});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfStepUpdateRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfStepUpdateRequest.copyWith.fieldName(...)`
class _$StepUpdateRequestCWProxyImpl implements _$StepUpdateRequestCWProxy {
  const _$StepUpdateRequestCWProxyImpl(this._value);

  final StepUpdateRequest _value;

  @override
  StepUpdateRequest name(String? name) => this(name: name);

  @override
  StepUpdateRequest config(Map<String, Object>? config) => this(config: config);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepUpdateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepUpdateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  StepUpdateRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? config = const $CopyWithPlaceholder(),
  }) {
    return StepUpdateRequest(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      config: config == const $CopyWithPlaceholder()
          ? _value.config
          // ignore: cast_nullable_to_non_nullable
          : config as Map<String, Object>?,
    );
  }
}

extension $StepUpdateRequestCopyWith on StepUpdateRequest {
  /// Returns a callable class that can be used as follows: `instanceOfStepUpdateRequest.copyWith(...)` or like so:`instanceOfStepUpdateRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StepUpdateRequestCWProxy get copyWith =>
      _$StepUpdateRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StepUpdateRequest _$StepUpdateRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('StepUpdateRequest', json, ($checkedConvert) {
      final val = StepUpdateRequest(
        name: $checkedConvert('name', (v) => v as String?),
        config: $checkedConvert(
          'config',
          (v) => (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as Object),
          ),
        ),
      );
      return val;
    });

Map<String, dynamic> _$StepUpdateRequestToJson(StepUpdateRequest instance) =>
    <String, dynamic>{'name': ?instance.name, 'config': ?instance.config};
