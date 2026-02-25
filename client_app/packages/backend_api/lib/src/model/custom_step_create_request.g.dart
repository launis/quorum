// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'custom_step_create_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CustomStepCreateRequestCWProxy {
  CustomStepCreateRequest componentType(String componentType);

  CustomStepCreateRequest nameHint(String? nameHint);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CustomStepCreateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CustomStepCreateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CustomStepCreateRequest call({String componentType, String? nameHint});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCustomStepCreateRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCustomStepCreateRequest.copyWith.fieldName(...)`
class _$CustomStepCreateRequestCWProxyImpl
    implements _$CustomStepCreateRequestCWProxy {
  const _$CustomStepCreateRequestCWProxyImpl(this._value);

  final CustomStepCreateRequest _value;

  @override
  CustomStepCreateRequest componentType(String componentType) =>
      this(componentType: componentType);

  @override
  CustomStepCreateRequest nameHint(String? nameHint) =>
      this(nameHint: nameHint);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CustomStepCreateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CustomStepCreateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CustomStepCreateRequest call({
    Object? componentType = const $CopyWithPlaceholder(),
    Object? nameHint = const $CopyWithPlaceholder(),
  }) {
    return CustomStepCreateRequest(
      componentType: componentType == const $CopyWithPlaceholder()
          ? _value.componentType
          // ignore: cast_nullable_to_non_nullable
          : componentType as String,
      nameHint: nameHint == const $CopyWithPlaceholder()
          ? _value.nameHint
          // ignore: cast_nullable_to_non_nullable
          : nameHint as String?,
    );
  }
}

extension $CustomStepCreateRequestCopyWith on CustomStepCreateRequest {
  /// Returns a callable class that can be used as follows: `instanceOfCustomStepCreateRequest.copyWith(...)` or like so:`instanceOfCustomStepCreateRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CustomStepCreateRequestCWProxy get copyWith =>
      _$CustomStepCreateRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CustomStepCreateRequest _$CustomStepCreateRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'CustomStepCreateRequest',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['component_type']);
    final val = CustomStepCreateRequest(
      componentType: $checkedConvert('component_type', (v) => v as String),
      nameHint: $checkedConvert('name_hint', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'componentType': 'component_type',
    'nameHint': 'name_hint',
  },
);

Map<String, dynamic> _$CustomStepCreateRequestToJson(
  CustomStepCreateRequest instance,
) => <String, dynamic>{
  'component_type': instance.componentType,
  'name_hint': ?instance.nameHint,
};
