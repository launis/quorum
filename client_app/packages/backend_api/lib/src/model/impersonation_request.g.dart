// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'impersonation_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ImpersonationRequestCWProxy {
  ImpersonationRequest targetId(String targetId);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ImpersonationRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ImpersonationRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ImpersonationRequest call({String targetId});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfImpersonationRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfImpersonationRequest.copyWith.fieldName(...)`
class _$ImpersonationRequestCWProxyImpl
    implements _$ImpersonationRequestCWProxy {
  const _$ImpersonationRequestCWProxyImpl(this._value);

  final ImpersonationRequest _value;

  @override
  ImpersonationRequest targetId(String targetId) => this(targetId: targetId);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ImpersonationRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ImpersonationRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ImpersonationRequest call({Object? targetId = const $CopyWithPlaceholder()}) {
    return ImpersonationRequest(
      targetId: targetId == const $CopyWithPlaceholder()
          ? _value.targetId
          // ignore: cast_nullable_to_non_nullable
          : targetId as String,
    );
  }
}

extension $ImpersonationRequestCopyWith on ImpersonationRequest {
  /// Returns a callable class that can be used as follows: `instanceOfImpersonationRequest.copyWith(...)` or like so:`instanceOfImpersonationRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ImpersonationRequestCWProxy get copyWith =>
      _$ImpersonationRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ImpersonationRequest _$ImpersonationRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ImpersonationRequest', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['target_id']);
  final val = ImpersonationRequest(
    targetId: $checkedConvert('target_id', (v) => v as String),
  );
  return val;
}, fieldKeyMap: const {'targetId': 'target_id'});

Map<String, dynamic> _$ImpersonationRequestToJson(
  ImpersonationRequest instance,
) => <String, dynamic>{'target_id': instance.targetId};
